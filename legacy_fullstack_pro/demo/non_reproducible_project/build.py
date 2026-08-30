from pathlib import Path
from datetime import datetime, timezone
p=Path('dist');p.mkdir(exist_ok=True);(p/'app.txt').write_text('Built at '+datetime.now(timezone.utc).isoformat()+'\n')
