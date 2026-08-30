from dataclasses import dataclass
from pathlib import Path
import os, secrets

ROOT = Path(__file__).resolve().parents[1]

def _load_dotenv():
    p = ROOT / '.env'
    if not p.exists(): return
    for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k,v=line.split('=',1)
        os.environ.setdefault(k.strip(), v.strip())

@dataclass
class Config:
    root: Path
    data_dir: Path
    project_dir: Path
    db_path: Path
    frontend_dir: Path
    host: str
    port: int
    debug: bool
    secret_key: str
    execution_mode: str
    exec_timeout: int
    otp_mode: str
    dev_show_otp: bool
    otp_ttl: int
    session_ttl: int
    max_upload_bytes: int
    max_uncompressed_bytes: int
    max_files: int

    @classmethod
    def load(cls):
        _load_dotenv()
        data = ROOT / 'data'; projects=data/'projects'
        data.mkdir(exist_ok=True); projects.mkdir(exist_ok=True)
        secret=os.getenv('RUNPROOF_SECRET_KEY','').strip()
        if not secret:
            secret = secrets.token_hex(32)
        return cls(
            root=ROOT, data_dir=data, project_dir=projects, db_path=data/'runproof.db',
            frontend_dir=ROOT/'frontend', host=os.getenv('RUNPROOF_HOST','127.0.0.1'),
            port=int(os.getenv('RUNPROOF_PORT','8000')), debug=os.getenv('RUNPROOF_DEBUG','1')=='1',
            secret_key=secret, execution_mode=os.getenv('RUNPROOF_EXECUTION_MODE','static').lower(),
            exec_timeout=int(os.getenv('RUNPROOF_EXEC_TIMEOUT','60')), otp_mode=os.getenv('RUNPROOF_OTP_MODE','console'),
            dev_show_otp=os.getenv('RUNPROOF_DEV_SHOW_OTP','1')=='1', otp_ttl=int(os.getenv('RUNPROOF_OTP_TTL_SECONDS','300')),
            session_ttl=int(os.getenv('RUNPROOF_SESSION_TTL_SECONDS','604800')),
            max_upload_bytes=int(os.getenv('RUNPROOF_MAX_UPLOAD_MB','50'))*1024*1024,
            max_uncompressed_bytes=int(os.getenv('RUNPROOF_MAX_UNCOMPRESSED_MB','250'))*1024*1024,
            max_files=int(os.getenv('RUNPROOF_MAX_FILES','5000')),
        )
