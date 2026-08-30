import os, sys
from pathlib import Path

if not os.environ.get("DATABASE_URL"):
    print("DATABASE_URL is required.", file=sys.stderr)
    raise SystemExit(2)
Path("dist").mkdir(exist_ok=True)
Path("dist/artifact.txt").write_text("connected\n",encoding="utf-8")
