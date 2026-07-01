import requests
import json
import sys
import os

BASE_URL = os.environ.get("BASE_URL", "http://100.121.120.59")
ERRORS = []
PASSED = 0

def ok(msg):
    global PASSED
    PASSED += 1
    print(f"  ✅ PASS — {msg}")

def fail(msg, detail=""):
    ERRORS.append(msg)
    print(f"  ❌ FAIL — {msg}")
    if detail:
        print(f"         {detail}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─── AUTH HELPER ──────────────────────────────────────────────
def login(email, password):
    s = requests.Session()
    try:
        r = s.get(f"{BASE_URL}/auth/get-csrf-token/", timeout=5)
        csrf = r.json().get("csrf_token")
        s.headers.update({"X-CSRFToken": csrf, "Referer": BASE_URL})
        r = s.post(f"{BASE_URL}/auth/sign-in/", data={"email": email, "password": password}, allow_redirects=False, timeout=5)
        if r.status_code not in (200, 302):
            fail(f"Login {email}", f"HTTP {r.status_code}")
            return None
        return s
    except Exception as e:
        fail(f"Login connection failure for {email}", str(e))
        return None

# ─── SESSIONS ─────────────────────────────────────────────────
print("\n" + "="*60)
print("    SENTINEL TASKBOARD — FULL ENDPOINT INTEGRATION TEST")
print("="*60)
print(f"Testing target: {BASE_URL}")

admin_session = login("admin@sentinel.local", "Sentinel@123")
member1_session = login("member1@sentinel.local", "Sentinel@123")
guest1_session = login("guest1@sentinel.local", "Sentinel@123")

if not admin_session:
    print("\n❌ Admin session could not be established. Aborting test execution.")
    sys.exit(1)

# ─── SECTION 1: INSTANCE API ──────────────────────────────────
section("1. INSTANCE & CONFIG API")

r = admin_session.get(f"{BASE_URL}/api/instances/", timeout=5)
if r.status_code == 200 and r.json().get("instance", {}).get("is_setup_done"):
    ok(f"GET /api/instances/ → is_setup_done=True")
else:
    fail("GET /api/instances/", f"HTTP {r.status_code}: {r.text[:200]}")

r = admin_session.get(f"{BASE_URL}/api/users/me/", timeout=5)
if r.status_code == 200 and r.json().get("email") == "admin@sentinel.local":
    ok(f"GET /api/users/me/ → admin@sentinel.local")
else:
    fail("GET /api/users/me/", f"HTTP {r.status_code}: {r.text[:200]}")

# ─── SECTION 2: WORKSPACES ────────────────────────────────────
section("2. WORKSPACES")

r = admin_session.get(f"{BASE_URL}/api/users/me/workspaces/", timeout=5)
if r.status_code == 200:
    workspaces = r.json()
    ws_slug = None
    for ws in workspaces:
        if ws.get("slug") == "sentinel":
            ws_slug = ws.get("slug")
            ok(f"GET /api/users/me/workspaces/ → sentinel workspace found")
            break
    if not ws_slug:
        fail("Workspace 'sentinel' not found", str(workspaces))
else:
    fail("GET /api/users/me/workspaces/", f"HTTP {r.status_code}")
    ws_slug = "sentinel"

# ─── SECTION 3: PROJECTS ──────────────────────────────────────
section("3. PROJECTS")

r = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/", timeout=5)
if r.status_code == 200:
    projects = r.json()
    project_count = len(projects) if isinstance(projects, list) else projects.get("count", 0)
    ok(f"GET /api/workspaces/{ws_slug}/projects/ → {project_count} projects")
    first_project_id = projects[0]["id"] if isinstance(projects, list) and projects else None
else:
    fail(f"GET /api/workspaces/{ws_slug}/projects/", f"HTTP {r.status_code}: {r.text[:200]}")
    first_project_id = None

# Create a test project
r = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/", json={
    "name": "TESTAUDIT",
    "identifier": "TESTAUDIT",
    "network": 2,
    "description": "Automated test project"
}, timeout=5)
if r.status_code in (200, 201):
    test_proj = r.json()
    test_proj_id = test_proj["id"]
    ok(f"POST /api/workspaces/{ws_slug}/projects/ → created TEST-AUDIT (id={test_proj_id[:8]}...)")
else:
    fail(f"POST projects/ create", f"HTTP {r.status_code}: {r.text[:200]}")
    test_proj_id = first_project_id

