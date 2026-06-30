# ✅ MASTER CHECKLIST — Plane Self-Hosted Deployment

> **Đây là file chính cho Agent.** Đọc file này trước khi làm bất kỳ task nào.
> Mỗi task có link đến file hướng dẫn chi tiết. Agent đọc hướng dẫn → thực thi → tick hoàn thành.

---

## Cách sử dụng

- `[ ]` = Chưa làm
- `[/]` = Đang làm
- `[x]` = Hoàn thành
- `[!]` = Blocked / Cần input từ user
- Mỗi task có **file hướng dẫn** kèm theo → đọc trước khi thực thi
- Các task phải làm **theo thứ tự** trừ khi ghi rõ có thể làm song song

---

## PHASE 0: CHUẨN BỊ (Ngày 1)

> 📖 Hướng dẫn: [01-prerequisites.md](./01-prerequisites.md)

- [x] **0.1** Kiểm tra server specs (CPU, RAM, Disk, OS version)
- [x] **0.2** Cài Docker Engine 24+ và Docker Compose v2
  - [x] `docker --version` → phải >= 24.0
  - [x] `docker compose version` → phải >= 2.0
- [x] **0.3** Cài Git
- [x] **0.4** Cấu hình firewall: mở port 80, 443 (hoặc port custom)
- [x] **0.5** Tạo user riêng cho Plane (không chạy bằng root)
  ```bash
  sudo useradd -m -s /bin/bash plane-admin
  sudo usermod -aG docker plane-admin
  ```
- [x] **0.6** Kiểm tra DNS/IP: quyết định domain hay dùng IP trực tiếp
- [x] **0.7** Chạy script check prerequisites: `./scripts/check-prerequisites.sh`

---

## PHASE 1: DEPLOY PoC (Ngày 1-2)

> 📖 Hướng dẫn: [02-poc-deployment.md](./02-poc-deployment.md)

### 1A. Clone & Setup

- [x] **1.1** Clone Plane repository (Đã thay thế bằng bản Prebuilt Docker Hub tối ưu và bảo mật)
- [x] **1.2** Chạy setup script của Plane (Sử dụng script setup prebuilt có patch lỗi JSON)
- [x] **1.3** Copy và chỉnh sửa environment file (Đã cấu hình plane-app/plane.env tự động tạo mật khẩu mạnh)
- [x] **1.4** Start services
- [x] **1.5** Verify: tất cả container running
- [x] **1.6** Truy cập web UI: `http://<server-ip>` → trang đăng nhập hiện ra

### 1B. Verify PoC Healthy

- [x] **1.7** API health check (Đã kiểm tra uvicorn nội bộ hoạt động phản hồi HTTP 200)
- [x] **1.8** PostgreSQL connected: kết nối db thành công và migrate bảng dữ liệu
- [x] **1.9** Redis connected: ping/pong kết nối redis thành công
- [x] **1.10** MinIO/Storage working: khởi tạo container minio lưu trữ uploads thành công

---

## PHASE 2: CẤU HÌNH WORKSPACE & PROJECTS (Ngày 2-3)

> 📖 Hướng dẫn: [03-configuration.md](./03-configuration.md)

### 2A. Instance Admin (God Mode)

- [x] **2.1** Đăng nhập God Mode (Khởi tạo admin@sentinel.local bằng Django Shell tự động)
- [x] **2.2** Cấu hình instance settings:
  - [x] Instance name: `Sentinel-ANTT`
  - [x] Enable/disable sign-ups
  - [ ] Email settings (SMTP) nếu có mail server internal

### 2B. Tạo Workspace

- [x] **2.3** Tạo workspace: `Sentinel-ANTT`
- [x] **2.4** Set workspace URL slug: `sentinel`
- [ ] **2.5** Upload workspace logo (logo phòng 5 nếu có)

### 2C. Tạo 7 Projects (mỗi tổ = 1 project)

- [x] **2.6** Project `PRJ1-Core` — Tham mưu Tổng hợp
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 1 (admin@sentinel.local)
- [x] **2.7** Project `PRJ2-Security` — GRC & Chính sách
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 2 (admin@sentinel.local)
- [x] **2.8** Project `PRJ3-DevOps` — An ninh Vật lý
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 3 (admin@sentinel.local)
- [x] **2.9** Project `PRJ4-QA` — Kiểm thử
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 4 (admin@sentinel.local)
- [x] **2.10** Project `PRJ5-Integrations` — Tích hợp & Triển khai
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 5 (admin@sentinel.local)
- [x] **2.11** Project `PRJ6-Analytics` — Security Operations Center
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 6 (admin@sentinel.local)
- [x] **2.12** Project `PRJ7-AI` — AI & Automation
  - [x] Set description, cover image
  - [x] Assign lead: Trưởng Tổ 7 (admin@sentinel.local)

### 2D. Cấu hình Workflow States

- [x] **2.13** Tạo workflow chung cho tất cả projects:
  ```
  Backlog → Todo → In Progress → In Review → Testing → Done → Cancelled
  ```
- [x] **2.14** Tạo workflow riêng cho PRJ6-Analytics (Incident Response):
  ```
  Detected → Triaging → Investigating → Containment → Eradication → Recovery → Post-Mortem → Closed
  ```
