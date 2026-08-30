# RunProof Ultimate V4 — Fully Wired

**RunProof — Build. Verify. Prove.**

This is the complete full-stack RunProof prototype. V3 focuses on one rule:

> If a user can see a button, card, icon, project, notification, setting, or menu item, it should open, respond, or clearly explain why an external setup is required.

## Fastest way to start on Windows

1. Extract the ZIP.
2. Open the extracted `RunProof_Ultimate_v3` folder.
3. Double-click `START_RUNPROOF.bat`.
4. Wait until the terminal says RunProof is running.
5. Open `http://127.0.0.1:8000`.

The starter automatically creates `.venv`, installs packages, creates `.env` if missing, checks Python files, and starts RunProof.

## What V3 includes

### Account and security
- Signup and login
- Mandatory phone verification before first account access
- Real SMS OTP support with Twilio Verify
- OTP expiry, resend limits, and attempt limits
- Password hashing
- HttpOnly browser sessions
- Change Password
- Profile page and Edit Profile
- Masked phone number display
- Security Center
- API/CLI tokens: create, one-time reveal, hashed storage, revoke

### Dashboard
- Time-aware greeting: Good morning / afternoon / evening
- Clickable Projects, Verified, Need Attention, and Average Score cards
- Clickable recent project names
- Activity history
- Workspace empty state when nothing exists

### Top-bar controls
- Working Dark/Light theme button
- Working notification bell and unread indicator
- Working profile/avatar dropdown
- Working Ctrl+K command/search palette
- Project search

### RunProof project journey
- Add project ZIP
- Good Reproducible Demo
- Broken Setup Demo
- Non-Reproducible Demo
- Live scan animation
- Execution Contract
- Deep checks
- RunProof Doctor
- Readiness score
- Verification Lab
- RunProof Passport
- HTML report

### Honest reproducibility proof
V3 does not call a source copy a deterministic build proof.

- Built-in demos can run their controlled `build.py` twice.
- Good Demo → two artifacts match → **VERIFIED REPRODUCIBLE**.
- Broken Demo → build fails → **BUILD VERIFICATION FAILED**.
- Non-Repro Demo → both builds succeed but hashes differ → **NOT REPRODUCIBLE**.
- Uploaded projects in default Safe Mode are **not executed**. They can receive a Source Snapshot Match, but not a Verified Reproducible passport.

To execute a `build.py` from a project you personally trust, set:

```text
RUNPROOF_EXECUTION_MODE=trusted
```

Do not use trusted mode for unknown uploaded code.

### Workspace pages that actually work
- Projects
- RunProof Doctor — all project issues
- Verifications list
- Passports list
- Reports list
- Notifications
- Team invitation records
- Security Center
- Settings
- GitHub integration status/setup page
- Developer Settings
- Help Center

### RunProof Guide
A floating RunProof Guide box is included. It can answer app questions such as:
- How do I add a project?
- Why is my score low?
- How do I verify?
- What is a Passport?
- How can my friend open RunProof?

The built-in guide works without an external AI API.

## Real phone OTP

The backend is already coded for **Twilio Verify**.

Open `.env` and add:

```text
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_VERIFY_SERVICE_SID=...
RUNPROOF_DEMO_MODE=0
```

Then restart RunProof. Signup will fail safely if real-only OTP is enabled but the SMS provider is not configured.

See `docs/REAL_OTP_SETUP.md`.

## Another laptop on the same Wi-Fi

V3 defaults to:

```text
RUNPROOF_HOST=0.0.0.0
```

When RunProof starts, the terminal prints:

```text
This laptop : http://127.0.0.1:8000
Same Wi-Fi  : http://YOUR_LOCAL_IP:8000
```

Give the **Same Wi-Fi** address to your friend. Windows Firewall may ask to allow Python on Private networks.

See `docs/FRIENDS_LAPTOP_SETUP.md`.

## Main folders

```text
RunProof_Ultimate_v3/
├── backend/
│   ├── app.py
│   └── core/
├── frontend/
│   ├── index.html
│   ├── styles/app.css
│   └── scripts/app.js
├── demo/
│   ├── good_project/
│   ├── broken_project/
│   └── non_reproducible_project/
├── docs/
├── START_RUNPROOF.bat
├── CHECK_RUNPROOF.bat
├── SHOW_NETWORK_ADDRESS.bat
├── requirements.txt
├── .env.example
└── run.py
```

## For SIH demonstration

Use the three built-in demos to show the difference between:

1. Ready and reproducible
2. Broken setup
3. Successful but non-deterministic build

That makes the verification claim demonstrable instead of only visual.


## V4 dashboard update

The dashboard now follows the supplied premium developer-dashboard reference: sidebar profile card, live notification count, clickable issue count, richer Recent Projects card, score ring, check strip, Recent Activity table, public GitHub import, Share RunProof button, CLI page, and Documentation page.
