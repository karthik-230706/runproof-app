# RunProof Frontend Prototype

A polished, beginner-friendly frontend prototype for **RunProof — Software Reproducibility Verifier**.

## What is included
- Landing page
- Sign up
- Login
- OTP verification (demo/mock)
- First-time onboarding
- Main dashboard
- New project analysis wizard
- Live scanning animation
- Project overview
- RunProof Doctor
- Readiness score
- Reproducibility verification
- Build A / Build B hash comparison
- RunProof Passport
- Reports page
- Security Center
- Settings
- Beginner Mode
- Dark / Light mode
- Command palette (Ctrl + K)

## Important
This ZIP contains the **frontend prototype only**.

The OTP flow is a **safe demo**. It does **not send a real SMS**.
For real phone OTP, connect the frontend to a backend/auth provider such as:
- Firebase Authentication
- Supabase Auth
- Twilio Verify
- AWS Cognito

Never put OTP secrets, API keys, database passwords, or service credentials in frontend JavaScript.

## Run in VS Code

### Easiest
1. Extract the ZIP.
2. Open the extracted `RunProof_Frontend` folder in VS Code.
3. Install the **Live Server** extension.
4. Right-click `index.html`.
5. Click **Open with Live Server**.

### Without Live Server
If Python is installed:

```bash
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

## Demo login
You can use any email/password in the demo.

The OTP screen accepts:

```text
482175
```

## Suggested next step
Connect this frontend to the RunProof Python backend using REST APIs:

- `POST /scan`
- `POST /check`
- `POST /verify`
- `GET /passport`
- `GET /report`