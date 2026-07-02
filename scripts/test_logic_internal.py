import sys

print("=== Chạy Kiểm thử Logic Backend Nội bộ ===")

from plane.db.models import User, Workspace, Project, Issue

# 1. Tìm hoặc tạo User
user = User.objects.filter(email="admin@sentinel.local").first()
if not user:
    user = User.objects.create(email="admin@sentinel.local", username="admin_sentinel")
    user.set_password("Sentinel@123")
    user.save()
print(f"✅ [PASS] Lấy User thành công: {user.email}")

# 2. Tạo Workspace
workspace, created = Workspace.objects.get_or_create(
    slug="sentinel-test-ws",
    defaults={
        "name": "Sentinel Test Workspace",
        "organization_size": "1",
        "created_by": user,
        "owner": user,
    }
)
print(f"✅ [PASS] Logic Workspace thành công. ID: {workspace.id}")

# 3. Tạo Project
project, created = Project.objects.get_or_create(
    workspace=workspace,
    identifier="SEC",
    defaults={
        "name": "Test Security Project",
        "description": "Project test automation",
        "created_by": user,
        "network": 2
    }
)
print(f"✅ [PASS] Logic Project thành công. ID: {project.id}")

# 4. Tạo Issue
issue = Issue.objects.create(
    workspace=workspace,
    project=project,
    name="Test Detect Malware in Network",
    description_html="<p>Detected suspicious traffic.</p>",
    priority="high",
    created_by=user
)
print(f"✅ [PASS] Logic Issue thành công. Tên: {issue.name}")

print("\n🎉 Toàn bộ Logic Backend (DB Models) đã PASS!")
