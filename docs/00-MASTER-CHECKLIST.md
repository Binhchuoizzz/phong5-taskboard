# ✅ MASTER CHECKLIST — Plane Self-Hosted Deployment

> **This is the main file for Agents.** Read this file before starting any task.
> Each task links to a detailed guide file. Agent reads guide → executes → checks off.

---

## How to Use

- `[ ]` = Not started
- `[/]` = In progress
- `[x]` = Complete
- `[!]` = Blocked / Requires user input
- Each task has an accompanying **guide file** → read before executing
- Tasks must be done **in order** unless explicitly noted as parallelizable

---

## PHASE 0: PREPARATION (Day 1)

> 📖 Guide: [01-prerequisites.md](./01-prerequisites.md)

- [x] **0.1** Check server specs (CPU, RAM, Disk, OS version)
- [x] **0.2** Install Docker Engine 24+ and Docker Compose v2
  - [x] `docker --version` → must be >= 24.0
  - [x] `docker compose version` → must be >= 2.0
- [x] **0.3** Install Git
- [x] **0.4** Configure firewall: open ports 80, 443 (or custom port)
- [x] **0.5** Create a dedicated user for Plane (do not run as root)
  ```bash
  sudo useradd -m -s /bin/bash plane-admin
  sudo usermod -aG docker plane-admin
  ```
- [x] **0.6** Check DNS/IP: decide on domain or direct IP
- [x] **0.7** Run prerequisites check script: `./scripts/check-prerequisites.sh`

---

## PHASE 1: DEPLOY PoC (Day 1-2)

> 📖 Guide: [02-poc-deployment.md](./02-poc-deployment.md)

### 1A. Clone & Setup

- [x] **1.1** Clone Plane repository (replaced with optimized & secured Prebuilt Docker Hub version)
- [x] **1.2** Run Plane's setup script (using prebuilt setup script with JSON bug fix)
- [x] **1.3** Copy and edit environment file (auto-generates strong passwords in plane-app/plane.env)
- [x] **1.4** Start services
- [x] **1.5** Verify: all containers running
- [x] **1.6** Access web UI: `http://<server-ip>` → login page appears

### 1B. Verify PoC Healthy

- [x] **1.7** API health check (uvicorn responding HTTP 200 internally)
- [x] **1.8** PostgreSQL connected: DB connection successful, migrations applied
- [x] **1.9** Redis connected: ping/pong successful
- [x] **1.10** MinIO/Storage working: minio container initialized successfully for uploads

---

## PHASE 2: CONFIGURE WORKSPACE & PROJECTS (Day 2-3)

> 📖 Guide: [03-configuration.md](./03-configuration.md)

### 2A. Instance Admin (God Mode)

- [x] **2.1** Log in to God Mode (admin@sentinel.local auto-initialized via Django Shell)
- [x] **2.2** Configure instance settings:
  - [x] Instance name: `Sentinel-Workspace`
  - [x] Enable/disable sign-ups
  - [ ] Email settings (SMTP) if internal mail server available

### 2B. Create Workspace

- [x] **2.3** Create workspace: `Sentinel-Workspace`
- [x] **2.4** Set workspace URL slug: `sentinel`
- [ ] **2.5** Upload workspace logo (if available)

### 2C. Create 7 Projects (one per functional area)

- [x] **2.6** Project `PRJ1-Core` — Core Platform
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.7** Project `PRJ2-Security` — Security Compliance
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.8** Project `PRJ3-DevOps` — Infrastructure & DevOps
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.9** Project `PRJ4-QA` — Quality Assurance
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.10** Project `PRJ5-Integrations` — System Integrations
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.11** Project `PRJ6-Analytics` — Threat Analytics
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local
- [x] **2.12** Project `PRJ7-AI` — AI Engine
  - [x] Set description, cover image
  - [x] Assign lead: admin@sentinel.local

### 2D. Configure Workflow States

- [x] **2.13** Create general workflow for all projects:
  ```
  Backlog → Todo → In Progress → In Review → Testing → Done → Cancelled
  ```
- [x] **2.14** Create custom workflow for PRJ6-Analytics (Incident Response):
  ```
  Detected → Triaging → Investigating → Containment → Eradication → Recovery → Post-Mortem → Closed
  ```
- [x] **2.15** Create custom workflow for PRJ4-QA (Pentest):
  ```
  Scoping → Reconnaissance → Exploitation → Reporting → Remediation Verify → Closed
  ```

### 2E. Configure Labels

