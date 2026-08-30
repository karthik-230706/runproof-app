def make_issues(deps, env, runtime, security):
    issues = []
    if not runtime.get("available"):
        issues.append({
            "severity":"high","title":"Required runtime is missing",
            "what":"RunProof could not find the required runtime on this computer.",
            "why":"The project cannot start without its runtime.",
            "fix":"Install the required runtime or use a matching isolated environment."
        })
    if deps.get("unpinned",0):
        issues.append({
            "severity":"medium","title":f"{deps['unpinned']} dependency version(s) are not fixed",
            "what":"Some dependencies do not use an exact version.",
            "why":"A future package release can change the project result.",
            "fix":"Pin exact compatible versions and commit the lock/manifest file."
        })
    if env.get("missing_names"):
        issues.append({
            "severity":"high","title":"Required environment settings are missing",
            "what":"Missing names: " + ", ".join(env["missing_names"][:8]),
            "why":"The project may fail at startup or behave differently.",
            "fix":"Configure the missing environment values securely. Do not commit real secrets."
        })
    if security.get("sensitive_files"):
        issues.append({
            "severity":"high","title":"Sensitive file names were found",
            "what":"Potential secret-bearing files exist in the project.",
            "why":"Secrets can leak when a repository is shared.",
            "fix":"Remove secrets from the repository, rotate exposed credentials, and use a secrets manager."
        })
    if security.get("machine_specific_paths"):
        issues.append({
            "severity":"medium","title":"Machine-specific paths were detected",
            "what":"Some files contain local absolute paths.",
            "why":"Those paths may not exist on another computer.",
            "fix":"Use relative paths or environment-based configuration."
        })
    if not issues:
        issues.append({
            "severity":"info","title":"No major static reproducibility issues found",
            "what":"The current static checks passed.",
            "why":"This improves readiness, but deterministic build proof is still a separate step.",
            "fix":"Run reproducibility verification in an isolated build environment."
        })
    return issues