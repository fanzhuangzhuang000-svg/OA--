#!/usr/bin/env python3
"""
Session B 阶段 3：全面业务流转测试
覆盖所有核心业务模块，直到所有流程无 bug
在 172 服务器上直接运行，避免 Windows 端口限制
"""
import requests
import json
from datetime import datetime, date
import time

BASE_URL = "http://127.0.0.1/api"
TOKEN = None
results = {"pass": 0, "fail": 0, "errors": []}

def login():
    """登录获取 token"""
    print("🔑 登录获取 token...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123",
    }, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            global TOKEN
            TOKEN = data["data"]["token"]
            print(f"  ✅ 登录成功")
            return True
    
    print(f"  ❌ 登录失败: {resp.status_code} {resp.text[:200]}")
    return False

def auth_request(method, path, **kwargs):
    """带认证的请求"""
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TOKEN}"
    headers["Accept"] = "application/json"
    headers["Content-Type"] = kwargs.pop("force_content_type", "application/json")
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)

def expect(resp, desc, expected_status=200):
    """检查响应，返回 (success, data)"""
    try:
        data = resp.json()
    except:
        data = {"raw": resp.text[:200]}
    
    code_ok = resp.status_code == expected_status or data.get("code") == 0
    if code_ok:
        results["pass"] += 1
        print(f"    ✅ {desc}")
        return True, data
    else:
        results["fail"] += 1
        msg = f"{desc} — {resp.status_code} {json.dumps(data, ensure_ascii=False)[:150]}"
        results["errors"].append(msg)
        print(f"    ❌ {msg}")
        return False, data

# ═══════════════════════════════════════════
# 1. 💰 财务流转（应付 / 报销 / 发票）
# ═══════════════════════════════════════════
def test_payables_flow():
    """测试应付流转"""
    print("\n💰 [财务] 应付流转测试...")
    
    # 1. 创建应付款
    print("  1️⃣ 创建应付款...")
    payload = {
        "supplier_id": 1,
        "project_id": None,
        "amount": 50000,
        "paid_amount": 0,
        "status": "pending",
        "due_date": (date.today().replace(month=12, day=31)).strftime("%Y-%m-%d"),
        "note": f"测试应付款 {datetime.now().strftime('%H:%M:%S')}",
    }
    resp = auth_request("POST", "/finance/payables", json=payload)
    ok, data = expect(resp, "创建应付款")
    if not ok:
        # 尝试不带 supplier_id（可能字段名不同）
        print("    ⚠️ 尝试不同字段格式...")
        # 不 fail 整个测试，继续
        return
    payable_id = data.get("data", {}).get("id")
    if not payable_id:
        print("    ⚠️ 无法获取应付款 ID，跳过后续测试")
        return
    
    # 2. 创建付款记录
    print("  2️⃣ 创建付款记录 (30000)...")
    resp = auth_request("POST", f"/finance/payables/{payable_id}/payments", json={
        "amount": 30000,
        "payment_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "bank_transfer",
        "note": "测试付款 - 第一笔",
    })
    expect(resp, "创建付款记录 (第一笔)")
    
    # 3. 再付一笔（凑满）
    print("  3️⃣ 创建付款记录 (20000)...")
    resp = auth_request("POST", f"/finance/payables/{payable_id}/payments", json={
        "amount": 20000,
        "payment_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "bank_transfer",
        "note": "测试付款 - 第二笔",
    })
    expect(resp, "创建付款记录 (第二笔)")
    
    # 4. 查看应付款状态
    print("  4️⃣ 查看应付款列表...")
    resp = auth_request("GET", "/finance/payables")
    expect(resp, "查询应付款列表")
    print("  ✅ 应付流转测试完成")

