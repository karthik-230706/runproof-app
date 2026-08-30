from pathlib import Path
import hashlib

root=Path(__file__).resolve().parent
source=(root/"app.py").read_bytes()
digest=hashlib.sha256(source).hexdigest()
out=root/"dist"
out.mkdir(exist_ok=True)
(out/"artifact.txt").write_text("RunProof deterministic demo artifact\nsource="+digest+"\n",encoding="utf-8")
print("Built deterministic artifact.")
