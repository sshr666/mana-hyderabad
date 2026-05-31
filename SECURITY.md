# Security Policy

## Supported Versions

Mana Hyderabad is currently a hackathon MVP. Security fixes are accepted on the `main` branch until formal releases are created.

## Reporting a Vulnerability

Please do not open public issues for vulnerabilities. Report suspected issues privately to the maintainers through GitLab private channels.

Include:

- Affected route, endpoint, or file.
- Steps to reproduce.
- Expected and observed behaviour.
- Any logs or screenshots with secrets redacted.

## Security Expectations

- Do not commit `.env`, API keys, Cloudinary secrets, database credentials, or citizen personal data.
- Use `npm audit`, `pip-audit`, and Gitleaks before release.
- Keep uploaded files restricted to validated image types.
- Treat AI outputs as recommendations that require human verification.
- Avoid wildcard CORS origins outside local development.

## Current MVP Limitations

Authentication and role-based authorization are not implemented yet. Do not deploy this MVP as a public production municipal service without adding authentication, rate limiting, audit logging, and a privacy review.
