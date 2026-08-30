from pathlib import Path
from .util import safe_walk, rel

IMPORTANT=['requirements.txt','pyproject.toml','Pipfile','package.json','package-lock.json','yarn.lock','pom.xml','build.gradle','gradlew','gradlew.bat','.env.example','README.md','runproof.json']

def scan_project(root, max_files=5000):
    root=Path(root).resolve(); files=[]; exts={}; size=0
    for p in safe_walk(root,max_files):
        files.append(rel(p,root)); exts[p.suffix.lower()]=exts.get(p.suffix.lower(),0)+1
        try:size+=p.stat().st_size
        except:pass
    found={name:any(f==name or f.endswith('/'+name) for f in files) for name in IMPORTANT}
    return {'project_name':root.name,'root':str(root),'file_count':len(files),'total_bytes':size,'files':files[:500],
            'extensions':dict(sorted(exts.items(),key=lambda kv:kv[1],reverse=True)[:20]),'important_files':found}
