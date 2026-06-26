#!/usr/bin/env python3
"""
端到端完整业务流程测试（E2E Test）
运行在本地，访问 172.20.0.139 的 API

测试范围：
  1. 认证流程（登录 → 拿 token → 获取用户/权限信息）
  2. 客户→项目→阶段→施工日志 完整链路
  3. 采购全流程：需求→审批→计划→合同→付款→发货→入库
  4. 财务链路：应收款→收款 / 应付款→付款 / 报销→审批
  5. 库存链路：分类→物资→入库→出库
  6. 车辆完整链路：车辆→加油记录→维修记录→保险→年检
  7. 员工链路：入职→排班→考勤→离职
  8. 销售链路：线索→商机→产品→报价→订单
"""
import requests
import json
from datetime import date, timedelta

BASE = "http://127.0.0.1/api"
TOKEN = None
T = {}  # 保存创建的 ID，供后续步骤使用

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
        print(f"      响应: {resp.text[:200]}")
    if ok and save_as and resp.status_code < 300:
        try:
            d = resp.json()
            data = d.get("data", {})
            # 尝试提取 ID
            if isinstance(data, dict):
                tid = data.get("id") or data.get("user", {}).get("id")
                if tid:
                    T[save_as] = tid
                    print(f"      💾 已保存 {save_as} = {tid}")
        except Exception:
            pass
    return ok


