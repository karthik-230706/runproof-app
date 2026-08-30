# Backend Integration Guide

The frontend is designed so your Python backend can later replace the demo data.

## Recommended API routes

### POST /api/scan
Input:
```json
{
  "project_id": "uploaded-project-id"
}
```

Output:
```json
{
  "name": "MyProject",
  "type": "Python",
  "runtime": "Python 3.11",
  "dependencies": 18,
  "tests": 12
}
```

### POST /api/check
Output:
```json
{
  "checks": [
    {"name": "Runtime", "status": "pass"},
    {"name": "Dependencies", "status": "warning"},
    {"name": "Environment", "status": "fail"}
  ],
  "issues": [
    {
      "title": "DATABASE_URL is missing",
      "severity": "high",
      "why": "The project expects a database connection.",
      "fix": "Configure DATABASE_URL before running."
    }
  ],
  "score": 92
}
```

### POST /api/verify
Output:
```json
{
  "build_a_hash": "A72F...",
  "build_b_hash": "A72F...",
  "match": true,
  "verified": true
}
```

### GET /api/passport/:project_id
Returns RunProof Passport JSON.

### GET /api/report/:project_id
Returns an HTML or PDF report.

## Authentication
For production, use a proven authentication provider or backend library.

Recommended:
- Firebase Authentication
- Supabase Auth
- AWS Cognito
- Auth0
- Twilio Verify for SMS OTP

## Security rules
- Use HTTPS.
- Never store plaintext passwords.
- Never verify OTP in frontend JavaScript.
- Never expose service/API credentials in frontend files.
- Rate-limit login and OTP attempts.
- Use secure, HTTP-only session cookies where possible.
- Validate uploaded project files.
- Isolate build execution in a sandbox/container.
- Never run arbitrary uploaded commands directly on your host machine.
- Redact secrets from logs and reports.