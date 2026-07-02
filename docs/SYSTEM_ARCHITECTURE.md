# Sentinel Taskboard — System Architecture

> Bản mô tả kiến trúc kỹ thuật tổng thể phục vụ triển khai, bảo trì và mở rộng hệ thống.

---

## 1. Sơ đồ Tổng thể Hệ thống (System Overview)

```mermaid
graph LR
    subgraph "1. Người dùng Sentinel"
        Leader([Lãnh đạo / Owner])
        Commander([Chỉ huy đội / Project Lead])
        Staff([Cán bộ xử lý / Member])
        SysAdmin([Quản trị hệ thống / Admin])
    end

    subgraph "2. Lớp Truy cập"
        LAN[LAN 192.168.0.0/16]
        VPN[Tailscale VPN 100.64.0.0/10]
    end

    subgraph "3. Lớp Bảo mật"
        UFW[UFW Firewall]
        Caddy[Caddy Reverse Proxy]
    end

    subgraph "4. Nền tảng Plane"
        Web[plane-web Next.js]
        Space[plane-space]
        AdminUI[plane-admin God Mode]
        API[plane-api Django REST]
        Worker[Celery Workers]
        Beat[Celery Beat Scheduler]
    end

    subgraph "5. Dịch vụ Nền tảng"
        Notify[Notification Service]
        IntAPI[Integration API]
        Audit[Audit Service]
    end

    subgraph "6. Lớp Dữ liệu (Cô lập)"
        PG[(PostgreSQL 15.7)]
        Redis[(Valkey/Redis)]
        MQ[(RabbitMQ)]
        MinIO[(MinIO Object Store)]
        AuditLog[(Audit Log)]
        Backup[(Backup/Restore)]
    end

    subgraph "7. Monitoring"
        Grafana[Grafana Dashboard]
        Prom[Prometheus]
        NodeExp[Node Exporter]
        cAdv[cAdvisor]
    end

    subgraph "8. Tích hợp mở rộng"
        SIEM[Hệ thống giám sát ATTT]
        Email[Email / nhắc việc nội bộ]
        Report[Hệ thống báo cáo nội bộ]
    end

    Leader & Commander & Staff & SysAdmin --> LAN & VPN
    LAN & VPN --> UFW --> Caddy
    Caddy -->|/* routes| Web & Space
    Caddy -->|/api/* /auth/*| API
    Caddy -->|/god-mode* ACL| AdminUI
    API --> Worker & Beat
    API --> Notify & IntAPI & Audit
    API --> PG & Redis & MQ & MinIO
    Worker --> PG & Redis & MQ
    Audit --> AuditLog
    Notify --> Email
    IntAPI --> SIEM & Report
    Prom --> NodeExp & cAdv
    Grafana --> Prom
    Backup -.->|2AM Daily| PG & MinIO
```

---

## 2. Sơ đồ Use Case (Actors & Functions)

```mermaid
graph TD
    Admin([System Admin / Owner])
    Lead([Project Lead / Commander])
    Member([Staff / Member])
    Guest([Guest / Viewer])
    Cron([Automated System])

    subgraph "Quản trị Hệ thống"
        UC01[Cấu hình Instance & God-Mode]
        UC02[Quản lý Workspace & Settings]
        UC03[Phân quyền RBAC & Cấp phát thành viên]
    end

    subgraph "Quản lý Dự án (PRJ1-PRJ7)"
        UC04[Tạo & Cấu hình Project]
        UC05[Thiết lập Workflow States & Labels]
        UC06[Quản lý Cycles / Sprints]
        UC07[Quản lý Modules / Epics]
    end

    subgraph "Cộng tác Hàng ngày"
        UC08[Tạo & Quản lý Issues / Tasks]
        UC09[Kanban Board / List / Calendar]
        UC10[Soạn thảo Pages / Wiki]
        UC11[Tải lên/xuống File đính kèm]
        UC12[Comment & Mention thành viên]
    end

    subgraph "Giám sát & Báo cáo"
        UC13[Dashboard Analytics]
        UC14[Theo dõi Tiến độ / Quá hạn]
        UC15[Xuất Báo cáo]
    end

    subgraph "Vận hành Hệ thống"
        UC16[Sao lưu DB & Object Store]
        UC17[Health Check & Monitoring]
        UC18[Khôi phục thảm họa]
    end

    Admin --> UC01 & UC02 & UC03 & UC04 & UC05
    Admin --> UC08 & UC13 & UC17

    Lead --> UC04 & UC05 & UC06 & UC07
    Lead --> UC08 & UC09 & UC10 & UC13 & UC14 & UC15

    Member --> UC08 & UC09 & UC10 & UC11 & UC12
    Member --> UC13 & UC14

    Guest --> UC13 & UC14 & UC15

    Cron --> UC16 & UC17 & UC18
```