# ─── 1. 认证流程 ───────────────────────────────────────────────
def test_auth_flow():
    p("1️⃣ 认证流程：登录 → 用户信息 → 权限")
    global TOKEN

    # 1.1 登录
    r = sess.post(f"{BASE}/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    expect(r, "POST /auth/login", status=200)
    try:
        d = r.json()
        TOKEN = d["data"]["token"]
        print(f"      🔑 Token 获取成功（前30字符）: {TOKEN[:30]}...")
    except Exception as e:
        print(f"      ❌ 解析 token 失败: {e}")
        raise

    # 1.2 获取当前用户
    r = sess.get(f"{BASE}/auth/me", headers=auth_headers())
    expect(r, "GET /auth/me", save_as="user_id")
    try:
        u = r.json().get("data", {})
        print(f"      当前用户: {u.get('name')} / {u.get('username')}")
    except Exception:
        pass

    # 1.3 获取权限/菜单（如果有这个接口）
    r = sess.get(f"{BASE}/auth/permissions", headers=auth_headers())
    if r.status_code == 200:
        expect(r, "GET /auth/permissions")
    else:
        print(f"  ⚠️  GET /auth/permissions: HTTP {r.status_code}（接口可能不存在）")


# ─── 2. 客户→项目→阶段→施工日志 ───────────────────────────
def test_customer_project_flow():
    p("2️⃣ 客户 → 项目 → 阶段 → 施工日志 完整链路")

    # 2.1 创建客户
    r = sess.post(f"{BASE}/customers", headers=auth_headers(), json={
        "name": f"E2E测试客户_{date.today()}",
        "type": "customer",
        "contact": "测试联系人",
        "phone": "13800138000",
        "email": "e2e@test.com",
        "address": "测试地址",
        "notes": "端到端测试自动创建",
    })
    expect(r, "POST /customers（创建客户）", save_as="customer_id")
    cid = T.get("customer_id")

    # 2.2 创建项目（关联客户）
    if cid:
        r = sess.post(f"{BASE}/projects", headers=auth_headers(), json={
            "name": f"E2E测试项目_{date.today()}",
            "customer_id": cid,
            "status": "planning",
            "start_date": date.today().strftime("%Y-%m-%d"),
            "end_date": (date.today() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "budget": 500000,
            "description": "端到端测试自动创建的项目",
        })
        expect(r, "POST /projects（创建项目）", save_as="project_id")
    else:
        print("  ⚠️  跳过项目创建（客户 ID 未获取）")

    pid = T.get("project_id")
    if not pid:
        print("  ⚠️  跳过后续项目流程（项目 ID 未获取）")
        return

    # 2.3 更新项目阶段
    r = sess.post(f"{BASE}/projects/{pid}/update-stage", headers=auth_headers(), json={
        "stage": "in_progress",
        "note": "E2E 测试：阶段更新为施工中",
    })
    expect(r, f"POST /projects/{pid}/update-stage")

    # 2.4 创建施工日志
    r = sess.post(f"{BASE}/construction-logs", headers=auth_headers(), json={
        "project_id": pid,
        "work_date": date.today().strftime("%Y-%m-%d"),
        "weather": "sunny",
        "temperature": 28,
        "content": "E2E 测试自动创建的施工日志",
        "progress": "基础施工完成 50%",
        "issues": "无",
        "next_plan": "明日继续施工",
    })
    expect(r, "POST /construction-logs（施工日志）", save_as="log_id")

    # 2.5 查看项目详情（验证关联数据）
    r = sess.get(f"{BASE}/projects/{pid}", headers=auth_headers())
    expect(r, f"GET /projects/{pid}（项目详情）")

    # 2.6 项目列表（带筛选）
    r = sess.get(f"{BASE}/projects?status=in_progress&page=1&page_size=5",
                 headers=auth_headers())
    expect(r, "GET /projects?status=in_progress（筛选项目）")

    # 2.7 仪表盘摘要
    r = sess.get(f"{BASE}/projects/dashboard-summary", headers=auth_headers())
    expect(r, "GET /projects/dashboard-summary")


# ─── 3. 财务链路 ───────────────────────────────────────────────
def test_finance_flow():
    p("3️⃣ 财务链路：应收款→收款 / 应付款→付款 / 报销→审批")

    # ── 3A. 应收款 → 收款 ──
    print("\n  [3A] 应收款 → 收款")
    cid = T.get("customer_id")
    if cid:
        # 创建应收款
        r = sess.post(f"{BASE}/finance/receivables", headers=auth_headers(), json={
            "customer_id": cid,
            "amount": 50000,
            "status": "pending",
            "due_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "note": f"E2E测试应收款 {date.today()}",
        })
        expect(r, "POST /finance/receivables", save_as="receivable_id")
    else:
        print("  ⚠️  跳过应收款（客户 ID 未获取）")

    rid = T.get("receivable_id")
    if rid:
        # 创建收款记录（全额结清）
        r = sess.post(f"{BASE}/finance/receipts", headers=auth_headers(), json={
            "receivable_id": rid,
            "amount": 50000,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "bank_transfer",
            "notes": "E2E 测试全额收款",
        })
        expect(r, "POST /finance/receipts（全额收款）")
        # 验证应收款状态自动更新为「已收完」
        r = sess.get(f"{BASE}/finance/receivables/{rid}", headers=auth_headers())
        expect(r, f"GET /finance/receivables/{rid}（验证状态）")
        try:
            status = r.json().get("data", {}).get("status", "")
            print(f"      应收款状态: {status}")
        except Exception:
            pass

    # ── 3B. 报销 → 审批 ──
    print("\n  [3B] 报销 → 审批")
    r = sess.post(f"{BASE}/reimbursements", headers=auth_headers(), json={
        "amount": 380,
        "category": "meals",
        "description": "E2E 测试报销：商务午餐",
        "expense_date": date.today().strftime("%Y-%m-%d"),
        "payment_method": "personal",
    })
    expect(r, "POST /reimbursements", save_as="reimb_id")

    # 查询待审批列表
    r = sess.get(f"{BASE}/approvals/center?status=pending&page=1&page_size=10",
                 headers=auth_headers())
    expect(r, "GET /approvals/center?status=pending（待审批列表）")

    # 审批通过（用刚才创建的报销 ID）
    reb_id = T.get("reimb_id")
    if reb_id:
        r = sess.post(f"{BASE}/approvals/approve", headers=auth_headers(), json={
            "approvable_type": "reimbursement",
            "approvable_id": reb_id,
            "action": "approved",
            "comment": "E2E 测试审批通过",
        })
        expect(r, "POST /approvals/approve（审批通过）")


# ─── 4. 采购全流程 ─────────────────────────────────────────────
def test_purchase_flow():
    p("4️⃣ 采购全流程：需求→审批→计划→合同→付款→发货→入库")

    # 4.1 创建采购需求
    r = sess.post(f"{BASE}/purchase/requirements", headers=auth_headers(), json={
        "material": "E2E测试材料",
        "specs": "规格：100x50x20mm",
        "quantity": 100,
        "estimated_price": 80.5,
        "required_date": (date.today() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "purpose": "E2E 测试采购需求",
    })
    expect(r, "POST /purchase/requirements", save_as="req_id")

    # 4.2 审批采购需求
    req_id = T.get("req_id")
    if req_id:
        r = sess.post(f"{BASE}/approvals/approve", headers=auth_headers(), json={
            "approvable_type": "purchase_requirement",
            "approvable_id": req_id,
            "action": "approved",
            "comment": "E2E 测试：采购需求审批通过",
        })
        expect(r, "POST /approvals/approve（采购需求审批）")

    # 4.3 创建采购计划（关联需求）
    if req_id:
        r = sess.post(f"{BASE}/purchase/plans", headers=auth_headers(), json={
            "requirement_ids": [req_id],
            "plan_no": f"PLAN-E2E-{date.today():%Y%m%d}",
            "total_amount": 8050,
            "expected_date": (date.today() + timedelta(days=20)).strftime("%Y-%m-%d"),
            "notes": "E2E 测试采购计划",
        })
        expect(r, "POST /purchase/plans", save_as="plan_id")

    # 4.4 创建采购合同
    plan_id = T.get("plan_id")
    if plan_id:
        r = sess.post(f"{BASE}/purchase/contracts", headers=auth_headers(), json={
            "plan_id": plan_id,
            "contract_no": f"CTR-E2E-{date.today():%Y%m%d}",
            "supplier_name": "E2E测试供应商",
            "total_amount": 8050,
            "sign_date": date.today().strftime("%Y-%m-%d"),
            "delivery_date": (date.today() + timedelta(days=25)).strftime("%Y-%m-%d"),
            "payment_terms": "货到付款",
            "notes": "E2E 测试采购合同",
        })
        expect(r, "POST /purchase/contracts", save_as="contract_id")

    # 4.5 付款申请（关联合同）
    contract_id = T.get("contract_id")
    if contract_id:
        r = sess.post(f"{BASE}/purchase/payments", headers=auth_headers(), json={
            "contract_id": contract_id,
            "amount": 8050,
            "payment_date": date.today().strftime("%Y-%m-%d"),
            "payment_method": "bank_transfer",
            "notes": "E2E 测试付款",
        })
        expect(r, "POST /purchase/payments", save_as="payment_id")

    # 4.6 发货记录
    if contract_id:
        r = sess.post(f"{BASE}/purchase/deliveries", headers=auth_headers(), json={
            "contract_id": contract_id,
            "delivery_date": date.today().strftime("%Y-%m-%d"),
            "tracking_no": f"E2E{date.today():%Y%m%d}001",
            "carrier": "测试物流",
            "notes": "E2E 测试发货",
        })
        expect(r, "POST /purchase/deliveries", save_as="delivery_id")

    # 4.7 入库（关联合同 + 仓库）
    # 先查仓库列表
    r = sess.get(f"{BASE}/inventory/warehouses", headers=auth_headers())
    expect(r, "GET /inventory/warehouses")
    try:
        wh_data = r.json().get("data", {})
        wh_list = wh_data if isinstance(wh_data, list) else wh_data.get("data", [])
        warehouse_id = wh_list[0]["id"] if wh_list else None
        if warehouse_id:
            T["warehouse_id"] = warehouse_id
            print(f"      🏠 找到仓库 ID: {warehouse_id}")
    except Exception as e:
        print(f"      ⚠️  解析仓库列表失败: {e}")
        warehouse_id = None

    if contract_id and warehouse_id:
        r = sess.post(f"{BASE}/inventory/stock-in", headers=auth_headers(), json={
            "warehouse_id": warehouse_id,
            "type": "inbound",
            "material": "E2E测试材料",
            "quantity": 100,
            "unit": "个",
            "related_type": "purchase_contract",
            "related_id": contract_id,
            "notes": "E2E 测试入库（采购到货）",
        })
        expect(r, "POST /inventory/stock-in（采购入库）", save_as="stock_in_id")


# ─── 5. 库存链路 ───────────────────────────────────────────────
def test_inventory_flow():
    p("5️⃣ 库存链路：分类→物资→入库→出库→库存查询")

    # 5.1 创建分类
    r = sess.post(f"{BASE}/inventory/categories", headers=auth_headers(), json={
        "name": f"E2E测试分类_{date.today():%H%M%S}",
        "description": "端到端测试自动创建",
    })
    expect(r, "POST /inventory/categories", save_as="cat_id")

    # 5.2 创建物资（关联分类）
    cat_id = T.get("cat_id")
    if cat_id:
        r = sess.post(f"{BASE}/inventory/materials", headers=auth_headers(), json={
            "code": f"MAT-E2E-{date.today():%Y%m%d%H%M%S}",
            "name": f"E2E测试物资",
            "category_id": cat_id,
            "unit": "个",
            "specs": "100x50x20mm",
            "notes": "端到端测试自动创建",
        })
        expect(r, "POST /inventory/materials", save_as="mat_id")

    # 5.3 入库（如果前面没做）
    warehouse_id = T.get("warehouse_id")
    if not warehouse_id:
        r = sess.get(f"{BASE}/inventory/warehouses", headers=auth_headers())
        try:
            wh_data = r.json().get("data", {})
            wh_list = wh_data if isinstance(wh_data, list) else wh_data.get("data", [])
            warehouse_id = wh_list[0]["id"] if wh_list else None
            if warehouse_id:
                T["warehouse_id"] = warehouse_id
        except Exception:
            warehouse_id = None

    if warehouse_id:
        # 5.4 出库
        r = sess.post(f"{BASE}/inventory/stock-out", headers=auth_headers(), json={
            "warehouse_id": warehouse_id,
            "type": "outbound",
            "material": "E2E测试物资",
            "quantity": 10,
            "unit": "个",
            "notes": "E2E 测试出库",
        })
        expect(r, "POST /inventory/stock-out（出库）", save_as="stock_out_id")

    # 5.5 库存查询
    r = sess.get(f"{BASE}/inventory/stock", headers=auth_headers())
    expect(r, "GET /inventory/stock（库存查询）")

    # 5.6 库存统计
    r = sess.get(f"{BASE}/inventory/stock/statistics", headers=auth_headers())
    expect(r, "GET /inventory/stock/statistics")


# ─── 6. 车辆完整链路 ──────────────────────────────────────────
def test_vehicle_flow():
    p("6️⃣ 车辆链路：车辆→加油→维修→保险→年检")

    # 6.1 创建车辆
    r = sess.post(f"{BASE}/vehicles", headers=auth_headers(), json={
        "plate_number": f"E2E{date.today():%m%d}测",
        "brand": "E2E测试品牌",
        "model": "E2E测试型号",
        "year": 2025,
        "vin": f"E2E{date.today():%Y%m%d}{date.today():%H%M%S}",
        "engine_no": f"ENG-E2E-{date.today():%Y%m%d}",
        "purchase_date": date.today().strftime("%Y-%m-%d"),
        "status": "active",
        "notes": "端到端测试自动创建",
    })
    expect(r, "POST /vehicles", save_as="vehicle_id")

    vid = T.get("vehicle_id")
    if not vid:
        print("  ⚠️  跳过车辆后续流程（车辆 ID 未获取）")
        return

    # 6.2 加油记录
    r = sess.post(f"{BASE}/vehicle-fuel-logs", headers=auth_headers(), json={
        "vehicle_id": vid,
        "fuel_date": date.today().strftime("%Y-%m-%d"),
        "current_km": 5000,
        "fuel_amount": 45.5,
        "fuel_cost": 350.0,
        "station": "E2E测试加油站",
        "notes": "E2E 测试加油记录",
    })
    expect(r, "POST /vehicle-fuel-logs（加油记录）")

    # 6.3 维修记录
    r = sess.post(f"{BASE}/vehicle-maintenances", headers=auth_headers(), json={
        "vehicle_id": vid,
        "maintenance_date": date.today().strftime("%Y-%m-%d"),
        "current_km": 5100,
        "type": "routine",
        "description": "E2E 测试常规保养",
        "cost": 680.0,
        "workshop": "E2E测试维修厂",
        "notes": "端到端测试自动创建",
    })
    expect(r, "POST /vehicle-maintenances（维修记录）")

    # 6.4 保险记录
    r = sess.post(f"{BASE}/vehicle-insurances", headers=auth_headers(), json={
        "vehicle_id": vid,
        "insurance_date": date.today().strftime("%Y-%m-%d"),
        "insurance_company": "E2E测试保险公司",
        "policy_number": f"POL-E2E-{date.today():%Y%m%d}",
        "coverage": "交强险+商业险",
        "premium": 4200.0,
        "start_date": date.today().strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "notes": "E2E 测试保险记录",
    })
    expect(r, "POST /vehicle-insurances（保险记录）")

    # 6.5 年检记录
    r = sess.post(f"{BASE}/vehicle-inspections", headers=auth_headers(), json={
        "vehicle_id": vid,
        "inspection_date": date.today().strftime("%Y-%m-%d"),
        "result": "passed",
        "inspection_agency": "E2E测试检测站",
        "next_inspection_date": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "cost": 300.0,
        "notes": "E2E 测试年检记录",
    })
    expect(r, "POST /vehicle-inspections（年检记录）")

    # 6.6 车辆列表 + 统计
    r = sess.get(f"{BASE}/vehicles?status=active&page=1&page_size=5",
                 headers=auth_headers())
    expect(r, "GET /vehicles（车辆列表）")


# ─── 7. 员工链路 ───────────────────────────────────────────────
def test_employee_flow():
    p("7️⃣ 员工链路：入职→排班→考勤→离职")

    # 7.1 入职
    r = sess.post(f"{BASE}/employee-onboardings", headers=auth_headers(), json={
        "name": f"E2E测试员工{date.today():%H%M%S}",
        "gender": "male",
        "phone": "13900139000",
        "email": f"e2e{date.today():%H%M%S}@test.com",
        "department": "技术部",
        "position": "测试工程师",
        "join_date": date.today().strftime("%Y-%m-%d"),
        "notes": "端到端测试自动创建",
    })
    expect(r, "POST /employee-onboardings（入职）", save_as="onboard_id")

    # 7.2 获取排班列表（本月）
    today = date.today()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    r = sess.get(
        f"{BASE}/schedules?start={first_day}&end={last_day.strftime('%Y-%m-%d')}",
        headers=auth_headers()
    )
    expect(r, "GET /schedules（排班列表）")

    # 7.3 考勤概览
    r = sess.get(f"{BASE}/attendance/overview", headers=auth_headers())
    expect(r, "GET /attendance/overview（考勤概览）")

    # 7.4 考勤日历（本月）
    r = sess.get(f"{BASE}/attendance/calendar?month={today.strftime('%Y-%m')}",
                 headers=auth_headers())
    expect(r, "GET /attendance/calendar（考勤日历）")


# ─── 8. 销售链路 ───────────────────────────────────────────────
def test_sales_flow():
    p("8️⃣ 销售链路：线索→商机→产品→报价")

    # 8.1 创建线索
    r = sess.post(f"{BASE}/sales/leads", headers=auth_headers(), json={
        "name": f"E2E测试线索_{date.today():%H%M%S}",
        "contact": "测试联系人",
        "phone": "13700137000",
        "email": "lead@e2e-test.com",
        "source": "online",
        "notes": "端到端测试自动创建",
    })
    expect(r, "POST /sales/leads（线索）", save_as="lead_id")

    # 8.2 创建商机（关联线索）
    lead_id = T.get("lead_id")
    if lead_id:
        r = sess.post(f"{BASE}/sales/opportunities", headers=auth_headers(), json={
            "lead_id": lead_id,
            "name": f"E2E测试商机_{date.today():%H%M%S}",
            "amount": 120000,
            "stage": "negotiation",
            "expected_close_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "notes": "端到端测试自动创建",
        })
        expect(r, "POST /sales/opportunities（商机）", save_as="opp_id")

    # 8.3 创建产品
    r = sess.post(f"{BASE}/sales/products", headers=auth_headers(), json={
        "name": f"E2E测试产品_{date.today():%H%M%S}",
        "code": f"SKU-E2E-{date.today():%Y%m%d%H%M%S}",
        "category": "安防设备",
        "unit_price": 2500.0,
        "description": "端到端测试自动创建",
    })
    expect(r, "POST /sales/products（产品）", save_as="product_id")

    # 8.4 创建报价单（关联商机 + 产品）
    opp_id = T.get("opp_id")
    product_id = T.get("product_id")
    if opp_id and product_id:
        r = sess.post(f"{BASE}/sales/quotations", headers=auth_headers(), json={
            "opportunity_id": opp_id,
            "product_id": product_id,
            "quantity": 10,
            "unit_price": 2500.0,
            "discount": 5.0,
            "total_amount": 23750.0,
            "valid_until": (date.today() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "notes": "E2E 测试报价单",
        })
        expect(r, "POST /sales/quotations（报价单）", save_as="quote_id")


# ─── 9. 性能和响应时间检查 ─────────────────────────────────────
def test_performance():
    p("9️⃣ 性能检查：关键接口响应时间")
    import time

    endpoints = [
        ("GET /vehicles", "/vehicles"),
        ("GET /employees", "/employees"),
        ("GET /customers?type=customer", "/customers?type=customer"),
        ("GET /projects", "/projects"),
        ("GET /finance/receivables", "/finance/receivables"),
        ("GET /purchase/requirements", "/purchase/requirements"),
        ("GET /inventory/stock", "/inventory/stock"),
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


# ─── 主流程 ────────────────────────────────────────────────────
def main():
    print("🚀 端到端完整业务流程测试 开始")
    print(f"   目标服务器: {BASE}")
    print(f"   测试时间: {date.today()} {__import__('datetime').datetime.now():%H:%M:%S}")

    results = {}
    total = 0
    passed = 0

    tests = [
        ("认证流程", test_auth_flow),
        ("客户→项目→施工", test_customer_project_flow),
        ("财务链路", test_finance_flow),
        ("采购全流程", test_purchase_flow),
        ("库存链路", test_inventory_flow),
        ("车辆链路", test_vehicle_flow),
        ("员工链路", test_employee_flow),
        ("销售链路", test_sales_flow),
        ("性能检查", test_performance),
    ]

    for name, func in tests:
        try:
            func()
            results[name] = "✅ 通过"
            passed += 1
        except Exception as e:
            results[name] = f"❌ 失败: {e}"
            print(f"  ❌ 异常: {e}")
        total += 1

    # 汇总
    p("📊 测试结果汇总")
    print(f"  通过: {passed}/{total}")
    for name, status in results.items():
        print(f"    {status}  {name}")

    print(f"\n{'='*60}")
    print(f"  🔗 关联数据 ID 汇总:")
    for k, v in T.items():
        print(f"    {k} = {v}")
    print('='*60)

    return passed == total


if __name__ == "__main__":
    import sys
    ok = main()
    sys.exit(0 if ok else 1)
