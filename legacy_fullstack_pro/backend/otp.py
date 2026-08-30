import secrets, time
from .auth import otp_hash
from .database import connect, now

class OTPService:
    def __init__(self,cfg): self.cfg=cfg
    def send(self, phone):
        code=f'{secrets.randbelow(1_000_000):06d}'
        exp=int(time.time())+self.cfg.otp_ttl
        with connect(self.cfg.db_path) as c:
            c.execute('UPDATE otps SET consumed=1 WHERE phone=? AND consumed=0',(phone,))
            c.execute('INSERT INTO otps(phone,code_hash,expires_at,attempts,consumed,created_at) VALUES(?,?,?,?,?,?)',
                      (phone,otp_hash(phone,code,self.cfg.secret_key),exp,0,0,now()))
        if self.cfg.otp_mode=='console':
            print(f'[RunProof DEV OTP] {phone}: {code}')
        return code if self.cfg.dev_show_otp and self.cfg.debug else None
    def verify(self, phone, code):
        with connect(self.cfg.db_path) as c:
            row=c.execute('SELECT * FROM otps WHERE phone=? AND consumed=0 ORDER BY id DESC LIMIT 1',(phone,)).fetchone()
            if not row: return False,'No active OTP. Request a new code.'
            if row['expires_at']<int(time.time()): return False,'OTP expired.'
            if row['attempts']>=5: return False,'Too many attempts. Request a new OTP.'
            c.execute('UPDATE otps SET attempts=attempts+1 WHERE id=?',(row['id'],))
            if row['code_hash'] != otp_hash(phone,code,self.cfg.secret_key): return False,'Invalid OTP.'
            c.execute('UPDATE otps SET consumed=1 WHERE id=?',(row['id'],))
            return True,'Verified.'
