from pathlib import Path
import zipfile, shutil, os

class UploadError(ValueError): pass

def safe_extract_zip(zip_path: Path, dest: Path, cfg):
    dest.mkdir(parents=True, exist_ok=True)
    total=0; count=0
    with zipfile.ZipFile(zip_path) as z:
        infos=z.infolist()
        if len(infos)>cfg.max_files: raise UploadError('Too many files in ZIP.')
        for info in infos:
            count += 1; total += info.file_size
            if total>cfg.max_uncompressed_bytes: raise UploadError('ZIP expands beyond allowed size.')
            name=info.filename.replace('\\','/')
            p=Path(name)
            if p.is_absolute() or '..' in p.parts: raise UploadError('Unsafe ZIP path detected.')
            # Unix symlink file type in external attrs
            mode=(info.external_attr>>16)&0o170000
            if mode==0o120000: raise UploadError('Symlinks are not allowed in uploaded ZIPs.')
        for info in infos:
            name=info.filename.replace('\\','/')
            target=(dest/Path(name)).resolve()
            if dest.resolve() not in target.parents and target!=dest.resolve(): raise UploadError('Path escape blocked.')
            if info.is_dir(): target.mkdir(parents=True, exist_ok=True); continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target,'wb') as dst: shutil.copyfileobj(src,dst,1024*1024)
    # collapse a single top-level directory
    children=list(dest.iterdir())
    if len(children)==1 and children[0].is_dir():
        return children[0]
    return dest
