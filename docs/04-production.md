# 04 — Production Deployment (Kubernetes Scale cho 5K Users)

## Mục tiêu

Migrate từ Docker Compose (PoC) sang Kubernetes cluster cho production 5K users. High availability, auto-scaling, zero downtime.

> [!WARNING]
> **Chỉ thực hiện sau khi PoC đã chạy ổn định 2-4 tuần.**
> Cần có Kubernetes cluster sẵn sàng trước khi bắt đầu.

---

## 1. Infrastructure Requirements

### Cluster Sizing cho 5K Users

| Component | Specs/Node | Replicas | Tổng |
|---|---|---|---|
| K8s Master | 4 vCPU, 8 GB RAM | 3 (HA) | 12 vCPU, 24 GB |
| K8s Worker | 8 vCPU, 16 GB RAM, 100 GB SSD | 3+ | 24+ vCPU, 48+ GB |
| PostgreSQL | 8 vCPU, 32 GB RAM, 500 GB SSD | 1P + 1R | 16 vCPU, 64 GB |
| Redis | 4 vCPU, 8 GB RAM | 3 (sentinel) | 12 vCPU, 24 GB |
| MinIO | 4 vCPU, 8 GB RAM, 1 TB SSD | 4 nodes | 16 vCPU, 32 GB |

**Tổng ước tính:** ~80 vCPU, ~192 GB RAM, ~5 TB storage

### Network Requirements

- Internal network 1 Gbps+
- Ingress Controller (Nginx Ingress hoặc Traefik)
- Load Balancer (MetalLB cho bare-metal hoặc hardware LB)

---

## 2. Kubernetes Setup

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: plane
  labels:
    app: plane
    environment: production
```

### Apply:

```bash
kubectl apply -f k8s/namespace.yaml
```

---

## 3. PostgreSQL HA

### Option A: PostgreSQL Operator (Khuyến nghị)

Dùng CloudNativePG hoặc Zalando Postgres Operator:

```bash
# Install CloudNativePG operator
kubectl apply --server-side -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/main/releases/cnpg-1.22.0.yaml

# Deploy PostgreSQL cluster
kubectl apply -f k8s/postgres-statefulset.yaml
```

### PgBouncer

Bắt buộc cho 5K users — connection pooling:

```yaml
# Trong postgres-statefulset.yaml
pgbouncer:
  poolMode: transaction
  defaultPoolSize: 100
  maxClientConn: 1000
```

---

## 4. Redis Cluster

```bash
# Dùng Bitnami Redis Helm chart
helm install redis oci://registry-1.docker.io/bitnamicharts/redis \
  --namespace plane \
  --set architecture=replication \
  --set replica.replicaCount=2 \
  --set auth.password=<REDIS_PASSWORD>
```

---

## 5. MinIO Cluster

```bash
# Dùng MinIO Operator
kubectl apply -k "https://github.com/minio/operator/resources/?ref=v5.0.0"

# Deploy tenant
kubectl apply -f k8s/minio-tenant.yaml
```

---

## 6. Deploy Plane

### Option A: Helm Chart (nếu có official chart)

```bash
helm repo add plane https://charts.plane.so
helm install plane plane/plane \
  --namespace plane \
  --values k8s/plane-values.yaml
```

### Option B: Custom Manifests

```bash
kubectl apply -f k8s/plane-deployment.yaml
```

---

## 7. Ingress & SSL

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: plane-ingress
  namespace: plane
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/websocket-services: "plane-live"
spec:
  tls:
  - hosts:
    - plane.sentinel.internal
    secretName: plane-tls
  rules:
  - host: plane.sentinel.internal
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: plane-web
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: plane-api
            port:
              number: 8000
```

---

## 8. Migration từ PoC → Production

### Bước 1: Backup PoC data

```bash
# Trên server PoC
./scripts/backup.sh
# Output: backup-YYYY-MM-DD.tar.gz
```

### Bước 2: Restore vào K8s PostgreSQL

```bash
# Copy backup vào PostgreSQL pod
kubectl cp backup.sql plane/postgres-0:/tmp/backup.sql

# Restore
kubectl exec -it postgres-0 -n plane -- \
  psql -U plane -d plane -f /tmp/backup.sql
```

### Bước 3: Migrate MinIO data

```bash
# Dùng mc (MinIO client) để sync
mc mirror source/plane-uploads target/plane-uploads
```

### Bước 4: Update DNS/IP

Switch domain/IP từ PoC server sang K8s Ingress IP.

### Bước 5: Verify

- Tất cả data còn nguyên
- Users đăng nhập được
- Issues, projects, cycles đúng
- File attachments hiển thị

---

## 9. Scaling Policies

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: plane-api-hpa
  namespace: plane
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: plane-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Recommended Replicas cho 5K Users

| Service | Min | Max | Note |
|---|---|---|---|
| plane-web | 3 | 8 | Frontend Next.js |
| plane-api | 5 | 15 | Django API |
| plane-worker | 3 | 10 | Celery workers |
| plane-beat | 1 | 1 | Celery beat (singleton) |
| plane-live | 2 | 5 | Real-time/WebSocket |

---

## 10. Load Testing

```bash
# Dùng k6 hoặc locust
# Test 500 concurrent users
k6 run --vus 500 --duration 5m load-test.js

# Targets:
# - API p95 latency < 3s
# - Error rate < 1%
# - Throughput > 100 req/s
```
