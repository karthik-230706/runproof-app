from pathlib import Path
import hashlib

def sha256_file(path):
    h = hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_tree(root):
    root = Path(root)
    h = hashlib.sha256()
    ignored = {".git","__pycache__",".venv","node_modules",".runproof"}
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not any(part in ignored for part in p.parts):
            files.append(p)
    for p in sorted(files, key=lambda x:str(x.relative_to(root))):
        rel = str(p.relative_to(root)).replace("\\","/")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        with open(p,"rb") as f:
            for chunk in iter(lambda:f.read(1024*1024), b""):
                h.update(chunk)
        h.update(b"\0")
    return h.hexdigest()