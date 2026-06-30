# 05 — Security Hardening

## Mục tiêu

Bảo mật Plane deployment cho môi trường an ninh mạng quốc gia. Zero trust, defense in depth.

---

## 1. Network Security

### 1.1 Nginx Reverse Proxy — SSL/TLS

Dùng config tại `docker/nginx/plane.conf`:

```nginx
# Force TLS 1.3 only
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 1.2 Security Headers

```nginx
# Trong plane.conf
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' wss:;" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

### 1.3 IP Restriction (chỉ cho mạng nội bộ)

```nginx
# Chỉ cho phép IP range nội bộ
allow 10.0.0.0/8;
allow 172.16.0.0/12;
allow 192.168.0.0/16;
deny all;
```

### 1.4 Firewall Rules

```bash
# UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.0.0/16 to any port 443 proto tcp
sudo ufw allow from 10.0.0.0/8 to any port 443 proto tcp
sudo ufw allow ssh
sudo ufw enable
```

---

## 2. Database Security

### 2.1 Strong Passwords

```bash
# Generate strong password
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Áp dụng cho:
- `POSTGRES_PASSWORD`
- `SECRET_KEY` (64+ ký tự)
- `MINIO_ROOT_PASSWORD`
- Redis password (nếu dùng)

### 2.2 PostgreSQL Hardening

```sql
-- Trong postgresql.conf (mount vào container)
-- Chỉ listen trên internal interface
listen_addresses = '172.18.0.0/16'  -- Docker internal network

-- SSL
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'

-- Connection limits
max_connections = 200
```

### 2.3 pg_hba.conf (Authentication)

```
# Chỉ cho phép kết nối từ Docker network, bắt buộc SSL
hostssl plane plane 172.18.0.0/16 scram-sha-256
host   all   all   0.0.0.0/0     reject
```

---

## 3. Application Security

### 3.1 Disable Public Sign-up

Trong God Mode → Settings → General:
- **Allow sign-ups:** ❌ Disabled
- Chỉ admin mới invite được

### 3.2 Session Security

```env
# Trong .env
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_AGE=1800  # 30 phút timeout
```

### 3.3 CORS Configuration

```env
CORS_ALLOWED_ORIGINS=https://plane.sentinel.internal
# KHÔNG dùng wildcard *
```

### 3.4 Rate Limiting

```nginx
# Trong plane.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /api/ {
    limit_req zone=api burst=50 nodelay;
    proxy_pass http://plane-api:8000;
}

location /api/sign-in/ {
    limit_req zone=login burst=3 nodelay;
    proxy_pass http://plane-api:8000;
}
```

---

## 4. Container Security

### 4.1 Non-root Containers

Verify tất cả container không chạy root:

```bash
docker compose exec api whoami
# Phải KHÔNG phải root
```

### 4.2 Read-only Filesystem (nếu Plane support)

```yaml
# Trong docker-compose.prod.yml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp
```

### 4.3 Resource Limits

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 5. Logging & Audit

### 5.1 Docker Log Configuration

```yaml
# Trong docker-compose.prod.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
        tag: "plane-api"
```

### 5.2 Log Rotation

```bash
# /etc/logrotate.d/plane
/var/lib/docker/containers/*/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 5.3 Audit Logging (Commercial/Air-gapped)

Nếu dùng Plane Commercial:
- Enable audit log trong God Mode → Settings
- Logs ghi lại: login/logout, issue changes, permission changes, project changes
- Export audit report hàng tháng

---

## 6. LDAP/SAML Integration (Nếu có AD)

### SAML (Plane Commercial)

```
God Mode → Authentication → SAML
- Entity ID: https://plane.sentinel.internal
- SSO URL: https://adfs.company.com/adfs/ls
- Certificate: (upload IdP certificate)
```

### LDAP (Plane Commercial)

```
God Mode → Authentication → LDAP
- Server: ldap://dc.company.com:389
- Base DN: ou=Sentinel,dc=company,dc=com
- Bind DN: cn=plane-service,ou=service-accounts,dc=company,dc=com
```

---

## 7. Security Checklist

```
- [ ] SSL/TLS 1.3 enabled, HTTP redirects to HTTPS
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] IP restriction: only internal network
- [ ] Firewall rules in place
- [ ] Strong passwords (all services)
- [ ] PostgreSQL: SSL, restricted access, strong auth
- [ ] Public sign-up disabled
- [ ] Session timeout configured (30 min)
- [ ] CORS restricted to specific domain
- [ ] Rate limiting on API and login endpoints
- [ ] Containers not running as root
- [ ] Resource limits set on containers
- [ ] Log rotation configured
- [ ] Audit logging enabled (if Commercial)
- [ ] Regular security updates scheduled
```