- [x] **2.15** Tạo workflow riêng cho PRJ4-QA (Pentest):
  ```
  Scoping → Reconnaissance → Exploitation → Reporting → Remediation Verify → Closed
  ```

### 2E. Cấu hình Labels

- [x] **2.16** Tạo labels phân loại:
  ```
  [Priority]  P0-Critical (đỏ) | P1-High (cam) | P2-Medium (vàng) | P3-Low (xanh)
  [Type]      Bug | Feature | Incident | Audit | Compliance | Research | Deployment | Task
  [Security]  Confidential (đỏ) | Internal (cam) | Public (xanh lá)
  [Team]      Cross-team (khi task liên quan nhiều tổ)
  ```

### 2F. Cấu hình RBAC & Members

- [ ] **2.17** Invite & assign roles:

  | Role | Người | Số lượng |
  |---|---|---|
  | Admin | Trưởng phòng, Phó phòng, IT admin | 3-5 |
  | Member | Trưởng tổ + nhân viên | ~5000 |
  | Guest | Lãnh đạo cấp trên, đối tác | 10-20 |

- [ ] **2.18** Assign members vào đúng project (mỗi người vào project tổ mình)
- [ ] **2.19** Test phân quyền: Member không thể xóa project, Guest chỉ view

---

## PHASE 3: TEST & VALIDATE (Ngày 3-4)

> 📖 Hướng dẫn: [02-poc-deployment.md](./02-poc-deployment.md) (phần Verification)

### 3A. Functional Testing

- [ ] **3.1** Tạo issue mới → assign → chuyển trạng thái qua workflow → done
- [ ] **3.2** Tạo Cycle (Sprint) → add issues → track progress
- [ ] **3.3** Tạo Module (Epic) → group related issues
- [ ] **3.4** Test Board view (Kanban) — drag & drop hoạt động
- [ ] **3.5** Test List view, Table view, Spreadsheet view
- [ ] **3.6** Test Pages (wiki/documentation)
- [ ] **3.7** Test file attachment upload/download
- [ ] **3.8** Test comment + mention (@user)
- [ ] **3.9** Test filter, search issues
- [ ] **3.10** Test Analytics/Dashboard — biểu đồ hiện đúng data

### 3B. Performance Testing

- [ ] **3.11** Đo response time: trang load < 3 giây
- [ ] **3.12** Tạo 100+ issues → search/filter vẫn nhanh
- [ ] **3.13** 10+ users đồng thời → không lag

### 3C. Phân quyền Testing

- [ ] **3.14** Admin: có thể tạo/xóa project, manage members → ✅
- [ ] **3.15** Member: tạo/edit issue trong project mình → ✅, không truy cập project khác → ✅
- [ ] **3.16** Guest: chỉ view, không tạo/edit → ✅

---

## PHASE 4: SECURITY HARDENING (Ngày 4-5)

> 📖 Hướng dẫn: [05-security.md](./05-security.md)

### 4A. Network & SSL

- [ ] **4.1** Cấu hình Nginx reverse proxy (dùng file `docker/nginx/plane.conf`)
- [ ] **4.2** Enable HTTPS với SSL certificate (self-signed hoặc internal CA)
- [ ] **4.3** Force redirect HTTP → HTTPS
- [ ] **4.4** Cấu hình security headers:
  ```
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000
  Content-Security-Policy: default-src 'self'
  ```
- [ ] **4.5** Restrict access: chỉ cho IP range nội bộ truy cập

### 4B. Database Security

- [ ] **4.6** Đổi default password PostgreSQL (đã set trong .env)
- [ ] **4.7** PostgreSQL: chỉ listen trên internal network, không expose port ra ngoài
- [ ] **4.8** Enable SSL connection cho PostgreSQL
- [ ] **4.9** Set `max_connections` phù hợp (tính theo user count)

### 4C. Application Security

- [ ] **4.10** Disable public sign-up (chỉ invite)
- [ ] **4.11** Set strong `SECRET_KEY` trong .env (64+ ký tự random)
- [ ] **4.12** Cấu hình LDAP/SAML nếu có Active Directory
- [ ] **4.13** Enable session timeout (30 phút idle)
- [ ] **4.14** Review Docker container: không chạy root trong container

### 4D. Audit & Compliance

- [ ] **4.15** Enable audit logging (Commercial/Air-gapped edition)
- [ ] **4.16** Log rotation: configure logrotate cho Docker logs
- [ ] **4.17** Export audit report test

---

## PHASE 5: BACKUP & DISASTER RECOVERY (Ngày 5)

> 📖 Hướng dẫn: [06-backup-restore.md](./06-backup-restore.md)

- [ ] **5.1** Tạo backup script: `./scripts/backup.sh`
  - [ ] pg_dump PostgreSQL → compressed file
  - [ ] Backup MinIO data directory
  - [ ] Backup .env và Docker configs
