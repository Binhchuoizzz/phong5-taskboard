# SYSTEM SECURITY ARCHITECTURE & INTERNAL COMPLIANCE (100% LOCAL)

The **Sentinel Taskboard** is designed and deployed in strict compliance with on-premises information security principles (On-Premises / Air-Gapped). This document demonstrates the system's complete isolation and its security-hardened technical architecture.

---

## 1. Commitment to Complete Isolation (100% Local / Offline)

The system ensures **no data is sent to any external internet environment** and operates in absolute independence through the following mechanisms:

1.  **On-Premises Storage:** All databases (PostgreSQL), file attachments (MinIO), cache/session (Valkey/Redis), and message queues (RabbitMQ) run as internal containers on the physical host server.
2.  **Telemetry Disabled:** Remote monitoring callbacks to Plane's upstream servers are fully disabled during system initialization (`is_telemetry_enabled = False` and via environment variable configuration).
3.  **Closed Enrollment:** Public registration has been disabled (`ENABLE_SIGNUP = 0`). Only the system administrator (Admin) can create and provision accounts directly in the database.
4.  **Docker Virtual Network Isolation:** Sensitive services such as Database, Cache, and Queue do not expose ports to the host's external interfaces. All inter-service data flows occur exclusively within the isolated internal bridge network (`plane-network`).

---

## 2. Technology Stack Map (Decoupled Architecture)

The system is designed with a clear Microservices model for scalability and resource optimization:

```mermaid
graph TD
    User([LAN Network Device]) -->|Port 80/443| Caddy[Caddy Reverse Proxy]
    
    subgraph Web & Logic Layer
        Caddy -->|Next.js Frontend| FE[plane-web / plane-space]
        Caddy -->|Django API| BE[plane-api]
        Caddy -->|Admin Console| Admin[plane-admin]
    end
    
    subgraph Storage & Queue Layer (Isolated)
        BE -->|Cache & Session| Redis[Valkey/Redis]
        BE -->|Relational Data| DB[(PostgreSQL 15.7)]
        BE -->|Task Broker| MQ[RabbitMQ Queue]
        BE -->|Async Workers| Worker[Celery Workers]
        FE & BE -->|S3 Uploads| MinIO[MinIO Storage]
    end
    
    subgraph Monitoring Layer
        Grafana[Grafana Dashboard] -->|Query| Prom[Prometheus Engine]
        Prom -->|Scrape Host| Node[Node Exporter]
        Prom -->|Scrape Containers| Cadvisor[cAdvisor]
    end
```

### Core Technologies:
*   **Reverse Proxy / Security Gateway:** Caddy Server (routing, IP filtering, security header injection).
*   **Frontend (FE):** Next.js (React) static build served via Nginx.
*   **Backend (BE) & API:** Django REST Framework (Python 3) & Celery (background task processing).
*   **Database (DB):** PostgreSQL 15.7 (ACID-compliant, hot backup support).
*   **Cache & Message Broker:** Valkey (Redis fork) for <1ms session read/write and RabbitMQ for async message passing.
*   **Object Storage (Local S3):** MinIO Server (internal file attachment storage management).

---

## 3. Active Security Measures (Security Hardening)

To protect the system against internal attack vectors (Insider Threats) and ensure information security compliance under **Zero Trust** principles:

### A. Zone-Based Access Control (IP ACL — Access Control List)
The advanced system configuration path `/god-mode` is protected by an IP filter at the Caddy Proxy layer. Only IPs within the Private LAN range (`127.0.0.1`, `192.168.0.0/16`, `172.16.0.0/12`, `10.0.0.0/8`) are permitted access. Requests from unknown sources are immediately blocked with a **403 Forbidden** error.

### B. Web UI Exploit Mitigation
The proxy automatically injects strict security headers into every browser response:
*   `X-Frame-Options: DENY` — prevents Clickjacking attacks.
*   `X-Content-Type-Options: nosniff` — prevents MIME-sniffing type confusion attacks.
*   `Content-Security-Policy (CSP)` — restricts the browser to only execute scripts and assets originating from the trusted server itself, blocking externally injected XSS payloads.

### C. Resource Exhaustion Defense (Anti-DoS & Log Rotation)
*   **Rate Limiting:** API request rate is capped at 30 requests/second per source IP to prevent brute-force attacks and automated vulnerability scanning.
*   **Log Rotation:** Each container's log is capped at 10MB and automatically rotated with a maximum of 3 files. This prevents disk-filling denial-of-service (Disk-Filling DoS) attacks on the host.

### D. Backup & Disaster Recovery
*   An automated daily backup script (`backup.sh`) is registered directly in the Host Crontab, running at 2:00 AM.
*   All PostgreSQL and MinIO backup files are compressed as `.tar.gz` tarballs and stored in a secure directory on the host server.
