#!/usr/bin/env python3
"""
Session B 阶段 3 v2：全面业务流转测试（基于真实路由表）
 Corrected version - uses actual API endpoints from routes/api.php
"""
import requests
import json
from datetime import datetime, date
import time

BASE_URL = "http://127.0.0.1/api"
TOKEN = None
results = {"pass": 0, "fail": 0, "errors": [], "bugs": []}

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

def expect(resp, desc, check_fields=None):
    """检查响应"""
    try:
        data = resp.json()
    except:
        data = {"raw": resp.text[:200]}
    
    # 201 也是成功（创建）
    ok = resp.status_code in [200, 201] and data.get("code", -1) in [0, None]
    
    if ok:
        results["pass"] += 1
        print(f"    ✅ {desc}")
        # 检查返回字段
        if check_fields and isinstance(data.get("data"), dict):
            for f in check_fields:
                if f not in data["data"]:
                    print(f"      ⚠️ 缺少字段: {f}")
        return True, data
    else:
        results["fail"] += 1
        msg = f"{desc} — {resp.status_code} {json.dumps(data, ensure_ascii=False)[:200]}"
        results["errors"].append(msg)
        print(f"    ❌ {msg}")
        return False, data

# ═══════════════════════════════════════════
# 1. 财务：应付
# ═══════════════════════════════════════════
def test_payables():
    print("\n💰 [财务-应付] 测试...")
    # 先查供应商列表（获取有效 ID）
    print("  0️⃣ 获取供应商列表...")
    resp = auth_request("GET", "/customers?type=supplier")
    supplier_id = 1
    if resp.status_code == 200:
        d = resp.json()
        items = d.get("data", {}).get("data", [])
        if items:
            supplier_id = items[0].get("id", 1)
            print(f"    ✅ 找到供应商 ID: {supplier_id}")
        else:
            # 没有供应商，用普通客户
            resp2 = auth_request("GET", "/customers")
            if resp2.status_code == 200:
                d2 = resp2.json()
                items2 = d2.get("data", {}).get("data", [])
                if items2:
                    supplier_id = items2[0].get("id", 1)
                    print(f"    ⚠️ 用客户 ID 代替: {supplier_id}")
    
    # 1. 创建应付款
    print("  1️⃣ 创建应付款...")
    resp = auth_request("POST", "/finance/payables", json={
        "supplier_id": supplier_id,
        "amount": 50000,
        "status": "pending",
        "due_date": (date.today().replace(month=12, day=31)).strftime("%Y-%m-%d"),
        "note": f"测试应付款 {datetime.now():%H:%M:%S}",
    })
    ok, data = expect(resp, "创建应付款")
    payable_id = None
    if ok:
        payable_id = data.get("data", {}).get("id")
    
    # 2. 付款
    if payable_id:
        print("  2️⃣ 创建付款记录 (30000)...")
        resp = auth_request("POST", f"/finance/payables/{payable_id}/payments", json={
            "amount": 30000,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "bank_transfer",
            "note": "测试付款",
        })
        expect(resp, "创建付款记录")
    
    # 3. 列表
    print("  3️⃣ 查看应付款列表...")
    resp = auth_request("GET", "/finance/payables")
    expect(resp, "查询应付款列表")
    print("  ✅ 应付测试完成")

# ═══════════════════════════════════════════
# 2. 财务：发票
# ═══════════════════════════════════════════
def test_invoices():
    print("\n🧾 [财务-发票] 测试...")
    # 1. 列表
    print("  1️⃣ 查看发票列表...")
    resp = auth_request("GET", "/finance/invoices")
    expect(resp, "查询发票列表")
    
    # 2. 创建销项发票
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
    ok, data = expect(resp, "创建销项发票")
    
    # 3. 创建进项发票
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

# ═══════════════════════════════════════════
# 3. 报销
# ═══════════════════════════════════════════
def test_expenses():
    print("\n💸 [报销] 测试...")
    # 1. 列表
    print("  1️⃣ 查看报销列表...")
    resp = auth_request("GET", "/expenses")
    expect(resp, "查询报销列表")
    
    # 2. 创建报销（先查字段要求）
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
    
    if ok:
        claim_id = data.get("data", {}).get("id")
        # 3. 审批
        print("  3️⃣ 审批报销...")
        resp = auth_request("POST", f"/expenses/{claim_id}/approve")
        expect(resp, "审批报销单")
    print("  ✅ 报销测试完成")

