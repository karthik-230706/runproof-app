from flask import Flask, request, jsonify, send_from_directory, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import sqlite3, os, secrets, time, json, shutil, tempfile, zipfile, hashlib, socket, re, base64, urllib.request, urllib.parse, urllib.error

from .core.analyzer import analyze_project
from .core.passport import create_passport
from .core.fingerprint import sha256_tree
from .core.verifier import verify_project

BASE = Path(__file__).resolve().parent.parent
FRONTEND = BASE / "frontend"
DATA = BASE / "backend" / "data"
UPLOADS = DATA / "uploads"
REPORTS = DATA / "reports"
for p in (DATA, UPLOADS, REPORTS):
    p.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE / ".env")

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
app.secret_key = os.environ.get("RUNPROOF_SECRET_KEY", secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # set True behind HTTPS in production
    MAX_CONTENT_LENGTH=50 * 1024 * 1024
)

DEMO_MODE = os.environ.get("RUNPROOF_DEMO_MODE","1") == "1"
EXECUTION_MODE = os.environ.get("RUNPROOF_EXECUTION_MODE","safe").strip().lower()
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_VERIFY_SERVICE_SID = os.environ.get("TWILIO_VERIFY_SERVICE_SID", "").strip()
DB = DATA / "runproof.db"
RATE = {}

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          phone TEXT,
          password_hash TEXT NOT NULL,
          phone_verified INTEGER DEFAULT 0,
          organization TEXT DEFAULT '',
          role TEXT DEFAULT 'Developer',
          bio TEXT DEFAULT '',
          notifications_read_at TEXT,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS otp_challenges(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          code_hash TEXT NOT NULL,
          expires_at TEXT NOT NULL,
          attempts INTEGER DEFAULT 0,
          used INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS projects(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          owner_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          path TEXT NOT NULL,
          created_at TEXT NOT NULL,
          last_score INTEGER,
          last_status TEXT,
          trusted_demo INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS audits(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          action TEXT NOT NULL,
          detail TEXT,
          created_at TEXT NOT NULL
        );
        """)
init_db()

def ensure_column(table, name, ddl):
    with db() as c:
        cols = {r[1] for r in c.execute(f"PRAGMA table_info({table})")}
        if name not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")

for _name, _ddl in [
    ("organization", "TEXT DEFAULT ''"),
    ("role", "TEXT DEFAULT 'Developer'"),
    ("bio", "TEXT DEFAULT ''"),
    ("notifications_read_at", "TEXT")
]:
    ensure_column("users", _name, _ddl)
ensure_column("projects", "trusted_demo", "INTEGER DEFAULT 0")


with db() as c:
    c.executescript("""
    CREATE TABLE IF NOT EXISTS api_tokens(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      label TEXT NOT NULL,
      prefix TEXT NOT NULL,
      token_hash TEXT NOT NULL UNIQUE,
      last4 TEXT NOT NULL,
      revoked INTEGER DEFAULT 0,
      created_at TEXT NOT NULL,
      last_used_at TEXT
    );
    CREATE TABLE IF NOT EXISTS team_invites(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      owner_id INTEGER NOT NULL,
      email TEXT NOT NULL,
      role TEXT NOT NULL,
      status TEXT DEFAULT 'pending',
      created_at TEXT NOT NULL
    );
    """)

def twilio_configured():
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_VERIFY_SERVICE_SID)

def _twilio_post(path, values):
    url = f"https://verify.twilio.com/v2/Services/{TWILIO_VERIFY_SERVICE_SID}/{path}"
    payload = urllib.parse.urlencode(values).encode("utf-8")
    token = base64.b64encode(f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode()).decode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Basic {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"SMS provider rejected the request: {detail[:300]}")
    except Exception as e:
        raise RuntimeError(f"Could not contact SMS provider: {e}")

def send_real_otp(phone):
    return _twilio_post("Verifications", {"To": phone, "Channel": "sms"})

def check_real_otp(phone, code):
    return _twilio_post("VerificationCheck", {"To": phone, "Code": code})

def mask_phone(phone):
    if not phone: return ""
    return phone[:3] + " •••••• " + phone[-3:] if len(phone) > 8 else phone

def nowiso():
    return datetime.now(timezone.utc).isoformat()

def audit(action, detail=""):
    uid = session.get("user_id")
    with db() as c:
        c.execute("INSERT INTO audits(user_id,action,detail,created_at) VALUES(?,?,?,?)",
                  (uid,action,detail,nowiso()))

def limited(key, limit=8, window=60):
    now = time.time()
    arr = [t for t in RATE.get(key,[]) if now-t < window]
    if len(arr) >= limit:
        RATE[key] = arr
        return True
    arr.append(now)
    RATE[key] = arr
    return False

def require_user():
    uid = session.get("user_id")
    if not uid:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer rp_live_"):
            token = auth.split(" ", 1)[1].strip()
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
            with db() as c:
                tok = c.execute("SELECT id,user_id FROM api_tokens WHERE token_hash=? AND revoked=0", (token_hash,)).fetchone()
                if tok:
                    uid = tok["user_id"]
                    c.execute("UPDATE api_tokens SET last_used_at=? WHERE id=?", (nowiso(), tok["id"]))
    if not uid:
        return None
    with db() as c:
        row = c.execute("SELECT id,name,email,phone,phone_verified,organization,role,bio,notifications_read_at,created_at FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None

def project_owned(project_id):
    user = require_user()
    if not user:
        return None
    with db() as c:
        row = c.execute("SELECT * FROM projects WHERE id=? AND owner_id=?", (project_id,user["id"])).fetchone()
        return dict(row) if row else None

@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return resp

@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")

@app.get("/api/health")
def health():
    return {"ok":True,"service":"RunProof","demo_mode":DEMO_MODE,"real_sms_otp":twilio_configured(),"execution_mode":EXECUTION_MODE}

@app.post("/api/auth/signup")
def signup():
    ip = request.remote_addr or "local"
    if limited("signup:"+ip, 8, 60):
        return jsonify(error="Too many signup attempts."), 429
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()[:100]
    email = (data.get("email") or "").strip().lower()[:180]
    phone = (data.get("phone") or "").strip()[:40]
    password = data.get("password") or ""
    if not name or "@" not in email or len(password) < 8:
        return jsonify(error="Use a name, valid email and password of at least 8 characters."),400
    if not re.match(r"^\+[1-9]\d{7,14}$", phone):
        return jsonify(error="Enter phone number with country code, for example +919876543210."),400
    try:
        with db() as c:
            cur = c.execute("INSERT INTO users(name,email,phone,password_hash,created_at) VALUES(?,?,?,?,?)",
                            (name,email,phone,generate_password_hash(password),nowiso()))
            uid = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify(error="Email already exists."),409

    expires = (datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
    try:
        if twilio_configured():
            send_real_otp(phone)
            otp_hash = "TWILIO_VERIFY"
            delivery = "sms"
            demo_otp = None
        elif DEMO_MODE:
            demo_otp = "482175"
            otp_hash = generate_password_hash(demo_otp)
            delivery = "demo"
        else:
            with db() as c:
                c.execute("DELETE FROM users WHERE id=?", (uid,))
            return jsonify(error="Real SMS OTP is required but SMS provider is not configured. Add Twilio Verify credentials in .env."),503
    except Exception as e:
        with db() as c:
            c.execute("DELETE FROM users WHERE id=?", (uid,))
        return jsonify(error=str(e)),502
    with db() as c:
        c.execute("INSERT INTO otp_challenges(user_id,code_hash,expires_at) VALUES(?,?,?)",(uid,otp_hash,expires))
    session["pending_user_id"] = uid
    audit("signup_started", email)
    response = {"ok":True,"message":"OTP sent.","delivery":delivery,"masked_phone":mask_phone(phone)}
    if demo_otp:
        response["demo_otp"] = demo_otp
    return jsonify(response)

@app.post("/api/auth/verify-otp")
def verify_otp():
    uid = session.get("pending_user_id")
    if not uid:
        return jsonify(error="No active OTP challenge."),400
    if limited(f"otp:{uid}", 6, 300):
        return jsonify(error="Too many OTP attempts. Try again later."),429
    code = (request.get_json(force=True).get("code") or "").strip()
    with db() as c:
        row = c.execute("SELECT * FROM otp_challenges WHERE user_id=? AND used=0 ORDER BY id DESC LIMIT 1",(uid,)).fetchone()
        if not row:
            return jsonify(error="OTP not found."),404
        if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            return jsonify(error="OTP expired."),400
        c.execute("UPDATE otp_challenges SET attempts=attempts+1 WHERE id=?",(row["id"],))
        if row["code_hash"] == "TWILIO_VERIFY":
            user_row = c.execute("SELECT phone FROM users WHERE id=?", (uid,)).fetchone()
            try:
                check = check_real_otp(user_row["phone"], code)
            except Exception as e:
                return jsonify(error=str(e)),502
            if check.get("status") != "approved":
                return jsonify(error="Incorrect or expired OTP."),400
        elif not check_password_hash(row["code_hash"],code):
            return jsonify(error="Incorrect OTP."),400
        c.execute("UPDATE otp_challenges SET used=1 WHERE id=?",(row["id"],))
        c.execute("UPDATE users SET phone_verified=1 WHERE id=?",(uid,))
    session.pop("pending_user_id",None)
    session["user_id"] = uid
    audit("phone_verified")
    return {"ok":True}

@app.post("/api/auth/login")
def login():
    ip = request.remote_addr or "local"
    if limited("login:"+ip, 12, 60):
        return jsonify(error="Too many login attempts."),429
    data=request.get_json(force=True)
    email=(data.get("email") or "").strip().lower()
    password=data.get("password") or ""
    with db() as c:
        row=c.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"],password):
        return jsonify(error="Invalid email or password."),401
    if not row["phone_verified"]:
        session["pending_user_id"] = row["id"]
        return jsonify(ok=True, requires_otp=True, message="Phone verification required.")
    session["user_id"]=row["id"]
    audit("login")
    return {"ok":True,"requires_otp":False}

@app.post("/api/auth/demo")
def demo_login():
    if not DEMO_MODE:
        return jsonify(error="Demo login is disabled."),403
    email=f"demo{int(time.time()*1000)}@runproof.local"
    password=generate_password_hash(secrets.token_urlsafe(18))
    with db() as c:
        cur=c.execute("INSERT INTO users(name,email,phone,password_hash,phone_verified,created_at) VALUES(?,?,?,?,1,?)",("Demo User",email,"+919000000000",password,nowiso()))
        uid=cur.lastrowid
    session["user_id"]=uid
    audit("demo_login")
    return {"ok":True}

@app.post("/api/auth/logout")
def logout():
    audit("logout")
    session.clear()
    return {"ok":True}

@app.get("/api/me")
def me():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    return u

@app.post("/api/auth/resend-otp")
def resend_otp():
    uid = session.get("pending_user_id")
    if not uid:
        return jsonify(error="No pending phone verification."),400
    if limited(f"resend:{uid}", 3, 300):
        return jsonify(error="Please wait before requesting another OTP."),429
    with db() as c:
        user = c.execute("SELECT phone FROM users WHERE id=?", (uid,)).fetchone()
    if not user:
        return jsonify(error="User not found."),404
    expires=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
    if twilio_configured():
        try: send_real_otp(user["phone"])
        except Exception as e: return jsonify(error=str(e)),502
        code_hash="TWILIO_VERIFY"; demo_otp=None; delivery="sms"
    elif DEMO_MODE:
        demo_otp="482175"; code_hash=generate_password_hash(demo_otp); delivery="demo"
    else:
        return jsonify(error="SMS provider is not configured."),503
    with db() as c:
        c.execute("UPDATE otp_challenges SET used=1 WHERE user_id=? AND used=0", (uid,))
        c.execute("INSERT INTO otp_challenges(user_id,code_hash,expires_at) VALUES(?,?,?)", (uid,code_hash,expires))
    response={"ok":True,"delivery":delivery,"masked_phone":mask_phone(user["phone"])}
    if demo_otp: response["demo_otp"]=demo_otp
    return jsonify(response)

@app.get("/api/profile")
def profile():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,last_score,last_status FROM projects WHERE owner_id=?",(u["id"],))]
    verified=sum(1 for r in rows if (r["last_status"] or "").lower().startswith("verified"))
    scores=[r["last_score"] for r in rows if r["last_score"] is not None]
    reports=sum(1 for r in rows if (REPORTS/f"report_{r['id']}.html").exists())
    passports=sum(1 for r in rows if (REPORTS/f"passport_{r['id']}.json").exists())
    return {"user":u,"stats":{"projects":len(rows),"verified":verified,"average_score":round(sum(scores)/len(scores)) if scores else 0,"passports":passports,"reports":reports}}

@app.put("/api/profile")
def update_profile():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    data=request.get_json(force=True)
    name=(data.get("name") or u["name"]).strip()[:100]
    organization=(data.get("organization") or "").strip()[:120]
    role=(data.get("role") or "Developer").strip()[:80]
    bio=(data.get("bio") or "").strip()[:300]
    with db() as c:
        c.execute("UPDATE users SET name=?,organization=?,role=?,bio=? WHERE id=?",(name,organization,role,bio,u["id"]))
    audit("profile_updated")
    return {"ok":True}

@app.post("/api/auth/change-password")
def change_password():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    data=request.get_json(force=True); old=data.get("old_password") or ""; new=data.get("new_password") or ""
    if len(new)<8:return jsonify(error="New password must contain at least 8 characters."),400
    with db() as c:
        row=c.execute("SELECT password_hash FROM users WHERE id=?",(u["id"],)).fetchone()
        if not check_password_hash(row["password_hash"],old):return jsonify(error="Current password is incorrect."),400
        c.execute("UPDATE users SET password_hash=? WHERE id=?",(generate_password_hash(new),u["id"]))
    audit("password_changed")
    return {"ok":True}

@app.get("/api/notifications")
def notifications_api():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    read_at=u.get("notifications_read_at")
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,action,detail,created_at FROM audits WHERE user_id=? ORDER BY id DESC LIMIT 30",(u["id"],))]
    def message(r):
        a=r["action"]
        title={"project_created":"Project added","project_analyzed":"Analysis completed","project_verified":"Verification completed","login":"New login","phone_verified":"Phone verified","profile_updated":"Profile updated","password_changed":"Password changed","report_generated":"Report generated","passport_opened":"Passport opened","api_token_created":"API token created","api_token_revoked":"API token revoked","team_invite_created":"Team invite created"}.get(a,a.replace("_"," ").title())
        return {**r,"title":title,"unread":not read_at or r["created_at"]>read_at}
    items=[message(r) for r in rows]
    return {"items":items,"unread":sum(1 for i in items if i["unread"])}

@app.post("/api/notifications/read-all")
def notifications_read_all():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:c.execute("UPDATE users SET notifications_read_at=? WHERE id=?",(nowiso(),u["id"]))
    return {"ok":True}

@app.get("/api/workspace")
def workspace_api():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,last_score,last_status,created_at FROM projects WHERE owner_id=? ORDER BY id DESC",(u["id"],))]
    return {"projects":rows,"empty":not bool(rows)}

@app.get("/api/projects/<int:project_id>")
def project_detail(project_id):
    p=project_owned(project_id)
    if not p:return jsonify(error="Project not found."),404
    analysis=analyze_project(p["path"])
    passport_exists=(REPORTS/f"passport_{project_id}.json").exists()
    return {"project":{k:p[k] for k in ("id","name","created_at","last_score","last_status")},"analysis":analysis,"passport_exists":passport_exists}

@app.get("/api/network-info")
def network_info():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    ip="127.0.0.1"
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sock.connect(("8.8.8.8",80)); ip=sock.getsockname()[0]; sock.close()
    except Exception: pass
    port=int(os.environ.get("RUNPROOF_PORT","8000"))
    return {"local_ip":ip,"url":f"http://{ip}:{port}","same_wifi_note":"This address normally works only for devices on the same local network, and Windows Firewall must allow Python on private networks."}

@app.post("/api/assistant")
def assistant_api():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    q=(request.get_json(force=True).get("message") or "").strip().lower()
    if not q:return {"answer":"Ask me how to add a project, understand a score, fix an issue, verify a build, open a passport, or share RunProof."}
    rules=[
      (("add project","upload","new project"),"Open New Analysis, choose a project ZIP, then press Continue. RunProof will scan it before showing checks."),
      (("otp","phone","code"),"For real phone OTP, RunProof uses the configured SMS Verify provider. Enter your phone with country code, for example +919876543210. You cannot continue signup until the OTP is approved."),
      (("score","readiness"),"The readiness score summarizes project type, runtime, required files, dependency stability, environment settings, security checks and test readiness. Open the Score page to see where points came from."),
      (("doctor","issue","fix"),"RunProof Doctor explains each issue in three parts: what happened, why it matters, and how to fix it."),
      (("verify","reproduc"),"Open Verify after analysis. The prototype compares two clean copies and fingerprints them. A production version should run independent builds inside an isolated sandbox before comparing artifacts."),
      (("passport",),"A RunProof Passport is the proof record created after verification. Open Passports from the sidebar or from a project detail page."),
      (("report",),"Open Reports to download the latest HTML analysis report for the selected project."),
      (("friend","other laptop","same wifi","share"),"Open Security Center → Network Sharing. Start RunProof on 0.0.0.0 and give your friend the local network URL shown there. Both devices must usually be on the same Wi‑Fi and Windows Firewall must allow Python."),
      (("security","password","secret"),"RunProof never displays stored passwords. Passwords are hashed on the backend, sessions are HttpOnly, and secret values should be redacted from reports."),
      (("team",),"Open Team Workspace to view roles. Owner, Developer and Viewer permissions can be connected to backend invitations in the next production stage."),
    ]
    for keys,ans in rules:
        if any(k in q for k in keys):return {"answer":ans}
    return {"answer":"I can guide you inside RunProof. Try asking: “How do I add a project?”, “Why is my score low?”, “How do I verify?”, “How do I share with another laptop?”, or “What is the Passport?”"}


@app.get("/api/otp-status")
def otp_status():
    return {
        "real_sms_configured": twilio_configured(),
        "demo_mode": DEMO_MODE,
        "provider": "Twilio Verify" if twilio_configured() else ("Demo OTP" if DEMO_MODE else "Not configured"),
        "real_sms_required_when_demo_off": True
    }

@app.get("/api/search")
def search_api():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    q=(request.args.get("q") or "").strip().lower()
    results=[]
    static=[
        ("New Analysis","new","Create and scan a project"),
        ("Workspace","workspace","Open all workspace projects"),
        ("Projects","projects","Browse project history"),
        ("RunProof Doctor","issues","View issues across projects"),
        ("Verifications","verifications","View verification history"),
        ("Passports","passports","Browse verified passports"),
        ("Reports","reports","Download project reports"),
        ("Security Center","security","Account and network security"),
        ("Settings","settings","RunProof preferences"),
        ("Help Center","help","Learn RunProof features"),
    ]
    if not q:
        for title,route,detail in static[:7]:
            results.append({"type":"route","title":title,"route":route,"detail":detail})
    else:
        for title,route,detail in static:
            if q in title.lower() or q in detail.lower():
                results.append({"type":"route","title":title,"route":route,"detail":detail})
        with db() as c:
            rows=c.execute("SELECT id,name,last_score,last_status FROM projects WHERE owner_id=? AND lower(name) LIKE ? ORDER BY id DESC LIMIT 10",
                           (u["id"], f"%{q}%")).fetchall()
        for r in rows:
            results.append({"type":"project","title":r["name"],"project_id":r["id"],"detail":f"Score {r['last_score'] if r['last_score'] is not None else '—'} · {r['last_status'] or 'New'}"})
    return {"results":results[:20]}

@app.get("/api/verifications")
def verification_list():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,last_score,last_status,created_at FROM projects WHERE owner_id=? ORDER BY id DESC",(u["id"],))]
    out=[]
    for r in rows:
        pp=REPORTS/f"passport_{r['id']}.json"
        out.append({**r,"passport_exists":pp.exists(),"verified":(r["last_status"] or "").lower().startswith("verified")})
    return {"items":out}

@app.get("/api/passports")
def passport_list():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,last_score,last_status,created_at FROM projects WHERE owner_id=? ORDER BY id DESC",(u["id"],))]
    items=[]
    for r in rows:
        pp=REPORTS/f"passport_{r['id']}.json"
        if pp.exists():
            try:
                data=json.loads(pp.read_text(encoding="utf-8"))
            except Exception:
                data={}
            items.append({
                "project_id":r["id"],"name":r["name"],"score":data.get("score",r["last_score"]),
                "status":r["last_status"],"issued_at":data.get("issued_at"),"signature":data.get("signature","")
            })
    return {"items":items}

@app.get("/api/reports")
def reports_list():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,last_score,last_status,created_at FROM projects WHERE owner_id=? ORDER BY id DESC",(u["id"],))]
    return {"items":[{**r,"report_exists":(REPORTS/f"report_{r['id']}.html").exists()} for r in rows]}

@app.get("/api/issues")
def issues_list():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,path,last_score,last_status FROM projects WHERE owner_id=? ORDER BY id DESC LIMIT 20",(u["id"],))]
    items=[]
    for p in rows:
        try:
            analysis=analyze_project(p["path"])
            for issue in analysis.get("issues",[]):
                if issue.get("severity")=="info" and len(analysis.get("issues",[]))==1:
                    continue
                items.append({"project_id":p["id"],"project_name":p["name"],**issue})
        except Exception as e:
            items.append({"project_id":p["id"],"project_name":p["name"],"severity":"high","title":"Analysis failed","what":str(e),"why":"RunProof could not inspect this project.","fix":"Open the project and run analysis again."})
    return {"items":items}

@app.get("/api/tokens")
def token_list():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,label,prefix,last4,revoked,created_at,last_used_at FROM api_tokens WHERE user_id=? ORDER BY id DESC",(u["id"],))]
    return {"items":rows}

@app.post("/api/tokens")
def token_create():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    data=request.get_json(force=True)
    label=(data.get("label") or "RunProof CLI").strip()[:80]
    token="rp_live_"+secrets.token_urlsafe(30)
    token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest()
    with db() as c:
        active=c.execute("SELECT count(*) FROM api_tokens WHERE user_id=? AND revoked=0",(u["id"],)).fetchone()[0]
        if active>=10:return jsonify(error="Maximum 10 active tokens."),400
        c.execute("INSERT INTO api_tokens(user_id,label,prefix,token_hash,last4,created_at) VALUES(?,?,?,?,?,?)",
                  (u["id"],label,"rp_live_",token_hash,token[-4:],nowiso()))
    audit("api_token_created",label)
    return {"ok":True,"token":token,"message":"Copy this token now. RunProof will not show the full token again."}

@app.delete("/api/tokens/<int:token_id>")
def token_revoke(token_id):
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        row=c.execute("SELECT id,label FROM api_tokens WHERE id=? AND user_id=?",(token_id,u["id"])).fetchone()
        if not row:return jsonify(error="Token not found."),404
        c.execute("UPDATE api_tokens SET revoked=1 WHERE id=?",(token_id,))
    audit("api_token_revoked",row["label"])
    return {"ok":True}

@app.get("/api/team/invites")
def team_invites():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,email,role,status,created_at FROM team_invites WHERE owner_id=? ORDER BY id DESC",(u["id"],))]
    return {"items":rows}

@app.post("/api/team/invites")
def team_invite_create():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    data=request.get_json(force=True)
    email=(data.get("email") or "").strip().lower()[:180]
    role=(data.get("role") or "Viewer").strip().title()
    if "@" not in email:return jsonify(error="Enter a valid email."),400
    if role not in ("Developer","Viewer"):return jsonify(error="Role must be Developer or Viewer."),400
    with db() as c:
        c.execute("INSERT INTO team_invites(owner_id,email,role,status,created_at) VALUES(?,?,?,?,?)",
                  (u["id"],email,role,"pending",nowiso()))
    audit("team_invite_created",f"{email} · {role}")
    return {"ok":True,"message":"Invitation saved as pending. Connect an email provider to deliver invitation emails."}

@app.delete("/api/team/invites/<int:invite_id>")
def team_invite_cancel(invite_id):
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        row=c.execute("SELECT id FROM team_invites WHERE id=? AND owner_id=?",(invite_id,u["id"])).fetchone()
        if not row:return jsonify(error="Invite not found."),404
        c.execute("DELETE FROM team_invites WHERE id=?",(invite_id,))
    return {"ok":True}

@app.get("/api/settings/status")
def settings_status():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    return {
        "otp":{"configured":twilio_configured(),"demo_mode":DEMO_MODE,"provider":"Twilio Verify" if twilio_configured() else ("Demo OTP" if DEMO_MODE else "Not configured")},
        "network":{"host":os.environ.get("RUNPROOF_HOST","0.0.0.0"),"port":int(os.environ.get("RUNPROOF_PORT","8000"))},
        "github":{"configured":False},
        "assistant":{"mode":"built-in RunProof Guide"},
        "verification":{"execution_mode":EXECUTION_MODE,"trusted_upload_execution":EXECUTION_MODE=="trusted"}
    }

@app.get("/api/dashboard")
def dashboard():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT id,name,last_score,last_status,created_at FROM projects WHERE owner_id=? ORDER BY id DESC LIMIT 8",(u["id"],))]
        audits=[dict(r) for r in c.execute("SELECT action,detail,created_at FROM audits WHERE user_id=? ORDER BY id DESC LIMIT 8",(u["id"],))]
    verified=sum(1 for r in rows if (r["last_status"] or "").lower().startswith("verified"))
    avg=round(sum((r["last_score"] or 0) for r in rows)/len(rows)) if rows else 0
    return {"projects":rows,"stats":{"projects":len(rows),"verified":verified,"average_score":avg},"activity":audits}

def safe_extract_zip(zip_path, dest):
    dest=Path(dest).resolve()
    total=0
    with zipfile.ZipFile(zip_path) as z:
        members=z.infolist()
        if len(members)>3000:
            raise ValueError("Too many files in ZIP.")
        for info in members:
            total += info.file_size
            if total > 200*1024*1024:
                raise ValueError("Expanded project is too large.")
            target=(dest / info.filename).resolve()
            try:
                safe = os.path.commonpath([str(dest), str(target)]) == str(dest)
            except ValueError:
                safe = False
            if not safe:
                raise ValueError("Unsafe ZIP path.")
        z.extractall(dest)


@app.post("/api/projects/import-github")
def import_github_project():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    data=request.get_json(force=True)
    raw=(data.get("url") or "").strip()
    m=re.match(r"^https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$", raw)
    if not m:
        return jsonify(error="Use a public GitHub URL like https://github.com/owner/repository"),400
    owner, repo=m.group(1),m.group(2)
    try:
        api_req=urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"User-Agent":"RunProof/1.0","Accept":"application/vnd.github+json"}
        )
        with urllib.request.urlopen(api_req, timeout=12) as resp:
            meta=json.loads(resp.read().decode("utf-8"))
        if meta.get("private"):
            return jsonify(error="This screen supports public repositories only."),400
        branch=meta.get("default_branch") or "main"
        display_name=(meta.get("name") or repo)[:100]
        archive_url=f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{urllib.parse.quote(branch)}"
        zreq=urllib.request.Request(archive_url, headers={"User-Agent":"RunProof/1.0"})
        with urllib.request.urlopen(zreq, timeout=25) as resp:
            data_bytes=resp.read(50*1024*1024+1)
        if len(data_bytes)>50*1024*1024:
            return jsonify(error="Repository archive is larger than 50 MB."),400
    except urllib.error.HTTPError as e:
        return jsonify(error=f"GitHub could not open this repository ({e.code})."),400
    except Exception as e:
        return jsonify(error=f"Could not download GitHub repository: {e}"),502

    project_key=secrets.token_hex(6)
    project_dir=UPLOADS / f"{u['id']}_github_{project_key}"
    project_dir.mkdir(parents=True, exist_ok=True)
    zip_path=project_dir/"repo.zip"
    zip_path.write_bytes(data_bytes)
    try:
        safe_extract_zip(zip_path, project_dir/"unpacked")
        roots=[p for p in (project_dir/"unpacked").iterdir() if p.is_dir()]
        scan_path=roots[0] if len(roots)==1 else (project_dir/"unpacked")
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        return jsonify(error=f"Could not safely extract repository: {e}"),400
    finally:
        zip_path.unlink(missing_ok=True)

    with db() as c:
        cur=c.execute("INSERT INTO projects(owner_id,name,path,created_at,trusted_demo) VALUES(?,?,?,?,0)",
                      (u["id"],display_name,str(scan_path),nowiso()))
        pid=cur.lastrowid
    audit("github_project_imported",f"{owner}/{repo}")
    return {"ok":True,"project_id":pid,"name":display_name,"branch":branch}

@app.post("/api/projects")
def create_project():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    name=(request.form.get("name") or "MyProject").strip()[:100]
    demo_kind=(request.form.get("demo_kind") or "good").strip().lower()
    if demo_kind not in ("good","broken","nonrepro"): demo_kind="good"
    file=request.files.get("project_zip")
    project_id=secrets.token_hex(6)
    project_dir=UPLOADS / f"{u['id']}_{project_id}"
    project_dir.mkdir(parents=True, exist_ok=True)
    if file:
        zip_path=project_dir/"project.zip"
        file.save(zip_path)
        try:
            safe_extract_zip(zip_path, project_dir/"src")
        except Exception as e:
            shutil.rmtree(project_dir,ignore_errors=True)
            return jsonify(error=str(e)),400
        zip_path.unlink(missing_ok=True)
        scan_path=project_dir/"src"
    else:
        # Built-in demos are trusted because their source is shipped with RunProof.
        demo_map={"good":"good_project","broken":"broken_project","nonrepro":"non_reproducible_project"}
        demo=BASE/"demo"/demo_map[demo_kind]
        shutil.copytree(demo,project_dir/"src",dirs_exist_ok=True)
        scan_path=project_dir/"src"
        name={"good":"Good Reproducible Demo","broken":"Broken Setup Demo","nonrepro":"Non-Reproducible Demo"}[demo_kind]
    trusted_demo=0 if file else 1
    with db() as c:
        cur=c.execute("INSERT INTO projects(owner_id,name,path,created_at,trusted_demo) VALUES(?,?,?,?,?)",(u["id"],name,str(scan_path),nowiso(),trusted_demo))
        pid=cur.lastrowid
    audit("project_created",name)
    return {"ok":True,"project_id":pid,"name":name}

@app.post("/api/projects/<int:project_id>/analyze")
def analyze(project_id):
    p=project_owned(project_id)
    if not p:return jsonify(error="Project not found."),404
    result=analyze_project(p["path"])
    with db() as c:
        c.execute("UPDATE projects SET last_score=?,last_status=? WHERE id=?",(result["score"]["score"],result["score"]["label"],project_id))
    audit("project_analyzed",p["name"])
    return result

@app.post("/api/projects/<int:project_id>/verify")
def verify(project_id):
    p=project_owned(project_id)
    if not p:return jsonify(error="Project not found."),404
    allow_execution = bool(p.get("trusted_demo")) or EXECUTION_MODE == "trusted"
    result=verify_project(p["path"], allow_execution=allow_execution)
    analysis=analyze_project(p["path"])
    status = (
        "Verified Reproducible" if result.get("verified")
        else "Not Reproducible" if result.get("status")=="NOT_REPRODUCIBLE"
        else "Build Failed" if result.get("status")=="BUILD_FAILED"
        else "Source Match Only" if result.get("status")=="SOURCE_MATCH_ONLY"
        else "Not Verified"
    )
    response={"verification":result,"passport":None}
    if result.get("verified"):
        passport=create_passport(p["name"],analysis,result)
        pass_path=REPORTS/f"passport_{project_id}.json"
        pass_path.write_text(json.dumps(passport,indent=2),encoding="utf-8")
        response["passport"]=passport
    else:
        (REPORTS/f"passport_{project_id}.json").unlink(missing_ok=True)
    with db() as c:
        c.execute("UPDATE projects SET last_score=?,last_status=? WHERE id=?",(analysis["score"]["score"],status,project_id))
    audit("project_verified" if result.get("verified") else "verification_finished",f"{p['name']} · {status}")
    return response

@app.get("/api/projects/<int:project_id>/passport")
def get_passport(project_id):
    p=project_owned(project_id)
    if not p:return jsonify(error="Project not found."),404
    path=REPORTS/f"passport_{project_id}.json"
    if not path.exists():
        return jsonify(error="Verify project first."),404
    audit("passport_opened",p["name"])
    return jsonify(json.loads(path.read_text(encoding="utf-8")))

@app.get("/api/projects/<int:project_id>/report")
def report(project_id):
    p=project_owned(project_id)
    if not p:return jsonify(error="Project not found."),404
    analysis=analyze_project(p["path"])
    issues="".join(f"<li><b>{i['severity'].upper()}</b> — {i['title']}<br><small>{i['fix']}</small></li>" for i in analysis["issues"])
    html=f"""<!doctype html><html><head><meta charset='utf-8'><title>RunProof Report</title>
    <style>body{{font-family:Inter,Arial;max-width:980px;margin:40px auto;padding:20px;color:#14213d}}.card{{padding:20px;border:1px solid #dbe4f0;border-radius:16px;margin:14px 0}}.ok{{color:#16803d}}</style></head>
    <body><h1>RunProof Report</h1><h2>{p['name']}</h2>
    <div class='card'><h3>Readiness</h3><p style='font-size:38px;font-weight:800'>{analysis['score']['score']}/100</p><p>{analysis['score']['label']}</p></div>
    <div class='card'><h3>Project</h3><p>{analysis['project_type']['type']} · {analysis['runtime'].get('version') or 'Runtime unavailable'}</p></div>
    <div class='card'><h3>Issues & Fixes</h3><ul>{issues}</ul></div>
    <div class='card'><h3>Source Fingerprint</h3><code>{analysis['source_fingerprint']}</code></div>
    <p class='ok'>Generated by RunProof</p></body></html>"""
    out=REPORTS/f"report_{project_id}.html"
    out.write_text(html,encoding="utf-8")
    audit("report_generated",p["name"])
    return send_from_directory(REPORTS,out.name,as_attachment=True)

@app.get("/api/audit")
def get_audit():
    u=require_user()
    if not u:return jsonify(error="Not authenticated."),401
    with db() as c:
        rows=[dict(r) for r in c.execute("SELECT action,detail,created_at FROM audits WHERE user_id=? ORDER BY id DESC LIMIT 100",(u["id"],))]
    return {"events":rows}

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="Upload too large."),413