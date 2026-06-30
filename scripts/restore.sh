#!/bin/bash
# ============================================================
# Plane Restore Script
# Restores PostgreSQL and MinIO from backup archive
# Usage: ./scripts/restore.sh /path/to/plane-backup-XXXXXXXX.tar.gz
# ============================================================

set -euo pipefail

BACKUP_FILE="${1:?Usage: ./scripts/restore.sh <backup-file.tar.gz>}"
PLANE_DIR="${PLANE_INSTALL_DIR:-/opt/plane}"

if docker compose version &>/dev/null; then
    DC_CMD="docker compose"
else
    DC_CMD="docker-compose"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Plane Restore Script                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "Backup file: ${BACKUP_FILE}"
echo "Plane dir:   ${PLANE_DIR}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will OVERWRITE current data!${NC}"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

# 1. Extract backup
echo -e "${BLUE}[1/5] Extracting backup...${NC}"
tar xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"
BACKUP_NAME=$(ls "${TEMP_DIR}" | head -1)
echo -e "  ${GREEN}✅ Extracted: ${BACKUP_NAME}${NC}"

# 2. Stop app services (keep DB running)
echo -e "${BLUE}[2/5] Stopping Plane services...${NC}"
cd "${PLANE_DIR}"
$DC_CMD stop api web worker beat proxy 2>/dev/null || true
echo -e "  ${GREEN}✅ Services stopped${NC}"

# 3. Restore PostgreSQL
echo -e "${BLUE}[3/5] Restoring PostgreSQL...${NC}"
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/database.dump" ]; then
    # Drop and recreate database
    $DC_CMD exec -T postgres psql -U plane -d postgres -c "DROP DATABASE IF EXISTS plane;" 2>/dev/null || true
    $DC_CMD exec -T postgres psql -U plane -d postgres -c "CREATE DATABASE plane;" 2>/dev/null || true

    # Restore
    $DC_CMD exec -T postgres \
        pg_restore -U plane -d plane --no-owner --no-privileges \
        < "${TEMP_DIR}/${BACKUP_NAME}/database.dump"
    echo -e "  ${GREEN}✅ Database restored${NC}"
else
    echo -e "  ${RED}❌ database.dump not found in backup${NC}"
    exit 1
fi

# 4. Restore MinIO
echo -e "${BLUE}[4/5] Restoring MinIO storage...${NC}"
if [ -f "${TEMP_DIR}/${BACKUP_NAME}/minio-data.tar.gz" ] && [ -s "${TEMP_DIR}/${BACKUP_NAME}/minio-data.tar.gz" ]; then
    $DC_CMD exec -T minio \
        tar xzf - -C / \
        < "${TEMP_DIR}/${BACKUP_NAME}/minio-data.tar.gz"
    echo -e "  ${GREEN}✅ MinIO data restored${NC}"
else
    echo "  ℹ️  No MinIO data to restore (empty backup)"
fi

# 5. Restart all services
echo -e "${BLUE}[5/5] Restarting Plane...${NC}"
$DC_CMD up -d
sleep 15

# Verify
echo ""
echo "Verifying services..."
ALL_OK=true
for svc in $($DC_CMD ps --services); do
    status=$($DC_CMD ps --format "{{.Status}}" ${svc} 2>/dev/null | head -1)
    if echo "$status" | grep -qi "running\|up"; then
        echo -e "  ${GREEN}✅ ${svc}${NC}"
    else
        echo -e "  ${RED}❌ ${svc}: ${status}${NC}"
        ALL_OK=false
    fi
done

echo ""
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}=== Restore Complete ===${NC}"
    echo "Please verify:"
    echo "  1. Open http://<server-ip> in browser"
    echo "  2. Login with existing credentials"
    echo "  3. Check issues, projects, and file attachments"
else
    echo -e "${RED}Some services failed. Check: $DC_CMD logs -f${NC}"
    exit 1
fi
