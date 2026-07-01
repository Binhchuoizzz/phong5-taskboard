# TÀI LIỆU KIẾN TRÚC CÔNG NGHỆ VÀ CAM KẾT BẢO MẬT NỘI BỘ (100% LOCAL)

Hệ thống **Sentinel Taskboard** được thiết kế và triển khai tuân thủ nghiêm ngặt các nguyên tắc an ninh thông tin của mạng nội bộ (On-Premises / Air-Gapped). Tài liệu này chứng minh tính khép kín hoàn toàn và kiến trúc kỹ thuật bảo mật của hệ thống.

---

## 1. Cam Kết Khép Kín Hoàn Toàn (100% Local / Offline)

Hệ thống đảm bảo **không gửi bất kỳ dữ liệu nào ra môi trường internet** và hoạt động độc lập tuyệt đối nhờ các cơ chế sau:

1.  **Dữ liệu tại chỗ (On-Premises Storage):** Toàn bộ cơ sở dữ liệu (PostgreSQL), tệp tin đính kèm (MinIO), bộ nhớ đệm (Valkey/Redis), và thông điệp hàng đợi (RabbitMQ) đều chạy dưới dạng các Container nội bộ trên máy chủ vật lý của anh.
2.  **Tắt Telemetry (Vô hiệu hóa thu thập dữ liệu):** Cờ giám sát từ xa gửi về máy chủ hãng Plane đã được tắt hoàn toàn trong cài đặt khởi tạo hệ thống (`is_telemetry_enabled = False` và cấu hình biến môi trường).
3.  **Khóa đăng ký tự do (Closed Enrollment):** Đã tắt tính năng đăng ký công khai (`ENABLE_SIGNUP = 0`). Chỉ quản trị viên hệ thống (Admin) mới có quyền tạo và cấp phát tài khoản trực tiếp trong cơ sở dữ liệu.
4.  **Cách ly mạng ảo Docker:** Các dịch vụ nhạy cảm như Database, Cache, Queue không mở (expose) cổng kết nối ra ngoài máy host. Mọi luồng giao tiếp dữ liệu chỉ diễn ra trong mạng ảo bridge cô lập (`plane-network`).

---

## 2. Bản Đồ Công Nghệ Sử Dụng (Decoupled Tech Stack)

Hệ thống được thiết kế theo mô hình Microservices phân tách rõ ràng để dễ dàng mở rộng và tối ưu hóa tài nguyên:

```mermaid
graph TD
    User([Thiết bị mạng LAN]) -->|Port 80/443| Caddy[Caddy Reverse Proxy]
    
    subgraph Web & Logic Layer
        Caddy -->|Next.js Frontend| FE[plane-web / plane-space]
        Caddy -->|Django API| BE[plane-api]
        Caddy -->|Admin Console| Admin[plane-admin]
    end
    
    subgraph Storage & Queue Layer (Isolated)
        BE -->|Cache & Session| Redis[Valkey/Redis]
        BE -->|Relational Data| DB[(PostgreSQL 15.7)]
        BE -->|Task Broker| MQ[RabbitMQ Queue]
        BE -->|Asynchronous Workers| Worker[Celery Workers]
        FE & BE -->|S3 Uploads| MinIO[MinIO Storage]
    end
    
    subgraph Monitoring Layer
        Grafana[Grafana Dashboard] -->|Query| Prom[Prometheus Engine]
        Prom -->|Scrape Host| Node[Node Exporter]
        Prom -->|Scrape Containers| Cadvisor[cAdvisor]
    end
```

### Các công nghệ lõi:
*   **Reverse Proxy / Security Gateway:** Caddy Server (Định tuyến, lọc IP, chèn Security Headers).
*   **Frontend (FE):** Next.js (React) biên dịch tĩnh chạy trên Nginx.
*   **Backend (BE) & API:** Django REST Framework (Python 3) & Celery (xử lý tác vụ ngầm).
*   **Database (DB):** PostgreSQL 15.7 (Hỗ trợ ACID, sao lưu nóng).
*   **Cache & Message Broker:** Valkey (Redis forks) cho tốc độ đọc/ghi session < 1ms và RabbitMQ cho truyền tin bất đồng bộ.
*   **Object Storage (Local S3):** MinIO Server (Quản lý lưu trữ tệp đính kèm nội bộ).

---

## 3. Các Biện Pháp Bảo Mật Hệ Thống Đang Áp Dụng (Security Hardening)

Để bảo vệ hệ thống trước các vector tấn công nội bộ (Insider Threats) và đảm bảo an toàn thông tin theo chuẩn **Zero Trust**:

### A. Kiểm soát truy cập phân vùng (IP ACL - Access Control List)
Đường dẫn cấu hình hệ thống chuyên sâu `/god-mode` được thiết lập bộ lọc IP tại lớp Proxy Caddy. Chỉ cho phép các IP thuộc dải Private LAN (`127.0.0.1`, `192.168.0.0/16`, `172.16.0.0/12`, `10.0.0.0/8`) kết nối. Các truy cập từ nguồn không xác định sẽ bị chặn đứng với mã lỗi **403 Forbidden**.

### B. Chống tấn công khai thác lỗ hổng Web UI
Proxy tự động chèn các tiêu chuẩn Header bảo mật nghiêm ngặt vào mọi Response trả về trình duyệt:
*   `X-Frame-Options: DENY`: Chống tấn công Clickjacking (miết đè khung hình ẩn).
*   `X-Content-Type-Options: nosniff`: Chống tấn công thay đổi kiểu file (MIME-sniffing).
*   `Content-Security-Policy (CSP)`: Chỉ cho phép trình duyệt thực thi các mã nguồn đáng tin cậy phát sinh từ chính máy chủ, chặn đứng mã độc XSS từ ngoài tiêm vào.

### C. Cơ chế phòng thủ cạn kiệt tài nguyên (Anti-DoS & Log Rotation)
*   **Rate Limiting:** Giới hạn tần suất gửi yêu cầu API tối đa là 30 requests/giây trên một địa chỉ IP để chống brute-force và quét lỗ hổng tự động.
*   **Log Rotation:** Giới hạn dung lượng Log của mỗi Container tối đa là 10MB và tự động cuốn chiếu luân phiên tối đa 3 file. Đảm bảo ổ đĩa của máy chủ không bị ghi đầy (Disk-Filling DoS).

### D. Phương án sao lưu & Khôi phục thảm họa (Disaster Recovery)
*   Tích hợp sẵn kịch bản sao lưu tự động hàng ngày lúc 2:00 AM (`backup.sh`) được đăng ký trực tiếp vào Host Crontab.
*   Tất cả tệp tin backup của Postgres và MinIO được mã hóa, nén dưới dạng tarball `.tar.gz` lưu trữ tại thư mục an toàn trên máy chủ Host (`/home/binhchuoiz/plane-backups`).