---

## 3. Sơ đồ Kiến trúc Mạng & Biên Bảo mật (Network Security)

```mermaid
graph TD
    subgraph "Vùng Người dùng (Client Zones)"
        LAN["LAN nội bộ<br/>192.168.0.0/16"]
        TS["Tailscale VPN<br/>100.64.0.0/10"]
        WAN["Internet / WAN<br/>Bị chặn hoàn toàn"]
    end

    subgraph "Máy chủ Host (ubuntu-binh)"
        UFW["UFW Firewall<br/>Chỉ mở cổng 80/443"]

        subgraph "Docker Network: plane-network (Cô lập)"
            Caddy["Caddy Reverse Proxy<br/>- Security Headers CSP/HSTS<br/>- Rate Limit 30 req/s<br/>- IP ACL /god-mode"]

            subgraph "Frontend Layer"
                Web["plane-web :3000"]
                AdminUI["plane-admin :3000"]
                Space["plane-space :3000"]
            end

            subgraph "Backend Layer"
                API["plane-api :8000<br/>Django REST Framework"]
                Celery["Celery Workers"]
                Beat["Celery Beat"]
                Live["plane-live :3000"]
            end

            subgraph "Data Layer (Không expose cổng ra Host)"
                PG["PostgreSQL :5432"]
                Redis["Valkey/Redis :6379"]
                MQ["RabbitMQ :5672"]
                MinIO["MinIO :9000"]
            end
        end

        subgraph "Monitoring Stack"
            Prom["Prometheus :9090"]
            Grafana["Grafana :3001"]
            NodeExp["Node Exporter :9100"]
            cAdv["cAdvisor :8080"]
        end
    end

    LAN -->|Port 80/443| UFW
    TS -->|Port 80/443| UFW
    WAN -->|BLOCKED| UFW

    UFW --> Caddy

    Caddy --> Web & Space
    Caddy -->|/api/* /auth/*| API
    Caddy -->|/live/*| Live
    Caddy --> ACL{"/god-mode*<br/>IP in LAN/Tailscale?"}
    ACL -->|Allow| AdminUI
    ACL -->|Deny| Block["403 Forbidden"]

    API --> PG & Redis & MQ & MinIO
    Celery --> PG & Redis & MQ
    Beat --> MQ

    Prom --> NodeExp & cAdv
    Grafana --> Prom
```

---

## 4. Sơ đồ Luồng Dữ liệu (Data Flow)

```mermaid
sequenceDiagram
    participant User as Browser (LAN/Tailscale)
    participant Caddy as Caddy Proxy
    participant Web as plane-web (Next.js)
    participant API as plane-api (Django)
    participant DB as PostgreSQL
    participant Cache as Valkey/Redis
    participant MQ as RabbitMQ
    participant Worker as Celery Worker
    participant S3 as MinIO

    Note over User,S3: Luồng tạo Issue mới

    User->>Caddy: POST /api/workspaces/sentinel/issues/
    Caddy->>Caddy: Check Security Headers + Rate Limit
    Caddy->>API: Forward request
    API->>Cache: Check session token
    Cache-->>API: Session valid
    API->>DB: INSERT issue record
    DB-->>API: Issue created (ID: xxx)
    API->>MQ: Publish notification event
    API-->>Caddy: 201 Created + JSON
    Caddy-->>User: Response with security headers

    Note over MQ,Worker: Async Background Processing

    MQ->>Worker: Consume notification event
    Worker->>DB: Lookup assigned user email
    Worker->>Worker: Send notification (email/webhook)
    Worker->>Cache: Update activity feed cache

    Note over User,S3: Luồng upload file đính kèm

    User->>Caddy: PUT /api/.../attachments/
    Caddy->>API: Forward multipart upload
    API->>S3: Store file in bucket
    S3-->>API: File URL
    API->>DB: Save attachment metadata
    API-->>User: 200 OK + file URL
```

---

## 5. Sơ đồ Deployment Topology (Docker Compose)