- [x] **2.16** Create classification labels:
  ```
  [Priority]  P0-Critical (red) | P1-High (orange) | P2-Medium (yellow) | P3-Low (green)
  [Type]      Bug | Feature | Incident | Audit | Compliance | Research | Deployment | Task
  [Security]  Confidential (red) | Internal (orange) | Public (green)
  [Team]      Cross-team (for tasks spanning multiple projects)
  ```

### 2F. Configure RBAC & Members

- [ ] **2.17** Invite & assign roles:

  | Role | Target Users | Quantity |
  |---|---|---|
  | Admin | Department leads, IT admin | 3-5 |
  | Member | Team leads + staff | ~5000 |
  | Guest | Senior leadership, external partners | 10-20 |

- [ ] **2.18** Assign members to their correct projects
- [ ] **2.19** Test permissions: Member cannot delete project, Guest is view-only

---

## PHASE 3: TEST & VALIDATE (Day 3-4)

> 📖 Guide: [02-poc-deployment.md](./02-poc-deployment.md) (Verification section)

### 3A. Functional Testing

- [ ] **3.1** Create new issue → assign → transition through workflow → done
- [ ] **3.2** Create Cycle (Sprint) → add issues → track progress
- [ ] **3.3** Create Module (Epic) → group related issues
- [ ] **3.4** Test Board view (Kanban) — drag & drop works
- [ ] **3.5** Test List view, Table view, Spreadsheet view
- [ ] **3.6** Test Pages (wiki/documentation)
- [ ] **3.7** Test file attachment upload/download
- [ ] **3.8** Test comment + mention (@user)
- [ ] **3.9** Test filter, search issues
- [ ] **3.10** Test Analytics/Dashboard — charts show correct data

### 3B. Performance Testing

- [ ] **3.11** Measure response time: page load < 3 seconds
- [ ] **3.12** Create 100+ issues → search/filter remains fast
- [ ] **3.13** 10+ concurrent users → no lag

### 3C. Permission Testing

- [ ] **3.14** Admin: can create/delete project, manage members → ✅
- [ ] **3.15** Member: create/edit issue in assigned project → ✅, cannot access other projects → ✅
- [ ] **3.16** Guest: read-only, cannot create/edit → ✅

---

## PHASE 4: SECURITY HARDENING (Day 4-5)

> 📖 Guide: [05-security.md](./05-security.md)

### 4A. Network & SSL

- [x] **4.1** Configure high-security reverse proxy (Caddyfile optimized configuration)
- [x] **4.2** Enable HTTPS with SSL certificate (auto-issued internal CA by Caddy)
- [x] **4.3** Force redirect HTTP → HTTPS (automatic redirect from port 80 to 443)
- [x] **4.4** Configure security headers (X-Frame-Options: DENY, nosniff, HSTS, CSP, Referrer, Permissions)
- [x] **4.5** Restrict access: only internal IP ranges allowed for `/god-mode` (all external IPs blocked)

### 4B. Database Security

- [x] **4.6** Changed default PostgreSQL password (strong random password in plane.env)
- [x] **4.7** PostgreSQL: only listens on internal network, port not exposed externally (runs in plane-network only)
- [ ] **4.8** Enable SSL connection for PostgreSQL (optional for Docker internal virtual network)
- [x] **4.9** Set appropriate `max_connections` (configured max_connections=1000 in docker-compose.db.yaml)

### 4C. Application Security

- [x] **4.10** Disable public sign-up (invite-only — set ENABLE_SIGNUP to 0 in Django DB)
- [x] **4.11** Set strong `SECRET_KEY` in .env (64-char random hex)
- [ ] **4.12** Configure LDAP/SAML if Active Directory available (not yet configured)
- [ ] **4.13** Enable session timeout (30-minute idle)
- [x] **4.14** Review Docker containers: run non-root for data containers (Postgres, Redis, MQ, MinIO)

### 4D. Audit & Compliance

- [ ] **4.15** Enable audit logging (Commercial/Air-gapped edition)
- [x] **4.16** Log rotation: configured rotation limits in docker-compose for all services (max-size 10MB, max-file 3)
- [ ] **4.17** Export audit report test

---

## PHASE 5: BACKUP & DISASTER RECOVERY (Day 5)

> 📖 Guide: [06-backup-restore.md](./06-backup-restore.md)

- [x] **5.1** Create backup script: `./scripts/backup.sh`
  - [x] pg_dump PostgreSQL → compressed file
  - [x] Backup MinIO data directory
  - [x] Backup .env and Docker configs
- [x] **5.2** Test backup: run script → backup file created successfully
- [x] **5.3** Create restore script: `./scripts/restore.sh`
- [x] **5.4** Test restore: restore to new instance → data intact
- [ ] **5.5** Setup automated cron backup:
  ```bash
  # Daily backup at 2:00 AM
  0 2 * * * /path/to/project/scripts/backup.sh
  ```
