from pathlib import Path
import re
from .util import safe_walk, rel, read_text

SENSITIVE_NAMES={'.env','id_rsa','id_dsa','credentials.json','service-account.json','.npmrc','.pypirc'}
SENSITIVE_EXT={'.pem','.key','.p12','.pfx'}
DANGEROUS=re.compile(r'(?i)(rm\s+-rf\s+/|curl.+\|\s*(sh|bash)|wget.+\|\s*(sh|bash)|format\s+[a-z]:|del\s+/[sq])')
ABS_PATH=re.compile(r'(?i)([A-Z]:\\Users\\[^\s"\']+|/home/[^/\s"\']+|/Users/[^/\s"\']+)')

def scan_security(root):
    root=Path(root); sensitive=[]; absolute=[]; dangerous=[]
    for p in safe_walk(root,3000):
        rp=rel(p,root)
        if p.name in SENSITIVE_NAMES or p.suffix.lower() in SENSITIVE_EXT:sensitive.append(rp)
        if p.suffix.lower() in {'.json','.toml','.yaml','.yml','.gradle','.txt','.md','.sh','.bat','.ps1','.py','.js'}:
            txt=read_text(p,300000)
            if ABS_PATH.search(txt): absolute.append(rp)
            if DANGEROUS.search(txt): dangerous.append(rp)
    return {'sensitive_files':sensitive[:50],'absolute_path_files':absolute[:50],'dangerous_command_files':dangerous[:50],
            'secret_values_exposed':False,'note':'RunProof reports file names/patterns only and does not include secret values.'}
