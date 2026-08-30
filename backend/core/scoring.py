def score_analysis(scan, project_type, runtime, deps, env, security):
    categories = {}
    categories["project"] = 5 if project_type.get("type") != "Unknown" else 0
    categories["runtime"] = 10 if runtime.get("available") else 0
    categories["files"] = 10 if scan.get("important_files") else 5
    categories["dependencies"] = 10 if deps.get("source") else 5
    pin_ratio = 1.0 if deps.get("count",0) == 0 else deps.get("pinned",0) / max(deps.get("count",1),1)
    categories["dependency_pinning"] = round(15 * pin_ratio)
    categories["environment"] = 10 if not env.get("missing_names") else max(0,10 - min(10,2*len(env.get("missing_names",[]))))
    categories["configuration"] = 5 if ".env.example" in scan.get("important_files",[]) or project_type.get("manifest") else 3
    categories["static_security"] = 10
    if security.get("sensitive_files"): categories["static_security"] -= 4
    if security.get("dangerous_patterns"): categories["static_security"] -= 4
    if security.get("machine_specific_paths"): categories["static_security"] -= 2
    categories["build"] = 10   # static/demo placeholder
    categories["tests"] = 15 if any("test" in f.lower() for f in scan.get("files",[])) else 8
    total = sum(max(0,v) for v in categories.values())
    total = min(100,total)
    if total >= 90: label = "Very Ready"
    elif total >= 75: label = "Ready with Warnings"
    elif total >= 60: label = "Needs Attention"
    else: label = "Not Ready"
    return {"score": total, "label": label, "categories": categories}