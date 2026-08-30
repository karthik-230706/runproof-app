# RunProof Security Model

## Authentication
- Passwords hashed on backend.
- OTP challenge expires.
- OTP attempts are rate-limited.
- Session cookie is HttpOnly.
- Use Secure cookies behind HTTPS in production.

## Project access
- Every project belongs to an owner.
- API endpoints check ownership.
- Uploaded ZIP paths are validated.
- ZIP file count and expanded size are limited.

## Secrets
- Environment variable names can be checked.
- Secret values must not be displayed in frontend reports.
- Sensitive file names are flagged.
- Production logs must redact tokens and passwords.

## Build safety
The included prototype does NOT execute arbitrary uploaded code.

Production design:
- isolated container / microVM
- no host credentials
- no privileged mode
- restricted network
- CPU / memory / time limits
- read-only base image
- separate ephemeral workspace
- output artifact collection only

## OTP production
Replace demo OTP with a trusted provider.