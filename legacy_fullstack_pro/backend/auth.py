from functools import wraps
from flask import request, jsonify, g
import hashlib, hmac, secrets, base64, time
from .database import connect, now, audit

RATE = {}

def _b64(b): return base64.urlsafe_b64encode(b).decode().rstrip('=')
def _unb64(s): return base64.urlsafe_b64decode(s + '='*((4-len(s)%4)%4))

def hash_password(password: str) -> str:
    if len(password) < 8: raise ValueError('Password must be at least 8 characters.')
    salt=secrets.token_bytes(16)
    digest=hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f'scrypt$16384$8$1${_b64(salt)}${_b64(digest)}'

def verify_password(password, stored):
    try:
        alg,n,r,p,salt,digest=stored.split('$')
        if alg!='scrypt': return False
        got=hashlib.scrypt(password.encode(), salt=_unb64(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(got,_unb64(digest))
    except Exception: return False

def token_hash(raw): return hashlib.sha256(raw.encode()).hexdigest()
def otp_hash(phone, code, secret): return hmac.new(secret.encode(), f'{phone}:{code}'.encode(), hashlib.sha256).hexdigest()

def rate_limit(key, limit=5, window=300):
    now_t=time.time(); arr=RATE.setdefault(key,[]); arr[:]=[t for t in arr if now_t-t<window]
    if len(arr)>=limit: return False
    arr.append(now_t); return True

def create_session(cfg, user_id):
    raw=secrets.token_urlsafe(32); exp=int(time.time())+cfg.session_ttl
    with connect(cfg.db_path) as c:
        c.execute('DELETE FROM sessions WHERE expires_at < ?', (int(time.time()),))
        c.execute('INSERT INTO sessions(user_id,token_hash,expires_at,created_at) VALUES(?,?,?,?)',(user_id,token_hash(raw),exp,now()))
    return raw, exp

def get_current_user(cfg):
    raw=request.cookies.get('rp_session') or request.headers.get('Authorization','').removeprefix('Bearer ').strip()
    if not raw: return None
    with connect(cfg.db_path) as c:
        row=c.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?',(token_hash(raw),int(time.time()))).fetchone()
        return dict(row) if row else None

def require_auth(cfg):
    def deco(fn):
        @wraps(fn)
        def inner(*a,**kw):
            user=get_current_user(cfg)
            if not user: return jsonify({'error':'authentication_required'}),401
            g.user=user
            return fn(*a,**kw)
        return inner
    return deco

def set_session_cookie(resp, raw, cfg):
    resp.set_cookie('rp_session', raw, max_age=cfg.session_ttl, httponly=True, samesite='Strict', secure=not cfg.debug, path='/')
    return resp

def clear_session_cookie(resp):
    resp.delete_cookie('rp_session', path='/'); return resp
