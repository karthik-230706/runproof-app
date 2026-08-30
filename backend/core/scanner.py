from pathlib import Path

IMPORTANT_FILES = {
    "requirements.txt", "pyproject.toml", "Pipfile",
    "package.json", "package-lock.json",
    "pom.xml", "build.gradle", "gradlew", "gradlew.bat",
    ".env.example", "README.md", "pytest.ini"
}

def scan_project(path: str):
    root = Path(path).resolve()
    files = []
    dirs = []
    for p in root.rglob("*"):
        rel = str(p.relative_to(root))
        if p.is_file():
            files.append(rel)
        elif p.is_dir():
            dirs.append(rel)
    important = [f for f in files if Path(f).name in IMPORTANT_FILES]
    return {
        "project_name": root.name,
        "root": str(root),
        "file_count": len(files),
        "folder_count": len(dirs),
        "files": files[:500],
        "important_files": important
    }