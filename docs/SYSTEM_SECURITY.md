# SYSTEM SECURITY ARCHITECTURE & INTERNAL COMPLIANCE (100% LOCAL)

The **Sentinel Taskboard** is designed and deployed in strict compliance with on-premises information security principles (On-Premises / Air-Gapped). This document demonstrates the system's complete isolation and its security-hardened technical architecture.

---

## 1. Commitment to Complete Isolation (100% Local / Offline)

The system ensures **no data is sent to any external internet environment** and operates in absolute independence through the following mechanisms:

1. **On-Premises Storage:** All databases (PostgreSQL), file attachments (MinIO), cache/session (Valkey/Redis), and message queues (RabbitMQ) run as internal containers on the physical host server.
2. **Telemetry Disabled:** Remote monitoring callbacks to Plane's upstream servers are fully disabled during system initialization (`is_telemetry_enabled = False` and via environment variable configuration).
3. **Closed Enrollment:** Public registration has been disabled (`ENABLE_SIGNUP = 0`). Only the system administrator (Admin) can create and provision accounts directly in the database.
4. **Docker Virtual Network Isolation:** Sensitive services such as Database, Cache, and Queue do not expose ports to the host's external interfaces. All inter-service data flows occur exclusively within the isolated internal bridge network (`plane-network`).

---

## 2. Technology Stack Map (Decoupled Architecture)

The system is designed with a clear Microservices model for scalability and resource optimization:

```mermaid
graph TD
    User([LAN Network Device]) -->|Port 80/443| Caddy[Caddy Reverse Proxy]
    
    subgraph Web & Logic Layer
        Caddy -->|Next.js Frontend| FE[plane-web / plane-space]
        Caddy -->|Django API| BE[plane-api]
        Caddy -->|Admin Console| Admin[plane-admin]
    end
    
    subgraph Storage & Queue Layer (Isolated)
        BE -->|Cache & Session| Redis[Valkey/Redis]
        BE -->|Relational Data| DB[(PostgreSQL 15.7)]
        BE -->|Task Broker| MQ[RabbitMQ Queue]
        BE -->|Async Workers| Worker[Celery Workers]
        FE & BE -->|S3 Uploads| MinIO[MinIO Storage]
    end
    
    subgraph Monitoring Layer
        Grafana[Grafana Dashboard] -->|Query| Prom[Prometheus Engine]
        Prom -->|Scrape Host| Node[Node Exporter]
        Prom -->|Scrape Containers| Cadvisor[cAdvisor]
    end
```

### Core Technologies

* **Reverse Proxy / Security Gateway:** Caddy Server (routing, IP filtering, security header injection).
* **Frontend (FE):** Next.js (React) static build served via Nginx.
* **Backend (BE) & API:** Django REST Framework (Python 3) & Celery (background task processing).
* **Database (DB):** PostgreSQL 15.7 (ACID-compliant, hot backup support).
* **Cache & Message Broker:** Valkey (Redis fork) for <1ms session read/write and RabbitMQ for async message passing.
* **Object Storage (Local S3):** MinIO Server (internal file attachment storage management).

---

## 3. Active Security Measures (Security Hardening)

To protect the system against internal attack vectors (Insider Threats) and ensure information security compliance under **Zero Trust** principles:

### A. Zone-Based Access Control (IP ACL — Access Control List)

The advanced system configuration path `/god-mode` is protected by an IP filter at the Caddy Proxy layer. Only IPs within the Private LAN range (`127.0.0.1`, `192.168.0.0/16`, `172.16.0.0/12`, `10.0.0.0/8`) are permitted access. Requests from unknown sources are immediately blocked with a **403 Forbidden** error.

### B. Web UI Exploit Mitigation

The proxy automatically injects strict security headers into every browser response:

* `X-Frame-Options: DENY` — prevents Clickjacking attacks.
* `X-Content-Type-Options: nosniff` — prevents MIME-sniffing type confusion attacks.
* `Content-Security-Policy (CSP)` — restricts the browser to only execute scripts and assets originating from the trusted server itself, blocking externally injected XSS payloads.

### C. Resource Exhaustion Defense (Anti-DoS & Log Rotation)

* **Rate Limiting:** API request rate is capped at 30 requests/second per source IP to prevent brute-force attacks and automated vulnerability scanning.
* **Log Rotation:** Each container's log is capped at 10MB and automatically rotated with a maximum of 3 files. This prevents disk-filling denial-of-service (Disk-Filling DoS) attacks on the host.

### D. Phương án sao lưu & Khôi phục thảm họa (Disaster Recovery)

* Tích hợp sẵn kịch bản sao lưu tự động hàng ngày lúc 2:00 AM (`backup.sh`) được đăng ký trực tiếp vào Host Crontab.
* Tất cả tệp tin backup của Postgres và MinIO được mã hóa, nén dưới dạng tarball `.tar.gz` lưu trữ tại thư mục an toàn trên máy chủ Host (`/home/binhchuoiz/plane-backups`).

---

## 4. System Use Cases (Sơ đồ Use Case)

Sơ đồ dưới đây mô tả tương tác của các tác nhân (Actors) với các chức năng cốt lõi của hệ thống **Sentinel Taskboard**:

