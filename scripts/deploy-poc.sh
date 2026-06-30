#!/bin/bash
# ============================================================
# Plane PoC Deploy Script
# Deploys Plane Community Edition using Docker Compose
# ============================================================

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PLANE_DIR="${PLANE_INSTALL_DIR:-/opt/plane}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if docker compose version &>/dev/null; then
    DC_CMD="docker compose"
else
    DC_CMD="docker-compose"
fi

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Plane PoC Deployment Script             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"
if ! bash "${SCRIPT_DIR}/check-prerequisites.sh"; then
    echo -e "${RED}Prerequisites check failed. Fix issues above first.${NC}"
    exit 1
fi
echo ""

# Step 2: Configure Environment
echo -e "${BLUE}[2/6] Configuring Environment variables...${NC}"
PLANE_APP_DIR="${PROJECT_DIR}/plane-app"
mkdir -p "${PLANE_APP_DIR}"

if [ ! -f "${PROJECT_DIR}/env/.env.local" ]; then
    echo -e "${YELLOW}  Creating fresh env/.env.local from template...${NC}"
    cp "${PROJECT_DIR}/env/.env.example" "${PROJECT_DIR}/env/.env.local"
    python3 -c "
import secrets
local_env = '${PROJECT_DIR}/env/.env.local'
with open(local_env, 'r') as f:
    content = f.read()
content = content.replace('CHANGE_ME_USE_STRONG_PASSWORD', secrets.token_urlsafe(24))
content = content.replace('CHANGE_ME_64_CHARS_RANDOM_STRING', secrets.token_hex(32))
with open(local_env, 'w') as f:
    f.write(content)
"
fi

# Run helper to generate plane-app/plane.env with URLs
python3 "${PROJECT_DIR}/scripts/setup-plane-app-env.py"
echo -e "${GREEN}  ✅ plane-app/plane.env updated.${NC}"
echo ""

# Step 3: Setup Shared Docker Network
echo -e "${BLUE}[3/6] Configuring Shared External Network...${NC}"
docker network create plane-network 2>/dev/null || true
echo -e "${GREEN}  ✅ External Network 'plane-network' ready.${NC}"
echo ""

# Step 4: Pull Docker Images
echo -e "${BLUE}[4/6] Pulling images for all decoupled stacks...${NC}"
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.db.yaml" --env-file "${PLANE_APP_DIR}/plane.env" pull -q
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.app.yaml" --env-file "${PLANE_APP_DIR}/plane.env" pull -q
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.proxy.yaml" --env-file "${PLANE_APP_DIR}/plane.env" pull -q
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.monitor.yaml" --env-file "${PLANE_APP_DIR}/plane.env" pull -q
echo -e "${GREEN}  ✅ All images pulled.${NC}"
echo ""

# Step 5: Start Decoupled Stacks Sequentially
echo -e "${BLUE}[5/6] Starting decoupled service stacks...${NC}"

# A. Start Backing Database Tier
echo -e "  Starting Database Stack..."
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.db.yaml" --env-file "${PLANE_APP_DIR}/plane.env" up -d
echo "  Waiting 15 seconds for Database Services (Postgres, Redis, MQ) to be ready..."
sleep 15

# B. Run Data Migration
echo -e "  Running Database Migrations..."
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.app.yaml" --env-file "${PLANE_APP_DIR}/plane.env" run --rm migrator
echo -e "${GREEN}  ✅ Migrations complete.${NC}"

# C. Start Application Stack
echo -e "  Starting Core Application Stack..."
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.app.yaml" --env-file "${PLANE_APP_DIR}/plane.env" up -d
echo "  Waiting 10 seconds for Application API to boot..."
sleep 10

# D. Start Proxy and Monitor Stack
echo -e "  Starting Reverse Proxy & Monitoring Stacks..."
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.proxy.yaml" --env-file "${PLANE_APP_DIR}/plane.env" up -d
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.monitor.yaml" --env-file "${PLANE_APP_DIR}/plane.env" up -d
echo ""

# Step 6: Seeding & Verification
echo -e "${BLUE}[6/6] Seeding Workspace & Verifying Health...${NC}"
echo ""

# Database seeding
echo "  Running initialize-plane-data.py seeding script..."
$DC_CMD -f "${PLANE_APP_DIR}/docker-compose.app.yaml" --env-file "${PLANE_APP_DIR}/plane.env" exec -T api python manage.py shell < "${PROJECT_DIR}/scripts/initialize-plane-data.py"
echo ""

# Run health checks
echo "  Running health-check.sh..."
PLANE_INSTALL_DIR="${PLANE_APP_DIR}" bash "${PROJECT_DIR}/scripts/health-check.sh"
HEALTH_CHECK_STATUS=$?

echo ""
if [ $HEALTH_CHECK_STATUS -eq 0 ]; then
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Decoupled Plane deployed successfully!    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  🌐 Web Access (Port 80):    ${BLUE}http://${SERVER_IP}${NC}"
    echo -e "  📊 Monitoring (Grafana):   ${BLUE}http://${SERVER_IP}:3001${NC}"
    echo ""
    echo "  Login Credentials (God Mode Admin):"
    echo "  - Email:    admin@sentinel.local"
    echo "  - Password: Sentinel@123"
    echo ""
else
    echo -e "${RED}Health check failed. Check docker container logs for errors.${NC}"
    exit 1
fi
