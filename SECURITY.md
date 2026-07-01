# Security Policy

## Supported Versions

| Version | Supported |
| :--- | :--- |
| Latest (`master`) | ✅ Active |
| Older commits | ❌ No support |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub Issue for security vulnerabilities.**

If you discover a security issue in this project (misconfiguration, leaked credential, exploit vector), please report it privately:

1. **Email:** Send details to the repository owner via GitHub's private contact.
2. **Scope:** Include steps to reproduce, affected component, and potential impact.
3. **Response time:** You will receive an acknowledgement within **48 hours** and a resolution timeline within **7 days**.

---

## Security Design Principles

This project follows these security principles:

- **Zero Trust:** All access restricted to private network ranges. No public exposure of admin interfaces.
- **Secrets management:** All credentials are stored in `.env.local` (git-ignored), never in source code.
- **Least privilege:** RBAC enforced at both workspace and project level.
- **Air-gapped by design:** Telemetry disabled, no external API calls from the deployed stack.
- **Defence in depth:** Caddy security headers, rate limiting, Docker network isolation, UFW firewall.

---

## Known Security Controls

| Control | Status |
| :--- | :--- |
| Security headers (CSP, HSTS, X-Frame, nosniff) | ✅ Active |
| Rate limiting (30 req/s per IP) | ✅ Active |
| `/god-mode` restricted to LAN/Tailscale IPs | ✅ Active |
| Public registration disabled | ✅ Active |
| Docker internal network isolation | ✅ Active |
| Log rotation (10MB max) | ✅ Active |
| Automated daily backup | ✅ Active |
| Secrets in `.env.local` (git-ignored) | ✅ Active |
| Branch protection (master) | ✅ Recommended |
| GitHub secret scanning | ✅ Recommended |

---

## Credential Hygiene

- `.env.local` is git-ignored and must **never** be committed.
- All default credentials in `.env.example` are placeholder values (`CHANGE_ME_*`).
- Rotate credentials immediately if any secret is exposed.

---

> This project is for internal on-premises deployment. Do not expose any service ports publicly without a full security review.
