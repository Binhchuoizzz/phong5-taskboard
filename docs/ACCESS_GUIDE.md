# ACCESS GUIDE — Sentinel Taskboard (Internal LAN)

The **Sentinel Taskboard** has been deployed with a fully decoupled architecture (Frontend, Backend, Database, Monitoring) and hardened for security. This guide provides access details for team members on the local LAN.

---

## 1. Service Access URLs (LAN)

| Component | URL (Enter in browser) | Notes |
| :--- | :--- | :--- |
| 🌐 **Web Application** | **`http://<server-ip>`** | Main workspace interface |
| ⚙️ **System Admin Panel (God Mode)** | **`http://<server-ip>/god-mode/`** | Restricted to LAN private IP ranges only |
| 📊 **Monitoring Dashboard (Grafana)** | **`http://<server-ip>:3001`** | Default credentials: `admin` / `admin` |
| 🚨 **Prometheus Alerting** | **`http://<server-ip>:9090`** | Monitor resource state and automatic alerts |

> Replace `<server-ip>` with the actual server LAN IP address (e.g., `192.168.0.x`) or Tailscale IP.

---

## 2. Test Account Credentials (RBAC Demo)

The system is pre-seeded with test accounts covering different permission levels for RBAC validation:

### 🔑 Account 1: Workspace Owner (Full Admin)
*   **Email:** `admin@sentinel.local`
*   **Password:** `Sentinel@123`
*   **Permissions:** Full workspace management — configure states, labels, create projects, manage members.

### 🔑 Account 2: Project Member (Threat Analytics)
*   **Email:** `member1@sentinel.local`
*   **Password:** `Sentinel@123`
*   **Permissions:** Can create and update Tasks within `PRJ6-Analytics`. Cannot access other projects.

### 🔑 Account 3: Guest / Viewer (Core Platform)
*   **Email:** `guest1@sentinel.local`
*   **Password:** `Sentinel@123`
*   **Permissions:** Read-only access to view progress in `PRJ1-Core`. Cannot create or edit data.

---

## 3. Password Input Notes (IME / Input Method)

If your operating system keyboard input method (e.g., Vietnamese IME) is active, special characters in the password may be transformed unexpectedly.

> [!TIP]
> **Recommended:**
> *   Switch your keyboard input to English (`ENG`) before typing the password.
> *   Or **Copy** the password from above and **Paste** it directly into the login field.