def test_expense_flow():
    """测试报销流转"""
    print("\n💸 [财务] 报销流转测试...")
    
    # 1. 创建报销单
    print("  1️⃣ 创建报销单...")
    payload = {
        "employee_id": 1,
        "amount": 3500,
        "category": "travel",
        "description": f"测试报销 {datetime.now().strftime('%H:%M:%S')}",
        "expense_date": date.today().strftime("%Y-%m-%d"),
        "status": "pending",
    }
    resp = auth_request("POST", "/expenses", json=payload)
    ok, data = expect(resp, "创建报销单")
    if not ok:
        return
    expense_id = data.get("data", {}).get("id")
    
    # 2. 提交审批（如果有关联审批流）
    print("  2️⃣ 查看报销单详情...")
    if expense_id:
        resp = auth_request("GET", f"/expenses/{expense_id}")
        expect(resp, f"查看报销单详情 (ID:{expense_id})")
    
    print("  ✅ 报销流转测试完成")

def test_invoice_flow():
    """测试发票流转"""
    print("\n🧾 [财务] 发票流转测试...")
    
    # 1. 创建发票（销项）
    print("  1️⃣ 创建销项发票...")
    payload = {
        "type": "output",
        "customer_id": 1,
        "amount": 100000,
        "tax_amount": 13000,
        "total_amount": 113000,
        "invoice_number": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "invoice_date": date.today().strftime("%Y-%m-%d"),
        "status": "pending",
    }
    resp = auth_request("POST", "/invoices", json=payload)
    ok, data = expect(resp, "创建销项发票")
    
    # 2. 创建进项发票
    print("  2️⃣ 创建进项发票...")
    payload["type"] = "input"
    payload["supplier_id"] = 1
    del payload["customer_id"]
    payload["invoice_number"] = f"PUR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    resp = auth_request("POST", "/invoices", json=payload)
    expect(resp, "创建进项发票")
    
    # 3. 查看发票列表
    print("  3️⃣ 查看发票列表...")
    resp = auth_request("GET", "/invoices")
    expect(resp, "查询发票列表")
    
    print("  ✅ 发票流转测试完成")

# ═══════════════════════════════════════════
# 2. 📋 审批流转
# ═══════════════════════════════════════════
def test_approval_flow():
    """测试审批流转"""
    print("\n📋 [审批] 审批流转测试...")
    
    # 1. 查看审批模板列表
    print("  1️⃣ 查看审批模板列表...")
    resp = auth_request("GET", "/approval-templates")
    expect(resp, "查询审批模板列表")
    
    # 2. 查看审批中心（我的申请）
    print("  2️⃣ 查看我的申请...")
    resp = auth_request("GET", "/approval-center/my-applications")
    expect(resp, "查询我的申请")
    
    # 3. 查看待审列表
    print("  3️⃣ 查看待审列表...")
    resp = auth_request("GET", "/approval-center/pending")
    expect(resp, "查询待审列表")
    
    # 4. 查看审批历史
    print("  4️⃣ 查看审批历史...")
    resp = auth_request("GET", "/approval-center/history")
    expect(resp, "查询审批历史")
    
    print("  ✅ 审批流转测试完成")