# ═══════════════════════════════════════════
# 4. 审批中心
# ═══════════════════════════════════════════
def test_approvals():
    print("\n📋 [审批中心] 测试...")
    print("  1️⃣ 审批中心（聚合）...")
    resp = auth_request("GET", "/approvals/center")
    expect(resp, "查询审批中心")
    
    print("  2️⃣ 审批统计...")
    resp = auth_request("GET", "/approvals/center/stats")
    expect(resp, "查询审批统计")
    
    print("  3️⃣ 财务审批列表...")
    resp = auth_request("GET", "/approvals/finance")
    expect(resp, "查询财务审批列表")
    
    print("  4️⃣ 运营审批列表...")
    resp = auth_request("GET", "/approvals/operation")
    expect(resp, "查询运营审批列表")
    
    print("  5️⃣ 项目审批列表...")
    resp = auth_request("GET", "/approvals/project")
    expect(resp, "查询项目审批列表")
    
    print("  ✅ 审批中心测试完成")

# ═══════════════════════════════════════════
# 5. 采购全流程
# ═══════════════════════════════════════════
def test_purchase():
    print("\n🛒 [采购] 测试...")
    
    # 5.1 采购需求
    print("  [5.1] 采购需求列表...")
    resp = auth_request("GET", "/purchase/requirements")
    expect(resp, "查询采购需求列表")
    
    print("  [5.1] 创建采购需求...")
    resp = auth_request("POST", "/purchase/requirements", json={
        "title": f"测试需求 {datetime.now():%H:%M:%S}",
        "description": "全面业务流转测试",
        "quantity": 10,
        "estimated_amount": 50000,
        "urgency": "normal",
    })
    ok, data = expect(resp, "创建采购需求")
    req_id = data.get("data", {}).get("id") if ok else None
    
    # 5.2 采购计划
    print("  [5.2] 采购计划列表...")
    resp = auth_request("GET", "/purchase/plans")
    expect(resp, "查询采购计划列表")
    
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
    
    # 5.3 采购合同
    print("  [5.3] 采购合同列表...")
    resp = auth_request("GET", "/purchase/contracts")
    expect(resp, "查询采购合同列表")
    
    # 5.4 付款申请
    print("  [5.4] 付款申请列表...")
    resp = auth_request("GET", "/purchase/payment-requests")
    expect(resp, "查询付款申请列表")
    
    # 5.5 付款
    print("  [5.5] 付款列表...")
    resp = auth_request("GET", "/purchase/payments")
    expect(resp, "查询付款列表")
    
    # 5.6 发货
    print("  [5.6] 发货列表...")
    resp = auth_request("GET", "/purchase/shipments")
    expect(resp, "查询发货列表")
    
    # 5.7 物流
    print("  [5.7] 物流总览...")
    resp = auth_request("GET", "/purchase/logistics")
    expect(resp, "查询物流总览")
    
    print("  ✅ 采购测试完成")

# ═══════════════════════════════════════════
# 6. 库存
# ═══════════════════════════════════════════
def test_inventory():
    print("\n📦 [库存] 测试...")
    
    # 6.1 分类
    print("  [6.1] 分类树...")
    resp = auth_request("GET", "/inventory-categories/tree")
    expect(resp, "查询分类树")
    
    print("  [6.1] 创建分类...")
    resp = auth_request("POST", "/inventory-categories", json={
        "name": f"测试分类{datetime.now():%H%M%S}",
        "description": "测试",
    })
    ok, data = expect(resp, "创建库存分类")
    cat_id = data.get("data", {}).get("id") if ok else None
    
    # 6.2 物资
    print("  [6.2] 物资列表...")
    resp = auth_request("GET", "/inventory")
    expect(resp, "查询物资列表")
    
    if cat_id:
        print("  [6.2] 创建物资...")
        resp = auth_request("POST", "/inventory", json={
            "name": f"测试物资{datetime.now():%H%M%S}",
            "category_id": cat_id,
            "unit": "个",
            "specs": "测试规格",
        })
        ok2, data2 = expect(resp, "创建物资")
        item_id = data2.get("data", {}).get("id") if ok2 else None
        
        # 6.3 入库
        if item_id:
            print("  [6.3] 物资入库...")
            resp = auth_request("POST", "/inventory/stock-in", json={
                "inventory_item_id": item_id,
                "quantity": 50,
                "reason": "测试入库",
            })
            expect(resp, "物资入库")
            
            # 6.4 出库
            print("  [6.4] 物资出库...")
            resp = auth_request("POST", "/inventory/stock-out", json={
                "inventory_item_id": item_id,
                "quantity": 10,
                "reason": "测试出库",
            })
            expect(resp, "物资出库")
    
    print("  ✅ 库存测试完成")

