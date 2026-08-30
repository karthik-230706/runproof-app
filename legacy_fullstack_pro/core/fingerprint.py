from pathlib import Path
import hashlib, glob

def hash_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def collect_artifacts(root, patterns):
    root=Path(root); out=[]
    for pat in patterns:
        for p in root.glob(pat):
            if p.is_file():out.append(p)
    return sorted(set(out), key=lambda p:p.as_posix())

def hash_artifacts(root,patterns):
    root=Path(root); files=collect_artifacts(root,patterns)
    if not files:return {'hash':None,'files':[]}
    h=hashlib.sha256(); details=[]
    for p in files:
        rp=p.relative_to(root).as_posix(); fh=hash_file(p)
        h.update(rp.encode());h.update(b'\0');h.update(bytes.fromhex(fh))
        details.append({'path':rp,'sha256':fh,'bytes':p.stat().st_size})
    return {'hash':h.hexdigest(),'files':details}
