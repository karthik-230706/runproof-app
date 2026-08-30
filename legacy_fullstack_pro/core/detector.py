from pathlib import Path

def detect_project_type(root, scan):
    files=set(scan.get('files',[])); ext=scan.get('extensions',{})
    scores={'python':0,'node':0,'java':0}
    if 'pyproject.toml' in files or 'requirements.txt' in files or 'Pipfile' in files:scores['python']+=6
    scores['python']+=min(ext.get('.py',0),5)
    if 'package.json' in files:scores['node']+=8
    scores['node']+=min(ext.get('.js',0)+ext.get('.ts',0)+ext.get('.jsx',0)+ext.get('.tsx',0),5)
    if 'pom.xml' in files or 'build.gradle' in files:scores['java']+=8
    scores['java']+=min(ext.get('.java',0),5)
    kind=max(scores,key=scores.get)
    if scores[kind]==0: return {'type':'unknown','confidence':0,'scores':scores}
    label={'python':'Python','node':'Node.js','java':'Java'}[kind]
    total=max(sum(scores.values()),1)
    return {'type':label,'confidence':round(scores[kind]/total,2),'scores':scores}
