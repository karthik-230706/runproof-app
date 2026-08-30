def _status(ok,warn=False): return 'warning' if warn else ('pass' if ok else 'fail')

def calculate(scan,det,runtime,tools,deps,env,security,execution):
    checks={}
    checks['project_detection']={'weight':5,'status':_status(det['type']!='Unknown' and det['type']!='unknown')}
    checks['runtime']={'weight':10,'status':_status(runtime.get('available',False))}
    missing_tools=[x['tool'] for x in tools if not x['available']]
    checks['tools']={'weight':10,'status':_status(not missing_tools, bool(missing_tools)),'detail':missing_tools}
    important=scan.get('important_files',{}); has_manifest=any(important.get(x) for x in ['requirements.txt','pyproject.toml','package.json','pom.xml','build.gradle'])
    checks['required_files']={'weight':10,'status':_status(has_manifest)}
    checks['dependencies']={'weight':10,'status':_status(bool(deps['dependency_files']) or deps['total']==0)}
    unp=deps.get('unpinned',0); checks['dependency_pinning']={'weight':15,'status':_status(unp==0,unp>0),'detail':unp}
    missing_env=env.get('missing_names',[]); checks['environment']={'weight':10,'status':_status(not missing_env,bool(missing_env)),'detail':missing_env}
    risky=security.get('dangerous_command_files',[]); checks['configuration']={'weight':5,'status':_status(not risky,bool(risky)),'detail':risky}
    build=execution.get('build',{}).get('status','skipped'); test=execution.get('test',{}).get('status','skipped')
    checks['build']={'weight':10,'status':'pass' if build=='passed' else 'warning' if build=='skipped' else 'fail','detail':build}
    checks['tests']={'weight':15,'status':'pass' if test=='passed' else 'warning' if test=='skipped' else 'fail','detail':test}
    total=0
    for c in checks.values():
        if c['status']=='pass':total+=c['weight']
        elif c['status']=='warning':total+=round(c['weight']*.6,2)
    score=round(total,1)
    status='Very Ready' if score>=90 else 'Needs Attention' if score>=70 else 'Not Ready'
    return {'score':score,'status':status,'checks':checks}
