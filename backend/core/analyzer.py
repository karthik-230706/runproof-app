from .scanner import scan_project
from .detector import detect_project_type
from .runtime_checker import check_runtime
from .dependencies import inspect_dependencies
from .environment_checker import check_environment
from .static_security import inspect_static_security
from .scoring import score_analysis
from .doctor import make_issues
from .fingerprint import sha256_tree

def analyze_project(path):
    scan = scan_project(path)
    ptype = detect_project_type(scan)
    runtime = check_runtime(ptype)
    deps = inspect_dependencies(path, ptype)
    env = check_environment(path)
    security = inspect_static_security(path)
    score = score_analysis(scan, ptype, runtime, deps, env, security)
    issues = make_issues(deps, env, runtime, security)
    fingerprint = sha256_tree(path)
    return {
        "scan": scan,
        "project_type": ptype,
        "runtime": runtime,
        "dependencies": deps,
        "environment": env,
        "security": security,
        "score": score,
        "issues": issues,
        "source_fingerprint": fingerprint
    }