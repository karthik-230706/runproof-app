from pathlib import Path
from .scanner import scan_project
from .detector import detect_project_type
from .runtime_checker import check_runtime
from .tools_checker import check_tools
from .dependency_checker import analyze_dependencies
from .environment_checker import check_environment
from .security_scanner import scan_security
from .executor import execute
from .scoring import calculate
from .doctor import diagnose
from .verifier import verify_reproducibility
from .sbom import make_sbom
from .passport import make_passport
from .report import render_report

TOOL_VERSION='0.2.0-hackathon'

def analyze_project(root, execution_mode='static', timeout=60, verify=False, secret='dev-secret'):
    root=Path(root).resolve()
    scan=scan_project(root); det=detect_project_type(root,scan); ptype=det['type']
    runtime=check_runtime(root,ptype); tools=check_tools(ptype); deps=analyze_dependencies(root,ptype)
    env=check_environment(root); security=scan_security(root); execution=execute(root,ptype,execution_mode,timeout)
    score=calculate(scan,det,runtime,tools,deps,env,security,execution)
    verification=verify_reproducibility(root,ptype,execution_mode,timeout) if verify else None
    issues=diagnose(runtime,tools,deps,env,security,execution,verification)
    analysis={'tool_version':TOOL_VERSION,'scan':scan,'detection':det,'runtime':runtime,'tools':tools,'dependencies':deps,'environment':env,
              'security':security,'execution':execution,'score':score,'verification':verification,'issues':issues}
    sbom=make_sbom(scan['project_name'],ptype,deps); passport=make_passport(analysis,secret); report=render_report(analysis,passport)
    return analysis,passport,sbom,report