# ═══════════════════════════════════════════
# 3. 🛒 采购流转
# ═══════════════════════════════════════════
def test_purchase_flow():
    """测试采购流转：需求 → 计划 → 合同 → 付款 → 发货 → 物流"""
    print("\n🛒 [采购] 采购全流转测试...")
    
    # 3.1 采购需求
    print("  [3.1] 采购需求...")
    resp = auth_request("POST", "/purchase-requirements", json={
        "title": f"测试采购需求 {datetime.now().strftime('%H:%M:%S')}",
        "description": "全面业务流转测试 - 采购需求",
        "quantity": 10,
        "estimated_amount": 50000,
        "urgency": "normal",
        "status": "pending",
    })
    ok, data = expect(resp, "创建采购需求")
    req_id = None
    if ok:
        req_id = data.get("data", {}).get("id")
    
    # 3.2 采购计划
    print("  [3.2] 采购计划...")
    resp = auth_request("POST", "/purchase-plans", json={
        "title": f"测试采购计划 {datetime.now().strftime('%H:%M:%S')}",
        "requirement_id": req_id,
        "estimated_amount": 48000,
        "status": "draft",
    })
    ok2, data2 = expect(resp, "创建采购计划")
    plan_id = None
    if ok2:
        plan_id = data2.get("data", {}).get("id")
    
    # 3.3 采购合同
    print("  [3.3] 采购合同...")
    resp = auth_request("POST", "/purchase-contracts", json={
        "plan_id": plan_id,
        "supplier_id": 1,
        "contract_number": f"PC{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "amount": 48000,
        "sign_date": date.today().strftime("%Y-%m-%d"),
        "status": "draft",
    })
    ok3, data3 = expect(resp, "创建采购合同")
    contract_id = None
    if ok3:
        contract_id = data3.get("data", {}).get("id")
    
    # 3.4 付款申请
    print("  [3.4] 付款申请...")
    resp = auth_request("POST", "/purchase-payments", json={
        "contract_id": contract_id,
        "amount": 48000,
        "payment_method": "bank_transfer",
        "payment_date": date.today().strftime("%Y-%m-%d"),
        "status": "pending",
    })
    expect(resp, "创建付款申请")
    
    # 3.5 发货记录
    print("  [3.5] 发货记录...")
    resp = auth_request("POST", "/purchase-shipments", json={
        "contract_id": contract_id,
        "shipment_number": f"SH{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "ship_date": date.today().strftime("%Y-%m-%d"),
        "status": "shipped",
    })
    expect(resp, "创建发货记录")
    
    # 3.6 物流信息
    print("  [3.6] 物流信息...")
    resp = auth_request("POST", "/purchase-logistics", json={
        "shipment_id": None,  # 如果有关联
        "tracking_number": f"TN{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "carrier": "测试物流",
        "status": "in_transit",
    })
    expect(resp, "创建物流信息")
    
    print("  ✅ 采购全流转测试完成")

# ═══════════════════════════════════════════
# 4. 📦 库存流转
# ═══════════════════════════════════════════
def test_inventory_flow():
    """测试库存流转：分类 → 物资 → 入库 → 出库"""
    print("\n📦 [库存] 库存流转测试...")
    
    # 4.1 库存分类
    print("  [4.1] 库存分类...")
    resp = auth_request("POST", "/inventory-categories", json={
        "name": f"测试分类{datetime.now().strftime('%H%M%S')}",
        "description": "全面业务流转测试 - 库存分类",
        "parent_id": None,
    })
    ok, data = expect(resp, "创建库存分类")
    cat_id = None
    if ok:
        cat_id = data.get("data", {}).get("id")
    
    # 4.2 物资信息
    print("  [4.2] 物资信息...")
    resp = auth_request("POST", "/inventories", json={
        "name": f"测试物资{datetime.now().strftime('%H%M%S')}",
        "category_id": cat_id,
        "unit": "个",
        "specs": "测试规格",
        "stock_quantity": 0,
        "min_stock": 5,
        "status": "active",
    })
    ok2, data2 = expect(resp, "创建物资信息")
    inv_id = None
    if ok2:
        inv_id = data2.get("data", {}).get("id")
    
    # 4.3 入库操作
    print("  [4.3] 入库操作...")
    resp = auth_request("POST", f"/inventories/{inv_id}/stock-in", json={
        "quantity": 50,
        "reason": "测试入库",
        "operator_id": 1,
    } if inv_id else {})
    if inv_id:
        expect(resp, "物资入库")
    else:
        print("    ⚠️ 无物资 ID，跳过入库测试")
    
    # 4.4 出库操作
    print("  [4.4] 出库操作...")
    if inv_id:
        resp = auth_request("POST", f"/inventories/{inv_id}/stock-out", json={
            "quantity": 10,
            "reason": "测试出库",
            "operator_id": 1,
        })
        expect(resp, "物资出库")
    
    # 4.5 查看库存列表
    print("  [4.5] 查看库存列表...")
    resp = auth_request("GET", "/inventories")
    expect(resp, "查询库存列表")
    
    print("  ✅ 库存流转测试完成")

