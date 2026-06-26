#!/usr/bin/env python3
"""
Session B 阶段 3 v4：全面业务流转测试（所有字段修正）
基于 v3 结果修正剩余 4 个 422 错误
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://127.0.0.1/api"
TOKEN = None
results = {"pass": 0, "fail": 0, "errors": []}

def login():
    print("🔑 登录...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin", "password": "admin123",
    }, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            global TOKEN
            TOKEN = data["data"]["token"]
            print("  ✅ 登录成功")
            return True
    print(f"  ❌ 登录失败: {resp.status_code} {resp.text[:200]}")
    return False

def auth_request(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TOKEN}"
    headers["Accept"] = "application/json"
    if method.upper() in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)

def expect(resp, desc):
    try:
        data = resp.json()
    except:
        data = {"raw": resp.text[:200]}
    ok = resp.status_code in [200, 201] and data.get("code", -1) in [0, None]
    if ok:
        results["pass"] += 1
        print(f"    ✅ {desc}")
        return True, data
    else:
        results["fail"] += 1
        msg = f"{desc} — {resp.status_code} {json.dumps(data, ensure_ascii=False)[:200]}"
        results["errors"].append(msg)
        print(f"    ❌ {msg}")
        return False, data

# ═════════════════════════════════════
# 1. 财务：应付（不传 supplier_id，它是 nullable）
# ═════════════════════════════════════
def test_payables():
    print("\n💰 [财务-应付] 测试...")
    print("  1️⃣ 创建应付款（不传 supplier_id）...")
    resp = auth_request("POST", "/finance/payables", json={
        # supplier_id 是 nullable，不传
        "amount": 50000,
        "status": "pending",
        "due_date": (date.today().replace(month=12, day=31)).strftime("%Y-%m-%d"),
        "notes": f"测试应付款 {datetime.now():%H:%M:%S}",
    })
    ok, data = expect(resp, "创建应付款")
    payable_id = data.get("data", {}).get("id") if ok else None

    if payable_id:
        print("  2️⃣ 创建付款记录...")
        resp = auth_request("POST", f"/finance/payables/{payable_id}/payments", json={
            "amount": 30000,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "bank_transfer",
            "remark": "测试付款",
        })
        expect(resp, "创建付款记录")

    print("  3️⃣ 查看应付款列表...")
    resp = auth_request("GET", "/finance/payables")
    expect(resp, "查询应付款列表")
    print("  ✅ 应付测试完成")

# ═════════════════════════════════════
# 2. 财务：发票
# ═════════════════════════════════════
def test_invoices():
    print("\n🧾 [财务-发票] 测试...")
    print("  1️⃣ 查看发票列表...")
    resp = auth_request("GET", "/finance/invoices")
    expect(resp, "查询发票列表")

    print("  2️⃣ 创建销项发票...")
    resp = auth_request("POST", "/finance/invoices", json={
        "type": "output",
        "customer_id": 1,
        "amount": 100000,
        "tax_amount": 13000,
        "total_amount": 113000,
        "invoice_number": f"TEST{datetime.now():%Y%m%d%H%M%S}",
        "invoice_date": date.today().strftime("%Y-%m-%d"),
    })
    expect(resp, "创建销项发票")

    print("  3️⃣ 创建进项发票...")
    resp = auth_request("POST", "/finance/invoices", json={
        "type": "input",
        "supplier_name": "测试供应商",
        "amount": 50000,
        "tax_amount": 6500,
        "total_amount": 56500,
        "invoice_number": f"PUR{datetime.now():%Y%m%d%H%M%S}",
        "invoice_date": date.today().strftime("%Y-%m-%d"),
    })
    expect(resp, "创建进项发票")
    print("  ✅ 发票测试完成")

# ═════════════════════════════════════
# 3. 报销
# ═════════════════════════════════════
def test_expenses():
    print("\n💸 [报销] 测试...")
    print("  1️⃣ 查看报销列表...")
    resp = auth_request("GET", "/expenses")
    expect(resp, "查询报销列表")

    print("  2️⃣ 创建报销单...")
    resp = auth_request("POST", "/expenses", json={
        "employee_id": 1,
        "amount": 3500,
        "category": "travel",
        "description": f"测试报销 {datetime.now():%H:%M:%S}",
        "expense_date": date.today().strftime("%Y-%m-%d"),
        "items": [
            {"name": "交通费", "amount": 2000, "date": date.today().strftime("%Y-%m-%d")},
            {"name": "住宿费", "amount": 1500, "date": date.today().strftime("%Y-%m-%d")},
        ],
    })
    ok, data = expect(resp, "创建报销单")
    claim_id = data.get("data", {}).get("id") if ok else None

    if claim_id:
        print("  3️⃣ 审批报销（带 action 字段）...")
        resp = auth_request("POST", f"/expenses/{claim_id}/approve", json={
            "action": "approved",
            "remark": "测试审批通过",
        })
        expect(resp, "审批报销单")
    print("  ✅ 报销测试完成")

# ═════════════════════════════════════
# 4. 审批中心
# ═════════════════════════════════════
def test_approvals():
    print("\n📋 [审批中心] 测试...")
    for name, path in [
        ("审批中心聚合", "/approvals/center"),
        ("审批统计", "/approvals/center/stats"),
        ("财务审批列表", "/approvals/finance"),
        ("运营审批列表", "/approvals/operation"),
        ("项目审批列表", "/approvals/project"),
    ]:
        print(f"  {name}...")
        resp = auth_request("GET", path)
        expect(resp, f"查询{name}")
    print("  ✅ 审批中心测试完成")

# ═════════════════════════════════════
# 5. 采购全流程
# ═════════════════════════════════════
def test_purchase():
    print("\n🛒 [采购] 测试...")
    today = date.today().strftime("%Y-%m-%d")

    # 5.1 采购需求（加 material 字段）
    print("  [5.1] 创建采购需求...")
    resp = auth_request("POST", "/purchase/requirements", json={
        "title": f"测试需求 {datetime.now():%H:%M:%S}",
        "material": "测试材料/安防设备",
        "quantity": 10,
        "estimated_amount": 50000,
        "urgency": "normal",
        "reason": "全面业务流转测试",
    })
    ok, data = expect(resp, "创建采购需求")
    req_id = data.get("data", {}).get("id") if ok else None

    # 5.2 采购计划
    if req_id:
        print("  [5.2] 创建采购计划...")
        resp = auth_request("POST", "/purchase/plans", json={
            "requirement_id": req_id,
            "title": f"测试计划 {datetime.now():%H:%M:%S}",
            "estimated_amount": 48000,
        })
        ok2, data2 = expect(resp, "创建采购计划")
        plan_id = data2.get("data", {}).get("id") if ok2 else None
        if plan_id:
            print("  [5.2] 提交采购计划...")
            resp = auth_request("POST", f"/purchase/plans/{plan_id}/submit")
            expect(resp, "提交采购计划")

    # 5.3~5.7 列表查询
    for name, path in [
        ("需求列表", "/purchase/requirements"),
        ("计划列表", "/purchase/plans"),
        ("合同列表", "/purchase/contracts"),
        ("付款申请列表", "/purchase/payment-requests"),
        ("付款列表", "/purchase/payments"),
        ("发货列表", "/purchase/shipments"),
        ("物流总览", "/purchase/logistics"),
    ]:
        print(f"  [{name}]...")
        resp = auth_request("GET", path)
        expect(resp, f"查询{name}")
    print("  ✅ 采购测试完成")

# ═════════════════════════════════════
# 6. 库存（先查仓库，再入库/出库）
# ═════════════════════════════════════
def test_inventory():
    print("\n📦 [库存] 测试...")
    code_suffix = datetime.now().strftime("%H%M%S")

    # 6.0 查仓库列表
    print("  [6.0] 查询仓库列表...")
    resp = auth_request("GET", "/inventory/warehouses")
    warehouse_id = None
    try:
        d = resp.json()
        # 响应可能是 {code:0, data:{data:[...]}} 或 [...]
        if isinstance(d, list):
            items = d
        elif isinstance(d, dict):
            items = d.get("data", {}).get("data", d.get("data", []))
        else:
            items = []
        if items:
            warehouse_id = items[0]["id"]
            print(f"    ✅ 找到仓库 ID: {warehouse_id}")
        else:
            print("    ⚠️ 没有仓库，跳过入库/出库测试")
    except Exception as e:
        print(f"    ⚠️ 解析仓库响应失败: {e}")
    # 不在这里 expect，避免计数问题
    if resp.status_code in [200, 201]:
        results["pass"] += 1
        print("    ✅ 查询仓库列表")
    else:
        results["fail"] += 1
        print(f"    ❌ 查询仓库列表 — {resp.status_code}")

    # 6.1 分类
    print("  [6.1] 创建分类...")
    resp = auth_request("POST", "/inventory-categories", json={
        "name": f"测试分类{code_suffix}",
        "description": "测试",
    })
    ok, data = expect(resp, "创建库存分类")
    cat_id = data.get("data", {}).get("id") if ok else None

    # 6.2 物资（加 code 字段）
    print("  [6.2] 创建物资...")
    if cat_id:
        resp = auth_request("POST", "/inventory", json={
            "code": f"TEST{code_suffix}",
            "name": f"测试物资{code_suffix}",
            "category_id": cat_id,
            "unit": "个",
            "specs": "测试规格",
        })
        ok2, data2 = expect(resp, "创建物资")
        item_id = data2.get("data", {}).get("id") if ok2 else None

        # 6.3 入库（加 warehouse_id 和 type 字段）
        if item_id and warehouse_id:
            print("  [6.3] 物资入库...")
            resp = auth_request("POST", "/inventory/stock-in", json={
                "inventory_item_id": item_id,
                "warehouse_id": warehouse_id,
                "quantity": 50,
                "type": "inbound",
                "remark": "测试入库",
            })
            expect(resp, "物资入库")

        # 6.4 出库（加 warehouse_id 和 type 字段）
        if item_id and warehouse_id:
            print("  [6.4] 物资出库...")
            resp = auth_request("POST", "/inventory/stock-out", json={
                "inventory_item_id": item_id,
                "warehouse_id": warehouse_id,
                "quantity": 10,
                "type": "outbound",
                "remark": "测试出库",
            })
            expect(resp, "物资出库")

    # 6.5 物资列表
    print("  [6.5] 物资列表...")
    resp = auth_request("GET", "/inventory")
    expect(resp, "查询物资列表")
    print("  ✅ 库存测试完成")

# ═════════════════════════════════════
# 7. 销售（修正 source 枚举值）
# ═════════════════════════════════════
def test_sales():
    print("\n💼 [销售] 测试...")
    now_str = datetime.now().strftime("%H%M%S")

    # 7.1 线索（修正 source 为有效枚举值）
    print("  [7.1] 创建线索...")
    resp = auth_request("POST", "/sales/leads", json={
        "customer_name": f"测试客户{now_str}",
        "contact_name": "测试联系人",
        "contact_phone": "13800138000",
        "source": "online",  # 有效值: online|phone|exhibition|referral|other
        "description": "全面业务流转测试",
    })
    ok, data = expect(resp, "创建线索")
    lead_id = data.get("data", {}).get("id") if ok else None

    # 7.2 商机列表
    print("  [7.2] 商机列表...")
    resp = auth_request("GET", "/sales/opps")
    expect(resp, "查询商机列表")

    # 7.3 产品
    print("  [7.3] 产品列表...")
    resp = auth_request("GET", "/sales/products")
    expect(resp, "查询产品列表")

    # 7.4 报价单
    print("  [7.4] 报价单列表...")
    resp = auth_request("GET", "/sales/quotes")
    expect(resp, "查询报价单列表")

    # 7.5 项目池
    print("  [7.5] 项目池列表...")
    resp = auth_request("GET", "/sales/pool")
    expect(resp, "查询项目池列表")

    print("  ✅ 销售测试完成")

# ═════════════════════════════════════
# 8. 车辆
# ═════════════════════════════════════
def test_vehicle_full():
    print("\n🚗 [车辆] 测试...")
    for name, path in [
        ("油卡列表", "/fuel-cards"),
        ("油卡充值记录", "/fuel-cards/recharges"),
        ("保险列表", "/vehicles/insurances"),
        ("保养列表", "/vehicles/maintenances"),
        ("用车申请列表", "/vehicles/usage"),
    ]:
        print(f"  [{name}]...")
        resp = auth_request("GET", path)
        expect(resp, f"查询{name}")
    print("  ✅ 车辆测试完成")

# ═════════════════════════════════════
# 9. 员工
# ═════════════════════════════════════
def test_employee_full():
    print("\n👥 [员工] 测试...")
    from datetime import timedelta
    today = date.today()
    start_str = today.strftime("%Y-%m-%d")
    end_str = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    this_month = today.strftime("%Y-%m")

    for name, path in [
        ("入职列表", "/employee-onboardings"),
        ("离职列表", "/employee-resignations"),
        ("考勤概览", "/attendance/overview"),
        ("考勤日历", "/attendance/calendar"),
        ("班次列表", "/schedules/shifts"),
    ]:
        print(f"  [{name}]...")
        resp = auth_request("GET", path)
        expect(resp, f"查询{name}")

    # 排班列表（带 start/end 参数）
    print("  [排班列表]（带日期参数）...")
    resp = auth_request("GET", f"/schedules?start={today}&end={next_month}")
    expect(resp, "查询排班列表")
    print("  ✅ 员工测试完成")

# ═════════════════════════════════════
# 10. 知识库 & 其他
# ═════════════════════════════════════
def test_knowledge_others():
    print("\n📚 [知识库&其他] 测试...")
    this_month = date.today().strftime("%Y-%m")

    for name, path in [
        ("知识库分类", "/knowledge/categories"),
        ("知识库文章", "/knowledge/articles"),
        ("客户漏斗", "/customers/pipeline"),
        ("仪表盘统计", "/dashboard/stats"),
    ]:
        print(f"  [{name}]...")
        resp = auth_request("GET", path)
        expect(resp, f"查询{name}")

    # 跟进日历（带 month 参数）
    print("  [跟进日历]（带 month 参数）...")
    resp = auth_request("GET", f"/follow-ups/calendar?month={this_month}")
    expect(resp, "查询跟进日历")
    print("  ✅ 知识库&其他测试完成")

# ═════════════════════════════════════
# MAIN
# ═════════════════════════════════════
def main():
    print("🚀 Session B 阶段 3 v4：全面业务流转测试（所有字段修正）")
    print("=" * 60)

    if not login():
        return

    tests = [
        ("财务-应付", test_payables),
        ("财务-发票", test_invoices),
        ("报销", test_expenses),
        ("审批中心", test_approvals),
        ("采购", test_purchase),
        ("库存", test_inventory),
        ("销售", test_sales),
        ("车辆", test_vehicle_full),
        ("员工", test_employee_full),
        ("知识库&其他", test_knowledge_others),
    ]

    for name, func in tests:
        try:
            func()
        except Exception as e:
            results["fail"] += 1
            err_msg = f"{name} 异常: {str(e)}"
            results["errors"].append(err_msg)
            print(f"  ❌ {err_msg}")

    # 汇总
    print("\n" + "=" * 60)
    print("📋 测试汇总")
    print("=" * 60)
    total = results["pass"] + results["fail"]
    print(f"总用例: {total}")
    print(f"  ✅ 通过: {results['pass']}")
    print(f"  ❌ 失败: {results['fail']}")
    if total > 0:
        print(f"  通过率: {results['pass']/total*100:.1f}%")

    if results["errors"]:
        print(f"\n❌ 失败详情:")
        for i, err in enumerate(results["errors"][:20], 1):
            print(f"  {i}. {err}")

    print(f"\n✅ 测试完成")
    return 0 if results["fail"] == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
