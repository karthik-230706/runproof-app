from pathlib import Path
p=Path('dist');p.mkdir(exist_ok=True);(p/'app.txt').write_text('broken demo\n')