- [ ] **5.2** Test backup: chạy script → file backup tạo thành công
- [ ] **5.3** Tạo restore script: `./scripts/restore.sh`
- [ ] **5.4** Test restore: restore vào instance mới → data nguyên vẹn
- [ ] **5.5** Setup cron job backup tự động:
  ```bash
  # Daily backup lúc 2:00 AM
  0 2 * * * /opt/plane-deploy/scripts/backup.sh
  ```
- [ ] **5.6** Backup retention policy: giữ 7 daily + 4 weekly + 3 monthly
- [ ] **5.7** Test disaster recovery: destroy instance → restore từ backup → verify data

---

## PHASE 6: MONITORING & ALERTING (Ngày 5-6)

> 📖 Hướng dẫn: [07-monitoring.md](./07-monitoring.md)

- [ ] **6.1** Deploy Prometheus (dùng `monitoring/prometheus.yml`)
- [ ] **6.2** Deploy Grafana (import dashboard `monitoring/grafana/dashboards/`)
- [ ] **6.3** Cấu hình health check script: `./scripts/health-check.sh`
- [ ] **6.4** Setup alerts:
  - [ ] CPU > 80% → alert
  - [ ] RAM > 85% → alert
  - [ ] Disk > 90% → alert
  - [ ] API response time > 5s → alert
  - [ ] Container restart → alert
- [ ] **6.5** Test alert: trigger condition → nhận được notification
- [ ] **6.6** Setup uptime monitoring: check endpoint mỗi 5 phút

---

## PHASE 7: ONBOARDING TEAMS (Tuần 2-4)

> 📖 Hướng dẫn: [08-onboarding.md](./08-onboarding.md)

### 7A. Pilot (Tuần 2)

- [ ] **7.1** Chọn 2 tổ pilot: Tổ 7 (AI) + Tổ 4 (Kiểm thử)
- [ ] **7.2** Tạo tài khoản cho pilot users (20-30 người)
- [ ] **7.3** Training session 30 phút: demo tạo issue, board, sprint
- [ ] **7.4** Pilot users tự dùng 1 tuần
- [ ] **7.5** Thu feedback: form khảo sát hoặc họp 15 phút

### 7B. Điều chỉnh (Tuần 3)

- [ ] **7.6** Fix issues từ feedback pilot
- [ ] **7.7** Điều chỉnh workflow/labels nếu cần
- [ ] **7.8** Tối ưu performance nếu chậm
- [ ] **7.9** Cập nhật tài liệu hướng dẫn sử dụng

### 7C. Rollout toàn phòng (Tuần 4)

- [ ] **7.10** Tạo tài khoản cho toàn bộ nhân viên
- [ ] **7.11** Gửi email hướng dẫn + link truy cập
- [ ] **7.12** Training session cho trưởng 7 tổ
- [ ] **7.13** Trưởng tổ training cho nhân viên trong tổ
- [ ] **7.14** Hỗ trợ tuần đầu: standby giải đáp thắc mắc

---

## PHASE 8: SCALE TO PRODUCTION — KUBERNETES (Tháng 2-3)

> 📖 Hướng dẫn: [04-production.md](./04-production.md)

> [!WARNING]
> Phase này chỉ làm sau khi PoC đã chạy ổn định 2-4 tuần với Docker Compose.
> Cần Kubernetes cluster sẵn sàng trước khi bắt đầu.

- [ ] **8.1** Setup Kubernetes cluster (3+ nodes)
- [ ] **8.2** Deploy PostgreSQL HA (primary + replica + PgBouncer)
- [ ] **8.3** Deploy Redis cluster (3 nodes)
- [ ] **8.4** Deploy MinIO cluster (4 nodes)
- [ ] **8.5** Migrate data từ Docker Compose → Kubernetes
- [ ] **8.6** Deploy Plane trên K8s (Helm chart hoặc custom manifests)
- [ ] **8.7** Cấu hình Ingress Controller + SSL
- [ ] **8.8** Load test: 500 concurrent users
- [ ] **8.9** Failover test: kill pod → auto-recover
- [ ] **8.10** Cutover: switch DNS/IP từ PoC sang Production
- [ ] **8.11** Decommission PoC instance

---

## PHASE 9: MAINTENANCE & CONTINUOUS IMPROVEMENT

- [ ] **9.1** Plane version upgrade process documented
- [ ] **9.2** Monthly security patch review
- [ ] **9.3** Quarterly capacity review (disk, CPU, RAM trends)
- [ ] **9.4** Upgrade to Air-gapped edition khi có license
- [ ] **9.5** LDAP/SAML integration khi có AD
- [ ] **9.6** Custom automation rules (Commercial edition)
- [ ] **9.7** API integration với các tool khác (SIEM, ticketing)

---

## QUICK REFERENCE — Lệnh thường dùng

```bash
# Start/Stop
docker compose up -d
docker compose down

# Logs
docker compose logs -f api
docker compose logs -f web

# Backup ngay
./scripts/backup.sh

# Health check
./scripts/health-check.sh

# Update Plane
cd /opt/plane && git pull && docker compose pull && docker compose up -d
```

---

> **Tổng: 9 phases, ~70 tasks.** Ưu tiên Phase 0→3 (chạy được). Phase 4→6 (chạy an toàn). Phase 7→9 (chạy production).
