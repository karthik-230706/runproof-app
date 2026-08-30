from pathlib import Path
import subprocess, os, json, sys, time
from .util import load_json

ALLOWED_EXE={'python','python3','node','npm','mvn','gradle','gradlew','gradlew.bat'}
SHELL_TOKENS={'|','||','&&',';','>','>>','<','`','$(', '${'}

def get_plan(root,ptype):
    root=Path(root); data=load_json(root/'runproof.json')
    if data:
        return {'build':data.get('build'),'test':data.get('test'),'artifacts':data.get('artifacts',[]),'source':'runproof.json'}
    if ptype=='Python': return {'build':[sys.executable,'-m','compileall','-q','.'],'test':[sys.executable,'-m','unittest','discover','-v'],'artifacts':[],'source':'default'}
    if ptype=='Java' and (root/'pom.xml').exists(): return {'build':['mvn','-q','-DskipTests','package'],'test':['mvn','-q','test'],'artifacts':['target/*.jar'],'source':'default'}
    return {'build':None,'test':None,'artifacts':[],'source':'none'}

def validate_command(cmd, root):
    if cmd is None:return True,'not configured'
    if not isinstance(cmd,list) or not cmd or not all(isinstance(x,str) for x in cmd):return False,'Command must be a list of strings.'
    exe=Path(cmd[0]).name.lower()
    if exe not in ALLOWED_EXE and Path(cmd[0]).resolve()!=Path(sys.executable).resolve():return False,f'Executable not allowlisted: {exe}'
    for a in cmd:
        if any(tok in a for tok in SHELL_TOKENS):return False,'Shell control operators are blocked.'
        if '..' in Path(a).parts:return False,'Path traversal argument blocked.'
    return True,'ok'

def run_command(cmd, root, timeout=60, mode='static'):
    if not cmd:return {'status':'skipped','reason':'No command configured.'}
    ok,reason=validate_command(cmd,root)
    if not ok:return {'status':'blocked','reason':reason}
    if mode!='trusted':return {'status':'skipped','reason':'Execution disabled. Use trusted mode only for code you control.'}
    env={'PATH':os.environ.get('PATH',''),'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
    start=time.time()
    try:
        cp=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=timeout,shell=False,env=env)
        return {'status':'passed' if cp.returncode==0 else 'failed','returncode':cp.returncode,'duration_ms':int((time.time()-start)*1000),
                'stdout':cp.stdout[-12000:],'stderr':cp.stderr[-12000:]}
    except subprocess.TimeoutExpired as e:return {'status':'timeout','reason':f'Exceeded {timeout}s timeout.'}
    except Exception as e:return {'status':'failed','reason':str(e)}

def execute(root,ptype,mode='static',timeout=60):
    plan=get_plan(root,ptype)
    return {'plan':plan,'build':run_command(plan['build'],root,timeout,mode),'test':run_command(plan['test'],root,timeout,mode)}
