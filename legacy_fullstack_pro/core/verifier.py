from pathlib import Path
import tempfile, shutil
from .executor import execute, get_plan
from .fingerprint import hash_artifacts

EXCLUDE=shutil.ignore_patterns('.git','node_modules','.venv','venv','__pycache__','.pytest_cache','dist','build','target')

def verify_reproducibility(root,ptype,mode='static',timeout=60):
    root=Path(root).resolve(); plan=get_plan(root,ptype)
    if mode!='trusted':
        return {'status':'not_executed','verified':False,'reason':'Static mode does not execute project code. Enable trusted mode only for your own demo project.'}
    if not plan.get('build'):
        return {'status':'inconclusive','verified':False,'reason':'No build command configured. Add runproof.json.'}
    if not plan.get('artifacts'):
        return {'status':'inconclusive','verified':False,'reason':'No artifact patterns configured. Add artifacts to runproof.json.'}
    with tempfile.TemporaryDirectory(prefix='runproof-a-') as a, tempfile.TemporaryDirectory(prefix='runproof-b-') as b:
        pa=Path(a)/'project'; pb=Path(b)/'project'; shutil.copytree(root,pa,ignore=EXCLUDE); shutil.copytree(root,pb,ignore=EXCLUDE)
        ra=execute(pa,ptype,mode,timeout); rb=execute(pb,ptype,mode,timeout)
        if ra['build']['status']!='passed' or rb['build']['status']!='passed':
            return {'status':'build_failed','verified':False,'build_a':ra,'build_b':rb}
        ha=hash_artifacts(pa,plan['artifacts']); hb=hash_artifacts(pb,plan['artifacts'])
        if not ha['hash'] or not hb['hash']:return {'status':'inconclusive','verified':False,'reason':'Configured build artifacts were not found.','build_a':ra,'build_b':rb}
        match=ha['hash']==hb['hash']
        return {'status':'verified' if match else 'mismatch','verified':match,'match':match,'hash_a':ha['hash'],'hash_b':hb['hash'],
                'artifacts_a':ha['files'],'artifacts_b':hb['files'],'build_a':ra,'build_b':rb}
