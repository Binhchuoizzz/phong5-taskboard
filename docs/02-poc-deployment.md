# 02 — PoC Deployment (Deploy Bản Demo)

## Mục tiêu

Deploy Plane Community Edition trên 1 server bằng Docker Compose. Mục đích: validate workflow, test features, cho 5-10 user dùng thử.

---

## Bước 1: Clone Plane

```bash
# Clone vào /opt/plane (hoặc đường dẫn khác)
sudo mkdir -p /opt/plane
sudo chown $(whoami):$(whoami) /opt/plane
git clone --depth 1 -b master https://github.com/makeplane/plane.git /opt/plane
cd /opt/plane
```

---

## Bước 2: Chạy Setup

Plane có script setup tự động tạo `.env` và pull Docker images:

```bash
./setup.sh
```

Script sẽ hỏi:
- **Domain:** Nhập IP hoặc domain (VD: `192.168.1.100` hoặc `plane.sentinel.internal`)
- **Express/Advanced:** Chọn **Express** cho PoC (setup nhanh, default values)

---

## Bước 3: Chỉnh sửa Environment (tùy chỉnh)

Nếu cần custom, sửa file `.env`:

```bash
nano .env
```

Các biến quan trọng:

```env
# === DATABASE ===
POSTGRES_USER=plane
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>    # Đổi password mạnh!
POSTGRES_DB=plane

# === SECURITY ===
SECRET_KEY=<RANDOM_64_CHARS>               # python3 -c "import secrets; print(secrets.token_hex(32))"

# === DOMAIN ===
WEB_URL=http://192.168.1.100               # Hoặc https://plane.sentinel.internal
CORS_ALLOWED_ORIGINS=http://192.168.1.100

# === STORAGE (MinIO) ===
MINIO_ROOT_USER=plane-minio
MINIO_ROOT_PASSWORD=<STRONG_PASSWORD_HERE>  # Đổi password mạnh!

# === OPTIONAL: Email (SMTP) ===
# EMAIL_HOST=smtp.sentinel.internal
# EMAIL_PORT=587
# EMAIL_HOST_USER=plane@sentinel.internal
# EMAIL_HOST_PASSWORD=xxx
# EMAIL_USE_TLS=1
```

---

## Bước 4: Start Services

```bash
docker compose up -d
```

Kiểm tra tất cả containers đang chạy:

```bash
docker compose ps
```

Expected output — tất cả phải `running`:

```
NAME              STATUS
plane-web         running
plane-api         running
plane-worker      running
plane-beat        running
plane-postgres    running
plane-redis       running
plane-minio       running
plane-proxy       running
```

---

## Bước 5: Truy cập & Setup Admin

1. Mở browser: `http://<server-ip>`
2. Tạo tài khoản admin đầu tiên (email + password)
3. Đăng nhập → bạn sẽ là **Instance Admin** (God Mode)

### God Mode Setup:

1. Vào **Settings** → **General**:
   - Instance name: `Sentinel-Workspace`
   - Disable public sign-up (chỉ cho invite)

2. Tạo **Workspace**: `Sentinel-Workspace`
   - URL slug: `sentinel`

3. Tiếp tục **Phase 2** trong [03-configuration.md](./03-configuration.md)

---

## Troubleshooting

### Container không start

```bash
# Xem logs
docker compose logs -f <service-name>

# Ví dụ: API server crash
docker compose logs -f api

# Restart all
docker compose down && docker compose up -d
```

### PostgreSQL connection refused

```bash
# Check PostgreSQL container
docker compose logs postgres

# Common: port conflict → đổi port trong .env
# Common: password sai → verify POSTGRES_PASSWORD
```

### Port 80 đã bị dùng

```bash
# Tìm process dùng port 80
sudo lsof -i :80

# Kill hoặc đổi port trong docker-compose.yml
# Sửa: ports: "8080:80" thay vì "80:80"
```

### Không truy cập được từ máy khác

```bash
# Check firewall
sudo ufw status

# Check Docker network
docker network ls
docker network inspect plane_default
```

---

## Verification Checklist

Sau khi deploy, verify từng mục:

```bash
# 1. Web UI accessible
curl -s -o /dev/null -w "%{http_code}" http://localhost
# Expected: 200

# 2. API health
curl -s http://localhost/api/health/
# Expected: {"status": "ok"}

# 3. All containers running
docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep -c "running"
# Expected: 8 (hoặc số lượng services)

# 4. Database connected
docker compose exec api python manage.py dbshell -c "SELECT 1;"
# Expected: no error

# 5. Disk usage check
docker system df
# Verify: enough space remaining
```
