# Real Phone OTP — Very Simple Setup

RunProof already contains the code to send and verify a real phone OTP through **Twilio Verify**.

A real SMS costs/uses an external SMS service, so RunProof needs your provider credentials. Frontend JavaScript alone cannot send a genuine phone SMS.

## Step 1
Create a Twilio account.

## Step 2
In Twilio, create a **Verify Service**.

## Step 3
Copy these three values:

- Account SID
- Auth Token
- Verify Service SID

## Step 4
Open RunProof `.env` and fill:

```text
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
RUNPROOF_DEMO_MODE=0
```

Keep these values only in `.env`. Never place them in `frontend/scripts/app.js`.

## Step 5
Restart RunProof.

Stop:

```text
Ctrl + C
```

Start again:

```powershell
python run.py
```

or double-click `START_RUNPROOF.bat`.

## Step 6
Create an account with international phone format:

```text
+919876543210
```

The flow is:

```text
Signup
  ↓
Twilio sends SMS OTP
  ↓
Enter OTP
  ↓
Twilio approves code
  ↓
RunProof marks phone verified
  ↓
Dashboard opens
```

When `RUNPROOF_DEMO_MODE=0`, RunProof does not silently fall back to a fake OTP. If the SMS provider is not configured, signup stops and tells you to configure it.
