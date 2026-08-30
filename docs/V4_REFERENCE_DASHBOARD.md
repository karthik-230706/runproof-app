# RunProof V4 Reference Dashboard

This version was updated to match the supplied dashboard direction.

## Working interactions

- Dashboard cards open their real pages.
- Recent project name and View Analysis open Project Details.
- Bell opens live notifications and unread count.
- Sidebar Issues shows a live issue count.
- Profile card / profile avatar open account actions and stats.
- Good morning / afternoon / evening changes from the user's local browser time.
- Light / dark mode works and is remembered.
- Ctrl+K opens RunProof search.
- Import from GitHub accepts a public GitHub repository URL and creates a RunProof project.
- Share RunProof shows the LAN URL for another laptop on the same Wi-Fi.
- CLI opens CLI documentation and Developer Token settings.
- Documentation opens feature explanations.
- RunProof Guide AI-style helper remains at the bottom-right.
- Empty pages show a clear empty state instead of doing nothing.

## Real OTP

Real phone OTP is supported with Twilio Verify.

Set:
RUNPROOF_DEMO_MODE=0
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_VERIFY_SERVICE_SID=...

Without a configured SMS provider, a real SMS cannot be sent. Demo mode is intentionally separate from production OTP.