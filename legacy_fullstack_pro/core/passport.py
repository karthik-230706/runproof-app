from datetime import datetime,timezone
import json,hmac,hashlib,copy

def _canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sign_payload(payload,secret):return hmac.new(secret.encode(),_canonical(payload),hashlib.sha256).hexdigest()
def make_passport(analysis,secret):
    p={'schema_version':'1.0','tool':'RunProof','issued_at':datetime.now(timezone.utc).isoformat(),
       'project':{'name':analysis['scan']['project_name'],'type':analysis['detection']['type']},
       'readiness':analysis['score'],'verification':analysis.get('verification'),
       'evidence':{'runtime':analysis['runtime'],'dependency_summary':{k:analysis['dependencies'].get(k) for k in ['total','pinned','unpinned','lockfiles']},
                   'environment_required_names':analysis['environment'].get('required_names',[]),'security_summary':{k:len(analysis['security'].get(k,[])) for k in ['sensitive_files','absolute_path_files','dangerous_command_files']}}}
    p['signature']={'alg':'HMAC-SHA256','value':sign_payload(p,secret)}
    return p

def verify_passport(passport,secret):
    p=copy.deepcopy(passport); sig=(p.pop('signature',{}) or {}).get('value')
    return bool(sig and hmac.compare_digest(sig,sign_payload(p,secret)))
