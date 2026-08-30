from pathlib import Path
import re, json, xml.etree.ElementTree as ET
from .util import read_text, load_json

def _req_line(line):
    line=line.strip()
    if not line or line.startswith('#') or line.startswith('-'):return None
    m=re.match(r'([A-Za-z0-9_.-]+)\s*(==|===|~=|>=|<=|>|<)?\s*([^;\s]+)?',line)
    if not m:return None
    name,op,ver=m.groups(); pinned=op in ('==','===') and bool(ver)
    return {'name':name,'version':ver if pinned else None,'constraint':(op or '')+(ver or ''),'pinned':pinned,'source':'requirements.txt'}

def analyze_dependencies(root,ptype):
    root=Path(root); items=[]; files=[]
    req=root/'requirements.txt'
    if req.exists():
        files.append('requirements.txt')
        for line in read_text(req).splitlines():
            d=_req_line(line)
            if d:items.append(d)
    pkg=root/'package.json'
    if pkg.exists():
        files.append('package.json'); data=load_json(pkg)
        for section in ('dependencies','devDependencies'):
            for name,ver in (data.get(section) or {}).items():
                pinned=bool(re.fullmatch(r'\d+\.\d+\.\d+(?:[-+].+)?',str(ver)))
                items.append({'name':name,'version':str(ver) if pinned else None,'constraint':str(ver),'pinned':pinned,'source':'package.json','scope':section})
    pom=root/'pom.xml'
    if pom.exists():
        files.append('pom.xml')
        try:
            tree=ET.parse(pom); rootx=tree.getroot()
            for dep in rootx.iter():
                if dep.tag.endswith('dependency'):
                    vals={c.tag.split('}')[-1]:(c.text or '').strip() for c in dep}
                    if vals.get('artifactId'):
                        ver=vals.get('version'); pinned=bool(ver and '${' not in ver)
                        items.append({'name':f"{vals.get('groupId','')}:{vals['artifactId']}",'version':ver if pinned else None,'constraint':ver,'pinned':pinned,'source':'pom.xml'})
        except Exception: pass
    pinned=sum(1 for x in items if x['pinned']); total=len(items)
    lockfiles=[n for n in ['package-lock.json','yarn.lock','pnpm-lock.yaml','Pipfile.lock','poetry.lock'] if (root/n).exists()]
    return {'dependency_files':files,'components':items[:500],'total':total,'pinned':pinned,'unpinned':total-pinned,'pinning_percent':round(pinned/total*100,1) if total else None,'lockfiles':lockfiles}
