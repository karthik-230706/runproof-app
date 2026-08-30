def diagnose(runtime,tools,deps,env,security,execution,verification=None):
    issues=[]
    def add(code,severity,title,why,fix,category):issues.append({'code':code,'severity':severity,'title':title,'why':why,'fix':fix,'category':category})
    if not runtime.get('available'):
        add('RUNTIME_MISSING','high',f"{runtime.get('name','Runtime')} is missing",'The project cannot run without its required runtime.',f"Install the required {runtime.get('name','runtime')} version.",'runtime')
    missing=[x['tool'] for x in tools if not x['available']]
    if missing:add('TOOLS_MISSING','medium','Required tools are missing','Build or test commands may not be available.','Install: '+', '.join(missing),'tools')
    if deps.get('unpinned',0):add('UNPINNED_DEPS','medium',f"{deps['unpinned']} dependency version(s) are not fixed",'Newer package versions can change behavior or break future builds.','Pin exact compatible versions or use a lock file.','dependencies')
    if env.get('missing_names'):add('ENV_MISSING','high','Environment settings are missing','The application may fail at startup or lose external service connections.','Configure: '+', '.join(env['missing_names'])+'. RunProof will never display the secret values.','environment')
    if security.get('sensitive_files'):add('SENSITIVE_FILES','high','Sensitive files are inside the project','Secret-bearing files can accidentally be shared or committed.','Remove secrets from the project archive and use a secure secret manager.','security')
    if security.get('absolute_path_files'):add('ABSOLUTE_PATHS','medium','Machine-specific paths were detected','Paths tied to one computer can break on another computer.','Replace absolute local paths with relative paths or configuration variables.','configuration')
    if security.get('dangerous_command_files'):add('DANGEROUS_COMMAND','critical','Potentially destructive command pattern detected','Executing unknown destructive commands can damage the host machine.','Review the file manually. RunProof blocks unsafe shell-style execution.','security')
    for k,label in [('build','Build'),('test','Tests')]:
        st=execution.get(k,{}).get('status')
        if st in ('failed','timeout','blocked'):add(k.upper()+'_FAIL','high',f'{label} did not pass',f'{label} evidence is required for stronger readiness.','Open the captured log, fix the error, and run the check again.',k)
    if verification:
        if verification.get('status')=='mismatch':add('HASH_MISMATCH','critical','Build fingerprints do not match','The same source produced different build artifacts.','Check timestamps, random IDs, unpinned dependencies, machine paths and environment-dependent output.','verification')
        elif verification.get('status') in ('inconclusive','not_executed'):add('VERIFY_INCOMPLETE','info','Reproducibility proof is not complete',verification.get('reason','Verification was not executed.'),'Use an isolated trusted build environment and configure artifact patterns.','verification')
    order={'critical':0,'high':1,'medium':2,'low':3,'info':4}
    return sorted(issues,key=lambda x:order.get(x['severity'],9))
