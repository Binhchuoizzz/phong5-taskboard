# 06 — Backup & Disaster Recovery

## Mục tiêu

Đảm bảo dữ liệu không bị mất trong mọi tình huống. Khôi phục nhanh khi có sự cố.

---

## 1. Backup Strategy

### Retention Policy

| Level | Tần suất | Giữ lại | Lưu tại |
|---|---|---|---|
| Daily | Hàng ngày 2:00 AM | 7 bản gần nhất | `/backup/daily/` |
| Weekly | Chủ nhật 3:00 AM | 4 bản gần nhất | `/backup/weekly/` |
| Monthly | Ngày 1 mỗi tháng 4:00 AM | 3 bản gần nhất | `/backup/monthly/` |

### Thành phần cần backup

1. **PostgreSQL database** — chứa toàn bộ data (issues, users, projects)
2. **MinIO/Storage** — file attachments, avatars, uploads
3. **Environment files** — `.env`, configs
4. **Docker Compose files** — `docker-compose.yml`, custom configs

---

## 2. Backup Script

File: `scripts/backup.sh`

```bash
#!/bin/bash
# Plane Backup Script
# Usage: ./scripts/backup.sh [daily|weekly|monthly]

set -euo pipefail

BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/${BACKUP_TYPE}"
BACKUP_NAME="plane-backup-${TIMESTAMP}"
PLANE_DIR="/opt/plane"

# Tạo thư mục backup
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

echo "=== Plane Backup Started: ${BACKUP_NAME} ==="

# 1. Backup PostgreSQL
echo "[1/4] Backing up PostgreSQL..."
docker compose -f ${PLANE_DIR}/docker-compose.yml exec -T postgres \
  pg_dump -U plane -d plane --format=custom --compress=9 \
  > "${BACKUP_DIR}/${BACKUP_NAME}/database.dump"
echo "  → Database backup: $(du -sh ${BACKUP_DIR}/${BACKUP_NAME}/database.dump | cut -f1)"

# 2. Backup MinIO data
echo "[2/4] Backing up MinIO storage..."
docker compose -f ${PLANE_DIR}/docker-compose.yml exec -T minio \
  tar czf - /data 2>/dev/null \
  > "${BACKUP_DIR}/${BACKUP_NAME}/minio-data.tar.gz"
echo "  → MinIO backup: $(du -sh ${BACKUP_DIR}/${BACKUP_NAME}/minio-data.tar.gz | cut -f1)"

# 3. Backup configs
echo "[3/4] Backing up configurations..."
cp ${PLANE_DIR}/.env "${BACKUP_DIR}/${BACKUP_NAME}/env.backup"
cp ${PLANE_DIR}/docker-compose.yml "${BACKUP_DIR}/${BACKUP_NAME}/docker-compose.yml.backup"
echo "  → Configs backed up"

# 4. Tạo archive
echo "[4/4] Creating archive..."
cd "${BACKUP_DIR}"
tar czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"
echo "  → Archive: $(du -sh ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"

# 5. Cleanup old backups
echo "=== Cleanup old backups ==="
case ${BACKUP_TYPE} in
  daily)   KEEP=7  ;;
  weekly)  KEEP=4  ;;
  monthly) KEEP=3  ;;
esac

ls -t "${BACKUP_DIR}"/plane-backup-*.tar.gz | tail -n +$((KEEP + 1)) | xargs -r rm -v

echo "=== Backup Complete: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz ==="
```

---

## 3. Restore Script

File: `scripts/restore.sh`

```bash
#!/bin/bash
# Plane Restore Script
# Usage: ./scripts/restore.sh /path/to/backup.tar.gz

set -euo pipefail

BACKUP_FILE="${1:?Usage: ./restore.sh <backup-file.tar.gz>}"
PLANE_DIR="/opt/plane"
TEMP_DIR=$(mktemp -d)

echo "=== Plane Restore Started ==="
echo "Backup file: ${BACKUP_FILE}"

# 1. Extract backup
echo "[1/5] Extracting backup..."
tar xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"
BACKUP_NAME=$(ls "${TEMP_DIR}")

# 2. Stop Plane services (keep database running)
echo "[2/5] Stopping Plane services..."
docker compose -f ${PLANE_DIR}/docker-compose.yml stop api web worker beat

# 3. Restore PostgreSQL
echo "[3/5] Restoring PostgreSQL..."
docker compose -f ${PLANE_DIR}/docker-compose.yml exec -T postgres \
  pg_restore -U plane -d plane --clean --if-exists \
  < "${TEMP_DIR}/${BACKUP_NAME}/database.dump"

# 4. Restore MinIO data
echo "[4/5] Restoring MinIO storage..."
docker compose -f ${PLANE_DIR}/docker-compose.yml exec -T minio \
  tar xzf - -C / \
  < "${TEMP_DIR}/${BACKUP_NAME}/minio-data.tar.gz"

# 5. Restart all services
echo "[5/5] Restarting Plane..."
docker compose -f ${PLANE_DIR}/docker-compose.yml up -d

# Cleanup
rm -rf "${TEMP_DIR}"

echo "=== Restore Complete ==="
echo "Verify: open http://<server-ip> and check data integrity"
```

---

## 4. Cron Jobs

```bash
# Thêm vào crontab (crontab -e)

# Daily backup lúc 2:00 AM
0 2 * * * /opt/plane-deploy/scripts/backup.sh daily >> /var/log/plane-backup.log 2>&1

# Weekly backup Chủ nhật 3:00 AM
0 3 * * 0 /opt/plane-deploy/scripts/backup.sh weekly >> /var/log/plane-backup.log 2>&1

# Monthly backup ngày 1 mỗi tháng 4:00 AM
0 4 1 * * /opt/plane-deploy/scripts/backup.sh monthly >> /var/log/plane-backup.log 2>&1
```

---

## 5. Disaster Recovery Plan

### Scenario 1: Server crash (hardware failure)

1. Provision server mới (cùng specs)
2. Cài Docker + Docker Compose
3. Clone Plane repo
4. Restore từ backup mới nhất: `./scripts/restore.sh /backup/daily/latest.tar.gz`
5. Update DNS/IP
6. **RTO: 1-2 giờ** | **RPO: max 24 giờ** (daily backup)

### Scenario 2: Database corruption

1. Stop API + Worker
2. Drop và recreate database
3. Restore: `./scripts/restore.sh /backup/daily/latest.tar.gz`
4. Restart services
5. **RTO: 30 phút** | **RPO: max 24 giờ**

### Scenario 3: Accidental data deletion

1. Identify thời điểm xóa
2. Restore backup gần nhất trước thời điểm đó
3. Có thể cần restore vào instance tạm để extract data cụ thể
4. **RTO: 1 giờ** | **RPO: tùy backup frequency**

---

## 6. Testing Backup/Restore

### Test hàng tháng (bắt buộc)

```bash
# 1. Chạy backup
./scripts/backup.sh daily

# 2. Tạo instance test (docker compose khác port)
# 3. Restore vào instance test
./scripts/restore.sh /backup/daily/latest.tar.gz

# 4. Verify data:
# - Đăng nhập được
# - Issues, projects đầy đủ
# - File attachments hiển thị
# - User accounts nguyên vẹn
```
