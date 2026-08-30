# RunProof V3 Feature Checklist

## Fully wired inside the prototype
- [x] Landing page
- [x] Signup
- [x] Login
- [x] Mandatory OTP verification gate
- [x] OTP resend / limits
- [x] Dynamic greeting
- [x] Workspace
- [x] Clickable dashboard cards
- [x] Clickable projects
- [x] Project details
- [x] Bell popup
- [x] Notification page
- [x] Profile popup
- [x] Profile page
- [x] Edit profile
- [x] Password change
- [x] Dark/light mode
- [x] Ctrl+K search
- [x] Project search
- [x] Project upload
- [x] Project scanner
- [x] Execution Contract
- [x] Deep checks
- [x] RunProof Doctor
- [x] All-project issues page
- [x] Score explanation
- [x] Verification list
- [x] Real controlled demo build verification
- [x] Deterministic good demo
- [x] Build-failure demo
- [x] Nondeterministic mismatch demo
- [x] Passport list
- [x] Passport JSON download
- [x] Reports list
- [x] HTML report download
- [x] Team invitation records
- [x] API/CLI token creation
- [x] API/CLI token revoke
- [x] Bearer-token backend authentication
- [x] Security Center
- [x] Local-network sharing address
- [x] Settings pages
- [x] GitHub setup/status page
- [x] Help Center
- [x] Floating RunProof Guide

## External services that require credentials
- Real SMS delivery → Twilio Verify credentials
- GitHub OAuth live account connection → GitHub OAuth App credentials
- Team invitation email delivery → email provider
- Public internet URL → production deployment/hosting

Those external services cannot be made real only with frontend code; the V3 UI shows their status instead of pretending they are connected.
