# 03 — Configuration (Workspace, Projects, Workflow)

## Objective

Configure organizational structure in Plane: workspace, 7 projects, workflow states, labels, RBAC.

---

## 1. Workspace Setup

### Create Workspace

- **Name:** `Sentinel-Workspace`
- **Slug:** `sentinel`
- **Timezone:** `Asia/Ho_Chi_Minh` (UTC+7)

### Workspace Settings

- **Sign-up mode:** Invite only (disable public registration)
- **Default role:** Member

---

## 2. Create 7 Projects

One project per functional area:

### Project 1: `PRJ1-Core`

| Field | Value |
|---|---|
| Name | Core Platform |
| Identifier | PRJ1 |
| Description | Architecture, API foundations, system coordination |
| Network | Secret (members only) |
| Lead | (Project Lead) |
| Default Assignee | (Project Lead) |

### Project 2: `PRJ2-Security`

| Field | Value |
|---|---|
| Name | Security Compliance |
| Identifier | PRJ2 |
| Description | Governance, Risk, Compliance. Policy management, risk assessment |
| Network | Secret |
| Lead | (Project Lead) |

### Project 3: `PRJ3-DevOps`

| Field | Value |
|---|---|
| Name | Infrastructure & DevOps |
| Identifier | PRJ3 |
| Description | CI/CD pipelines, deployment automation, network management |
| Network | Secret |
| Lead | (Project Lead) |

### Project 4: `PRJ4-QA`

| Field | Value |
|---|---|
| Name | Quality Assurance |
| Identifier | PRJ4 |
| Description | Penetration testing, red team operations, vulnerability assessment |
| Network | Confidential (highly restricted) |
| Lead | (Project Lead) |

### Project 5: `PRJ5-Integrations`

| Field | Value |
|---|---|
| Name | System Integrations |
| Identifier | PRJ5 |
| Description | Webhooks, API connectors, technology deployment, system integration |
| Network | Secret |
| Lead | (Project Lead) |

### Project 6: `PRJ6-Analytics`

| Field | Value |
|---|---|
| Name | Threat Analytics |
| Identifier | PRJ6 |
| Description | 24/7 security monitoring, incident response, SIEM operations |
| Network | Confidential |
| Lead | (Project Lead) |

### Project 7: `PRJ7-AI`

| Field | Value |
|---|---|
| Name | AI Engine |
| Identifier | PRJ7 |
| Description | AI research, ML models for security, AI-powered automation |
| Network | Secret |
| Lead | (Project Lead) |

---

## 3. Workflow States

### General Workflow (PRJ1, PRJ2, PRJ3, PRJ5, PRJ7)

| State | Category | Color | Description |
|---|---|---|---|
| Backlog | Backlog | Gray #94a3b8 | Not yet planned |
| Todo | Unstarted | Blue #3b82f6 | Planned, waiting to start |
| In Progress | Started | Yellow #eab308 | Currently in progress |
| In Review | Started | Purple #a855f7 | Under review |
| Testing | Started | Orange #f97316 | Testing/verification |
| Done | Completed | Green #22c55e | Complete |
| Cancelled | Cancelled | Red #ef4444 | Cancelled |

### Incident Response Workflow — PRJ6-Analytics

| State | Category | Color | Description |
|---|---|---|---|
| Detected | Backlog | Red #ef4444 | Threat/incident detected |
| Triaging | Unstarted | Orange #f97316 | Severity assessment |
| Investigating | Started | Yellow #eab308 | Root cause investigation |
| Containment | Started | Blue #3b82f6 | Spread containment |
| Eradication | Started | Purple #a855f7 | Threat removal |
| Recovery | Started | Teal #14b8a6 | System recovery |
| Post-Mortem | Started | Indigo #6366f1 | Post-incident analysis |
| Closed | Completed | Green #22c55e | Case closed |

### Pentest Workflow — PRJ4-QA

| State | Category | Color | Description |
|---|---|---|---|
| Scoping | Unstarted | Blue #3b82f6 | Define test scope |
| Reconnaissance | Started | Yellow #eab308 | Information gathering |
| Exploitation | Started | Red #ef4444 | Exploit vulnerabilities |
| Reporting | Started | Purple #a855f7 | Write report |
| Remediation Verify | Started | Orange #f97316 | Verify patch |
| Closed | Completed | Green #22c55e | Complete |
| On Hold | Cancelled | Gray #94a3b8 | Paused |

---

## 4. Labels

Create the following labels at workspace level (applies to all projects):

### Priority Labels

| Label | Color | Description |
|---|---|---|
| `P0-Critical` | #dc2626 (deep red) | Critical incident, requires immediate action |
| `P1-High` | #ea580c (orange) | High priority, handle within the day |
| `P2-Medium` | #ca8a04 (yellow) | Medium priority, within the week |
| `P3-Low` | #16a34a (green) | Low priority, when time allows |

### Type Labels

| Label | Color | Description |
|---|---|---|
| `Bug` | #dc2626 | Defect to fix |
| `Feature` | #2563eb | New feature or enhancement |
| `Incident` | #9333ea | Security incident |
| `Audit` | #0891b2 | Review/audit |
| `Compliance` | #4f46e5 | Policy compliance |
| `Research` | #7c3aed | Research & development |
| `Deployment` | #059669 | Production deployment |
| `Task` | #6b7280 | General task |

### Security Classification Labels

| Label | Color | Description |
|---|---|---|
| `Confidential` | #dc2626 (red) | Restricted to authorized personnel only |
| `Internal` | #ea580c (orange) | Internal use only |
| `Public` | #16a34a (green) | Public information |

### Scope Labels

| Label | Color | Description |
|---|---|---|
| `Cross-team` | #8b5cf6 | Involves multiple projects/teams |
| `Urgent-Report` | #dc2626 | Requires immediate leadership escalation |

---

## 5. RBAC Configuration

### Workspace Roles

| Role | Permissions | Assigned To |
|---|---|---|
| **Owner** | Full workspace control | Department head |
| **Admin** | Manage projects, members, settings | IT admin, leads |
| **Member** | Access assigned projects, create/edit issues | All staff |
| **Guest** | View-only in invited projects | Senior leadership |

### Project-level Permissions

| Action | Admin | Member | Guest |
|---|---|---|---|
| Create issue | ✅ | ✅ | ❌ |
| Edit issue | ✅ | ✅ (own + assigned) | ❌ |
| Delete issue | ✅ | ❌ | ❌ |
| Manage members | ✅ | ❌ | ❌ |
| View issues | ✅ | ✅ | ✅ |
| Manage settings | ✅ | ❌ | ❌ |

### Assignment Strategy

- Each staff member is only added to their assigned project
- Project lead = Project Admin
- Cross-team tasks: create issue in the lead project, tag members from other projects

---

## 6. Modules (Epics) — Suggestions

Each project should have default Modules:

| Module | Applies To | Description |
|---|---|---|
| `Q3-2026` | All | Q3 2026 work items |
| `Q4-2026` | All | Q4 2026 work items |
| `Project-X` | Per project | Specific project/campaign |
| `Incident-YYYY-MM` | PRJ6-Analytics | Group incidents by month |

---

## 7. Cycles (Sprints) — Suggestions

2-week sprints:

| Cycle | Start | End |
|---|---|---|
| Sprint 2026-W27 | 30/06/2026 | 13/07/2026 |
| Sprint 2026-W29 | 14/07/2026 | 27/07/2026 |
| ... | ... | ... |
