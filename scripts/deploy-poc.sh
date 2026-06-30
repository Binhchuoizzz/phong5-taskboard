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

# Step 2: Clone Plane
echo -e "${BLUE}[2/6] Cloning Plane repository...${NC}"
if [ -d "${PLANE_DIR}" ] && [ "$(ls -A ${PLANE_DIR})" ]; then
    echo -e "${YELLOW}  Directory ${PLANE_DIR} already exists.${NC}"
    read -p "  Overwrite? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "${PLANE_DIR}"
    else
        echo "  Skipping clone, using existing directory."
    fi
fi

if [ ! -d "${PLANE_DIR}" ] || [ -z "$(ls -A ${PLANE_DIR} 2>/dev/null)" ]; then
    sudo mkdir -p "${PLANE_DIR}"
    sudo chown $(whoami):$(whoami) "${PLANE_DIR}"
    git clone --depth 1 -b master https://github.com/makeplane/plane.git "${PLANE_DIR}"
    echo -e "${GREEN}  ✅ Cloned to ${PLANE_DIR}${NC}"
fi
echo ""

# Step 3: Setup
echo -e "${BLUE}[3/6] Running Plane setup...${NC}"
cd "${PLANE_DIR}"

# Check if .env already exists from our template
if [ -f "${PROJECT_DIR}/env/.env.local" ]; then
    echo -e "${YELLOW}  Found custom .env.local — copying to Plane directory${NC}"
    cp "${PROJECT_DIR}/env/.env.local" "${PLANE_DIR}/.env"
else
    echo "  Running Plane's setup script..."
    ./setup.sh
fi
echo ""

# Step 4: Pull images
echo -e "${BLUE}[4/6] Pulling Docker images...${NC}"
$DC_CMD pull
echo -e "${GREEN}  ✅ Images pulled${NC}"
echo ""

# Step 5: Start services
echo -e "${BLUE}[5/6] Starting Plane services...${NC}"
$DC_CMD up -d
echo ""

# Wait for services to start
echo "  Waiting 30 seconds for services to initialize..."
sleep 30

# Step 6: Verify
echo -e "${BLUE}[6/6] Verifying deployment...${NC}"
echo ""

ALL_OK=true
for svc in $($DC_CMD ps --services); do
    status=$($DC_CMD ps --format "{{.Status}}" ${svc} 2>/dev/null | head -1)
    if echo "$status" | grep -qi "running\|up"; then
        echo -e "  ${GREEN}✅ ${svc}: running${NC}"
    else
        echo -e "  ${RED}❌ ${svc}: ${status}${NC}"
        ALL_OK=false
    fi
done

echo ""
if [ "$ALL_OK" = true ]; then
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Plane deployed successfully!          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  🌐 Access Plane: ${BLUE}http://${SERVER_IP}${NC}"
    echo ""
    echo "  Next steps:"
    echo "  1. Open the URL above in your browser"
    echo "  2. Create your admin account"
    echo "  3. Follow docs/03-configuration.md to setup workspace"
    echo ""
else
    echo -e "${RED}Some services failed to start. Check logs:${NC}"
    echo "  $DC_CMD logs -f"
    exit 1
fi
