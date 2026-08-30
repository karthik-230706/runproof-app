from pathlib import Path

def detect_project_type(scan):
    files = scan.get("files", [])
    names = {Path(f).name for f in files}
    suffixes = {Path(f).suffix.lower() for f in files}
    if "package.json" in names:
        return {"type":"Node.js","runtime":"node","manifest":"package.json"}
    if "pom.xml" in names:
        return {"type":"Java Maven","runtime":"java","manifest":"pom.xml"}
    if "build.gradle" in names:
        return {"type":"Java Gradle","runtime":"java","manifest":"build.gradle"}
    if ".py" in suffixes or "pyproject.toml" in names or "requirements.txt" in names:
        return {"type":"Python","runtime":"python","manifest":"requirements.txt" if "requirements.txt" in names else "pyproject.toml"}
    return {"type":"Unknown","runtime":None,"manifest":None}