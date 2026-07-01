#!/bin/bash
# ============================================================
# Backup Cron Job Setup Helper
# Sets up a daily cron job at 2:00 AM to run backup.sh
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup.sh"
PLANE_APP_DIR="${PROJECT_DIR}/plane-app"
BACKUP_OUT_DIR="${PROJECT_DIR}/backup"

echo -e "${BLUE}=== Configuring Backup Cron Job ===${NC}"

# Check if backup script is executable
chmod +x "${BACKUP_SCRIPT}"

# Define the cron expression
# Daily backup at 2:00 AM, with absolute environment paths
CRON_JOB="0 2 * * * BACKUP_DIR=\"${BACKUP_OUT_DIR}\" PLANE_INSTALL_DIR=\"${PLANE_APP_DIR}\" bash \"${BACKUP_SCRIPT}\" >/dev/null 2>&1"

# Temporary file for crontab
TMP_CRON=$(mktemp)
trap "rm -f ${TMP_CRON}" EXIT

# Read existing crontab
crontab -l > "${TMP_CRON}" 2>/dev/null || true

# Check if cron job already exists
if grep -Fq "${BACKUP_SCRIPT}" "${TMP_CRON}"; then
    echo -e "  ⚠️  Cron job for backup.sh already exists. Updating entry..."
    # Remove existing entry to avoid duplicates
    sed -i "\|${BACKUP_SCRIPT}|d" "${TMP_CRON}"
fi

# Append new job
echo "${CRON_JOB}" >> "${TMP_CRON}"

# Apply crontab
if crontab "${TMP_CRON}"; then
    echo -e "  ${GREEN}✅ Success! Backup cron job added successfully.${NC}"
    echo "  New crontab entry:"
    echo -e "  ${BLUE}${CRON_JOB}${NC}"
    echo ""
    echo "  The backup will run automatically every day at 2:00 AM."
    echo "  Backups will be saved to: ${BACKUP_OUT_DIR}/daily/"
else
    echo -e "  ${RED}❌ Failed to apply crontab settings.${NC}"
    exit 1
fi
