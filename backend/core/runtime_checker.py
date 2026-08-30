import shutil
import subprocess

def _version(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=4, shell=False)
        text = (r.stdout or r.stderr).strip().splitlines()
        return text[0] if text else "Available"
    except Exception:
        return None

def check_runtime(project_type):
    runtime = project_type.get("runtime")
    if not runtime:
        return {"runtime":None,"available":False,"version":None}
    exe = shutil.which(runtime)
    if not exe and runtime == "python":
        exe = shutil.which("python3")
    if not exe:
        return {"runtime":runtime,"available":False,"version":None}
    if runtime == "java":
        version = _version([exe, "-version"])
    else:
        version = _version([exe, "--version"])
    return {"runtime":runtime,"available":True,"version":version}