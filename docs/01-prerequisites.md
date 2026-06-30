# 01 — Prerequisites (Yêu cầu Hệ thống)

## Mục tiêu

Đảm bảo server đủ điều kiện trước khi deploy Plane.

---

## Yêu cầu Phần cứng

### PoC (1 server, < 50 users)

| Thành phần | Minimum | Recommended |
|---|---|---|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Disk | 30 GB SSD | 50 GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Production (5K users)

| Thành phần | Specs | Số lượng |
|---|---|---|
| K8s Worker Nodes | 8 vCPU, 16 GB RAM, 100 GB SSD | 3+ |
| PostgreSQL | 8 vCPU, 32 GB RAM, 500 GB SSD | 1 primary + 1 replica |
| Redis | 4 vCPU, 8 GB RAM | 3 nodes |
| MinIO | 4 vCPU, 8 GB RAM, 1 TB SSD | 4 nodes |

---

## Yêu cầu Phần mềm

| Software | Version | Kiểm tra |
|---|---|---|
| OS | Ubuntu 22.04/24.04 LTS | `lsb_release -a` |
| Docker Engine | >= 24.0 | `docker --version` |
| Docker Compose | >= 2.0 (plugin) | `docker compose version` |
| Git | >= 2.30 | `git --version` |
| curl | any | `curl --version` |

---

## Cài đặt Docker (nếu chưa có)

```bash
# Cài Docker Engine
curl -fsSL https://get.docker.com | sh

# Thêm user hiện tại vào group docker
sudo usermod -aG docker $USER

# Logout và login lại (hoặc newgrp docker)
newgrp docker

# Verify
docker run hello-world
```

---

## Cấu hình Network

### Ports cần mở (firewall)

| Port | Service | Hướng |
|---|---|---|
| 80 | HTTP (Nginx) | Inbound từ LAN |
| 443 | HTTPS (Nginx) | Inbound từ LAN |
| 5432 | PostgreSQL | Internal only (KHÔNG mở ra ngoài) |
| 6379 | Redis | Internal only |
| 9000 | MinIO API | Internal only |
| 9001 | MinIO Console | Internal only (admin debug) |

```bash
# UFW example
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp   # Block external PostgreSQL
sudo ufw deny 6379/tcp   # Block external Redis
sudo ufw enable
```

---

## Tạo User riêng (khuyến nghị)

```bash
# Không chạy Plane bằng root
sudo useradd -m -s /bin/bash plane-admin
sudo usermod -aG docker plane-admin
sudo passwd plane-admin

# Switch sang user plane-admin
su - plane-admin
```

---

## DNS / Domain

Có 2 option:

1. **Dùng IP trực tiếp:** `http://192.168.x.x` — đơn giản, phù hợp PoC
2. **Dùng internal domain:** `https://plane.sentinel.internal` — khuyến nghị cho production
   - Cần DNS server nội bộ hoặc sửa `/etc/hosts` trên client machines
   - Cần SSL certificate (self-signed hoặc internal CA)

---

## Checklist kiểm tra

Sau khi chuẩn bị xong, chạy script kiểm tra:

```bash
./scripts/check-prerequisites.sh
```

Script sẽ verify tất cả yêu cầu trên và báo PASS/FAIL cho từng mục.