# ═══════════════════════════════════════════
# 7. 销售
# ═══════════════════════════════════════════
def test_sales():
    print("\n💼 [销售] 测试...")
    
    # 7.1 线索池
    print("  [7.1] 线索列表...")
    resp = auth_request("GET", "/sales/leads")
    expect(resp, "查询线索列表")
    
    print("  [7.1] 创建线索...")
    resp = auth_request("POST", "/sales/leads", json={
        "name": f"测试线索{datetime.now():%H%M%S}",
        "phone": "13800138000",
        "source": "website",
    })
    ok, data = expect(resp, "创建线索")
    lead_id = data.get("data", {}).get("id") if ok else None
    
    # 7.2 商机池
    print("  [7.2] 商机列表...")
    resp = auth_request("GET", "/sales/opps")
    expect(resp, "查询商机列表")
    
    # 7.3 产品库
    print("  [7.3] 产品列表...")
    resp = auth_request("GET", "/sales/products")
    expect(resp, "查询产品列表")
    
    print("  [7.3] 产品分类...")
    resp = auth_request("GET", "/sales/products/categories")
    expect(resp, "查询产品分类")
    
    # 7.4 报价单
    print("  [7.4] 报价单列表...")
    resp = auth_request("GET", "/sales/quotes")
    expect(resp, "查询报价单列表")
    
    # 7.5 项目池
    print("  [7.5] 项目池列表...")
    resp = auth_request("GET", "/sales/pool")
    expect(resp, "查询项目池列表")
    
    print("  ✅ 销售测试完成")

# ═══════════════════════════════════════════
# 8. 车辆
# ═══════════════════════════════════════════
def test_vehicle_full():
    print("\n🚗 [车辆] 测试...")
    
    # 8.1 油卡
    print("  [8.1] 油卡列表...")
    resp = auth_request("GET", "/fuel-cards")
    expect(resp, "查询油卡列表")
    
    print("  [8.1] 油卡充值记录...")
    resp = auth_request("GET", "/fuel-cards/recharges")
    expect(resp, "查询油卡充值记录")
    
    # 8.2 保险
    print("  [8.2] 保险列表...")
    resp = auth_request("GET", "/vehicles/insurances")
    expect(resp, "查询保险列表")
    
    # 8.3 保养
    print("  [8.3] 保养列表...")
    resp = auth_request("GET", "/vehicles/maintenances")
    expect(resp, "查询保养列表")
    
    # 8.4 用车申请
    print("  [8.4] 用车申请列表...")
    resp = auth_request("GET", "/vehicles/usage")
    expect(resp, "查询用车申请列表")
    
    print("  ✅ 车辆测试完成")

# ═══════════════════════════════════════════
# 9. 员工
# ═══════════════════════════════════════════
def test_employee_full():
    print("\n👥 [员工] 测试...")
    
    # 9.1 入职
    print("  [9.1] 入职列表...")
    resp = auth_request("GET", "/employee-onboardings")
    expect(resp, "查询入职列表")
    
    # 9.2 离职
    print("  [9.2] 离职列表...")
    resp = auth_request("GET", "/employee-resignations")
    expect(resp, "查询离职列表")
    
    # 9.3 考勤
    print("  [9.3] 考勤概览...")
    resp = auth_request("GET", "/attendance/overview")
    expect(resp, "查询考勤概览")
    
    print("  [9.3] 考勤日历...")
    resp = auth_request("GET", "/attendance/calendar")
    expect(resp, "查询考勤日历")
    
    # 9.4 排班
    print("  [9.4] 排班列表...")
    resp = auth_request("GET", "/schedules")
    expect(resp, "查询排班列表")
    
    print("  [9.4] 班次列表...")
    resp = auth_request("GET", "/schedules/shifts")
    expect(resp, "查询班次列表")
    
    print("  ✅ 员工测试完成")

# ═══════════════════════════════════════════
# 10. 知识库 & 其他
# ═══════════════════════════════════════════
def test_knowledge_others():
    print("\n📚 [知识库&其他] 测试...")
    
    print("  [知识库] 分类列表...")
    resp = auth_request("GET", "/knowledge/categories")
    expect(resp, "查询知识库分类")
    
    print("  [知识库] 文章列表...")
    resp = auth_request("GET", "/knowledge/articles")
    expect(resp, "查询知识库文章")
    
    print("  [客户漏斗] 漏斗数据...")
    resp = auth_request("GET", "/customers/pipeline")
    expect(resp, "查询客户漏斗")
    
    print("  [跟进日历] 日历数据...")
    resp = auth_request("GET", "/follow-ups/calendar")
    expect(resp, "查询跟进日历")
    
    print("  [仪表盘] 统计...")
    resp = auth_request("GET", "/dashboard/stats")
    expect(resp, "查询仪表盘统计")
    
    print("  ✅ 知识库&其他测试完成")

# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("🚀 Session B 阶段 3 v2：全面业务流转测试（基于真实路由）")
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
        print(f"\n❌ 失败详情（前 20 条）:")
        for i, err in enumerate(results["errors"][:20], 1):
            print(f"  {i}. {err}")
    
    print(f"\n✅ 测试完成 — 通过率: {results['pass']}/{total}")

if __name__ == "__main__":
    main()
