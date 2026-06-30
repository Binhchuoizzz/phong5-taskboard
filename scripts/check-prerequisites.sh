#!/bin/bash
# ============================================================
# Plane Prerequisites Check Script
# Checks all requirements before deploying Plane
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

check_pass() {
    echo -e "  ${GREEN}✅ PASS${NC} — $1"
    PASS=$((PASS + 1))
}

check_fail() {
    echo -e "  ${RED}❌ FAIL${NC} — $1"
    FAIL=$((FAIL + 1))
}

check_warn() {
    echo -e "  ${YELLOW}⚠️  WARN${NC} — $1"
    WARN=$((WARN + 1))
}

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Plane Self-Hosted — Prerequisites Check   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo "Time: $(date)"

# ============================================================
header "1. Operating System"
# ============================================================

OS=$(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown")
echo "  OS: ${OS}"

if echo "$OS" | grep -qi "ubuntu"; then
    check_pass "Ubuntu detected"
elif echo "$OS" | grep -qi "debian\|centos\|rhel"; then
    check_warn "Non-Ubuntu Linux (should work but Ubuntu recommended)"
else
    check_fail "Unsupported OS: ${OS}"
fi

# ============================================================
header "2. Docker"
# ============================================================

if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+' | head -1)
    DOCKER_MAJOR=$(echo "$DOCKER_VERSION" | cut -d. -f1)
    if [ "$DOCKER_MAJOR" -ge 24 ]; then
        check_pass "Docker ${DOCKER_VERSION} (>= 24.0)"
    else
        check_fail "Docker ${DOCKER_VERSION} (need >= 24.0)"
    fi
else
    check_fail "Docker not installed"
fi

if docker compose version &>/dev/null; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || docker compose version | grep -oP '\d+\.\d+' | head -1)
    check_pass "Docker Compose ${COMPOSE_VERSION}"
else
    check_fail "Docker Compose not installed (need v2 plugin)"
fi

# Check docker daemon running
if docker info &>/dev/null; then
    check_pass "Docker daemon running"
else
    check_fail "Docker daemon not running"
fi

# Check current user in docker group
if groups | grep -q docker; then
    check_pass "Current user in docker group"
else
    check_warn "Current user NOT in docker group (need sudo for docker)"
fi

# ============================================================
header "3. Git"
# ============================================================

if command -v git &>/dev/null; then
    GIT_VERSION=$(git --version | grep -oP '\d+\.\d+' | head -1)
    check_pass "Git ${GIT_VERSION}"
else
    check_fail "Git not installed"
fi

# ============================================================
header "4. Hardware Resources"
# ============================================================

# CPU
CPU_COUNT=$(nproc)
if [ "$CPU_COUNT" -ge 4 ]; then
    check_pass "CPU: ${CPU_COUNT} cores (recommended: 4+)"
elif [ "$CPU_COUNT" -ge 2 ]; then
    check_warn "CPU: ${CPU_COUNT} cores (minimum met, recommended: 4+)"
else
    check_fail "CPU: ${CPU_COUNT} cores (need >= 2)"
fi

# RAM
TOTAL_RAM_MB=$(free -m | awk '/Mem:/ {print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_MB / 1024))
if [ "$TOTAL_RAM_MB" -ge 8000 ]; then
    check_pass "RAM: ${TOTAL_RAM_GB} GB (recommended: 8+ GB)"
elif [ "$TOTAL_RAM_MB" -ge 4000 ]; then
    check_warn "RAM: ${TOTAL_RAM_GB} GB (minimum met, recommended: 8+ GB)"
else
    check_fail "RAM: ${TOTAL_RAM_GB} GB (need >= 4 GB)"
fi

# Disk
DISK_AVAIL_GB=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
if [ "$DISK_AVAIL_GB" -ge 50 ]; then
    check_pass "Disk: ${DISK_AVAIL_GB} GB available (recommended: 50+ GB)"
elif [ "$DISK_AVAIL_GB" -ge 30 ]; then
    check_warn "Disk: ${DISK_AVAIL_GB} GB available (minimum met, recommended: 50+ GB)"
else
    check_fail "Disk: ${DISK_AVAIL_GB} GB available (need >= 30 GB)"
fi

# ============================================================
header "5. Network"
# ============================================================

# Port 80
if ! ss -tlnp | grep -q ':80 '; then
    check_pass "Port 80 available"
else
    check_warn "Port 80 in use (will need to change Plane port)"
fi

# Port 443
if ! ss -tlnp | grep -q ':443 '; then
    check_pass "Port 443 available"
else
    check_warn "Port 443 in use"
fi

# ============================================================
header "6. Utilities"
# ============================================================

for cmd in curl wget bc; do
    if command -v $cmd &>/dev/null; then
        check_pass "${cmd} installed"
    else
        check_warn "${cmd} not installed (recommended)"
    fi
done

# ============================================================
# Summary
# ============================================================
echo ""
echo -e "${BLUE}══════════════════════════════════════════════${NC}"
echo -e "  Results: ${GREEN}${PASS} PASS${NC}  ${YELLOW}${WARN} WARN${NC}  ${RED}${FAIL} FAIL${NC}"
echo -e "${BLUE}══════════════════════════════════════════════${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "  ${GREEN}✅ Ready to deploy Plane!${NC}"
    echo ""
    echo "  Next step: Copy and edit environment file"
    echo "    cp env/.env.example env/.env.local"
    echo ""
    exit 0
else
    echo -e "  ${RED}❌ Fix ${FAIL} failure(s) before deploying.${NC}"
    echo ""
    exit 1
fi
