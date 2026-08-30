# RunProof FullStack Pro

**RunProof — Software Reproducibility Verifier**

This package combines the polished frontend with a real Python backend and a standard-library RunProof core engine.

## Included

### Frontend
- Landing page
- Signup, login and OTP UI
- Dashboard
- Project analysis journey
- RunProof Doctor
- Readiness score
- Build A / Build B verification view
- Passport, reports, security center and settings

### Backend
- Flask REST API
- SQLite database
- Account signup/login
- Secure password hashing with `hashlib.scrypt`
- 6-digit OTP with expiry and attempt limits
- Secure HttpOnly session cookie
- Rate limiting for auth routes
- ZIP project upload with Zip-Slip and zip-bomb checks
- Per-user project ownership
- Audit/activity log
- Dashboard/project APIs

### RunProof Core Engine
- Project scanner
- Python / Node.js / Java detector
- Runtime and tool checks
- Dependency and pinning analysis
- Environment-name analysis without exposing secret values
- Sensitive-file warnings
- Safe execution policy
- Build and test runner for trusted local demo projects
- Readiness scoring
- RunProof Doctor explanations
- Two-clean-build verification
- SHA-256 artifact fingerprint comparison
- Signed RunProof Passport (HMAC)
- HTML report
- Dependency inventory (SBOM-lite)
- Evidence bundle ZIP

## Important security rule

Uploaded code must be treated as **untrusted**. By default RunProof uses:

```text
RUNPROOF_EXECUTION_MODE=static
```

This performs static checks and DOES NOT execute uploaded code.

For the included hackathon demo projects only, you can enable:

```text
RUNPROOF_EXECUTION_MODE=trusted
```

Do not enable trusted local execution for unknown public uploads. A production version should execute builds in isolated disposable sandboxes/containers/VMs with no network, resource limits and strict filesystem controls.

## Start in VS Code

### Windows

1. Extract this ZIP.
2. Open `RunProof_FullStack_Pro` in VS Code.
3. Open Terminal.
4. Run:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Demo OTP

In console mode, the backend prints the OTP in the terminal. If `RUNPROOF_DEV_SHOW_OTP=1`, the API also returns it for local demo convenience. Never enable that in production.

## CLI demo

Static check:

```bash
python cli/runproof.py check demo/good_project
```

Trusted demo verification:

```bash
python cli/runproof.py verify demo/good_project --execution trusted
```

Non-reproducible demo:

```bash
python cli/runproof.py verify demo/non_reproducible_project --execution trusted
```

## Core claim

The **RunProof core engine** uses Python standard library modules only. Flask is the optional web/API layer.