- [x] **5.6** Backup retention policy: keep 7 daily + 4 weekly + 3 monthly (integrated in backup.sh)
- [x] **5.7** Test disaster recovery: destroy instance → restore from backup → verify data (tested successfully)

---

## PHASE 6: MONITORING & ALERTING (Day 5-6)

> 📖 Guide: [07-monitoring.md](./07-monitoring.md)

- [x] **6.1** Deploy Prometheus (using `monitoring/prometheus.yml`)
- [x] **6.2** Deploy Grafana (auto-provision Prometheus datasource & dashboards)
- [x] **6.3** Configure health check script: `./scripts/health-check.sh`
- [x] **6.4** Setup alerts:
  - [x] CPU > 80% → alert (configured in alert-rules.yml)
  - [x] RAM > 85% → alert (configured in alert-rules.yml)
  - [x] Disk > 90% → alert (configured in alert-rules.yml)
  - [x] API response time > 5s → alert (configured in alert-rules.yml)
  - [x] Container restart → alert (configured in alert-rules.yml)
- [ ] **6.5** Test alert: trigger condition → receive notification (requires Alertmanager + Webhook/Slack integration)
- [x] **6.6** Setup uptime monitoring: check endpoint every 5 minutes (monitored via Prometheus scrape targets)

---

## PHASE 7: TEAM ONBOARDING (Week 2-4)

> 📖 Guide: [08-onboarding.md](./08-onboarding.md)

### 7A. Pilot (Week 2)

- [ ] **7.1** Select 2 pilot teams: AI Engine (PRJ7) + Quality Assurance (PRJ4)
- [ ] **7.2** Create accounts for pilot users (20-30 people)
- [ ] **7.3** 30-minute training session: demo create issue, board, sprint
- [ ] **7.4** Pilot users self-use for 1 week
- [ ] **7.5** Collect feedback: survey form or 15-minute meeting

### 7B. Adjust (Week 3)

- [ ] **7.6** Fix issues from pilot feedback
- [ ] **7.7** Adjust workflow/labels if needed
- [ ] **7.8** Optimize performance if slow
- [ ] **7.9** Update user guide documentation

### 7C. Full Rollout (Week 4)

- [ ] **7.10** Create accounts for all staff
- [ ] **7.11** Send onboarding email + access link
- [ ] **7.12** Training session for 7 project leads
- [ ] **7.13** Project leads train their team members
- [ ] **7.14** First-week support: standby for Q&A

---

## PHASE 8: SCALE TO PRODUCTION — KUBERNETES (Month 2-3)

> 📖 Guide: [04-production.md](./04-production.md)

> [!WARNING]
> Only proceed after PoC has been stable for 2-4 weeks with Docker Compose.
> Requires a ready Kubernetes cluster before starting.

- [ ] **8.1** Setup Kubernetes cluster (3+ nodes)
- [ ] **8.2** Deploy PostgreSQL HA (primary + replica + PgBouncer)
- [ ] **8.3** Deploy Redis cluster (3 nodes)
- [ ] **8.4** Deploy MinIO cluster (4 nodes)
- [ ] **8.5** Migrate data from Docker Compose → Kubernetes
- [ ] **8.6** Deploy Plane on K8s (Helm chart or custom manifests)
- [ ] **8.7** Configure Ingress Controller + SSL
- [ ] **8.8** Load test: 500 concurrent users
- [ ] **8.9** Failover test: kill pod → auto-recover
- [ ] **8.10** Cutover: switch DNS/IP from PoC to Production
- [ ] **8.11** Decommission PoC instance

---

## PHASE 9: MAINTENANCE & CONTINUOUS IMPROVEMENT

- [ ] **9.1** Plane version upgrade process documented
- [ ] **9.2** Monthly security patch review
- [ ] **9.3** Quarterly capacity review (disk, CPU, RAM trends)
- [ ] **9.4** Upgrade to Air-gapped edition when licensed
- [ ] **9.5** LDAP/SAML integration when AD is available
- [ ] **9.6** Custom automation rules (Commercial edition)
- [ ] **9.7** API integration with other tools (SIEM, ticketing)

---

## QUICK REFERENCE — Common Commands

```bash
# Start/Stop
docker compose up -d
docker compose down

# Logs
docker compose logs -f api
docker compose logs -f web

# Backup now
./scripts/backup.sh

# Health check
./scripts/health-check.sh

# Update Plane
cd /opt/plane && git pull && docker compose pull && docker compose up -d
```

---

> **Total: 9 phases, ~70 tasks.** Priority: Phase 0→3 (get running). Phase 4→6 (run securely). Phase 7→9 (production).