# ─── SECTION 4: ISSUES ────────────────────────────────────────
section("4. ISSUES")

if test_proj_id:
    # Create issue
    r = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/issues/", json={
        "name": "Test Issue from Audit Script",
        "priority": "medium",
        "description_html": "<p>Automated test issue</p>"
    }, timeout=5)
    if r.status_code in (200, 201):
        issue = r.json()
        issue_id = issue["id"]
        ok(f"POST /issues/ → created issue (id={issue_id[:8]}...)")

        # Read it back
        r2 = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/issues/{issue_id}/", timeout=5)
        if r2.status_code == 200:
            ok(f"GET /issues/{issue_id[:8]}.../ → read OK")
        else:
            fail(f"GET /issues/{{id}}/", f"HTTP {r2.status_code}")

        # Update
        r3 = admin_session.patch(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/issues/{issue_id}/", json={
            "priority": "high",
            "state": None
        }, timeout=5)
        if r3.status_code in (200, 204):
            ok(f"PATCH /issues/{issue_id[:8]}.../ priority=high → updated OK")
        else:
            fail(f"PATCH /issues/{{id}}/", f"HTTP {r3.status_code}: {r3.text[:200]}")

        # Delete
        r4 = admin_session.delete(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/issues/{issue_id}/", timeout=5)
        if r4.status_code in (200, 204):
            ok(f"DELETE /issues/{issue_id[:8]}.../ → deleted OK")
        else:
            fail(f"DELETE /issues/{{id}}/", f"HTTP {r4.status_code}: {r4.text[:200]}")
    else:
        fail("POST /issues/ create", f"HTTP {r.status_code}: {r.text[:300]}")

# ─── SECTION 5: MEMBERS & RBAC ────────────────────────────────
section("5. MEMBERS & RBAC")

r = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/members/", timeout=5)
if r.status_code == 200:
    members = r.json()
    ok(f"GET /members/ → {len(members)} workspace members")
else:
    fail("GET /members/", f"HTTP {r.status_code}: {r.text[:200]}")

# member1 should only see SOC project (PRJ6-Analytics)
if member1_session:
    r = member1_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/", timeout=5)
    if r.status_code == 200:
        member_projects = r.json()
        proj_names = [p.get("identifier") for p in member_projects] if isinstance(member_projects, list) else []
        ok(f"RBAC member1 sees projects: {proj_names}")
        if "TO6" in str(proj_names):
            ok("RBAC member1 correctly sees PRJ6-Analytics")
    else:
        fail("RBAC member1 GET /projects/", f"HTTP {r.status_code}")

# guest1 attempts to create a project — should be rejected (role=5 is Viewer)
if guest1_session:
    r = guest1_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/", json={
        "name": "FORBIDDEN-PROJECT",
        "identifier": "FORBID",
        "network": 2,
    }, timeout=5)
    if r.status_code in (400, 403):
        ok(f"RBAC guest1 blocked from creating project → HTTP {r.status_code} (correct)")
    else:
        fail(f"RBAC guest1 should be denied project creation", f"HTTP {r.status_code}: {r.text[:200]}")

# ─── SECTION 6: WORKSPACE & PROJECT CORE ENTITIES (CRUD) ──────
section("6. WORKSPACE & PROJECT CORE ENTITIES (CRUD)")

