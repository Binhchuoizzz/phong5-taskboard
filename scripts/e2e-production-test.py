import requests
import sys

BASE_URL = "http://localhost/api"
LOGIN_DATA = {
    "email": "admin@sentinel.local",
    "password": "Sentinel@123"
}

def run_tests():
    print("=== Bắt đầu chạy Kịch bản Kiểm thử API Toàn diện (Logic Core) ===")
    session = requests.Session()
    
    # 1. Sign-in
    try:
        print("1. Kiểm tra Authentication...")
        res = session.post("http://localhost/auth/sign-in/", json=LOGIN_DATA)
        if res.status_code in [200, 201]:
            print("  ✅ [PASS] Đăng nhập thành công. Session cookie đã được lưu.")
            try:
                data = res.json()
                access_token = data.get("access_token")
                if access_token:
                    session.headers.update({"Authorization": f"Bearer {access_token}"})
            except:
                pass # Rely on session cookies
        else:
            print(f"  ❌ [FAIL] Đăng nhập thất bại. HTTP Code: {res.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ [FAIL] Lỗi kết nối Auth API: {e}")
        return False
        
    # 2. Get User Profile
    try:
        print("2. Lấy thông tin User Profile...")
        res = session.get(f"{BASE_URL}/users/me/")
        if res.status_code == 200:
            print("  ✅ [PASS] API /users/me/ hoạt động đúng.")
        else:
            print(f"  ❌ [FAIL] Lỗi /users/me/: {res.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ [FAIL] Lỗi kết nối Users API: {e}")
        return False

    # 3. Create a test workspace
    print("3. Kiểm tra logic tạo Workspace...")
    workspace_data = {
        "name": "Sentinel Test Workspace",
        "slug": "sentinel-test-ws",
        "organization_size": "1",
    }
    workspace_id = None
    res = session.post(f"{BASE_URL}/workspaces/", json=workspace_data)
    if res.status_code in [200, 201]:
        workspace_id = res.json().get("id")
        print("  ✅ [PASS] Tạo Workspace thành công.")
    elif res.status_code == 400 and "slug" in res.text:
        print("  ⚠️ [WARN] Workspace đã tồn tại, sẽ thử lấy danh sách để lấy ID.")
        res = session.get(f"{BASE_URL}/workspaces/")
        workspaces = res.json()
        if workspaces:
            workspace_id = workspaces[0].get("id")
            workspace_data["slug"] = workspaces[0].get("slug")
            print("  ✅ [PASS] Lấy Workspace cũ thành công.")
        else:
            print("  ❌ [FAIL] Không lấy được workspace.")
            return False
    else:
        print(f"  ❌ [FAIL] Lỗi tạo Workspace: {res.status_code} - {res.text}")
        return False

    # 4. Create a Project
    print("4. Kiểm tra logic tạo Project...")
    project_data = {
        "name": "Test Security Project",
        "identifier": "SEC",
        "description": "Project test automation",
        "network": 2
    }
    project_id = None
    res = session.post(f"{BASE_URL}/workspaces/{workspace_data['slug']}/projects/", json=project_data)
    if res.status_code in [200, 201]:
        project_id = res.json().get("id")
        print("  ✅ [PASS] Tạo Project thành công.")
    elif res.status_code == 400 and "identifier" in res.text:
        print("  ⚠️ [WARN] Project identifier đã tồn tại, lấy danh sách Project.")
        res = session.get(f"{BASE_URL}/workspaces/{workspace_data['slug']}/projects/")
        projects = res.json().get('results', [])
        if projects:
            project_id = projects[0].get("id")
            print("  ✅ [PASS] Lấy Project cũ thành công.")
        else:
            print("  ❌ [FAIL] Không lấy được Project.")
            return False
    else:
        print(f"  ❌ [FAIL] Lỗi tạo Project: {res.status_code} - {res.text}")
        return False

    # 5. Create an Issue
    print("5. Kiểm tra logic tạo Nhiệm vụ (Issue)...")
    issue_data = {
        "name": "Test Detect Malware in Network",
        "description_html": "<p>Detected suspicious traffic.</p>",
        "priority": "high",
    }
    res = session.post(f"{BASE_URL}/workspaces/{workspace_data['slug']}/projects/{project_id}/issues/", json=issue_data)
    if res.status_code in [200, 201]:
        print("  ✅ [PASS] Tạo Issue thành công.")
    else:
        print(f"  ❌ [FAIL] Lỗi tạo Issue: {res.status_code} - {res.text}")
        return False

    print("\n🎉 Toàn bộ Logic API cốt lõi đã PASS!")
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
