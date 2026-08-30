# What Was Checked Before Packaging V3

The generated package was checked for:

- Python syntax across backend and core modules
- JavaScript syntax for the full frontend application
- Good Demo core analysis
- Broken Demo core analysis
- Non-Reproducible Demo core analysis
- Good Demo controlled build twice → matching artifact fingerprints
- Broken Demo controlled build → build failure
- Non-Repro Demo controlled build twice → different artifact fingerprints
- Safe Mode → source snapshot match does **not** claim Verified Reproducible

Expected core self-test output ends with:

```text
ALL CORE TESTS PASSED
```

Full Flask HTTP endpoint testing requires the packages from `requirements.txt` to be installed. `START_RUNPROOF.bat` installs them on the user's machine before starting.