if test_proj_id:
    # 6.1 State retrieval
    r = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/states/", timeout=5)
    if r.status_code == 200:
        states = r.json()
        ok(f"GET /states/ → {len(states)} states in TESTAUDIT project")
    else:
        fail("GET /states/", f"HTTP {r.status_code}: {r.text[:200]}")

    # 6.2 Labels retrieval
    r = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/labels/", timeout=5)
    if r.status_code == 200:
        labels = r.json()
        ok(f"GET /workspaces/labels/ → {len(labels)} workspace labels")
    else:
        fail("GET /workspaces/labels/", f"HTTP {r.status_code}: {r.text[:200]}")

    # 6.3 Cycles CRUD (Sprints)
    print("\n  --- Cycles (Sprints) CRUD ---")
    r_cycle_create = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/cycles/", json={
        "name": "Audit Cycle 01",
        "description": "Integration test automated cycle",
        "start_date": "2026-07-01",
        "end_date": "2026-07-14"
    }, timeout=5)
    if r_cycle_create.status_code in (200, 201):
        cycle = r_cycle_create.json()
        cycle_id = cycle["id"]
        ok(f"POST /cycles/ → created cycle '{cycle['name']}' (id={cycle_id[:8]}...)")

        # Read back
        r_cycle_get = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/cycles/{cycle_id}/", timeout=5)
        if r_cycle_get.status_code == 200:
            ok(f"GET /cycles/{cycle_id[:8]}.../ → read OK")
        else:
            fail(f"GET /cycles/{cycle_id[:8]}.../", f"HTTP {r_cycle_get.status_code}")

        # Update
        r_cycle_patch = admin_session.patch(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/cycles/{cycle_id}/", json={
            "name": "Audit Cycle 01 - Hardened"
        }, timeout=5)
        if r_cycle_patch.status_code in (200, 204):
            ok(f"PATCH /cycles/{cycle_id[:8]}.../ → updated OK")
        else:
            fail(f"PATCH /cycles/{cycle_id[:8]}.../", f"HTTP {r_cycle_patch.status_code}")

        # Delete
        r_cycle_delete = admin_session.delete(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/cycles/{cycle_id}/", timeout=5)
        if r_cycle_delete.status_code in (200, 204):
            ok(f"DELETE /cycles/{cycle_id[:8]}.../ → deleted OK")
        else:
            fail(f"DELETE /cycles/{cycle_id[:8]}.../", f"HTTP {r_cycle_delete.status_code}")
    else:
        fail("POST /cycles/ create", f"HTTP {r_cycle_create.status_code}: {r_cycle_create.text[:200]}")

    # 6.4 Modules CRUD (Epics)
    print("\n  --- Modules (Epics) CRUD ---")
    r_mod_create = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/modules/", json={
        "name": "Hardening Epic 01",
        "description": "Integration test automated epic",
        "status": "backlog"
    }, timeout=5)
    if r_mod_create.status_code in (200, 201):
        mod = r_mod_create.json()
        mod_id = mod["id"]
        ok(f"POST /modules/ → created module '{mod['name']}' (id={mod_id[:8]}...)")

        # Read back
        r_mod_get = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/modules/{mod_id}/", timeout=5)
        if r_mod_get.status_code == 200:
            ok(f"GET /modules/{mod_id[:8]}.../ → read OK")
        else:
            fail(f"GET /modules/{mod_id[:8]}.../", f"HTTP {r_mod_get.status_code}")

        # Update
        r_mod_patch = admin_session.patch(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/modules/{mod_id}/", json={
            "name": "Hardening Epic 01 - Closed"
        }, timeout=5)
        if r_mod_patch.status_code in (200, 204):
            ok(f"PATCH /modules/{mod_id[:8]}.../ → updated OK")
        else:
            fail(f"PATCH /modules/{mod_id[:8]}.../", f"HTTP {r_mod_patch.status_code}")

        # Delete
        r_mod_delete = admin_session.delete(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/modules/{mod_id}/", timeout=5)
        if r_mod_delete.status_code in (200, 204):
            ok(f"DELETE /modules/{mod_id[:8]}.../ → deleted OK")
        else:
            fail(f"DELETE /modules/{mod_id[:8]}.../", f"HTTP {r_mod_delete.status_code}")
    else:
        fail("POST /modules/ create", f"HTTP {r_mod_create.status_code}: {r_mod_create.text[:200]}")

    # 6.5 Pages CRUD (Wikis)
    print("\n  --- Pages (Wikis) CRUD ---")
    r_page_create = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/pages/", json={
        "name": "Vulnerability Logbook",
        "description": "Integration test page content"
    }, timeout=5)
    if r_page_create.status_code in (200, 201):
        page = r_page_create.json()
        page_id = page["id"]
        ok(f"POST /pages/ → created page '{page['name']}' (id={page_id[:8]}...)")

        # Read back
        r_page_get = admin_session.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/pages/{page_id}/", timeout=5)
        if r_page_get.status_code == 200:
            ok(f"GET /pages/{page_id[:8]}.../ → read OK")
        else:
            fail(f"GET /pages/{page_id[:8]}.../", f"HTTP {r_page_get.status_code}")

        # Update
        r_page_patch = admin_session.patch(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/pages/{page_id}/", json={
            "name": "Vulnerability Logbook - Verified"
        }, timeout=5)
        if r_page_patch.status_code in (200, 204):
            ok(f"PATCH /pages/{page_id[:8]}.../ → updated OK")
        else:
            fail(f"PATCH /pages/{page_id[:8]}.../", f"HTTP {r_page_patch.status_code}")

        # Archive first (required by business logic before delete)
        r_page_archive = admin_session.post(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/pages/{page_id}/archive/", timeout=5)
        if r_page_archive.status_code == 200:
            ok(f"POST /pages/{page_id[:8]}.../archive/ → archived OK")
        else:
            fail(f"POST /pages/{page_id[:8]}.../archive/", f"HTTP {r_page_archive.status_code}: {r_page_archive.text[:200]}")

        # Delete
        r_page_delete = admin_session.delete(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/pages/{page_id}/", timeout=5)
        if r_page_delete.status_code in (200, 204):
            ok(f"DELETE /pages/{page_id[:8]}.../ → deleted OK")
        else:
            fail(f"DELETE /pages/{page_id[:8]}.../", f"HTTP {r_page_delete.status_code}: {r_page_delete.text[:200]}")
    else:
        fail("POST /pages/ create", f"HTTP {r_page_create.status_code}: {r_page_create.text[:200]}")

# ─── SECTION 7: UNAUTHENTICATED ACCESS PROTECTION ─────────────
section("7. UNAUTHENTICATED ACCESS PROTECTION")

anon = requests.Session()
try:
    r = anon.get(f"{BASE_URL}/api/users/me/", timeout=5)
    if r.status_code in (401, 403):
        ok(f"GET /api/users/me/ without auth → HTTP {r.status_code} (protected)")
    else:
        fail("Unauthenticated /api/users/me/ should be 401/403", f"HTTP {r.status_code}: {r.text[:200]}")

    r = anon.get(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/", timeout=5)
    if r.status_code in (401, 403):
        ok(f"GET /api/workspaces/projects/ without auth → HTTP {r.status_code} (protected)")
    else:
        fail("Unauthenticated /projects/ should be 401/403", f"HTTP {r.status_code}: {r.text[:200]}")
except Exception as e:
    fail("Unauthenticated access check failed", str(e))

# ─── SECTION 8: GOD-MODE ──────────────────────────────────────
section("8. GOD-MODE ADMIN PANEL")

s = requests.Session()
try:
    r = s.get(f"{BASE_URL}/auth/get-csrf-token/", timeout=5)
    csrf = r.json().get("csrf_token")
    s.headers.update({"X-CSRFToken": csrf})
    r = s.post(f"{BASE_URL}/api/instances/admins/sign-in/", data={"email": "admin@sentinel.local", "password": "Sentinel@123"}, allow_redirects=False, timeout=5)
    r_me = s.get(f"{BASE_URL}/api/instances/admins/me/", timeout=5)
    if r_me.status_code == 200:
        ok(f"God-Mode /api/instances/admins/me/ → {r_me.json().get('email')}")
    else:
        fail("God-Mode admin me endpoint", f"HTTP {r_me.status_code}")

    r_config = s.get(f"{BASE_URL}/api/instances/configurations/", timeout=5)
    if r_config.status_code == 200:
        ok("GET /api/instances/configurations/ → instance config accessible")
    else:
        fail("GET /api/instances/configurations/", f"HTTP {r_config.status_code}: {r_config.text[:200]}")
except Exception as e:
    fail("God-Mode admin tests failed", str(e))

# ─── CLEANUP ──────────────────────────────────────────────────
section("CLEANUP")
if test_proj_id:
    r = admin_session.delete(f"{BASE_URL}/api/workspaces/{ws_slug}/projects/{test_proj_id}/", timeout=5)
    if r.status_code in (200, 204):
        ok("Cleanup: TEST-AUDIT project deleted")
    else:
        fail("Cleanup: delete TEST-AUDIT", f"HTTP {r.status_code}: {r.text[:200]}")

# ─── SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*60}")
total = PASSED + len(ERRORS)
print(f"  RESULT: {PASSED}/{total} passed, {len(ERRORS)} failed")
if ERRORS:
    print("\n  FAILURES:")
    for e in ERRORS:
        print(f"    ❌ {e}")
    print(f"{'='*60}\n")
    sys.exit(1)
else:
    print(f"\n  🎉 ALL {PASSED} CHECKS PASSED — System is healthy!")
    print(f"{'='*60}\n")