```mermaid
graph TB
    subgraph "docker-compose.yaml (Orchestrator)"
        subgraph "docker-compose.proxy.yaml"
            Caddy["caddy:latest<br/>Ports: 80, 443"]
        end

        subgraph "docker-compose.app.yaml"
            Web["plane-web<br/>makeplane/plane-frontend"]
            Space["plane-space<br/>makeplane/plane-space"]
            AdminUI["plane-admin<br/>makeplane/plane-admin"]
            API["plane-api<br/>makeplane/plane-backend"]
            Worker["plane-worker<br/>makeplane/plane-backend"]
            Beat["plane-beat<br/>makeplane/plane-backend"]
            Live["plane-live<br/>makeplane/plane-backend"]
        end

        subgraph "docker-compose.db.yaml"
            PG["plane-db<br/>postgres:15.7-alpine"]
            Redis["plane-redis<br/>valkey/valkey:8"]
            MQ["plane-mq<br/>rabbitmq:4.1-alpine"]
            MinIO["plane-minio<br/>minio/minio"]
        end

        subgraph "docker-compose.monitor.yaml"
            Prom["prometheus<br/>prom/prometheus"]
            Grafana["grafana<br/>grafana/grafana"]
            NodeExp["node-exporter<br/>prom/node-exporter"]
            cAdv["cadvisor<br/>gcr.io/cadvisor"]
        end
    end

    subgraph "Volumes (Persistent Data)"
        V1[("pgdata")]
        V2[("redisdata")]
        V3[("uploads")]
        V4[("minio-data")]
        V5[("grafana-data")]
        V6[("prom-data")]
    end

    PG --- V1
    Redis --- V2
    API --- V3
    MinIO --- V4
    Grafana --- V5
    Prom --- V6
```

---

## 6. Sơ đồ CI/CD & DevOps Pipeline

```mermaid
graph LR
    subgraph "Developer Workflow"
        Dev[Developer] -->|git push| Branch["fix/* branch"]
        Branch -->|Open PR| PR[Pull Request]
    end

    subgraph "GitHub Actions CI"
        PR -->|Trigger| CI["ci.yml"]
        CI --> Test["Unit Tests<br/>python3 -m unittest"]
        CI --> Scan["Secret Leak Scan<br/>grep patterns"]
        Test -->|Pass| Review
        Scan -->|Pass| Review
    end

    subgraph "Code Review"
        Review["CODEOWNERS Review<br/>@Binhchuoizzz required"] -->|Approve| Merge["Merge to master"]
    end

    subgraph "Deployment (Manual)"
        Merge -->|git pull on server| Deploy["deploy-poc.sh"]
        Deploy --> DockerUp["docker compose up -d"]
        DockerUp --> Health["health-check.sh"]
        Health --> Inject["inject-custom-ui.sh"]
    end
```

---

## 7. RBAC Matrix (Phân quyền Chi tiết)

| Action | Admin | Project Lead | Member | Guest |
| :--- | :---: | :---: | :---: | :---: |
| God-Mode / Instance Settings | ✅ | ❌ | ❌ | ❌ |
| Create / Delete Workspace | ✅ | ❌ | ❌ | ❌ |
| Create / Delete Project | ✅ | ✅ | ❌ | ❌ |
| Manage Members & Roles | ✅ | ✅ (own project) | ❌ | ❌ |
| Configure Workflow & Labels | ✅ | ✅ (own project) | ❌ | ❌ |
| Create / Edit Issues | ✅ | ✅ | ✅ | ❌ |
| Delete Issues | ✅ | ✅ | ❌ | ❌ |
| Manage Cycles / Modules | ✅ | ✅ | ✅ | ❌ |
| Upload Attachments | ✅ | ✅ | ✅ | ❌ |
| Edit Pages / Wiki | ✅ | ✅ | ✅ | ❌ |
| View Dashboard & Analytics | ✅ | ✅ | ✅ | ✅ |
| Export Reports | ✅ | ✅ | ❌ | ✅ |

---

