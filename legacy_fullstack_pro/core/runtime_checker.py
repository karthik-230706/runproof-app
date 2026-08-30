from pathlib import Path
import subprocess, shutil, re
from .util import read_text, load_json

def _cmd(exe,args):
    path=shutil.which(exe)
    if not path:return {'available':False,'version':None,'path':None}
    try:
        cp=subprocess.run([path]+args,capture_output=True,text=True,timeout=5,shell=False)
        text=(cp.stdout+' '+cp.stderr).strip().splitlines()[0]
        m=re.search(r'(\d+\.\d+(?:\.\d+)?)',text)
        return {'available':True,'version':m.group(1) if m else text[:80],'path':path}
    except Exception as e:return {'available':True,'version':None,'path':path,'error':str(e)}

def infer_required(root, ptype):
    root=Path(root)
    if ptype=='Python':
        for n in ['.python-version','runtime.txt']:
            p=root/n
            if p.exists(): return read_text(p,200).strip()
        py=root/'pyproject.toml'
        if py.exists():
            m=re.search(r'requires-python\s*=\s*["\']([^"\']+)',read_text(py));
            if m:return m.group(1)
    if ptype=='Node.js':
        data=load_json(root/'package.json'); return (data.get('engines') or {}).get('node')
    if ptype=='Java':
        txt=read_text(root/'pom.xml')+read_text(root/'build.gradle')
        m=re.search(r'(?:maven.compiler.source|sourceCompatibility)[^0-9]*(\d+)',txt)
        if m:return m.group(1)
    return None

def check_runtime(root, ptype):
    map_={'Python':('python',['--version']),'Node.js':('node',['--version']),'Java':('java',['-version'])}
    if ptype not in map_:return {'name':'Unknown','available':False,'required':None}
    exe,args=map_[ptype]; r=_cmd(exe,args); r['name']=ptype; r['required']=infer_required(root,ptype); return r
