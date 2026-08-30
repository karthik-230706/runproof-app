from pathlib import Path
import re

SENSITIVE_NAMES = {".env","id_rsa","id_ed25519",".npmrc","credentials.json"}
DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bdel\s+/[sq]\b",
    r"\bformat\s+[a-z]:",
    r"\bshutdown\b",
    r"\bpowershell\b.*\bEncodedCommand\b",
]

def inspect_static_security(project_path):
    root = Path(project_path)
    sensitive = []
    dangerous = []
    machine_paths = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        if p.name in SENSITIVE_NAMES:
            sensitive.append(rel)
        if p.suffix.lower() in {".py",".js",".ts",".sh",".ps1",".bat",".cmd",".json",".yml",".yaml",".toml",".txt",".md"}:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")[:300000]
            except Exception:
                continue
            for pat in DANGEROUS_PATTERNS:
                if re.search(pat, text, flags=re.I):
                    dangerous.append({"file":rel,"pattern":pat})
            if re.search(r"[A-Za-z]:\\\\Users\\\\[^\\\\\s]+", text) or "/Users/" in text or "/home/" in text:
                machine_paths.append(rel)
    return {
        "sensitive_files": sensitive,
        "dangerous_patterns": dangerous,
        "machine_specific_paths": sorted(set(machine_paths))
    }