```mermaid
graph TD
    %% Tác nhân (Actors)
    Admin([System Admin / Workspace Owner])
    Member([Workspace Member])
    Guest([Guest / Viewer])
    System([Automated Cron/Backup System])

    subgraph Chức năng Workspace & Project (PRJ1-PRJ7)
        UC1(Cấu hình hệ thống & Instance settings)
        UC2(Quản lý dự án PRJ1-PRJ7)
        UC3(Phân quyền & Cấp phát thành viên)
        UC4(Cấu hình Workflow States & Labels)
        
        UC5(Quản lý Task / Issue & Board)
        UC6(Quản lý Cycles & Epics)
        UC7(Soạn thảo tài liệu Pages / Wiki)
        UC8(Tải lên/xuống File đính kèm)
        UC9(Theo dõi báo cáo Analytics)

        UC10(Sao lưu tự động DB & Object Store)
    end

    %% Mối liên kết (Associations)
    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9

    Member --> UC5
    Member --> UC6
    Member --> UC7
    Member --> UC8
    Member --> UC9

    Guest --> UC9

    System --> UC10
```

### Chi tiết phân quyền Use Case (RBAC Policy)

* **System Admin / Owner:** Toàn quyền thực hiện các nhóm Use Case cấu hình cấu trúc hệ thống, cấp phát tài khoản, thiết kế quy trình Workflow và thiết lập cài đặt an toàn.
* **Workspace Member:** Thực hiện các Use Case cộng tác hàng ngày như tạo và cập nhật Task/Issue, kéo thả Kanban Board, viết tài liệu Wiki (Pages), tải tệp lên/xuống và theo dõi Analytics của dự án được phân quyền.
* **Guest / Viewer:** Quyền hạn tối thiểu, chỉ được phép đọc dữ liệu (Read-only) tại các Use Case theo dõi tiến độ công việc và xem tài liệu, không có quyền chỉnh sửa.
* **Automated System:** Thực hiện tác vụ ngầm định kỳ (Sao lưu PostgreSQL qua pg_dump, nén thư mục MinIO và lưu giữ theo chính sách Retention Policy).

---

## 5. Network Architecture & Security Boundaries (Kiến trúc Mạng & Biên Bảo Mật)

Kiến trúc mạng của hệ thống tuân thủ mô hình **Zero Trust**, phân tách rõ ràng các phân vùng mạng và áp dụng Access Control List (ACL) nghiêm ngặt tại Proxy Caddy:

```mermaid
graph TD
    subgraph Phân Vùng Người Dùng (Client Zones)
        LAN[Mạng nội bộ LAN - 192.168.0.0/16]
        TS[Mạng ảo Tailscale VPN - 100.64.0.0/10]
        EXT[Mạng ngoài / Internet WAN]
    end

    subgraph Máy Chủ Host (ubuntu-binh)
        UFW[Tường lửa UFW]
        
        subgraph Mạng Ảo Cô Lập Docker (plane-network)
            Caddy[Caddy Reverse Proxy]
            
            subgraph Web & Admin Layer
                Web[plane-web :3000]
                Admin[plane-admin :3000]
                Space[plane-space :3000]
            end
            
            subgraph Nghiệp Vụ & Worker (Django/Celery)
                API[plane-api :8000]
                Celery[Celery Workers]
                Beat[Celery Beat]
            end
            
            subgraph Lưu Trữ Dữ Liệu (Không expose cổng ra Host)
                DB[(PostgreSQL DB)]
                Redis[(Valkey/Redis Cache)]
                MQ[(RabbitMQ Broker)]
                MinIO[(MinIO Object Store)]
            end
        end
    end

    %% Luồng kết nối mạng vào Host
    LAN -->|Cổng 80/443| UFW
    TS -->|Cổng 80/443| UFW
    EXT -->|Bị chặn / Lọc| UFW

    %% Tường lửa đẩy vào Proxy
    UFW -->|Định tuyến| Caddy

    %% Cơ chế lọc IP ACL tại Caddy
    Caddy -->|/api/* hoặc /auth/*| API
    Caddy -->|/*| Web
    
    Caddy -->|Đường dẫn /god-mode*| ACL{remote_ip thuộc LAN hoặc Tailscale?}
    ACL -->|Đồng ý| Admin
    ACL -->|Từ chối| Blocked[Trả về lỗi 403 Forbidden]

    %% Liên kết nội bộ mạng ảo Docker (Cô lập hoàn toàn)
    API -->|Read/Write| DB
    API -->|Session & Cache| Redis
    API -->|Message Queue| MQ
    Celery -->|Xử lý tác vụ ngầm| MQ
    Celery -->|Đồng bộ trạng thái| Redis
    Celery -->|Truy vấn dữ liệu| DB
    API -->|Lưu trữ tệp uploads| MinIO
    Web -->|Giao dịch tệp đính kèm| MinIO
```

### Các Biên Bảo Mật (Security Boundaries)

1. **Vành đai mạng ngoài (WAN Border):** Mọi cổng kết nối dịch vụ thô (`5432` Postgres, `6379` Valkey, `5672` RabbitMQ, `9000` MinIO) đều **bị đóng hoàn toàn** trên giao diện mạng vật lý của máy chủ Host.
2. **Lớp Reverse Proxy (Caddy):** Hoạt động như cổng kiểm soát biên duy nhất. Thực hiện chuyển hướng SSL nội bộ, chèn các header phòng vệ trình duyệt (CSP, HSTS) và thực thi bộ lọc IP (ACL) cho đường dẫn quản trị `/god-mode`.
3. **Vùng lưu trữ dữ liệu cô lập (Data Isolation Zone):** Toàn bộ cơ sở dữ liệu và hạ tầng hàng đợi chỉ giao tiếp thông qua mạng Docker Bridge nội bộ (`plane-network`). Kẻ tấn công nằm cùng mạng vật lý LAN cũng không thể kết nối trực tiếp đến PostgreSQL nếu chưa vượt qua được lớp xác thực của ứng dụng web.
