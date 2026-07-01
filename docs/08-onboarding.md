# 08 — Onboarding Teams (Đưa vào sử dụng)

## Mục tiêu

Đưa 7 tổ (~5K users) vào sử dụng Plane một cách trơn tru. Rollout theo giai đoạn, không big-bang.

---

## 1. Rollout Strategy

```
Tuần 1: Deploy + Admin setup
Week 2: Pilot 2 teams (PRJ7 AI Engine + PRJ4 QA)
Tuần 3: Thu feedback + điều chỉnh
Tuần 4: Rollout toàn phòng (5 tổ còn lại)
Tuần 5-6: Stabilize + support
```

### Why PRJ7 and PRJ4 for pilot?

- **PRJ7 (AI Engine):** Team tech-savvy, dễ adopt tool mới, feedback chất lượng
- **PRJ4 (QA):** Quen quản lý task theo project, có workflow rõ ràng

---

## 2. Tạo Account hàng loạt

### Option A: Invite qua email (recommend)

```
God Mode → Workspace → Members → Invite
- Nhập danh sách email
- Chọn role: Member
- Assign vào project tương ứng
```

### Option B: CSV import (nếu Plane support)

Chuẩn bị file CSV:

```csv
email,name,role,project
staff.a@sentinel.internal,Nguyễn A,Member,PRJ7-AI
staff.b@sentinel.internal,Trần B,Member,PRJ4-QA
...
```

### Option C: API bulk create (scripting)

```bash
# Dùng Plane API để tự động hóa
curl -X POST https://plane.sentinel.internal/api/v1/workspaces/sentinel/members/ \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@sentinel.internal",
    "role": 15
  }'
# Role: 5=Guest, 10=Viewer, 15=Member, 20=Admin
```

---

## 3. Training Plan

### Session cho Trưởng tổ (45 phút)

| Thời gian | Nội dung |
|---|---|
| 10 phút | Overview: tại sao dùng Plane, lợi ích |
| 15 phút | Demo: tạo issue, assign, chuyển trạng thái |
| 10 phút | Sprint/Cycle management |
| 5 phút | Dashboard & Analytics |
| 5 phút | Q&A |

### Session cho nhân viên (20 phút)

| Thời gian | Nội dung |
|---|---|
| 5 phút | Đăng nhập, giao diện cơ bản |
| 10 phút | Tạo task, comment, upload file, chuyển trạng thái |
| 5 phút | Board view, filter, search |

### Tài liệu hỗ trợ (chuẩn bị sẵn)

- [ ] Quick Start Guide (1 trang A4, có hình)
- [ ] FAQ — các câu hỏi thường gặp
- [ ] Video demo 5 phút (quay screen)

---

## 4. Feedback Collection

### Pilot Feedback (cuối tuần 2)

Gửi form khảo sát ngắn:

1. **Usability (1-5):** Giao diện dễ dùng không?
2. **Performance (1-5):** Tốc độ load có nhanh không?
3. **Workflow (1-5):** Workflow states có phù hợp không?
4. **Missing features:** Cần thêm gì?
5. **Pain points:** Gặp vấn đề gì?

### Action từ feedback

| Feedback | Action | Priority |
|---|---|---|
| "Chậm" | Check server resources, optimize | P1 |
| "Thiếu state X" | Thêm custom state | P2 |
| "Khó tìm task" | Training lại filter/search | P3 |
| "Muốn notification" | Setup email notification | P2 |

---

## 5. Post-Rollout Support

### Tuần 4-6: Stabilization

- [ ] Assign 1 person IT support (standby giải đáp)
- [ ] Kênh hỗ trợ: chat group hoặc email `plane-support@sentinel.internal`
- [ ] Check daily: server resources, error logs
- [ ] Weekly report: adoption rate (bao nhiêu % user active)

### Metrics đo adoption

| Metric | Target tuần 4 | Target tháng 2 |
|---|---|---|
| User active rate | > 50% | > 80% |
| Issues created/week | > 100 | > 500 |
| Average issues/user/week | > 2 | > 5 |

---

## 6. Tips Adoption thành công

1. **Trưởng tổ phải dùng trước** — lead by example
2. **Chuyển ngay từ Excel/email** — không cho dùng song song
3. **Meeting review trên Plane** — show board trong họp
4. **Celebrate wins** — highlight team nào dùng tốt nhất
5. **Lắng nghe feedback** — fix nhanh pain points
