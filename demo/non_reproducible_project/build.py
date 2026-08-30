from pathlib import Path
from datetime import datetime, timezone
out=Path("dist")
out.mkdir(exist_ok=True)
(out/"artifact.txt").write_text("built_at="+datetime.now(timezone.utc).isoformat()+"\n",encoding="utf-8")
print("Built timestamped artifact.")
