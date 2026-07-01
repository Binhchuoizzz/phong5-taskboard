#!/bin/bash
# ============================================================
# Plane Backup Script (Decoupled Stack Support)
# Backs up PostgreSQL, MinIO storage, and configs
# Usage: ./scripts/backup.sh [daily|weekly|monthly]
# ============================================================

set -euo pipefail

BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE_DIR="${BACKUP_DIR:-/backup}"
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_TYPE}"
BACKUP_NAME="plane-backup-${TIMESTAMP}"
PLANE_DIR="${PLANE_INSTALL_DIR:-/opt/plane}"

if docker compose version &>/dev/null; then
    DC_CMD="docker compose"
else
    DC_CMD="docker-compose"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Plane Backup Started ===${NC}"
echo "Type: ${BACKUP_TYPE}"
echo "Time: $(date)"
echo ""

# Load environment variables to read postgres password
if [ -f "${PLANE_DIR}/plane.env" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ ! "$line" =~ ^\s*# ]] && [[ "$line" =~ = ]]; then
            export "$line"
        fi
    done < "${PLANE_DIR}/plane.env"
fi

# Decoupled stack command
DC_DB="$DC_CMD -f ${PLANE_DIR}/docker-compose.db.yaml --env-file=${PLANE_DIR}/plane.env"

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# 1. Backup PostgreSQL
echo -e "${BLUE}[1/4] Backing up PostgreSQL...${NC}"
if $DC_DB exec -e PGPASSWORD="${POSTGRES_PASSWORD:-}" -T plane-db \
    pg_dump -U plane -d plane --format=custom --compress=9 \
    > "${BACKUP_DIR}/${BACKUP_NAME}/database.dump" 2>/dev/null; then
    SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}/database.dump" | cut -f1)
    echo -e "  ${GREEN}✅ Database: ${SIZE}${NC}"
else
    echo -e "  ${RED}❌ Database backup failed${NC}"
    exit 1
fi

# 2. Backup MinIO data
echo -e "${BLUE}[2/4] Backing up MinIO storage...${NC}"
# Use docker cp because minio/minio image lacks tar utility
if docker cp plane-app-plane-minio-1:/export "${BACKUP_DIR}/${BACKUP_NAME}/minio-data" 2>/dev/null; then
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/minio-data.tar.gz" -C "${BACKUP_DIR}/${BACKUP_NAME}" minio-data 2>/dev/null
    rm -rf "${BACKUP_DIR}/${BACKUP_NAME}/minio-data"
    SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}/minio-data.tar.gz" | cut -f1)
    echo -e "  ${GREEN}✅ MinIO: ${SIZE}${NC}"
else
    echo "  ℹ️  MinIO container not found or empty, skipping"
    touch "${BACKUP_DIR}/${BACKUP_NAME}/minio-data.tar.gz"
fi

# 3. Backup configs
echo -e "${BLUE}[3/4] Backing up configurations...${NC}"
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}/config"
cp "${PLANE_DIR}/plane.env" "${BACKUP_DIR}/${BACKUP_NAME}/config/plane.env.backup" 2>/dev/null || true
cp "${PLANE_DIR}/docker-compose.db.yaml" "${BACKUP_DIR}/${BACKUP_NAME}/config/docker-compose.db.yaml.backup" 2>/dev/null || true
cp "${PLANE_DIR}/docker-compose.app.yaml" "${BACKUP_DIR}/${BACKUP_NAME}/config/docker-compose.app.yaml.backup" 2>/dev/null || true
cp "${PLANE_DIR}/docker-compose.proxy.yaml" "${BACKUP_DIR}/${BACKUP_NAME}/config/docker-compose.proxy.yaml.backup" 2>/dev/null || true
cp "${PLANE_DIR}/docker-compose.monitor.yaml" "${BACKUP_DIR}/${BACKUP_NAME}/config/docker-compose.monitor.yaml.backup" 2>/dev/null || true
echo -e "  ${GREEN}✅ Configs backed up${NC}"

# 4. Create archive
echo -e "${BLUE}[4/4] Creating archive...${NC}"
cd "${BACKUP_DIR}"
tar czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"
SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo -e "  ${GREEN}✅ Archive: ${SIZE}${NC}"

# Cleanup old backups
echo ""
echo "Cleaning old backups..."
case ${BACKUP_TYPE} in
    daily)   KEEP=7  ;;
    weekly)  KEEP=4  ;;
    monthly) KEEP=3  ;;
    *)       KEEP=7  ;;
esac

DELETED=$(ls -t "${BACKUP_DIR}"/plane-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | wc -l)
ls -t "${BACKUP_DIR}"/plane-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -v
echo "  Deleted ${DELETED} old backup(s), keeping ${KEEP}"

echo ""
echo -e "${GREEN}=== Backup Complete ===${NC}"
echo "File: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "Size: ${SIZE}"
