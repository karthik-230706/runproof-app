from pathlib import Path
import json
import re

PIN_PATTERNS = ("==", "~=", "===")

def inspect_dependencies(project_path, project_type):
    root = Path(project_path)
    t = project_type.get("type","")
    deps = []
    pinned = []
    unpinned = []
    source = None

    if t == "Python":
        req = root / "requirements.txt"
        if req.exists():
            source = "requirements.txt"
            for raw in req.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                deps.append(line)
                if any(x in line for x in PIN_PATTERNS):
                    pinned.append(line)
                else:
                    unpinned.append(line)
    elif t == "Node.js":
        pkg = root / "package.json"
        if pkg.exists():
            source = "package.json"
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                all_deps = {}
                all_deps.update(data.get("dependencies",{}))
                all_deps.update(data.get("devDependencies",{}))
                for k,v in all_deps.items():
                    item = f"{k}@{v}"
                    deps.append(item)
                    if isinstance(v,str) and re.match(r"^\d+\.\d+\.\d+", v):
                        pinned.append(item)
                    else:
                        unpinned.append(item)
            except Exception:
                pass

    return {
        "source": source,
        "count": len(deps),
        "dependencies": deps[:200],
        "pinned": len(pinned),
        "unpinned": len(unpinned),
        "unpinned_items": unpinned[:50]
    }