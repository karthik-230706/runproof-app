import shutil

def check_tools(ptype):
    required={'Python':['python','git','pip'],'Node.js':['node','npm','git'],'Java':['java','git']} .get(ptype,['git'])
    if ptype=='Java':
        required += ['mvn'] if shutil.which('mvn') else ['gradle'] if shutil.which('gradle') else ['mvn/gradle']
    return [{'tool':t,'available': bool(shutil.which(t)) if '/' not in t else False,'path':shutil.which(t) if '/' not in t else None} for t in required]
