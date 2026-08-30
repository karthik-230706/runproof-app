# RunProof Security Model

## Web identity
- Passwords are never stored in plaintext.
- Passwords use Python `hashlib.scrypt` with a unique random salt.
- Login sessions use random tokens; only token hashes are stored in SQLite.
- The browser receives the session in an HttpOnly SameSite cookie.
- OTPs expire and have attempt limits.
- Auth endpoints include basic rate limiting.

## Project privacy
- Every project belongs to one authenticated user.
- API queries verify project ownership.
- ZIP extraction blocks path traversal and symlinks.
- Uploads have compressed size, uncompressed size and file-count limits.
- Reports include environment variable NAMES only, never their values.
- Sensitive files are warned about by file name only.

## Project execution
Uploaded source code is untrusted code.

**Default: `static` mode.** It never executes project code.

**Trusted mode** is only for local hackathon demos using code you personally control. It uses `subprocess.run(..., shell=False)`, an executable allowlist, timeouts and a reduced environment.

Production recommendation: move execution into ephemeral isolated containers/VMs with:
- network disabled by default,
- CPU / RAM / process limits,
- non-root user,
- read-only base filesystem,
- writable disposable workspace,
- no host secrets,
- strict artifact extraction,
- automatic destruction after the job.
