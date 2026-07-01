# 07 — Monitoring & Alerting

## Mục tiêu

Giám sát health, performance, resource usage của Plane deployment. Alert khi có vấn đề.

---

## 1. Health Check Script

File: `scripts/health-check.sh`

```bash
#!/bin/bash
# Plane Health Check Script
# Usage: ./scripts/health-check.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PLANE_URL="${PLANE_URL:-http://localhost}"
ERRORS=0

check() {
    local name="$1"
    local result="$2"
    if [ "$result" = "PASS" ]; then
        echo -e "  ${GREEN}✅ PASS${NC} — $name"
    elif [ "$result" = "WARN" ]; then
        echo -e "  ${YELLOW}⚠️  WARN${NC} — $name"
    else
        echo -e "  ${RED}❌ FAIL${NC} — $name"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "=== Plane Health Check ==="
echo "URL: ${PLANE_URL}"
echo "Time: $(date)"
echo ""

# 1. Container status
echo "[Containers]"
for svc in web api worker beat postgres redis minio proxy; do
    status=$(docker compose ps --format "{{.Status}}" ${svc} 2>/dev/null | head -1)
    if echo "$status" | grep -qi "running\|up"; then
        check "Container: ${svc}" "PASS"
    else
        check "Container: ${svc} (${status})" "FAIL"
    fi
done
echo ""

# 2. API Health
echo "[API]"
http_code=$(curl -s -o /dev/null -w "%{http_code}" "${PLANE_URL}/api/health/" 2>/dev/null || echo "000")
if [ "$http_code" = "200" ]; then
    check "API health endpoint" "PASS"
else
    check "API health endpoint (HTTP ${http_code})" "FAIL"
fi

response_time=$(curl -s -o /dev/null -w "%{time_total}" "${PLANE_URL}" 2>/dev/null || echo "999")
if (( $(echo "$response_time < 3" | bc -l) )); then
    check "Response time: ${response_time}s" "PASS"
elif (( $(echo "$response_time < 5" | bc -l) )); then
    check "Response time: ${response_time}s (slow)" "WARN"
else
    check "Response time: ${response_time}s (too slow)" "FAIL"
fi
echo ""

# 3. Resources
echo "[Resources]"
cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" 2>/dev/null | sed 's/%//g' | awk '{sum+=$1} END {printf "%.1f", sum}')
check "Total CPU usage: ${cpu_usage}%" "$([ $(echo "$cpu_usage < 80" | bc -l) -eq 1 ] && echo PASS || echo WARN)"

mem_usage=$(free | awk '/Mem:/ {printf "%.1f", $3/$2*100}')
check "System memory usage: ${mem_usage}%" "$([ $(echo "$mem_usage < 85" | bc -l) -eq 1 ] && echo PASS || echo WARN)"

disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
check "Disk usage: ${disk_usage}%" "$([ "$disk_usage" -lt 90 ] && echo PASS || echo FAIL)"
echo ""

# 4. Database
echo "[Database]"
db_conn=$(docker compose exec -T postgres psql -U plane -d plane -c "SELECT 1;" 2>/dev/null)
if echo "$db_conn" | grep -q "1"; then
    check "PostgreSQL connection" "PASS"
else
    check "PostgreSQL connection" "FAIL"
fi
echo ""

# Summary
echo "==========================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "${RED}${ERRORS} check(s) failed!${NC}"
    exit 1
fi
```

---

## 2. Prometheus Configuration

File: `monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert-rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  # Node metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Docker/container metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # PostgreSQL metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis metrics
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx metrics
  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Alert Rules

File: `monitoring/alert-rules.yml`

```yaml
groups:
  - name: plane-alerts
    rules:
      - alert: HighCPU
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage ({{ $value }}%)"

      - alert: HighMemory
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage ({{ $value }}%)"

      - alert: DiskAlmostFull
        expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk almost full ({{ $value }}%)"

      - alert: ContainerRestarting
        expr: increase(container_restart_count[15m]) > 3
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.name }} restarting frequently"

      - alert: APISlowResponse
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API p95 latency > 5s"

      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"

      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"
```

---

## 3. Grafana Dashboard

File: `monitoring/grafana/dashboards/plane-overview.json`

Dashboard bao gồm:
- CPU, RAM, Disk usage (host level)
- Container status (up/down)
- API response time (p50, p95, p99)
- Request rate (req/s)
- Error rate (%)
- PostgreSQL connections, query time
- Redis memory, hit rate

> **Note:** Import dashboard JSON vào Grafana UI hoặc provision tự động qua config.

---

## 4. Uptime Monitoring

### Cron-based (đơn giản)

```bash
# Crontab: check mỗi 5 phút
*/5 * * * * /opt/plane-deploy/scripts/health-check.sh >> /var/log/plane-health.log 2>&1
```

### Script gửi alert (nếu fail)

```bash
# Thêm vào cuối health-check.sh
if [ $ERRORS -gt 0 ]; then
    # Option 1: Gửi email
    echo "Plane health check failed: ${ERRORS} errors" | mail -s "alert: plane-down" admin@sentinel.internal

    # Option 2: Webhook (nếu có chat tool)
    # curl -X POST -H "Content-Type: application/json" \
    #   -d '{"text":"🔴 Plane health check FAILED!"}' \
    #   https://chat.sentinel.internal/webhook/xxx
fi
```

---

## 5. Log Monitoring

### View logs real-time

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api --tail 100

# Filter errors
docker compose logs api 2>&1 | grep -i "error\|exception\|critical"
```

### Centralized Logging (optional)

Nếu phòng có ELK/Loki stack:

```yaml
# docker-compose.prod.yml - gửi logs tới Loki
services:
  api:
    logging:
      driver: loki
      options:
        loki-url: "http://loki:3100/loki/api/v1/push"
        loki-batch-size: "400"
```
