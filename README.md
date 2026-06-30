# 🛡️ Plane Self-Hosted — Phòng 5 An ninh An toàn Hệ thống

> Task Management Platform (Jira Alternative) — 100% Local Deployment

## Tổng quan

Deploy [Plane](https://plane.so) self-hosted phục vụ Phòng 5 (An ninh An toàn Hệ thống) với 7 tổ và ~5.000 người dùng.
Chạy hoàn toàn trên hạ tầng on-premises, không phụ thuộc cloud.

## Cấu trúc 7 Tổ

| Tổ | Tên | Project Code | Chức năng |
|---|---|---|---|
| 1 | Tham mưu Tổng hợp | `PRJ1-Core` | Kế hoạch, báo cáo, điều phối |
| 2 | GRC & Chính sách | `PRJ2-Security` | Compliance, policy, risk assessment |
| 3 | An ninh Vật lý | `PRJ3-DevOps` | Camera, access control, patrol |
| 4 | Kiểm thử | `PRJ4-QA` | Pentest, red team, vuln assessment |
| 5 | Tích hợp & Triển khai | `PRJ5-Integrations` | Deploy tech mới, system integration |
| 6 | SOC | `PRJ6-Analytics` | Incident response, monitoring, SIEM |
| 7 | AI | `PRJ7-AI` | ML models, AI security, research |

## Kiến trúc

```
                      ┌──────────────────┐
                      │   Nginx Reverse   │
                      │   Proxy (SSL)     │
                      └────────┬─────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
       ┌────────▼──────┐ ┌────▼─────┐ ┌──────▼────────┐
       │  Plane Web    │ │ Plane API│ │ Plane Worker  │
       │  (Next.js)    │ │ (Django) │ │ (Celery)      │
       └───────────────┘ └────┬─────┘ └──────┬────────┘
                              │              │
                ┌─────────────┼──────────────┘
                │             │
       ┌────────▼──────┐ ┌───▼──────────┐ ┌──────────────┐
       │  PostgreSQL   │ │ Redis        │ │ MinIO (S3)   │
       │  + PgBouncer  │ │              │ │ Object Store │
       └───────────────┘ └──────────────┘ └──────────────┘
```

## Quick Start

```bash
# 1. Chạy script kiểm tra prerequisites
./scripts/check-prerequisites.sh

# 2. Tạo file .env từ template
cp env/.env.example env/.env.local
# Chỉnh sửa env/.env.local theo server thực tế

# 3. Deploy PoC (Docker Compose)
./scripts/deploy-poc.sh

# 4. Truy cập Plane
# http://<server-ip>:80
```

## Thư mục

```
.
├── README.md                  # File này
├── docs/                      # 📚 Hướng dẫn chi tiết (agent đọc folder này)
│   ├── 00-MASTER-CHECKLIST.md # ✅ Checklist tổng — agent đọc đầu tiên
│   ├── 01-prerequisites.md    # Yêu cầu hệ thống
│   ├── 02-poc-deployment.md   # Hướng dẫn deploy PoC
│   ├── 03-configuration.md    # Cấu hình workspace/project/workflow
│   ├── 04-production.md       # Scale lên production (K8s)
│   ├── 05-security.md         # Security hardening
│   ├── 06-backup-restore.md   # Backup & disaster recovery
│   ├── 07-monitoring.md       # Monitoring & alerting
│   └── 08-onboarding.md       # Onboarding teams
├── docker/                    # Docker configs
│   ├── docker-compose.yml     # PoC deployment
│   ├── docker-compose.prod.yml# Production overrides
│   └── nginx/                 # Nginx reverse proxy
│       └── plane.conf         # Nginx config
├── env/                       # Environment configs
│   ├── .env.example           # Template
│   └── .gitignore             # Ensure .env.local never committed
├── scripts/                   # Automation scripts
│   ├── check-prerequisites.sh # Kiểm tra yêu cầu hệ thống
│   ├── deploy-poc.sh          # Deploy PoC tự động
│   ├── backup.sh              # Backup database + storage
│   ├── restore.sh             # Restore từ backup
│   └── health-check.sh        # Health check services
├── k8s/                       # Kubernetes configs (Phase 2)
│   ├── namespace.yaml
│   ├── plane-deployment.yaml
│   ├── postgres-statefulset.yaml
│   ├── redis-deployment.yaml
│   └── ingress.yaml
└── monitoring/                # Monitoring stack
    ├── prometheus.yml
    └── grafana/
        └── dashboards/
            └── plane-overview.json
```

## Tài liệu cho Agent

> **Agent mới:** Đọc `docs/00-MASTER-CHECKLIST.md` trước. File đó chứa toàn bộ checklist từ A→Z.
> Mỗi task trong checklist trỏ đến file hướng dẫn chi tiết tương ứng trong `docs/`.