# ═══════════════════════════════════════════
# 5. 💼 销售流转
# ═══════════════════════════════════════════
def test_sales_flow():
    """测试销售流转：客户 → 产品 → 订单"""
    print("\n💼 [销售] 销售流转测试...")
    
    # 5.1 销售产品
    print("  [5.1] 销售产品...")
    resp = auth_request("POST", "/sales-products", json={
        "name": f"测试产品{datetime.now().strftime('%H%M%S')}",
        "category": "安防设备",
        "unit_price": 5000,
        "description": "全面业务流转测试 - 销售产品",
        "status": "active",
    })
    ok, data = expect(resp, "创建销售产品")
    product_id = None
    if ok:
        product_id = data.get("data", {}).get("id")
    
    # 5.2 销售订单
    print("  [5.2] 销售订单...")
    resp = auth_request("POST", "/sales", json={
        "customer_id": 1,
        "product_id": product_id,
        "quantity": 5,
        "unit_price": 5000,
        "total_amount": 25000,
        "order_date": date.today().strftime("%Y-%m-%d"),
        "status": "pending",
    })
    expect(resp, "创建销售订单")
    
    # 5.3 查看销售列表
    print("  [5.3] 查看销售列表...")
    resp = auth_request("GET", "/sales")
    expect(resp, "查询销售列表")
    
    print("  ✅ 销售流转测试完成")

# ═══════════════════════════════════════════
# 6. ⛽ 车辆管理流转
# ═══════════════════════════════════════════
def test_vehicle_flow():
    """测试车辆管理流转：加油卡 → 维修保养 → 保险"""
    print("\n⛽ [车辆] 车辆管理流转测试...")
    
    # 6.1 加油卡管理
    print("  [6.1] 加油卡充值/记录...")
    resp = auth_request("POST", "/fuel-cards/recharge", json={
        "vehicle_id": 1,
        "amount": 1000,
        "recharge_date": date.today().strftime("%Y-%m-%d"),
        "note": "测试加油卡充值",
    })
    expect(resp, "加油卡充值")
    
    # 6.2 维修保养记录
    print("  [6.2] 维修保养记录...")
    resp = auth_request("POST", "/vehicles/1/maintenances", json={
        "maintenance_date": date.today().strftime("%Y-%m-%d"),
        "mileage": 50000,
        "type": "regular",
        "cost": 800,
        "description": "测试维修保养",
        "status": "completed",
    })
    expect(resp, "创建维修保养记录")
    
    # 6.3 保险记录
    print("  [6.3] 保险记录...")
    resp = auth_request("POST", "/vehicles/1/insurances", json={
        "insurance_company": "测试保险公司",
        "policy_number": f"INS{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "start_date": date.today().strftime("%Y-%m-%d"),
        "end_date": (date.today().replace(year=date.today().year+1)).strftime("%Y-%m-%d"),
        "amount": 5000,
        "status": "active",
    })
    expect(resp, "创建保险记录")
    
    print("  ✅ 车辆管理流转测试完成")

