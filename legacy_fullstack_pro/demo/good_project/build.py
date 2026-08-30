from pathlib import Path
src=Path('src/message.txt').read_text(encoding='utf-8').strip()
out=Path('dist');out.mkdir(exist_ok=True);(out/'app.txt').write_text(src+'\n',encoding='utf-8')
print('deterministic artifact created')