## 8. Technology Stack Summary

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| Reverse Proxy | Caddy Server | Routing, SSL, security headers, rate limiting, IP ACL |
| Frontend | Next.js (React) | Web UI, SSR dashboard |
| Backend API | Django REST Framework | RESTful API, authentication, business logic |
| Background Jobs | Celery + Celery Beat | Async tasks, notifications, scheduled jobs |
| Message Broker | RabbitMQ 4.1 | Task queue for Celery workers |
| Cache & Session | Valkey (Redis fork) 8.x | Session storage, activity feed cache |
| Database | PostgreSQL 15.7 | Primary relational data store (ACID) |
| Object Storage | MinIO | S3-compatible file attachment storage |
| Monitoring | Prometheus + Grafana | Metrics collection, dashboards, alerting |
| Host Metrics | Node Exporter + cAdvisor | System + container resource monitoring |
| Container Runtime | Docker + Docker Compose | Service orchestration (PoC) |
| Production Orchestration | Kubernetes | HA deployment, auto-scaling (Phase 8) |
| CI/CD | GitHub Actions | Unit tests, secret scanning, code review |
| VPN | Tailscale | Zero-trust remote access |
| Firewall | UFW | Host-level port filtering |
| Backup | pg_dump + tar + cron | Automated daily backup with retention |

---

## 9. Project Directory Structure

```
sentinel-taskboard/
├── .github/
│   ├── CODEOWNERS                  # Owner review requirements
│   ├── PULL_REQUEST_TEMPLATE.md    # PR security checklist
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI pipeline
│
├── docs/                           # Architecture & deployment guides
│   ├── SYSTEM_ARCHITECTURE.md      # ← This file (diagrams)
│   ├── SYSTEM_SECURITY.md          # Security hardening details
│   ├── ACCESS_GUIDE.md             # User access documentation
│   ├── 00-MASTER-CHECKLIST.md      # 9-phase deployment checklist
│   ├── 01-prerequisites.md         # Server requirements
│   ├── 02-poc-deployment.md        # PoC setup guide
│   ├── 03-configuration.md         # Workspace & project config
│   ├── 04-production.md            # Kubernetes production guide
│   ├── 05-security.md              # Security hardening guide
│   ├── 06-backup-restore.md        # Backup & DR procedures
│   ├── 07-monitoring.md            # Prometheus/Grafana setup
│   └── 08-onboarding.md            # Team onboarding plan
│
├── env/                            # Environment configuration
│   ├── .env.example                # Template (safe to commit)
│   ├── .env.local                  # Actual secrets (git-ignored)
│   └── .gitignore
│
├── plane-app/                      # Docker Compose deployment
│   ├── docker-compose.yaml         # Main orchestrator
│   ├── docker-compose.app.yaml     # Application services
│   ├── docker-compose.db.yaml      # Database services
│   ├── docker-compose.proxy.yaml   # Caddy proxy
│   ├── docker-compose.monitor.yaml # Monitoring stack
│   ├── Caddyfile                   # Reverse proxy config
│   └── custom-ui.css               # UI theme injection
│
├── k8s/                            # Kubernetes manifests (Phase 8)
│   ├── namespace.yaml
│   ├── ingress.yaml
│   ├── plane-deployment.yaml
│   ├── postgres-statefulset.yaml
│   └── redis-deployment.yaml
│
├── monitoring/                     # Monitoring configuration
│   ├── prometheus.yml              # Scrape targets
│   ├── alert-rules.yml             # Alert conditions
│   └── grafana/
│       ├── dashboards/             # JSON dashboard definitions
│       └── provisioning/           # Auto-provisioning configs
│
├── scripts/                        # Automation scripts
│   ├── deploy-poc.sh               # Full stack deployment
│   ├── backup.sh                   # Automated backup
│   ├── restore.sh                  # Disaster recovery
│   ├── health-check.sh             # Service health verification
│   ├── check-prerequisites.sh      # Environment validation
│   ├── inject-custom-ui.sh         # UI theme injection
│   ├── setup-cron.sh               # Cron job installation
│   ├── initialize-plane-data.py    # Workspace/project seeding
│   ├── setup_plane_app_env.py      # Environment file generator
│   └── setup_plane_envs.py         # Multi-env setup utility
│
├── tests/
│   ├── unit/                       # Unit tests (no server needed)
│   │   ├── test_env_generator.py
│   │   └── test_ui_injector.py
│   └── integration/                # Integration tests (server required)
│       └── test_full_integration.py
│
├── backup/                         # Backup storage (git-ignored)
│   └── daily/
│
├── .gitignore                      # Comprehensive secret exclusions
├── CONTRIBUTING.md                 # Collaborator onboarding guide
├── SECURITY.md                     # Vulnerability disclosure policy
├── README.md                       # Project overview & quick start
└── pyrightconfig.json              # Python type checking config
```
