# RunProof V3 API

## Public
- `GET /api/health`
- `GET /api/otp-status`
- `POST /api/auth/signup`
- `POST /api/auth/verify-otp`
- `POST /api/auth/resend-otp`
- `POST /api/auth/login`
- `POST /api/auth/demo`

## Account
- `GET /api/me`
- `GET /api/profile`
- `PUT /api/profile`
- `POST /api/auth/change-password`
- `POST /api/auth/logout`

## Dashboard / navigation
- `GET /api/dashboard`
- `GET /api/workspace`
- `GET /api/search?q=`
- `GET /api/notifications`
- `POST /api/notifications/read-all`
- `GET /api/network-info`
- `POST /api/assistant`

## Projects
- `POST /api/projects`
- `GET /api/projects/:id`
- `POST /api/projects/:id/analyze`
- `POST /api/projects/:id/verify`
- `GET /api/projects/:id/passport`
- `GET /api/projects/:id/report`

## Aggregate product pages
- `GET /api/issues`
- `GET /api/verifications`
- `GET /api/passports`
- `GET /api/reports`

## Developer tokens
- `GET /api/tokens`
- `POST /api/tokens`
- `DELETE /api/tokens/:id`

A live, non-revoked token can authenticate supported API reads using:

```text
Authorization: Bearer rp_live_...
```

## Team
- `GET /api/team/invites`
- `POST /api/team/invites`
- `DELETE /api/team/invites/:id`

## Settings / audit
- `GET /api/settings/status`
- `GET /api/audit`
