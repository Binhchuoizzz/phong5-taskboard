# 03 — Configuration (Cấu hình Workspace, Projects, Workflow)

## Mục tiêu

Thiết lập cấu trúc tổ chức trong Plane: workspace, 7 projects, workflow states, labels, RBAC.

---

## 1. Workspace Setup

### Tạo Workspace

- **Name:** `Sentinel-ANTT`
- **Slug:** `sentinel`
- **Logo:** Upload logo phòng 5 (nếu có)
- **Timezone:** `Asia/Ho_Chi_Minh` (UTC+7)

### Workspace Settings

- **Sign-up mode:** Invite only (disable public registration)
- **Default role:** Member

---

## 2. Tạo 7 Projects

Mỗi tổ = 1 project. Cấu hình chi tiết:

### Project 1: `PRJ1-Core`

| Field | Value |
|---|---|
| Name | Tổ 1 — Tham mưu Tổng hợp |
| Identifier | TO1 |
| Description | Kế hoạch, báo cáo tổng hợp, điều phối công việc liên tổ |
| Network | Secret (chỉ members thấy) |
| Lead | (Trưởng Tổ 1) |
| Default Assignee | (Trưởng Tổ 1) |

### Project 2: `PRJ2-Security`

| Field | Value |
|---|---|
| Name | Tổ 2 — GRC & Chính sách |
| Identifier | TO2 |
| Description | Governance, Risk, Compliance. Quản lý chính sách ANTT, đánh giá rủi ro |
| Network | Secret |
| Lead | (Trưởng Tổ 2) |

### Project 3: `PRJ3-DevOps`

| Field | Value |
|---|---|
| Name | Tổ 3 — An ninh Vật lý |
| Identifier | TO3 |
| Description | Giám sát camera, access control, tuần tra, an ninh cơ sở vật chất |
| Network | Secret |
| Lead | (Trưởng Tổ 3) |

### Project 4: `PRJ4-QA`

| Field | Value |
|---|---|
| Name | Tổ 4 — Kiểm thử |
| Identifier | TO4 |
| Description | Penetration testing, red team operations, vulnerability assessment |
| Network | Confidential (highly restricted) |
| Lead | (Trưởng Tổ 4) |

### Project 5: `PRJ5-Integrations`

| Field | Value |
|---|---|
| Name | Tổ 5 — Tích hợp & Triển khai |
| Identifier | TO5 |
| Description | Tích hợp công nghệ mới, triển khai hệ thống, system integration |
| Network | Secret |
| Lead | (Trưởng Tổ 5) |

### Project 6: `PRJ6-Analytics`

| Field | Value |
|---|---|
| Name | Tổ 6 — SOC (Security Operations Center) |
| Identifier | TO6 |
| Description | Giám sát an ninh 24/7, incident response, SIEM operations |
| Network | Confidential |
| Lead | (Trưởng Tổ 6) |

### Project 7: `PRJ7-AI`

| Field | Value |
|---|---|
| Name | Tổ 7 — AI & Automation |
| Identifier | TO7 |
| Description | Nghiên cứu AI, ML models cho security, AI-powered automation |
| Network | Secret |
| Lead | (Trưởng Tổ 7) |

---

## 3. Workflow States

### Workflow chung (áp dụng cho TO1, TO2, TO3, TO5, TO7)

| State | Category | Color | Mô tả |
|---|---|---|---|
| Backlog | Backlog | Gray #94a3b8 | Chưa lên kế hoạch |
| Todo | Unstarted | Blue #3b82f6 | Đã lên kế hoạch, chờ bắt đầu |
| In Progress | Started | Yellow #eab308 | Đang thực hiện |
| In Review | Started | Purple #a855f7 | Đang được review |
| Testing | Started | Orange #f97316 | Đang test/kiểm tra |
| Done | Completed | Green #22c55e | Hoàn thành |
| Cancelled | Cancelled | Red #ef4444 | Hủy bỏ |

### Workflow SOC — Incident Response (PRJ6-Analytics)

| State | Category | Color | Mô tả |
|---|---|---|---|
| Detected | Backlog | Red #ef4444 | Phát hiện sự cố/mối đe dọa |
| Triaging | Unstarted | Orange #f97316 | Đánh giá mức độ nghiêm trọng |
| Investigating | Started | Yellow #eab308 | Điều tra nguyên nhân, phạm vi |
| Containment | Started | Blue #3b82f6 | Ngăn chặn lây lan |
| Eradication | Started | Purple #a855f7 | Loại bỏ mối đe dọa |
| Recovery | Started | Teal #14b8a6 | Khôi phục hệ thống |
| Post-Mortem | Started | Indigo #6366f1 | Phân tích sau sự cố |
| Closed | Completed | Green #22c55e | Đóng case |

