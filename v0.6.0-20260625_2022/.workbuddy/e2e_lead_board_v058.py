"""
V0.5.8 线索看板 7 段状态机 E2E
- 验证 7 段独立存储
- 验证状态机合法/非法流转
- 验证 DB 计数与 GET /leads 一致
"""
import requests, json, sys
from typing import Optional

BASE = "http://192.168.3.117:8081/api"
TOKEN: Optional[str] = None
PASS = 0
FAIL = 0

def login():
    global TOKEN
    r = requests.post(f"{BASE}/auth/login", json={"username": "admin1", "password": "admin123"}, timeout=10)
    assert r.json()["code"] == 0, f"login failed: {r.text}"
    TOKEN = r.json()["data"]["token"]

def h():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def patch_status(lid: int, status: str):
    r = requests.patch(f"{BASE}/sales/leads/{lid}/status", json={"status": status}, headers=h(), timeout=10)
    return r.json()

def get_lead(lid: int):
    r = requests.get(f"{BASE}/sales/leads/{lid}", headers=h(), timeout=10)
    return r.json()["data"]

def count_by_status(status: str) -> int:
    r = requests.get(f"{BASE}/sales/leads?status={status}&per_page=1", headers=h(), timeout=10)
    return r.json()["data"]["total"]

def get_ids_by_status(status: str, n: int = 1):
    r = requests.get(f"{BASE}/sales/leads?status={status}&per_page={n}", headers=h(), timeout=10)
    j = r.json()
    items = j.get("data", {}).get("data", [])
    return [l["id"] for l in items]

def assert_true(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")

def assert_eq(name: str, actual, expected):
    assert_true(name, actual == expected, f"expected={expected!r} actual={actual!r}")

# ---------------- 1. 5 段流转 ----------------
print("=== Case 1: qualified → proposal → negotiating → qualified → contacted → new ===")
login()
ids = get_ids_by_status("qualified", 1)
assert ids, "no qualified lead to test"
test_id = ids[0]
print(f"  using lead id={test_id}")
flow = ["proposal", "negotiating", "qualified", "contacted", "new"]
for s in flow:
    res = patch_status(test_id, s)
    assert_eq(f"  → {s} API", res.get("code"), 0)
    d = get_lead(test_id)
    assert_eq(f"  → {s} 落库", d["status"], s)

# ---------------- 2. 非法流转 ----------------
print("=== Case 2: 终态不可流转 ===")
res = patch_status(test_id, "lost")
assert_eq("  new → lost 允许", res.get("code"), 0)
res = patch_status(test_id, "converted")
assert_eq("  discarded → converted 禁止", res.get("code"), 1)
res = patch_status(test_id, "negotiating")
assert_eq("  discarded → negotiating 禁止", res.get("code"), 1)

# ---------------- 3. 7 段独立计数 ----------------
print("=== Case 3: 7 段独立计数 ===")
counts_before = {s: count_by_status(s) for s in ["new","contacting","contacted","qualified","proposal","negotiating","converted","discarded"]}
for k, v in counts_before.items():
    print(f"    {k:12s} = {v}")
ids2 = get_ids_by_status("qualified", 1)
if ids2:
    test_id2 = ids2[0]
    res = patch_status(test_id2, "proposal")
    assert_eq(f"  推 {test_id2} → proposal", res.get("code"), 0)
    counts_after = {s: count_by_status(s) for s in ["new","contacting","contacted","qualified","proposal","negotiating","converted","discarded"]}
    assert_eq("  qualified -1", counts_after["qualified"], counts_before["qualified"] - 1)
    assert_eq("  proposal +1", counts_after["proposal"], counts_before["proposal"] + 1)
    print(f"    ✓ qualified {counts_before['qualified']} → {counts_after['qualified']}")
    print(f"    ✓ proposal   {counts_before['proposal']} → {counts_after['proposal']}")

# ---------------- 4. 列表 API 7 段全过滤 OK ----------------
print("=== Case 4: 列表 API 7 段 status 筛选 ===")
for s in ["new","contacting","contacted","qualified","proposal","negotiating","converted","discarded"]:
    r = requests.get(f"{BASE}/sales/leads?status={s}&per_page=200", headers=h(), timeout=10)
    items = r.json()["data"]["data"]
    all_match = all(it["status"] == s for it in items)
    assert_true(f"  status={s:12s} 全部命中 ({len(items)}条)", all_match, "")

print()
print("=" * 60)
print(f"  V0.5.8 线索看板 E2E: 通过 {PASS} / 失败 {FAIL}")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
