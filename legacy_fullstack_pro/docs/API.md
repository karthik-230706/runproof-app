# RunProof API

## Authentication
- `POST /api/auth/signup`
- `POST /api/auth/verify-otp`
- `POST /api/auth/resend-otp`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

## Projects
- `GET /api/projects`
- `POST /api/projects/upload` (`multipart/form-data`, field `project_zip`)
- `DELETE /api/projects/<id>`

## Analysis
- `POST /api/projects/<id>/check`
- `POST /api/projects/<id>/verify`
- `GET /api/projects/<id>/passport`
- `GET /api/projects/<id>/report`
- `GET /api/projects/<id>/sbom`
- `GET /api/projects/<id>/evidence`
- `GET /api/projects/<id>/activity`

## Passport
- `POST /api/passports/verify`

## Dashboard
- `GET /api/dashboard`
