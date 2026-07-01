# 🛡️ Plane Self-Hosted — Sentinel Taskboard & Workspace Management

> Task Management Platform (Jira Alternative) — 100% Local Deployment

## Tổng quan

Deploy [Plane](https://plane.so) self-hosted phục vụ quản lý dự án nội bộ với ~5.000 người dùng.
Chạy hoàn toàn trên hạ tầng on-premises, không phụ thuộc cloud.

## Cấu trúc Projects

| # | Tên | Project Code | Chức năng |
| :--- | :--- | :--- | :--- |
| 1 | Core Platform | `PRJ1-Core` | Architecture, API foundations & coordination |
| 2 | Security Compliance | `PRJ2-Security` | Compliance, policy, risk assessment |
| 3 | Infrastructure & DevOps | `PRJ3-DevOps` | CI/CD, deployment, network logging |
| 4 | Quality Assurance | `PRJ4-QA` | Pentest, red team, vuln assessment |
| 5 | System Integrations | `PRJ5-Integrations` | Webhooks, API connectors, system integration |
| 6 | Threat Analytics | `PRJ6-Analytics` | Incident response, monitoring, SIEM |
| 7 | AI Engine | `PRJ7-AI` | ML models, AI security research |

## Kiến trúc

```
                      ┌──────────────────┐
                      │   Caddy Reverse   │
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
       │  PostgreSQL   │ │ Valkey/Redis │ │ MinIO (S3)   │
       │               │ │              │ │ Object Store │
       └───────────────┘ └──────────────┘ └──────────────┘
```

## Hướng dẫn Triển khai & Chạy dự án (Quick Start)

### 1. Yêu cầu hệ thống (Prerequisites)

Trước khi cài đặt, hãy đảm bảo máy chủ đích đã có sẵn:

- **Git**
- **Docker** & **Docker Compose** (V2)
- **Python 3** (cùng thư viện `requests` để chạy script test tự động)

---

### 2. Các bước triển khai chi tiết

#### Bước 1: Clone Repository

```bash
git clone https://github.com/Binhchuoizzz/sentinel-taskboard.git
cd sentinel-taskboard
```

#### Bước 2: Tạo cấu hình môi trường

Sao chép tệp cấu hình mẫu:

```bash
cp env/.env.example env/.env.local
```

Mở tệp `env/.env.local` và chỉnh sửa các biến cấu hình phù hợp với máy chủ mới:

- `WEB_URL`: Điền địa chỉ IP mạng (LAN IP, Tailscale IP hoặc Domain công khai) của máy chủ, ví dụ: `http://192.168.1.100` hoặc `http://100.121.120.59`.
- `CORS_ALLOWED_ORIGINS`: Thêm các IP/Domain được phép kết nối (phân tách bằng dấu phẩy), ví dụ: `http://192.168.1.100,http://100.121.120.59,http://localhost`.
- Thay đổi mật khẩu an toàn cho PostgreSQL (`POSTGRES_PASSWORD`), Valkey/Redis (`REDIS_PASSWORD`), RabbitMQ (`RABBITMQ_DEFAULT_PASS`), và MinIO (`MINIO_ROOT_PASSWORD`).

> **Lưu ý**: Tệp `env/.env.local` đã được cấu hình trong `.gitignore` để đảm bảo thông tin nhạy cảm không bao giờ bị đẩy lên Git.

#### Bước 3: Chạy kịch bản triển khai tự động

Khởi chạy lệnh cài đặt:

```bash
PLANE_INSTALL_DIR="./plane-app" ./scripts/deploy-poc.sh
```

Kịch bản này sẽ tự động:

1. Đồng bộ hóa cấu hình bảo mật và tạo tệp `plane-app/plane.env` động.
2. Khởi tạo cơ sở dữ liệu (PostgreSQL, Valkey, RabbitMQ, MinIO) được khóa mật khẩu bảo mật cao.
3. Chạy di trú dữ liệu (migrations) và nạp dữ liệu mẫu (Seeding): Workspace `sentinel`, 7 dự án (`PRJ1` → `PRJ7`), phân quyền RBAC và 3 tài khoản thử nghiệm.
4. Tự động chèn giao diện tùy biến **Cyber-Dark Glassmorphism** và font chữ **Outfit** vào giao diện chính và Admin.
5. Thực hiện tự kiểm tra trạng thái sức khỏe của 15 container dịch vụ.

---

### 3. Thông tin Đăng nhập Thử nghiệm

Sau khi cài đặt thành công, truy cập giao diện thông qua địa chỉ IP của máy chủ (ví dụ: `http://<server-ip>`):

- **Tài khoản Quản trị viên (Workspace Admin):**
  - Email: `admin@sentinel.local` | Mật khẩu: `Sentinel@123`
- **Tài khoản Thành viên (Member - Analytics):**
  - Email: `member1@sentinel.local` | Mật khẩu: `Sentinel@123`
- **Tài khoản Khách (Guest/Viewer - Core Platform):**
  - Email: `guest1@sentinel.local` | Mật khẩu: `Sentinel@123`
- **Giao diện Cấu hình Hệ thống (God-Mode Admin Panel):**
  - URL: `http://<server-ip>/god-mode/`

---

### 4. Kiểm thử Tích hợp & Xác minh (E2E Integration Testing)

Để kiểm tra toàn bộ tính năng nghiệp vụ của hệ thống (Workspaces, Projects, Issues, Sprints, Epics, Wikis và RBAC), hãy chạy kịch bản kiểm thử tự động sau:

1. Cài đặt thư viện kiểm thử:
   ```bash
   pip install requests
   ```
2. Chạy tệp kiểm thử tích hợp (truyền địa chỉ IP đích qua biến môi trường `BASE_URL`):
   ```bash
   BASE_URL="http://<server-ip>" python3 tests/integration/test_full_integration.py
   ```

Nếu 33/33 kiểm tra trả về kết quả `✅ PASS`, hệ thống đã sẵn sàng và hoạt động ổn định hoàn toàn!

## Cấu trúc Thư mục Project

```
.
├── README.md                  # File này
├── docs/                      # 📚 Hướng dẫn chi tiết
│   ├── 00-MASTER-CHECKLIST.md # ✅ Checklist tổng — đọc đầu tiên
│   ├── 01-prerequisites.md    # Yêu cầu hệ thống
│   ├── 02-poc-deployment.md   # Hướng dẫn deploy PoC
│   ├── 03-configuration.md    # Cấu hình workspace/project/workflow
│   ├── 04-production.md       # Scale lên production (K8s)
│   ├── 05-security.md         # Security hardening
│   ├── 06-backup-restore.md   # Backup & disaster recovery
│   ├── 07-monitoring.md       # Monitoring & alerting
│   ├── 08-onboarding.md       # Onboarding teams
│   ├── SYSTEM_SECURITY.md     # Security architecture overview
│   └── ACCESS_GUIDE.md        # Access & network guide
├── env/                       # Environment configs
│   ├── .env.example           # Template
│   └── .gitignore             # Ensure .env.local never committed
├── scripts/                   # Automation scripts
│   ├── check-prerequisites.sh # Kiểm tra yêu cầu hệ thống
│   ├── deploy-poc.sh          # Deploy PoC tự động
│   ├── backup.sh              # Backup database + storage
│   ├── restore.sh             # Restore từ backup
│   ├── setup_plane_app_env.py # Helper đồng bộ env
│   ├── setup_plane_envs.py    # Helper đồng bộ env plane
│   ├── inject-custom-ui.sh    # Chèn stylesheet giao diện tùy biến
│   └── health-check.sh        # Health check services
├── tests/                     # 🧪 Thư mục kiểm thử phần mềm độc lập
│   ├── integration/           # Kiểm thử tích hợp E2E API
│   │   └── test_full_integration.py
│   └── unit/                  # Kiểm thử đơn vị (Unit tests) các module helper
│       ├── test_env_generator.py
│       └── test_ui_injector.py
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
