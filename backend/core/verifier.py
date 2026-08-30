from pathlib import Path
import os, shutil, subprocess, sys, tempfile
from .fingerprint import sha256_tree

IGNORED = {".git","__pycache__",".venv","node_modules",".runproof"}

def _run_python_build(copy_root: Path):
    build_py = copy_root / "build.py"
    if not build_py.exists():
        return {
            "attempted": False,
            "success": False,
            "reason": "No build.py found. This prototype only executes an explicit Python build.py in trusted mode."
        }
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    try:
        r = subprocess.run(
            [sys.executable, "build.py"],
            cwd=copy_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False
        )
    except subprocess.TimeoutExpired:
        return {"attempted": True, "success": False, "reason": "Build timed out after 15 seconds."}
    except Exception as e:
        return {"attempted": True, "success": False, "reason": f"Build could not start: {e}"}
    return {
        "attempted": True,
        "success": r.returncode == 0,
        "returncode": r.returncode,
        "stdout": (r.stdout or "")[-2500:],
        "stderr": (r.stderr or "")[-2500:],
        "reason": "Build completed." if r.returncode == 0 else "Build command failed."
    }

def _artifact_root(copy_root: Path):
    for name in ("dist","build","out"):
        p = copy_root / name
        if p.exists():
            return p, name
    for name in ("artifact.txt","artifact.bin"):
        p = copy_root / name
        if p.exists():
            return p.parent, name
    return copy_root, "project-tree"

def verify_project(project_path: str, allow_execution: bool):
    src = Path(project_path).resolve()
    if not allow_execution:
        with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
            a=Path(ta)/"project"; b=Path(tb)/"project"
            shutil.copytree(src,a,dirs_exist_ok=True)
            shutil.copytree(src,b,dirs_exist_ok=True)
            ha=sha256_tree(a); hb=sha256_tree(b)
        return {
            "mode":"static-source-check",
            "proof_level":"Source Snapshot",
            "hash_a":ha,"hash_b":hb,
            "match":ha==hb,
            "verified":False,
            "status":"SOURCE_MATCH_ONLY" if ha==hb else "SOURCE_MISMATCH",
            "build_a":{"attempted":False,"success":False},
            "build_b":{"attempted":False,"success":False},
            "note":"The source copies match, but deterministic build proof was not executed. Use a trusted demo or explicitly enable trusted execution for code you own."
        }

    with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
        a=Path(ta)/"project"; b=Path(tb)/"project"
        shutil.copytree(src,a,dirs_exist_ok=True)
        shutil.copytree(src,b,dirs_exist_ok=True)
        ra=_run_python_build(a)
        rb=_run_python_build(b)
        if not (ra.get("success") and rb.get("success")):
            return {
                "mode":"trusted-build",
                "proof_level":"Build Verification",
                "hash_a":None,"hash_b":None,"match":False,"verified":False,
                "status":"BUILD_FAILED",
                "build_a":ra,"build_b":rb,
                "note":"RunProof could not complete two successful builds, so reproducibility is not verified."
            }
        arta, labela=_artifact_root(a)
        artb, labelb=_artifact_root(b)
        ha=sha256_tree(arta); hb=sha256_tree(artb)
        match=ha==hb
        return {
            "mode":"trusted-build",
            "proof_level":"Build Verification",
            "artifact_a":labela,"artifact_b":labelb,
            "hash_a":ha,"hash_b":hb,
            "match":match,"verified":match,
            "status":"VERIFIED_REPRODUCIBLE" if match else "NOT_REPRODUCIBLE",
            "build_a":ra,"build_b":rb,
            "note":"Two independent trusted builds produced matching artifact fingerprints." if match else "Two successful builds produced different artifact fingerprints. The build is nondeterministic."
        }