# ═══════════════════════════════════════════
# 7. 👥 员工管理流转
# ═══════════════════════════════════════════
def test_employee_flow():
    """测试员工管理流转：入职 → 考勤 → 排班 → 离职"""
    print("\n👥 [员工] 员工管理流转测试...")
    
    # 7.1 员工入职
    print("  [7.1] 员工入职...")
    resp = auth_request("POST", "/employee-onboarding", json={
        "name": f"测试员工{datetime.now().strftime('%H%M%S')}",
        "gender": "male",
        "phone": "13800138000",
        "email": "test@example.com",
        "department_id": 1,
        "position_id": 1,
        "join_date": date.today().strftime("%Y-%m-%d"),
        "status": "pending",
    })
    ok, data = expect(resp, "员工入职申请")
    onboarding_id = None
    if ok:
        onboarding_id = data.get("data", {}).get("id")
    
    # 7.2 考勤记录
    print("  [7.2] 考勤记录...")
    resp = auth_request("POST", "/attendance/check-in", json={
        "employee_id": 1,
        "check_in_time": f"{date.today()} 09:00:00",
        "note": "测试打卡",
    })
    expect(resp, "考勤打卡")
    
    # 7.3 查看考勤列表
    print("  [7.3] 查看考勤列表...")
    resp = auth_request("GET", "/attendance")
    expect(resp, "查询考勤列表")
    
    # 7.4 排班/日程
    print("  [7.4] 日程安排...")
    resp = auth_request("POST", "/schedules", json={
        "employee_id": 1,
        "title": f"测试日程{datetime.now().strftime('%H%M%S')}",
        "start_time": f"{date.today()} 10:00:00",
        "end_time": f"{date.today()} 11:00:00",
        "type": "meeting",
    })
    expect(resp, "创建日程安排")
    
    print("  ✅ 员工管理流转测试完成")

# ═══════════════════════════════════════════
# 8. 📊 仪表盘 & 知识库
# ═══════════════════════════════════════════
def test_dashboard_knowledge():
    """测试仪表盘和知识库"""
    print("\n📊 [仪表盘/知识库] 测试...")
    
    # 8.1 仪表盘
    print("  [8.1] 仪表盘数据...")
    resp = auth_request("GET", "/dashboard/stats")
    expect(resp, "查询仪表盘统计")
    
    # 8.2 知识库
    print("  [8.2] 知识库列表...")
    resp = auth_request("GET", "/knowledge")
    expect(resp, "查询知识库列表")
    
    # 8.3 客户漏斗
    print("  [8.3] 客户漏斗...")
    resp = auth_request("GET", "/customer-pipeline")
    expect(resp, "查询客户漏斗")
    
    # 8.4 跟进日历
    print("  [8.4] 跟进日历...")
    resp = auth_request("GET", "/follow-up-calendar")
    expect(resp, "查询跟进日历")
    
    print("  ✅ 仪表盘/知识库测试完成")

# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("🚀 Session B 阶段 3：全面业务流转测试")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 登录
    if not login():
        print("❌ 登录失败，测试终止")
        return
    
    # 执行所有测试
    tests = [
        ("💰 财务(应付)", test_payables_flow),
        ("💸 财务(报销)", test_expense_flow),
        ("🧾 财务(发票)", test_invoice_flow),
        ("📋 审批", test_approval_flow),
        ("🛒 采购", test_purchase_flow),
        ("📦 库存", test_inventory_flow),
        ("💼 销售", test_sales_flow),
        ("⛽ 车辆", test_vehicle_flow),
        ("👥 员工", test_employee_flow),
        ("📊 仪表盘", test_dashboard_knowledge),
    ]
    
    for name, func in tests:
        try:
            func()
        except Exception as e:
            results["fail"] += 1
            err_msg = f"{name} 异常: {str(e)}"
            results["errors"].append(err_msg)
            print(f"  ❌ {err_msg}")
    
    # 汇总报告
    print("\n" + "=" * 60)
    print("📋 测试汇总报告")
    print("=" * 60)
    total = results["pass"] + results["fail"]
    print(f"总测试用例: {total}")
    print(f"  ✅ 通过: {results['pass']}")
    print(f"  ❌ 失败: {results['fail']}")
    if total > 0:
        print(f"  通过率: {results['pass']/total*100:.1f}%")
    
    if results["errors"]:
        print("\n❌ 失败详情:")
        for i, err in enumerate(results["errors"], 1):
            print(f"  {i}. {err}")
    
    print("\n✅ 全面业务流转测试完成")
    
    # 返回状态码
    import sys
    sys.exit(0 if results["fail"] == 0 else 1)

if __name__ == "__main__":
    main()
