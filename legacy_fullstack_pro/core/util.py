from pathlib import Path
import json, re

IGNORED_DIRS={'.git','.hg','.svn','node_modules','.venv','venv','__pycache__','.idea','.vscode','.pytest_cache'}
BINARY_EXT={'.png','.jpg','.jpeg','.gif','.pdf','.zip','.jar','.class','.pyc','.exe','.dll','.so','.dylib'}

def rel(p,root):
    try:return p.relative_to(root).as_posix()
    except:return p.name

def read_text(path, limit=1_000_000):
    try:
        if path.stat().st_size>limit:return ''
        return path.read_text(encoding='utf-8',errors='ignore')
    except:return ''

def load_json(path):
    try:return json.loads(read_text(path))
    except:return {}

def safe_walk(root, max_files=5000):
    root=Path(root); n=0
    for p in root.rglob('*'):
        if any(part in IGNORED_DIRS for part in p.parts): continue
        if p.is_file():
            n+=1
            if n>max_files: break
            yield p
