#!/bin/bash
# ============================================================
# Plane Health Check Script
# Checks all services, resources, and connectivity
# Usage: ./scripts/health-check.sh
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PLANE_URL="${PLANE_URL:-http://localhost}"
PLANE_DIR="${PLANE_INSTALL_DIR:-/opt/plane}"
ERRORS=0
WARNINGS=0

# Load environment variables
if [ -f "${PLANE_DIR}/plane.env" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ ! "$line" =~ ^\s*# ]] && [[ "$line" =~ = ]]; then
            export "$line"
        fi
    done < "${PLANE_DIR}/plane.env"
elif [ -f "${PLANE_DIR}/.env" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        if [[ ! "$line" =~ ^\s*# ]] && [[ "$line" =~ = ]]; then
            export "$line"
        fi
    done < "${PLANE_DIR}/.env"
fi

if docker compose version &>/dev/null; then
    DC_CMD="docker compose"
else
    DC_CMD="docker-compose"
fi

check_pass() {
    echo -e "  ${GREEN}✅ PASS${NC} — $1"
}

check_fail() {
    echo -e "  ${RED}❌ FAIL${NC} — $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    echo -e "  ${YELLOW}⚠️  WARN${NC} — $1"
    WARNINGS=$((WARNINGS + 1))
}

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Plane Health Check                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo "URL:  ${PLANE_URL}"
echo "Time: $(date)"
echo ""

# ============================================================
echo -e "${BLUE}[Containers]${NC}"
# ============================================================
cd "${PLANE_DIR}" 2>/dev/null || true

for svc in $($DC_CMD ps --services 2>/dev/null); do
    status=$($DC_CMD ps --format "{{.Status}}" ${svc} 2>/dev/null | head -1)
    if echo "$status" | grep -qi "running\|up"; then
        check_pass "Container: ${svc}"
    else
        check_fail "Container: ${svc} — ${status:-not found}"
    fi
done
echo ""

# ============================================================
echo -e "${BLUE}[API]${NC}"
# ============================================================
http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${PLANE_URL}" 2>/dev/null || echo "000")
if [ "$http_code" = "200" ] || [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
    check_pass "Web UI accessible (HTTP ${http_code})"
else
    check_fail "Web UI not accessible (HTTP ${http_code})"
fi

api_code=$($DC_CMD exec -T api python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/').getcode())" 2>/dev/null || echo "000")
if [ "$api_code" = "200" ]; then
    check_pass "API health endpoint (internal)"
else
    check_fail "API health endpoint (internal, HTTP ${api_code})"
fi

response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "${PLANE_URL}" 2>/dev/null || echo "999")
if command -v bc &>/dev/null; then
    if (( $(echo "$response_time < 3" | bc -l) )); then
        check_pass "Response time: ${response_time}s"
    elif (( $(echo "$response_time < 5" | bc -l) )); then
        check_warn "Response time: ${response_time}s (slow)"
    else
        check_fail "Response time: ${response_time}s (too slow, > 5s)"
    fi
else
    echo "  ℹ️  Response time: ${response_time}s (install bc for threshold check)"
fi
echo ""

# ============================================================
echo -e "${BLUE}[Resources]${NC}"
# ============================================================

# CPU
cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d. -f1 2>/dev/null || echo "0")
cpu_used=$((100 - cpu_idle))
if [ "$cpu_used" -lt 80 ]; then
    check_pass "CPU usage: ${cpu_used}%"
elif [ "$cpu_used" -lt 90 ]; then
    check_warn "CPU usage: ${cpu_used}% (high)"
else
    check_fail "CPU usage: ${cpu_used}% (critical)"
fi

# RAM
mem_usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
if [ "$mem_usage" -lt 85 ]; then
    check_pass "Memory usage: ${mem_usage}%"
elif [ "$mem_usage" -lt 95 ]; then
    check_warn "Memory usage: ${mem_usage}% (high)"
else
    check_fail "Memory usage: ${mem_usage}% (critical)"
fi

# Disk
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    check_pass "Disk usage: ${disk_usage}%"
elif [ "$disk_usage" -lt 90 ]; then
    check_warn "Disk usage: ${disk_usage}% (high)"
else
    check_fail "Disk usage: ${disk_usage}% (critical)"
fi
echo ""

# ============================================================
echo -e "${BLUE}[Database]${NC}"
# ============================================================

db_check=$($DC_CMD exec -e PGPASSWORD="${POSTGRES_PASSWORD:-}" -T plane-db psql -U plane -d plane -c "SELECT COUNT(*) FROM information_schema.tables;" 2>/dev/null || echo "FAIL")
if echo "$db_check" | grep -q "[0-9]"; then
    check_pass "PostgreSQL connection OK"
else
    check_fail "PostgreSQL connection failed"
fi

# Redis
redis_check=$($DC_CMD exec -T plane-redis redis-cli ping 2>/dev/null || echo "FAIL")
if echo "$redis_check" | grep -qi "PONG"; then
    check_pass "Redis connection OK"
else
    check_fail "Redis connection failed"
fi
echo ""

# ============================================================
# Summary
# ============================================================
echo -e "${BLUE}══════════════════════════════════════════════${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "  ${GREEN}All checks passed! Plane is healthy.${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "  ${YELLOW}${WARNINGS} warning(s), but no critical issues.${NC}"
else
    echo -e "  ${RED}${ERRORS} FAILED check(s), ${WARNINGS} warning(s).${NC}"
    echo "  Check logs: $DC_CMD logs -f"
fi
echo -e "${BLUE}══════════════════════════════════════════════${NC}"

exit $ERRORS
