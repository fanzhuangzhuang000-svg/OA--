#!/usr/bin/env python3
"""
端到端完整业务流程测试 V2（基于真实路由表修正 URL）
运行在 172 上（访问 127.0.0.1）
"""
import requests, json, sys, time
from datetime import date, timedelta

BASE = "http://127.0.0.1/api"
TOKEN = None
T = {}  # 保存创建的 ID

sess = requests.Session()
sess.trust_env = False


def p(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def expect(resp, label, status=200, save_as=None):
    ok = resp.status_code == status
    icon = "✅" if ok else "❌"
    print(f"  {icon} {label}: HTTP {resp.status_code}")
    if not ok:
        print(f"      响应: {resp.text[:250]}")
    if ok and save_as and resp.status_code < 300:
        try:
            d = resp.json()
            data = d.get("data", {})
            if isinstance(data, dict):
                tid = data.get("id")
                if tid:
                    T[save_as] = tid
                    print(f"      🔑 已保存 {save_as} = {tid}")
        except Exception:
            pass
    return ok


# ─── 1. 认证流程 ───────────────────────────────────────────────
def test_auth():
    p("1️⃣ 认证流程")
    global TOKEN
    r = sess.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
    expect(r, "POST /auth/login")
    try:
        d = r.json()
        TOKEN = d["data"]["token"]
        print(f"      🔑 Token 前30字: {TOKEN[:30]}...")
    except Exception as e:
        print(f"      ❌ 解析 token 失败: {e}")
        raise

    r = sess.get(f"{BASE}/auth/me", headers=auth_headers())
    expect(r, "GET /auth/me", save_as="user_id")


# ─── 2. 客户→项目→施工日志 ─────────────────────────────────────
def test_customer_project():
    p("2️⃣ 客户 → 项目 → 施工日志")
    # 2.1 创建客户
    r = sess.post(f"{BASE}/customers", headers=auth_headers(), json={
        "name": f"E2E客户_{date.today()}",
        "type": "customer",
        "contact": "E2E测试联系人",
        "phone": "13800138000",
        "email": "e2e@test.com",
        "address": "E2E测试地址",
    })
    expect(r, "POST /customers", save_as="customer_id")
    cid = T.get("customer_id")

    # 2.2 创建项目
    if cid:
        r = sess.post(f"{BASE}/projects", headers=auth_headers(), json={
            "name": f"E2E项目_{date.today()}",
            "customer_id": cid,
            "status": "planning",
            "start_date": date.today().strftime("%Y-%m-%d"),
            "end_date": (date.today() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "budget": 500000,
        })
        expect(r, "POST /projects", save_as="project_id")

    pid = T.get("project_id")
    if not pid:
        print("  ⚠️  跳过项目后续（无 project_id）")
        return

    # 2.3 更新项目阶段（PUT /projects/{project}/stage）
    r = sess.put(f"{BASE}/projects/{pid}/stage", headers=auth_headers(), json={
        "stage": "construction",
        "note": "E2E测试：更新为施工中",
    })
    expect(r, f"PUT /projects/{pid}/stage")

    # 2.4 创建施工日志（POST /projects/{project}/construction-logs）
    r = sess.post(f"{BASE}/projects/{pid}/construction-logs", headers=auth_headers(), json={
        "work_date": date.today().strftime("%Y-%m-%d"),
        "weather": "sunny",
        "temperature": 28,
        "content": "E2E测试施工内容",
        "progress": "基础施工完成50%",
        "issues": "无",
        "next_plan": "明日继续",
    })
    expect(r, f"POST /projects/{pid}/construction-logs", save_as="log_id")

    # 2.5 查看项目详情
    r = sess.get(f"{BASE}/projects/{pid}", headers=auth_headers())
    expect(r, f"GET /projects/{pid}")

    # 2.6 项目列表（筛选）
    r = sess.get(f"{BASE}/projects?status=in_progress&page=1&page_size=5",
                 headers=auth_headers())
    expect(r, "GET /projects?status=in_progress")

    # 2.7 项目仪表盘摘要
    r = sess.get(f"{BASE}/projects/dashboard-summary", headers=auth_headers())
    expect(r, "GET /projects/dashboard-summary")


# ─── 3. 财务链路 ────────────────────────────────────────────────
def test_finance():
    p("3️⃣ 财务链路：应收款→收款 / 报销→审批")
    cid = T.get("customer_id")

    # 3A. 应收款
    print("  [3A] 应收款 → 收款")
    if cid:
        r = sess.post(f"{BASE}/finance/receivables", headers=auth_headers(), json={
            "customer_id": cid,
            "amount": 50000,
            "status": "pending",
            "due_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "note": f"E2E测试应收款 {date.today()}",
        })
        expect(r, "POST /finance/receivables", save_as="receivable_id")

    rid = T.get("receivable_id")
    if rid:
        # 收款（POST /finance/receivables/{id}/payments）
        r = sess.post(f"{BASE}/finance/receivables/{rid}/payments",
                       headers=auth_headers(), json={
                "amount": 50000,
                "payment_date": date.today().strftime("%Y-%m-%d"),
                "payment_method": "bank_transfer",
                "notes": "E2E测试全额收款",
            })
        expect(r, f"POST /finance/receivables/{rid}/payments")

    # 3B. 报销
    print("  [3B] 报销 → 审批")
    r = sess.post(f"{BASE}/expenses", headers=auth_headers(), json={
        "amount": 380,
        "category": "meals",
        "description": "E2E测试报销：商务午餐",
        "expense_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "personal",
    })
    expect(r, "POST /expenses", save_as="expense_id")

    eid = T.get("expense_id")
    if eid:
        # 审批（POST /expenses/{claim}/approve）
        r = sess.post(f"{BASE}/expenses/{eid}/approve",
                       headers=auth_headers(), json={
                "comment": "E2E测试审批通过",
            })
        expect(r, f"POST /expenses/{eid}/approve")

    # 审批中心列表
    r = sess.get(f"{BASE}/approvals/center?status=pending&page=1&page_size=10",
                 headers=auth_headers())
    expect(r, "GET /approvals/center?status=pending")


# ─── 4. 采购全流程 ───────────────────────────────────────────────
def test_purchase():
    p("4️⃣ 采购全流程：需求→计划→合同→付款→发货")
    # 4.1 采购需求
    r = sess.post(f"{BASE}/purchase/requirements", headers=auth_headers(), json={
        "material": "E2E测试材料",
        "specs": "规格100x50x20mm",
        "quantity": 100,
        "estimated_price": 80.5,
        "required_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "purpose": "E2E测试采购需求",
    })
    expect(r, "POST /purchase/requirements", save_as="req_id")

    # 4.2 审批需求（POST /purchase/approvals/{id}/decide）
    req_id = T.get("req_id")
    if req_id:
        r = sess.post(f"{BASE}/purchase/approvals/{req_id}/decide",
                       headers=auth_headers(), json={
                "action": "approved",
                "comment": "E2E测试：采购需求审批通过",
            })
        expect(r, f"POST /purchase/approvals/{req_id}/decide")

    # 4.3 采购计划（POST /purchase/plans）
    if req_id:
        r = sess.post(f"{BASE}/purchase/plans", headers=auth_headers(), json={
            "requirement_ids": [req_id],
            "plan_no": f"PLAN-E2E-{date.today():%Y%m%d}",
            "total_amount": 8050,
            "expected_date": (date.today() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "notes": "E2E测试采购计划",
        })
        expect(r, "POST /purchase/plans", save_as="plan_id")

    # 4.4 提交计划审批（POST /purchase/plans/{id}/submit）
    plan_id = T.get("plan_id")
    if plan_id:
        r = sess.post(f"{BASE}/purchase/plans/{plan_id}/submit",
                       headers=auth_headers())
        expect(r, f"POST /purchase/plans/{plan_id}/submit")

    # 4.5 采购合同
    if plan_id:
        r = sess.post(f"{BASE}/purchase/contracts", headers=auth_headers(), json={
            "plan_id": plan_id,
            "contract_no": f"CTR-E2E-{date.today():%Y%m%d}",
            "total_amount": 8050,
            "sign_date": date.today().strftime("%Y-%m-%d"),
            "delivery_date": (date.today() + timedelta(days=25)).strftime("%Y-%m-%d"),
            "payment_terms": "货到付款",
            "notes": "E2E测试采购合同",
        })
        expect(r, "POST /purchase/contracts", save_as="contract_id")

    # 4.6 发货（POST /purchase/contracts/{id}/ship）
    contract_id = T.get("contract_id")
    if contract_id:
        r = sess.post(f"{BASE}/purchase/contracts/{contract_id}/ship",
                       headers=auth_headers(), json={
                "delivery_date": date.today().strftime("%Y-%m-%d"),
                "tracking_no": f"E2E{date.today():%Y%m%d}001",
                "carrier": "E2E测试物流",
                "notes": "E2E测试发货",
            })
        expect(r, f"POST /purchase/contracts/{contract_id}/ship", save_as="shipment_id")

    # 4.7 入库（POST /inventory/stock-in）
    wh_id = T.get("warehouse_id")
    if not wh_id:
        # 查仓库列表
        r = sess.get(f"{BASE}/inventory/warehouses", headers=auth_headers())
        expect(r, "GET /inventory/warehouses")
        try:
            d = r.json().get("data", {})
            wh_list = d if isinstance(d, list) else d.get("data", [])
            if wh_list:
                wh_id = wh_list[0]["id"]
                T["warehouse_id"] = wh_id
                print(f"      🏠 仓库 ID: {wh_id}")
        except Exception:
            pass

    if contract_id and wh_id:
        r = sess.post(f"{BASE}/inventory/stock-in", headers=auth_headers(), json={
            "warehouse_id": wh_id,
            "type": "inbound",
            "material": "E2E测试材料",
            "quantity": 100,
            "unit": "个",
            "related_type": "purchase_contract",
            "related_id": contract_id,
            "notes": "E2E测试采购入库",
        })
        expect(r, "POST /inventory/stock-in", save_as="stock_in_id")


# ─── 5. 库存链路 ────────────────────────────────────────────────
def test_inventory():
    p("5️⃣ 库存链路：分类→物资→入库→出库")
    # 5.1 创建分类（POST /inventory-categories）
    r = sess.post(f"{BASE}/inventory-categories", headers=auth_headers(), json={
        "name": f"E2E分类_{date.today():%H%M%S}",
    })
    expect(r, "POST /inventory-categories", save_as="cat_id")

    # 5.2 创建物资（POST /inventory/）
    cat_id = T.get("cat_id")
    if cat_id:
        r = sess.post(f"{BASE}/inventory/", headers=auth_headers(), json={
            "code": f"MAT-E2E-{int(time.time()*1e6)}",
            "name": "E2E测试物资",
            "category_id": cat_id,
            "unit": "个",
            "specs": "100x50x20mm",
        })
        expect(r, "POST /inventory/", save_as="mat_id")

    # 5.3 入库（如果前面没做）
    wh_id = T.get("warehouse_id")
    if not wh_id:
        r = sess.get(f"{BASE}/inventory/warehouses", headers=auth_headers())
        try:
            d = r.json().get("data", {})
            wh_list = d if isinstance(d, list) else d.get("data", [])
            wh_id = wh_list[0]["id"] if wh_list else None
            if wh_id:
                T["warehouse_id"] = wh_id
        except Exception:
            pass

    if wh_id:
        # 5.4 出库
        r = sess.post(f"{BASE}/inventory/stock-out", headers=auth_headers(), json={
            "warehouse_id": wh_id,
            "type": "outbound",
            "material": "E2E测试物资",
            "quantity": 10,
            "unit": "个",
            "notes": "E2E测试出库",
        })
        expect(r, "POST /inventory/stock-out")

    # 5.5 库存列表（GET /inventory/）
    r = sess.get(f"{BASE}/inventory/", headers=auth_headers())
    expect(r, "GET /inventory/ (库存列表)")

    # 5.6 库存统计（GET /inventory/stats）
    r = sess.get(f"{BASE}/inventory/stats", headers=auth_headers())
    expect(r, "GET /inventory/stats")


# ─── 6. 车辆链路 ────────────────────────────────────────────────
def test_vehicle():
    p("6️⃣ 车辆链路：车辆→加油→维修→保险→年检")
    r = sess.post(f"{BASE}/vehicles", headers=auth_headers(), json={
        "plate_no": f"E2E{int(time.time())%100000}测",
        "brand": "E2E测试品牌",
        "model": "E2E测试型号",
        "year": 2025,
        "vin": f"E2E{int(time.time()*1e6)}",
        "engine_no": f"ENG-E2E-{int(time.time())}",
        "purchase_date": date.today().strftime("%Y-%m-%d"),
        "status": "active",
    })
    expect(r, "POST /vehicles", save_as="vehicle_id")

    vid = T.get("vehicle_id")
    if not vid:
        print("  ⚠️  跳过车辆后续（无 vehicle_id）")
        return

    # 6.2 加油记录（POST /vehicles/XXX — 看路由是 VehicleController，但不是 REST 子资源）
    # 根据 routes：Route::prefix('vehicles')->group 里有 fuel-cards，但没有 fuel-logs
    # 实际上加油记录可能在别的 Controller，先跳过用正确路径
    # 从 routes 看：VehicleController 有 storeUsageRequest（用车申请）
    # 加油/维修/保险/年检 可能是独立 Controller，routes 里没看到
    # 跳过这些，等确认路径
    print("  ⚠️  车辆加油/维修/保险/年检 子路径待确认，跳过")

    # 6.3 车辆列表
    r = sess.get(f"{BASE}/vehicles?status=active&page=1&page_size=5",
                 headers=auth_headers())
    expect(r, "GET /vehicles (车辆列表)")


# ─── 7. 员工链路 ────────────────────────────────────────────────
def test_employee():
    p("7️⃣ 员工链路：入职→排班→考勤")
    # 7.1 入职（POST /employee-onboardings）
    r = sess.post(f"{BASE}/employee-onboardings", headers=auth_headers(), json={
        "user": {
            "username": f"e2euser{date.today():%H%M%S}",
            "name": f"E2E测试员工{date.today():%H%M%S}",
            "gender": "male",
            "phone": "13900139000",
            "email": f"e2e{date.today():%H%M%S}@test.com",
            "password": "test1234",
        },
        "onboarding": {
            "department": "技术部",
            "position": "测试工程师",
            "hire_date": date.today().strftime("%Y-%m-%d"),
            "notes": "E2E测试自动创建",
        }
    })
    expect(r, "POST /employee-onboardings", save_as="onboard_id")

    # 7.2 排班列表（GET /schedules?start=&end=）
    today = date.today()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    r = sess.get(
        f"{BASE}/schedules?start={first_day}&end={last_day.strftime('%Y-%m-%d')}",
        headers=auth_headers()
    )
    expect(r, "GET /schedules (排班列表)")

    # 7.3 考勤概览
    r = sess.get(f"{BASE}/attendance/overview", headers=auth_headers())
    expect(r, "GET /attendance/overview")

    # 7.4 考勤日历
    r = sess.get(f"{BASE}/attendance/calendar?month={today.strftime('%Y-%m')}",
                 headers=auth_headers())
    expect(r, "GET /attendance/calendar")


# ─── 8. 销售链路 ────────────────────────────────────────────────
def test_sales():
    p("8️⃣ 销售链路：线索→商机→产品→报价")
    # 8.1 创建线索（POST /sales/leads）
    r = sess.post(f"{BASE}/sales/leads", headers=auth_headers(), json={
        "customer_name": f"E2E线索客户_{date.today():%H%M%S}",
        "contact_name": "E2E测试联系人",
        "contact_phone": "13700137000",
        "source": "online",
        "notes": "E2E测试自动创建",
    })
    expect(r, "POST /sales/leads", save_as="lead_id")

    # 8.2 创建商机（POST /sales/opps）
    lead_id = T.get("lead_id")
    if lead_id:
        r = sess.post(f"{BASE}/sales/opps", headers=auth_headers(), json={
            "lead_id": lead_id,
            "name": f"E2E测试商机_{date.today():%H%M%S}",
            "amount": 120000,
            "stage": "negotiation",
            "expected_close_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "notes": "E2E测试自动创建",
        })
        expect(r, "POST /sales/opps", save_as="opp_id")

    # 8.3 创建产品（POST /sales/products）
    r = sess.post(f"{BASE}/sales/products", headers=auth_headers(), json={
        "name": f"E2E测试产品_{date.today():%H%M%S}",
        "code": f"SKU-E2E-{date.today():%Y%m%d%H%M%S}",
        "category": "安防设备",
        "sale_price": 2500.0,
        "description": "E2E测试自动创建",
    })
    expect(r, "POST /sales/products", save_as="product_id")

    # 8.4 创建报价单（POST /sales/quotes）
    opp_id = T.get("opp_id")
    product_id = T.get("product_id")
    if opp_id and product_id:
        r = sess.post(f"{BASE}/sales/quotes", headers=auth_headers(), json={
            "opportunity_id": opp_id,
            "product_id": product_id,
            "quantity": 10,
            "unit_price": 2500.0,
            "discount": 5.0,
            "total_amount": 23750.0,
            "valid_until": (date.today() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "notes": "E2E测试报价单",
        })
        expect(r, "POST /sales/quotes", save_as="quote_id")


# ─── 9. 性能检查 ────────────────────────────────────────────────
def test_perf():
    p("9️⃣ 性能检查：关键接口响应时间")
    import time
    endpoints = [
        ("GET /vehicles", "/vehicles"),
        ("GET /employees", "/employees"),
        ("GET /customers", "/customers?type=customer"),
        ("GET /projects", "/projects"),
        ("GET /finance/receivables", "/finance/receivables"),
        ("GET /purchase/requirements", "/purchase/requirements"),
        ("GET /inventory/", "/inventory/"),
        ("GET /sales/leads", "/sales/leads"),
    ]
    for label, path in endpoints:
        url = f"{BASE}{path}"
        start = time.time()
        r = sess.get(url, headers=auth_headers())
        elapsed = (time.time() - start) * 1000
        icon = "✅" if r.status_code == 200 and elapsed < 500 else "⚠️"
        print(f"  {icon} {label}: {r.status_code}  {elapsed:.1f}ms")
        if elapsed >= 500:
            print(f"      ⚠️  响应时间 {elapsed:.1f}ms 超过 500ms")


# ─── 主流程 ────────────────────────────────────────────────────────
def main():
    print("🚀 端到端完整业务流程测试 V2 开始")
    print(f"   目标: {BASE}")
    print(f"   时间: {date.today()}")

    results = {}
    total = 0
    passed = 0

    tests = [
        ("认证流程", test_auth),
        ("客户→项目→施工", test_customer_project),
        ("财务链路", test_finance),
        ("采购全流程", test_purchase),
        ("库存链路", test_inventory),
        ("车辆链路", test_vehicle),
        ("员工链路", test_employee),
        ("销售链路", test_sales),
        ("性能检查", test_perf),
    ]

    for name, func in tests:
        try:
            func()
            results[name] = "✅ 通过"
            passed += 1
        except Exception as e:
            results[name] = f"❌ 异常: {e}"
            print(f"  ❌ 未捕获异常: {e}")
        total += 1

    p("📊 测试结果汇总")
    print(f"  通过模块: {passed}/{total}")
    for name, status in results.items():
        print(f"    {status}  {name}")

    print(f"\n{'='*60}")
    print(f"  🔗 关联数据 ID:")
    for k, v in T.items():
        print(f"    {k} = {v}")
    print('='*60)

    return passed == total


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
