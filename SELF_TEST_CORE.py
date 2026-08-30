from backend.core.analyzer import analyze_project
from backend.core.verifier import verify_project

cases = [
    ("demo/good_project", "VERIFIED_REPRODUCIBLE"),
    ("demo/broken_project", "BUILD_FAILED"),
    ("demo/non_reproducible_project", "NOT_REPRODUCIBLE"),
]

print("RunProof core self-test")
print("----------------------")
for path, expected in cases:
    analysis = analyze_project(path)
    result = verify_project(path, allow_execution=True)
    print(f"{path}: score={analysis['score']['score']} verification={result['status']}")
    if result["status"] != expected:
        raise SystemExit(f"FAILED: expected {expected}")

safe = verify_project("demo/good_project", allow_execution=False)
print(f"Safe uploaded-code mode: {safe['status']} verified={safe['verified']}")
if safe["verified"]:
    raise SystemExit("FAILED: Safe Mode must not claim deterministic build proof")

print("ALL CORE TESTS PASSED")
