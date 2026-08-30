from pathlib import Path
import os
import re

SECRET_WORDS = ("SECRET","TOKEN","PASSWORD","PASS","KEY","DATABASE_URL")

def required_env_names(project_path):
    root = Path(project_path)
    env_example = root / ".env.example"
    names = []
    if env_example.exists():
        for raw in env_example.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name = line.split("=",1)[0].strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                names.append(name)
    return sorted(set(names))

def check_environment(project_path):
    names = required_env_names(project_path)
    present = [n for n in names if os.environ.get(n)]
    missing = [n for n in names if not os.environ.get(n)]
    return {
        "required_names": names,
        "present_names": present,
        "missing_names": missing,
        "values_exposed": False
    }