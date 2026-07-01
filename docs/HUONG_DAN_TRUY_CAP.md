# HƯỚNG DẪN TRUY CẬP HỆ THỐNG SENTINEL TASKBOARD (MẠNG NỘI BỘ - LAN)

Hệ thống quản lý dự án **Sentinel Taskboard** đã được triển khai độc lập, phân tách kiến trúc (Frontend, Backend, Database, Monitor) và bảo mật hóa. Dưới đây là thông tin chi tiết để sếp và các thành viên trong mạng LAN truy cập trải nghiệm.

---

## 1. Địa Chỉ Truy Cập Dịch Vụ (LAN URL)

| Thành phần hệ thống | Địa chỉ URL (Gõ vào trình duyệt) | Ghi chú an toàn |
| :--- | :--- | :--- |
| 🌐 **Giao diện làm việc (Web App)** | **[http://192.168.0.177](http://192.168.0.177)** | Sử dụng giao thức HTTP thường để tránh lỗi chứng chỉ SSL |
| ⚙️ **Trang Quản trị hệ thống (God Mode)** | **[http://192.168.0.177/god-mode/](http://192.168.0.177/god-mode/)** | Chỉ cho phép truy cập từ dải mạng LAN nội bộ |
| 📊 **Hệ thống Giám sát (Grafana)** | **[http://192.168.0.177:3001](http://192.168.0.177:3001)** | Tài khoản mặc định: `admin` / `admin` |
| 🚨 **Cổng Prometheus Alerting** | **[http://192.168.0.177:9090](http://192.168.0.177:9090)** | Theo dõi trạng thái tài nguyên và các cảnh báo tự động |

---

## 2. Thông Tin Tài Khoản Đăng Nhập Thử Nghiệm

Hệ thống đã được gieo sẵn dữ liệu thành viên ứng với các phân quyền (RBAC) khác nhau để sếp dễ dàng kiểm thử:

### 🔑 Tài khoản 1: Quản trị viên tối cao (Workspace Owner)
*   **Họ và tên:** Nguyễn Đức Bình (Admin)
*   **Email:** `admin@sentinel.local`
*   **Mật khẩu:** `Sentinel@123`
*   **Quyền hạn:** Toàn quyền quản lý Workspace, cấu hình trạng thái, nhãn dán, tạo dự án và phân quyền.

### 🔑 Tài khoản 2: Thành viên nghiệp vụ (Member - Tổ 6 SOC)
*   **Họ và tên:** Member Tổ 6
*   **Email:** `member1@sentinel.local`
*   **Mật khẩu:** `Sentinel@123`
*   **Quyền hạn:** Có quyền thêm mới, cập nhật các Task trong dự án Incident Response `PRJ6-Analytics`. Không xem được các dự án nghiệp vụ khác.

### 🔑 Tài khoản 3: Lãnh đạo giám sát (Guest - Tổ 1 Tham Mưu)
*   **Họ và tên:** Lãnh đạo Tổ 1
*   **Email:** `guest1@sentinel.local`
*   **Mật khẩu:** `Sentinel@123`
*   **Quyền hạn:** Chỉ có quyền đọc (Read-only) để xem báo cáo, tiến độ công việc trong dự án Tham Mưu `PRJ1-Core`. Không thể sửa đổi dữ liệu.

---

## 3. Lưu Ý Khi Gõ Mật Khẩu (Tránh Lỗi Telex/VNI)
Do mật khẩu chứa phím số và ký tự đặc biệt (`Sentinel@123`), nếu sếp bật bộ gõ tiếng Việt (Unikey/EVKey) ở chế độ **VNI** hoặc **Telex**, ký tự gõ ra có thể bị biến đổi thành chữ tiếng Việt có dấu (ví dụ: `Phòng...@123`) dẫn đến lỗi đăng nhập.

> [!TIP]
> **Khuyên dùng:** 
> *   Chuyển bộ gõ sang tiếng Anh (`ENG` hoặc `E`) trước khi nhập mật khẩu.
> *   Hoặc **Copy (Sao chép)** mật khẩu `Sentinel@123` bên trên và **Paste (Dán)** trực tiếp vào ô nhập liệu.
