# Contributing Guide

This repository may be **private**. If you have been invited as a collaborator, follow this guide to get started.

---

## 1. Accept the Invitation

1. Check your email for a GitHub invitation from `Binhchuoizzz`.
2. Click **Accept invitation**.
3. You now have **write access** to the repository.

---

## 2. Clone the Repository

```bash
# HTTPS (recommended — use a GitHub Personal Access Token as password)
git clone https://github.com/Binhchuoizzz/sentinel-taskboard.git
cd sentinel-taskboard

# SSH (if you have your SSH key added to your GitHub account)
git clone git@github.com:Binhchuoizzz/sentinel-taskboard.git
cd sentinel-taskboard
```

> **If HTTPS asks for a password:** Use a [GitHub Personal Access Token (PAT)](https://github.com/settings/tokens)
> with scope `repo` — not your GitHub account password.

---

## 3. Set Up Your Environment

```bash
# Copy the environment template
cp env/.env.example env/.env.local

# Edit .env.local — fill in the server IP and credentials
nano env/.env.local
```

Key variables to set:
- `WEB_URL` — IP or domain of the target server
- `CORS_ALLOWED_ORIGINS` — same as WEB_URL
- All `*_PASSWORD` fields — use strong random values

> ⚠️ **Never commit `.env.local`** — it is git-ignored for security.

---

## 4. Deploy

```bash
# Install prerequisites: Docker, Docker Compose v2, Python 3
./scripts/check-prerequisites.sh

# Deploy the full stack
PLANE_INSTALL_DIR="./plane-app" ./scripts/deploy-poc.sh
```

---

## 5. Workflow for Contributing Changes

```bash
# Always pull latest before working
git pull origin master

# Create a feature/fix branch
git checkout -b fix/your-description

# Make your changes, then commit
git add .
git commit -m "fix: describe what you changed"

# Push your branch
git push origin fix/your-description

# Open a Pull Request on GitHub for review
```

---

## 6. Branch Rules

| Branch | Rule |
| :--- | :--- |
| `master` | Protected — requires PR review before merge |
| `fix/*` | Feature/fix branches — push freely |
| `hotfix/*` | Emergency patches |

---

## 7. What NOT to Commit

- `env/.env.local` — contains secrets (git-ignored automatically)
- `plane-app/plane.env` — generated at deploy time (git-ignored)
- Any `*.pem`, `*.key`, `*.crt` files
- Personal credentials or internal network addresses

---

## 8. Running Tests Locally

```bash
# Unit tests (no server needed)
python3 -m unittest discover -s tests/unit

# Integration tests (requires a running stack)
BASE_URL="http://<server-ip>" python3 tests/integration/test_full_integration.py
```

---

## Questions?

Open a GitHub Issue or contact the repository owner directly.