### Workflow Pentest (PRJ4-QA)

| State | Category | Color | Mô tả |
|---|---|---|---|
| Scoping | Unstarted | Blue #3b82f6 | Xác định phạm vi kiểm thử |
| Reconnaissance | Started | Yellow #eab308 | Thu thập thông tin |
| Exploitation | Started | Red #ef4444 | Khai thác lỗ hổng |
| Reporting | Started | Purple #a855f7 | Viết báo cáo |
| Remediation Verify | Started | Orange #f97316 | Kiểm tra sau khi vá |
| Closed | Completed | Green #22c55e | Hoàn tất |
| On Hold | Cancelled | Gray #94a3b8 | Tạm dừng |

---

## 4. Labels

Tạo các labels sau ở workspace level (áp dụng cho tất cả projects):

### Priority Labels

| Label | Color | Mô tả |
|---|---|---|
| `P0-Critical` | #dc2626 (đỏ đậm) | Sự cố nghiêm trọng, cần xử lý ngay |
| `P1-High` | #ea580c (cam) | Ưu tiên cao, cần xử lý trong ngày |
| `P2-Medium` | #ca8a04 (vàng) | Ưu tiên trung bình, trong tuần |
| `P3-Low` | #16a34a (xanh lá) | Ưu tiên thấp, khi có thời gian |

### Type Labels

| Label | Color | Mô tả |
|---|---|---|
| `Bug` | #dc2626 | Lỗi cần sửa |
| `Feature` | #2563eb | Tính năng mới |
| `Incident` | #9333ea | Sự cố an ninh |
| `Audit` | #0891b2 | Đánh giá/kiểm toán |
| `Compliance` | #4f46e5 | Tuân thủ chính sách |
| `Research` | #7c3aed | Nghiên cứu |
| `Deployment` | #059669 | Triển khai |
| `Task` | #6b7280 | Công việc thường ngày |

### Security Classification Labels

| Label | Color | Mô tả |
|---|---|---|
| `Confidential` | #dc2626 (đỏ) | Tối mật — chỉ người được ủy quyền |
| `Internal` | #ea580c (cam) | Nội bộ — nhân viên phòng |
| `Public` | #16a34a (xanh lá) | Công khai |

### Scope Labels

| Label | Color | Mô tả |
|---|---|---|
| `Cross-team` | #8b5cf6 | Liên quan nhiều tổ |
| `Urgent-Report` | #dc2626 | Cần báo cáo lãnh đạo ngay |

---

## 5. RBAC Configuration

### Workspace Roles

| Role | Quyền | Áp dụng cho |
|---|---|---|
| **Owner** | Full control workspace | Trưởng phòng |
| **Admin** | Manage projects, members, settings | Phó phòng, IT admin |
| **Member** | Access assigned projects, create/edit issues | Nhân viên |
| **Guest** | View only trong projects được mời | Lãnh đạo cấp trên |

### Project-level Permissions

| Action | Admin | Member | Guest |
|---|---|---|---|
| Tạo issue | ✅ | ✅ | ❌ |
| Edit issue | ✅ | ✅ (own + assigned) | ❌ |
| Delete issue | ✅ | ❌ | ❌ |
| Manage members | ✅ | ❌ | ❌ |
| View issues | ✅ | ✅ | ✅ |
| Manage settings | ✅ | ❌ | ❌ |

### Assignment Strategy

- Mỗi nhân viên chỉ được thêm vào project **tổ mình**
- Trưởng tổ = Project Admin
- Cross-team tasks: tạo issue trong project tổ chủ trì, tag members tổ liên quan

---

## 6. Modules (Epics) — Gợi ý

Mỗi project nên có các Modules mặc định:

| Module | Áp dụng | Mô tả |
|---|---|---|
| `Q3-2026` | Tất cả | Công việc quý 3/2026 |
| `Q4-2026` | Tất cả | Công việc quý 4/2026 |
| `Dự án X` | Theo tổ | Dự án/campaign cụ thể |
| `Incident-YYYY-MM` | PRJ6-Analytics | Group incidents theo tháng |

---

## 7. Cycles (Sprints) — Gợi ý

Sprint 2 tuần:

| Cycle | Start | End |
|---|---|---|
| Sprint 2026-W27 | 30/06/2026 | 13/07/2026 |
| Sprint 2026-W29 | 14/07/2026 | 27/07/2026 |
| ... | ... | ... |
