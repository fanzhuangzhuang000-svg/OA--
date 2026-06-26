#!/usr/bin/env python3
"""
v0.3.9 P1 关键业务流程 E2E 验证
3 个核心流程 + 边界用例
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_API = "http://172.20.0.139:3001/api"
RESULTS = []
RESOURCES = {}


def http(method, path, body=None, token=None, expect=None):
    url = BASE_API + path
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8", errors="ignore")
            status = r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        status = e.code
    except Exception as e:
        return 0, None, f"EXC: {e}"
    try:
        j = json.loads(raw) if raw else None
    except Exception:
        j = None
    return status, j, raw


def login(username="admin", password="admin123"):
    s, j, _ = http("POST", "/auth/login", {"username": username, "password": password})
    if s == 200 and j:
        token = j.get("data", {}).get("token") or j.get("token")
        if token:
            return token
    raise RuntimeError(f"login failed: {s}")


def get_id(j, key="id"):
    if not j or not isinstance(j, dict):
        return None
    d = j.get("data")
    if isinstance(d, dict):
        return d.get(key)
    return None


def find_user(token, role=None):
    s, j, _ = http("GET", "/users?per_page=100", token=token)
    if s == 200 and j:
        data = j.get("data", {})
        users = data.get("data", []) if isinstance(data, dict) else data
        if users:
            return users[0]["id"]
    return 1


def find_customer(token):
    s, j, _ = http("GET", "/customers?per_page=10", token=token)
    if s == 200 and j:
        data = j.get("data", {})
        items = data.get("data", []) if isinstance(data, dict) else data
        if items:
            return items[0]["id"]
    return 1


def list_lost(token):
    """返回商机列表中 stage=lost 的数量"""
    s, j, _ = http("GET", "/sales/opps?stage=lost&per_page=100", token=token)
    if s == 200 and j:
        data = j.get("data", {})
        items = data.get("data", []) if isinstance(data, dict) else data
        return len(items or [])
    return 0


def list_pool(token):
    s, j, _ = http("GET", "/sales/pool?per_page=100", token=token)
    if s == 200 and j:
        data = j.get("data", {})
        items = data.get("data", []) if isinstance(data, dict) else data
        return items or [], len(items or [])
    return [], 0


def list_projects(token):
    s, j, _ = http("GET", "/projects?per_page=100", token=token)
    if s == 200 and j:
        data = j.get("data", {})
        items = data.get("data", []) if isinstance(data, dict) else data
        return items or [], len(items or [])
    return [], 0


def section(t):
    print(f"\n{'=' * 70}\n  {t}\n{'=' * 70}")


def record(flow, step, ok, detail=""):
    RESULTS.append({"flow": flow, "step": step, "ok": ok, "detail": detail})
    mark = "✅" if ok else "❌"
    print(f"  {mark} [{flow}] {step}: {detail}")


def main():
    print(f"v0.3.9 P1 业务流程 E2E - {datetime.now().isoformat()}")
    token = login()
    user_id = find_user(token)
    manager_id = find_user(token, "manager")
    customer_id = find_customer(token)
    print(f"user_id={user_id}  customer_id={customer_id}  manager_id={manager_id}")

    # ===== 流程 1: 录线索 → 转商机 → 战败 → 列表看到 lost 标签 =====
    section("流程 1: 录线索 → 转商机 → 战败 → 列表 lost")

    # 1.1 录线索
    s, j, _ = http("POST", "/sales/leads", {
        "customer_id": customer_id, "customer_name": "E2E-流程1-客户",
        "contact_name": "张三", "contact_phone": "13800000010",
        "source": "phone", "grade": "B", "estimated_amount": 30000,
        "owner_id": user_id, "requirement": "E2E 流程 1",
    }, token=token)
    lead1_id = get_id(j)
    record("流程1", "1.1 录线索", s == 200 and lead1_id, f"status={s} lead_id={lead1_id}")

    # 1.2 转商机
    s, j, _ = http("POST", f"/sales/leads/{lead1_id}/convert-to-opp", {
        "name": "E2E-流程1-商机", "estimated_amount": 30000,
        "sales_id": user_id, "presale_id": user_id,
    }, token=token)
    opp1_id = get_id(j)
    record("流程1", "1.2 转商机", s == 200 and opp1_id, f"status={s} opp_id={opp1_id}")

    # 1.3 战败
    s, j, _ = http("POST", f"/sales/opps/{opp1_id}/mark-lost", {
        "lost_reason": "price_high", "notes": "E2E 战败",
    }, token=token)
    record("流程1", "1.3 战败", s == 200, f"status={s}")

    # 1.4 列表看到 lost
    s, j, _ = http("GET", f"/sales/opps/{opp1_id}", token=token)
    stage = None
    if s == 200 and j and isinstance(j, dict):
        d = j.get("data")
        if isinstance(d, dict):
            stage = d.get("stage")
    record("流程1", "1.4 列表 lost", s == 200 and stage == "lost", f"status={s} stage={stage}")

    # ===== 流程 2: 录线索 → 转商机 → 成交 → 项目池多 1 条 → 转施工 → 项目列表多 1 条 =====
    section("流程 2: 录线索 → 转商机 → 成交 → 转施工")

    # 记录基线
    pools_before, pool_count_before = list_pool(token)
    projects_before, proj_count_before = list_projects(token)
    print(f"  [基线] pool={pool_count_before} project={proj_count_before}")

    # 2.1 录线索
    s, j, _ = http("POST", "/sales/leads", {
        "customer_id": customer_id, "customer_name": "E2E-流程2-客户",
        "contact_name": "李四", "contact_phone": "13800000011",
        "source": "phone", "grade": "A", "estimated_amount": 500000,
        "owner_id": user_id, "requirement": "E2E 流程 2",
    }, token=token)
    lead2_id = get_id(j)
    record("流程2", "2.1 录线索", s == 200 and lead2_id, f"status={s} lead_id={lead2_id}")

    # 2.2 转商机
    s, j, _ = http("POST", f"/sales/leads/{lead2_id}/convert-to-opp", {
        "name": "E2E-流程2-商机", "estimated_amount": 500000,
        "sales_id": user_id, "presale_id": user_id,
    }, token=token)
    opp2_id = get_id(j)
    record("流程2", "2.2 转商机", s == 200 and opp2_id, f"status={s} opp_id={opp2_id}")

    # 2.3 推进到 contracting
    for stage in ["solution", "negotiation", "contracting"]:
        s, _, _ = http("PATCH", f"/sales/opps/{opp2_id}/stage", {"stage": stage}, token=token)
    record("流程2", "2.3 推进 contracting", s == 200, f"最终 stage={stage}")

    # 2.4 成交
    s, j, _ = http("POST", f"/sales/opps/{opp2_id}/mark-won", {
        "contract_amount": 500000, "signed_at": "2026-06-19",
    }, token=token)
    pool2_id = None
    if j and isinstance(j, dict):
        d = j.get("data") or {}
        pool2_id = d.get("pool_id") or d.get("id")
        if isinstance(d.get("project_pool"), dict):
            pool2_id = d["project_pool"].get("id")
    record("流程2", "2.4 成交", s == 200 and pool2_id, f"status={s} pool_id={pool2_id}")

    # 2.5 项目池多 1 条
    pools_after, pool_count_after = list_pool(token)
    diff = pool_count_after - pool_count_before
    record("流程2", "2.5 项目池 +1", diff >= 1, f"差值={diff}  (before={pool_count_before}, after={pool_count_after})")

    # 2.6 转施工
    new_proj_id = None
    if pool2_id:
        s, j, _ = http("POST", f"/sales/pool/{pool2_id}/convert-to-project", {
            "name": "E2E-流程2-项目", "manager_id": manager_id,
            "start_date": "2026-06-19",
            "end_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "budget": 500000, "team_member_ids": [user_id],
        }, token=token)
        if j and isinstance(j, dict):
            d = j.get("data") or {}
            new_proj_id = d.get("id") or d.get("project_id")
        record("流程2", "2.6 转施工", s == 200 and new_proj_id, f"status={s} project_id={new_proj_id}")

    # 2.7 项目列表 +1
    projects_after, proj_count_after = list_projects(token)
    diff2 = proj_count_after - proj_count_before
    record("流程2", "2.7 项目列表 +1", diff2 >= 1, f"差值={diff2}  (before={proj_count_before}, after={proj_count_after})")

    # ===== 流程 3: 录商机 → 报价 → 客户接受 → 商机推到 contracting =====
    section("流程 3: 录商机 → 报价 → 客户接受 → contracting")

    # 3.1 录商机 (新)
    s, j, _ = http("POST", "/sales/opps", {
        "customer_id": customer_id, "name": "E2E-流程3-商机",
        "estimated_amount": 200000, "sales_id": user_id, "presale_id": user_id,
        "expected_sign_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    }, token=token)
    opp3_id = get_id(j)
    record("流程3", "3.1 录商机", s == 200 and opp3_id, f"status={s} opp_id={opp3_id}")

    # 3.2 推进到 negotiation (报价前置)
    s, _, _ = http("PATCH", f"/sales/opps/{opp3_id}/stage", {"stage": "solution"}, token=token)
    s, _, _ = http("PATCH", f"/sales/opps/{opp3_id}/stage", {"stage": "negotiation"}, token=token)
    record("流程3", "3.2 推进 negotiation", s == 200, "stage=negotiation")

    # 3.3 新建报价 V1
    s, j, _ = http("POST", "/sales/quotes", {
        "opportunity_id": opp3_id, "version": 1,
        "discount_rate": 10, "tax_rate": 13,
        "valid_until": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "items": [
            {"name": "海康摄像头", "specification": "4K", "unit": "台", "quantity": 10, "unit_price": 2000, "total_price": 20000},
            {"name": "线材", "specification": "Cat5e", "unit": "箱", "quantity": 5, "unit_price": 1000, "total_price": 5000},
        ],
    }, token=token)
    quote3_id = get_id(j)
    record("流程3", "3.3 新建报价 V1", s == 200 and quote3_id, f"status={s} quote_id={quote3_id}")

    # 3.4 提交
    s, _, _ = http("PUT", f"/sales/quotes/{quote3_id}/status", {"status": "submitted"}, token=token)
    record("流程3", "3.4 提交", s == 200, f"status={s}")

    # 3.5 客户接受
    s, _, _ = http("PUT", f"/sales/quotes/{quote3_id}/status", {"status": "accepted"}, token=token)
    record("流程3", "3.5 客户接受", s == 200, f"status={s}")

    # 3.6 商机 stage 推到 contracting
    s, j, _ = http("GET", f"/sales/opps/{opp3_id}", token=token)
    stage = None
    if s == 200 and j and isinstance(j, dict):
        d = j.get("data")
        if isinstance(d, dict):
            stage = d.get("stage")
    record("流程3", "3.6 商机 contracting", s == 200 and stage == "contracting", f"status={s} stage={stage}")

    # ===== 边界用例汇总 =====
    section("边界用例汇总 (由 e2e_api_v039p1.py 测，这里仅汇总)")

    # === 输出报告 ===
    section("业务流程汇总")
    total = len(RESULTS)
    ok = sum(1 for r in RESULTS if r["ok"])
    fail = total - ok
    print(f"\n  总计: {total}  ✅ {ok}  ❌ {fail}  通过率: {ok/total*100:.1f}%")

    if fail > 0:
        print(f"\n  失败清单:")
        for r in RESULTS:
            if not r["ok"]:
                print(f"    ❌ [{r['flow']}] {r['step']}: {r['detail']}")

    report_path = "D:/work/website/OA/.workbuddy/shots/v039p1/business_results.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base": BASE_API,
            "total": total, "ok": ok, "fail": fail,
            "pass_rate": f"{ok/total*100:.1f}",
            "results": RESULTS,
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  详细结果: {report_path}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
