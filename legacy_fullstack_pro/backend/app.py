from flask import Flask, request, jsonify, send_from_directory, make_response, g, send_file
from pathlib import Path
import uuid, json, shutil, tempfile, io, time
from .config import Config
from .database import init_db, connect, now, audit
from .auth import hash_password, verify_password, create_session, set_session_cookie, clear_session_cookie, require_auth, rate_limit, token_hash
from .otp import OTPService
from .storage import safe_extract_zip, UploadError
from core.engine import analyze_project
from core.passport import verify_passport
from core.evidence import write_evidence_bundle


def create_app():
    cfg=Config.load(); init_db(cfg.db_path); otp=OTPService(cfg)
    app=Flask(__name__, static_folder=None); app.config['MAX_CONTENT_LENGTH']=cfg.max_upload_bytes

    @app.after_request
    def headers(resp):
        resp.headers['X-Content-Type-Options']='nosniff';resp.headers['X-Frame-Options']='DENY';resp.headers['Referrer-Policy']='no-referrer'
        resp.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        resp.headers['Content-Security-Policy']="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
        return resp

    @app.get('/')
    def index(): return send_from_directory(cfg.frontend_dir,'index.html')
    @app.get('/<path:path>')
    def static_files(path):
        p=cfg.frontend_dir/path
        if p.exists() and p.is_file(): return send_from_directory(cfg.frontend_dir,path)
        return send_from_directory(cfg.frontend_dir,'index.html')

    @app.get('/api/health')
    def health():return jsonify({'ok':True,'service':'RunProof','execution_mode':cfg.execution_mode})

    @app.post('/api/auth/signup')
    def signup():
        key=f"signup:{request.remote_addr}"
        if not rate_limit(key,5,300):return jsonify({'error':'rate_limited'}),429
        d=request.get_json(silent=True) or {}; name=d.get('name','').strip(); email=d.get('email','').strip().lower(); phone=d.get('phone','').strip(); password=d.get('password','')
        if not name or '@' not in email or len(phone)<7:return jsonify({'error':'invalid_input'}),400
        try: ph=hash_password(password)
        except ValueError as e:return jsonify({'error':str(e)}),400
        try:
            with connect(cfg.db_path) as c:c.execute('INSERT INTO users(name,email,phone,password_hash,created_at) VALUES(?,?,?,?,?)',(name,email,phone,ph,now()))
        except Exception:return jsonify({'error':'account_already_exists'}),409
        dev=otp.send(phone); audit(cfg.db_path,'signup',metadata={'email':email})
        out={'ok':True,'message':'OTP sent.','phone_masked':'***'+phone[-4:]}
        if dev:out['dev_otp']=dev
        return jsonify(out),201

    @app.post('/api/auth/resend-otp')
    def resend():
        if not rate_limit(f"otp:{request.remote_addr}",5,300):return jsonify({'error':'rate_limited'}),429
        phone=(request.get_json(silent=True) or {}).get('phone','').strip();
        if not phone:return jsonify({'error':'phone_required'}),400
        dev=otp.send(phone); out={'ok':True,'message':'OTP sent.'};
        if dev:out['dev_otp']=dev
        return jsonify(out)

    @app.post('/api/auth/verify-otp')
    def verify_otp_route():
        d=request.get_json(silent=True) or {};phone=d.get('phone','').strip();code=d.get('code','').strip()
        ok,msg=otp.verify(phone,code)
        if not ok:return jsonify({'error':msg}),400
        with connect(cfg.db_path) as c:
            c.execute('UPDATE users SET phone_verified=1 WHERE phone=?',(phone,)); user=c.execute('SELECT * FROM users WHERE phone=?',(phone,)).fetchone()
        if not user:return jsonify({'error':'user_not_found'}),404
        raw,_=create_session(cfg,user['id']);resp=make_response(jsonify({'ok':True,'user':{'id':user['id'],'name':user['name'],'email':user['email'],'phone':user['phone']}}));set_session_cookie(resp,raw,cfg);return resp

    @app.post('/api/auth/login')
    def login():
        if not rate_limit(f"login:{request.remote_addr}",8,300):return jsonify({'error':'rate_limited'}),429
        d=request.get_json(silent=True) or {};email=d.get('email','').strip().lower();password=d.get('password','')
        with connect(cfg.db_path) as c:user=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if not user or not verify_password(password,user['password_hash']):return jsonify({'error':'invalid_credentials'}),401
        if not user['phone_verified']:return jsonify({'error':'phone_not_verified'}),403
        raw,_=create_session(cfg,user['id']);resp=make_response(jsonify({'ok':True,'user':{'id':user['id'],'name':user['name'],'email':user['email'],'phone':user['phone']}}));set_session_cookie(resp,raw,cfg);audit(cfg.db_path,'login',user_id=user['id']);return resp

    @app.post('/api/auth/logout')
    def logout():
        raw=request.cookies.get('rp_session')
        if raw:
            with connect(cfg.db_path) as c:c.execute('DELETE FROM sessions WHERE token_hash=?',(token_hash(raw),))
        resp=make_response(jsonify({'ok':True}));clear_session_cookie(resp);return resp

    @app.get('/api/auth/me')
    @require_auth(cfg)
    def me():
        u=g.user;return jsonify({'id':u['id'],'name':u['name'],'email':u['email'],'phone':u['phone'],'phone_verified':bool(u['phone_verified'])})

    @app.get('/api/dashboard')
    @require_auth(cfg)
    def dashboard():
        uid=g.user['id']
        with connect(cfg.db_path) as c:
            projects=c.execute('SELECT COUNT(*) n FROM projects WHERE user_id=?',(uid,)).fetchone()['n']
            analyses=c.execute('SELECT a.result_json FROM analyses a JOIN projects p ON p.id=a.project_id WHERE p.user_id=? ORDER BY a.id DESC LIMIT 100',(uid,)).fetchall()
        scores=[];verified=0;issues=0
        for r in analyses:
            try:
                d=json.loads(r['result_json']);scores.append(float(d.get('score',{}).get('score',0)));verified += 1 if (d.get('verification') or {}).get('verified') else 0;issues += len(d.get('issues',[]))
            except:pass
        return jsonify({'projects':projects,'analyses':len(analyses),'verified':verified,'issues':issues,'average_score':round(sum(scores)/len(scores),1) if scores else 0})

    def owned_project(pid):
        with connect(cfg.db_path) as c:r=c.execute('SELECT * FROM projects WHERE id=? AND user_id=?',(pid,g.user['id'])).fetchone()
        return dict(r) if r else None

    @app.get('/api/projects')
    @require_auth(cfg)
    def list_projects():
        with connect(cfg.db_path) as c:rows=c.execute('SELECT id,name,source_filename,created_at FROM projects WHERE user_id=? ORDER BY created_at DESC',(g.user['id'],)).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post('/api/projects/upload')
    @require_auth(cfg)
    def upload_project():
        f=request.files.get('project_zip')
        if not f or not f.filename.lower().endswith('.zip'):return jsonify({'error':'Upload a .zip project file.'}),400
        pid=uuid.uuid4().hex[:16];base=cfg.project_dir/str(g.user['id'])/pid;base.mkdir(parents=True,exist_ok=True)
        zpath=base/'upload.zip';f.save(zpath)
        try: root=safe_extract_zip(zpath,base/'src',cfg)
        except UploadError as e:shutil.rmtree(base,ignore_errors=True);return jsonify({'error':str(e)}),400
        zpath.unlink(missing_ok=True);name=request.form.get('name','').strip() or Path(f.filename).stem
        with connect(cfg.db_path) as c:c.execute('INSERT INTO projects(id,user_id,name,root_path,source_filename,created_at) VALUES(?,?,?,?,?,?)',(pid,g.user['id'],name,str(root),f.filename,now()))
        audit(cfg.db_path,'project_uploaded',g.user['id'],pid,{'filename':f.filename})
        return jsonify({'id':pid,'name':name}),201

    @app.delete('/api/projects/<pid>')
    @require_auth(cfg)
    def delete_project(pid):
        p=owned_project(pid)
        if not p:return jsonify({'error':'not_found'}),404
        shutil.rmtree((cfg.project_dir/str(g.user['id'])/pid),ignore_errors=True)
        with connect(cfg.db_path) as c:c.execute('DELETE FROM projects WHERE id=?',(pid,))
        audit(cfg.db_path,'project_deleted',g.user['id'],pid);return jsonify({'ok':True})

    def run_analysis(pid, kind, verify=False):
        p=owned_project(pid)
        if not p:return None,(jsonify({'error':'not_found'}),404)
        analysis,passport,sbom,report=analyze_project(p['root_path'],cfg.execution_mode,cfg.exec_timeout,verify,cfg.secret_key)
        with connect(cfg.db_path) as c:c.execute('INSERT INTO analyses(project_id,kind,result_json,created_at) VALUES(?,?,?,?)',(pid,kind,json.dumps(analysis),now()))
        audit(cfg.db_path,kind,g.user['id'],pid,{'score':analysis['score']['score'],'verified':bool((analysis.get('verification') or {}).get('verified'))})
        return (analysis,passport,sbom,report),None

    @app.post('/api/projects/<pid>/check')
    @require_auth(cfg)
    def check(pid):
        r,e=run_analysis(pid,'check',False);return e if e else jsonify(r[0])

    @app.post('/api/projects/<pid>/verify')
    @require_auth(cfg)
    def verify(pid):
        r,e=run_analysis(pid,'verify',True);return e if e else jsonify(r[0])

    def latest_analysis(pid):
        p=owned_project(pid)
        if not p:return None,None
        with connect(cfg.db_path) as c:r=c.execute('SELECT result_json FROM analyses WHERE project_id=? ORDER BY id DESC LIMIT 1',(pid,)).fetchone()
        if not r:return p,None
        return p,json.loads(r['result_json'])

    @app.get('/api/projects/<pid>/passport')
    @require_auth(cfg)
    def passport(pid):
        p,a=latest_analysis(pid)
        if not p:return jsonify({'error':'not_found'}),404
        if not a:return jsonify({'error':'run_check_first'}),409
        from core.passport import make_passport
        return jsonify(make_passport(a,cfg.secret_key))

    @app.get('/api/projects/<pid>/report')
    @require_auth(cfg)
    def report(pid):
        p,a=latest_analysis(pid)
        if not p:return jsonify({'error':'not_found'}),404
        if not a:return jsonify({'error':'run_check_first'}),409
        from core.passport import make_passport
        from core.report import render_report
        html=render_report(a,make_passport(a,cfg.secret_key));resp=make_response(html);resp.headers['Content-Type']='text/html; charset=utf-8';resp.headers['Content-Disposition']=f'attachment; filename="runproof-{pid}-report.html"';return resp

    @app.get('/api/projects/<pid>/sbom')
    @require_auth(cfg)
    def sbom(pid):
        p,a=latest_analysis(pid)
        if not p:return jsonify({'error':'not_found'}),404
        if not a:return jsonify({'error':'run_check_first'}),409
        from core.sbom import make_sbom
        return jsonify(make_sbom(a['scan']['project_name'],a['detection']['type'],a['dependencies']))

    @app.get('/api/projects/<pid>/evidence')
    @require_auth(cfg)
    def evidence(pid):
        p,a=latest_analysis(pid)
        if not p:return jsonify({'error':'not_found'}),404
        if not a:return jsonify({'error':'run_check_first'}),409
        from core.passport import make_passport
        from core.sbom import make_sbom
        from core.report import render_report
        passport=make_passport(a,cfg.secret_key);sbom=make_sbom(a['scan']['project_name'],a['detection']['type'],a['dependencies']);report=render_report(a,passport)
        tmp=Path(tempfile.mkdtemp())/'runproof-evidence.zip';write_evidence_bundle(tmp,a,passport,sbom,report)
        return send_file(tmp,as_attachment=True,download_name=f'runproof-{pid}-evidence.zip')

    @app.post('/api/passports/verify')
    def verify_passport_route():
        p=request.get_json(silent=True) or {};return jsonify({'valid':verify_passport(p,cfg.secret_key)})

    @app.get('/api/projects/<pid>/activity')
    @require_auth(cfg)
    def activity(pid):
        if not owned_project(pid):return jsonify({'error':'not_found'}),404
        with connect(cfg.db_path) as c:rows=c.execute('SELECT event,metadata_json,created_at FROM audit_log WHERE project_id=? ORDER BY id DESC LIMIT 100',(pid,)).fetchall()
        return jsonify([{'event':r['event'],'metadata':json.loads(r['metadata_json']),'created_at':r['created_at']} for r in rows])

    @app.errorhandler(413)
    def too_large(_):return jsonify({'error':'upload_too_large'}),413

    return app
