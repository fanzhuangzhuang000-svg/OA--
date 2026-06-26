#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OA 系统全业务流压测脚本 v1.0
按真实人工操作方式跑 15 大模块，生成结构化报告
"""
import json, time, sys, os
import requests
from datetime import datetime, timedelta
from typing import Optional

BASE = "http://172.20.0.139/api"
TIMEOUT = 15

# ---------- 颜色 ----------
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW= "\033[93m"
CYAN  = "\033[96m"
RESET = "\033[0m"
GRAY  = "\033[90m"

# ---------- 报告容器 ----------
class Report:
    def __init__(self):
        self.modules = {}        # {module_name: [ {test: ...} ]}
        self.tokens = {}         # {user: token}
        self.created_ids = {}    # {key: id}  跟踪创建的对象
        self.errors = []
        self.timing = {}         # {module: duration}

    def record(self, module, name, method, url, code, status, payload=None, response=None, latency=0):
        if module not in self.modules:
            self.modules[module] = []
        self.modules[module].append({
            "name": name, "method": method, "url": url, "code": code,
            "status": status, "payload": payload, "response": response,
            "latency_ms": round(latency*1000, 1)
        })

    def module_summary(self, module):
        if module not in self.modules:
            return None
        tests = self.modules[module]
        passed = sum(1 for t in tests if t['status'] == 'PASS')
        failed = sum(1 for t in tests if t['status'] == 'FAIL')
        warning= sum(1 for t in tests if t['status'] == 'WARN')
        return {"module": module, "total": len(tests), "pass": passed, "fail": failed, "warn": warning}

    def total_summary(self):
        total = pass_ = fail_ = warn_ = 0
        for m in self.modules.values():
            for t in m:
                total += 1
                if t['status'] == 'PASS': pass_ += 1
                elif t['status'] == 'FAIL': fail_ += 1
                elif t['status'] == 'WARN': warn_ += 1
        return {"total": total, "pass": pass_, "fail": fail_, "warn": warn_}

R = Report()

# ---------- HTTP 封装 ----------
class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method, path, token=None, json_body=None, params=None, files=None):
        url = BASE + path
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        t0 = time.time()
        try:
            r = self.session.request(method, url, headers=headers, json=json_body,
                                     params=params, files=files, timeout=TIMEOUT)
            latency = time.time() - t0
            try:
                data = r.json()
            except Exception:
                data = {"raw": r.text[:300]}
            return r.status_code, data, latency
        except Exception as e:
            return 0, {"error": str(e)[:200]}, time.time() - t0

c = Client()

# ---------- 测试辅助 ----------
def test(module, name, method, path, *, token=None, body=None, params=None, expect=200, save_id=None):
    """跑一次接口测试,自动记录"""
    code, data, lat = c.request(method, path, token=token, json_body=body, params=params)

    # 解析状态
    if code == 0:
        status = "FAIL"
        msg = "网络错误"
    elif isinstance(expect, list):
        if code in expect:
            status = "PASS"
        else:
            status = "FAIL"
        msg = f"code={code}, expect in {expect}"
    else:
        if code == expect:
            status = "PASS"
        elif code in [401, 403] and expect == 200:
            status = "FAIL"
            msg = f"鉴权失败 code={code}"
        elif code in [422, 400] and expect == 200:
            # 参数错误
            status = "WARN"
            msg = f"参数错误 code={code}: {str(data)[:200]}"
        else:
            status = "FAIL"
            msg = f"code={code}, expect {expect}: {str(data)[:200]}"

    # 提取 id
    if save_id and status == "PASS":
        d = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(d, dict):
            R.created_ids[save_id] = d.get("id") or (d.get("data", {}) or {}).get("id")
        elif isinstance(d, list) and d and isinstance(d[0], dict):
            R.created_ids[save_id] = d[0].get("id")

    R.record(module, name, method, path, code, status,
             payload=body, response=(str(data)[:500] if isinstance(data, dict) else data),
             latency=lat)
    sym = {"PASS": f"{GREEN}✓{RESET}", "FAIL": f"{RED}✗{RESET}", "WARN": f"{YELLOW}⚠{RESET}"}[status]
    extra = f" {GRAY}({round(lat*1000)}ms){RESET}" if status == "PASS" else f" {GRAY}{msg}{RESET}"
    print(f"    {sym} {name} [{method} {path}]{extra}")
    return status == "PASS", code, data

# ============== 1. 登录 ==============
print(f"\n{CYAN}{'='*70}{RESET}")
print(f"{CYAN}  OA 系统全业务流压测 - 模拟真实用户操作{RESET}")
print(f"{CYAN}{'='*70}{RESET}")

print(f"\n{YELLOW}[1/15] 系统登录{RESET}")
t0 = time.time()
code, data, _ = c.request("POST", "/auth/login", json_body={"username": "admin", "password": "admin123"})
if code == 200:
    R.tokens["admin"] = data["data"]["token"]
    R.created_ids["admin_user_id"] = data["data"]["user"]["id"]
    R.created_ids["admin_user_name"] = data["data"]["user"]["name"]
    print(f"  {GREEN}✓ 登录成功{RESET} - 用户: {R.created_ids['admin_user_name']} (id={R.created_ids['admin_user_id']})")
else:
    print(f"  {RED}✗ 登录失败 code={code} body={data}{RESET}")
    sys.exit(1)

TOKEN = R.tokens["admin"]

# ============== 2. 工作台 ==============
print(f"\n{YELLOW}[2/15] 工作台 Dashboard{RESET}")
test("工作台", "工作台统计", "GET", "/dashboard/stats", token=TOKEN)
test("工作台", "待办事项", "GET", "/dashboard/todo", token=TOKEN)
test("工作台", "最近项目", "GET", "/dashboard/recent-projects", token=TOKEN)
test("工作台", "最近工单", "GET", "/dashboard/recent-service-orders", token=TOKEN)
test("工作台", "营收趋势", "GET", "/dashboard/revenue-trend", token=TOKEN)
test("工作台", "服务统计", "GET", "/dashboard/service-stats", token=TOKEN)
test("工作台", "项目进度", "GET", "/dashboard/project-progress", token=TOKEN)
test("工作台", "数据大屏", "GET", "/dashboard/screen", token=TOKEN)

# ============== 3. 考勤管理 ==============
print(f"\n{YELLOW}[3/15] 考勤管理{RESET}")
test("考勤", "今日考勤", "GET", "/attendance/today", token=TOKEN)
test("考勤", "考勤总览", "GET", "/attendance/overview", token=TOKEN)
test("考勤", "考勤统计", "GET", "/attendance/stats", token=TOKEN)
test("考勤", "考勤日历", "GET", "/attendance/calendar", token=TOKEN)
test("考勤", "考勤记录", "GET", "/attendance/records", token=TOKEN)
test("考勤", "月度报表", "GET", "/attendance/report", token=TOKEN, params={"month": "2026-06"})
# 签到
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ok, code, data = test("考勤", "上班签到", "POST", "/attendance/clock-in", token=TOKEN,
    body={"clock_time": now, "location": "公司总部", "latitude": 29.8683, "longitude": 121.5440})
# 签退
ok, code, data = test("考勤", "下班签退", "POST", "/attendance/clock-out", token=TOKEN,
    body={"clock_time": now, "location": "公司总部"})
# 外勤
ok, code, data = test("考勤", "外勤打卡", "POST", "/attendance/field-clock", token=TOKEN,
    body={"clock_time": now, "location": "宁波港客户现场", "latitude": 29.8740, "longitude": 121.5550, "type": "外勤"})
# 请假申请
test("考勤", "请假申请", "POST", "/attendance/leave", token=TOKEN,
    body={"type": "annual", "start_date": "2026-07-01", "end_date": "2026-07-03",
          "days": 3, "reason": "家庭出游"})
test("考勤", "请假列表", "GET", "/attendance/leave", token=TOKEN)
# 加班
test("考勤", "加班申请", "POST", "/attendance/overtime", token=TOKEN,
    body={"overtime_date": "2026-06-23", "start_time": "18:00", "end_time": "21:00", "hours": 3, "reason": "项目验收赶工"})
test("考勤", "加班列表", "GET", "/attendance/overtime", token=TOKEN)
# 排班
test("考勤", "排班列表", "GET", "/schedules", token=TOKEN, params={"start": "2026-06-01", "end": "2026-06-30"})
test("考勤", "我的排班", "GET", "/schedules/my-schedule", token=TOKEN)
test("考勤", "班组列表", "GET", "/schedules/groups", token=TOKEN)
test("考勤", "班次列表", "GET", "/schedules/shifts", token=TOKEN)
test("考勤", "排班统计", "GET", "/schedules/stats", token=TOKEN)
test("考勤", "下次提醒", "GET", "/schedules/next-reminder", token=TOKEN)

# ============== 4. 客户管理 ==============
print(f"\n{YELLOW}[4/15] 客户管理{RESET}")
test("客户", "客户列表", "GET", "/customers", token=TOKEN, params={"per_page": 20})
test("客户", "客户统计", "GET", "/customers/stats", token=TOKEN)
test("客户", "客户地图", "GET", "/customers/map", token=TOKEN)
test("客户", "客户健康度", "GET", "/customers/health", token=TOKEN)
test("客户", "销售漏斗", "GET", "/customers/pipeline", token=TOKEN)
test("客户", "漏斗周趋势", "GET", "/customers/pipeline/weekly-trend", token=TOKEN)
test("客户", "跟进日历", "GET", "/follow-ups/calendar", token=TOKEN, params={"month": "2026-06"})
# 新建客户
ok, code, data = test("客户", "新建客户(测试用)", "POST", "/customers", token=TOKEN,
    body={"name": "压测客户-X", "category": "potential", "industry": "教育",
          "level": "C", "source": "推广", "address": "宁波市测试路1号"}, save_id="test_customer_id")
# 取一个真实客户 id 用于后续
if R.created_ids.get("test_customer_id") is None:
    code, data, _ = c.request("GET", "/customers?per_page=1", token=TOKEN)
    if code == 200 and data.get("data", {}).get("data"):
        R.created_ids["real_customer_id"] = data["data"]["data"][0]["id"]
cid = R.created_ids.get("test_customer_id") or R.created_ids.get("real_customer_id")
if cid:
    test("客户", "客户详情", "GET", f"/customers/{cid}", token=TOKEN)
    test("客户", "客户360画像", "GET", f"/customers/{cid}/profile", token=TOKEN)
    test("客户", "客户设备", "GET", f"/customers/{cid}/devices", token=TOKEN)
    test("客户", "客户跟进记录", "GET", f"/customers/{cid}/follow-ups", token=TOKEN)
    test("客户", "新增跟进", "POST", f"/customers/{cid}/follow-ups", token=TOKEN,
        body={"content": "电话回访,客户满意", "method": "phone", "next_date": "2026-07-01"})

# ============== 5. 员工管理 ==============
print(f"\n{YELLOW}[5/15] 员工管理 + 组织架构{RESET}")
test("员工", "员工列表", "GET", "/employees", token=TOKEN, params={"per_page": 20})
test("员工", "部门列表", "GET", "/employees/departments", token=TOKEN)
test("员工", "岗位列表", "GET", "/employees/positions", token=TOKEN)
test("员工", "技能标签", "GET", "/employees/skills", token=TOKEN)
test("员工", "员工证书", "GET", "/employees/certificates", token=TOKEN)
# 取一个员工 id
code, data, _ = c.request("GET", "/employees?per_page=1", token=TOKEN)
emp_id = None
if code == 200 and data.get("data", {}).get("data"):
    emp_id = data["data"]["data"][0]["id"]
if emp_id:
    test("员工", "员工详情", "GET", f"/employees/{emp_id}", token=TOKEN)
    test("员工", "员工技能", "GET", f"/employees/{emp_id}/skills", token=TOKEN)
# 入职管理
test("员工", "入职列表", "GET", "/employee-onboardings", token=TOKEN)
ok, code, data = test("员工", "新建入职", "POST", "/employee-onboardings", token=TOKEN,
    body={"user": {"username": "test_emp_" + str(int(time.time())), "name": "压测新员工"},
          "onboarding": {"hire_date": "2026-07-01", "department_id": 1, "position_id": 1}}, save_id="onboarding_id")
# 离职管理
test("员工", "离职列表", "GET", "/employee-resignations", token=TOKEN)

# ============== 6. 项目管理 ==============
print(f"\n{YELLOW}[6/15] 项目管理 (7 阶段){RESET}")
test("项目", "项目阶段", "GET", "/projects/stages", token=TOKEN)
test("项目", "项目列表", "GET", "/projects", token=TOKEN, params={"per_page": 20})
test("项目", "项目看板摘要", "GET", "/projects/dashboard-summary", token=TOKEN)
test("项目", "付款日历", "GET", "/projects/payment-calendar", token=TOKEN)
# 新建项目
if cid:
    ok, code, data = test("项目", "新建项目(测试)", "POST", "/projects", token=TOKEN,
        body={"name": "压测项目-测试A", "code": "TEST2026001", "customer_id": cid,
              "type": "安防", "amount": 100000, "manager_id": emp_id or 1,
              "planned_start": "2026-07-01", "planned_end": "2026-09-30",
              "address": "测试现场"}, save_id="project_id")
# 取一个真实项目
code, data, _ = c.request("GET", "/projects?per_page=1", token=TOKEN)
proj_id = R.created_ids.get("project_id")
if not proj_id and code == 200 and data.get("data", {}).get("data"):
    proj_id = data["data"]["data"][0]["id"]
if proj_id:
    test("项目", "项目详情", "GET", f"/projects/{proj_id}", token=TOKEN)
    test("项目", "项目跟踪", "GET", f"/projects/{proj_id}/tracking", token=TOKEN)
    test("项目", "项目看板", "GET", f"/projects/board", token=TOKEN)

# ============== 7. 售后服务 ==============
print(f"\n{YELLOW}[7/15] 售后服务 (6 环节){RESET}")
test("售后", "工单列表", "GET", "/service/orders", token=TOKEN, params={"per_page": 20})
test("售后", "工单统计", "GET", "/service/orders/stats", token=TOKEN)
test("售后", "服务统计", "GET", "/service/stats", token=TOKEN)
test("售后", "维保合同", "GET", "/service/maintenance-contracts", token=TOKEN)
# 新建工单
if cid and emp_id:
    ok, code, data = test("售后", "新建工单(测试)", "POST", "/service/orders", token=TOKEN,
        body={"customer_id": cid, "type": "故障报修", "priority": "high",
              "fault_description": "测试工单-网络故障",
              "address": "客户现场", "contact_phone": "13800001111"}, save_id="service_order_id")
so_id = R.created_ids.get("service_order_id")
if not so_id:
    code, data, _ = c.request("GET", "/service/orders?per_page=1", token=TOKEN)
    if code == 200 and data.get("data", {}).get("data"):
        so_id = data["data"]["data"][0]["id"]
if so_id:
    test("售后", "工单详情", "GET", f"/service/orders/{so_id}", token=TOKEN)
    test("售后", "工单派单", "POST", f"/service/orders/{so_id}/assign", token=TOKEN,
        body={"technician_id": emp_id, "scheduled_at": "2026-06-23 10:00:00"})
    test("售后", "工单开始", "POST", f"/service/orders/{so_id}/start", token=TOKEN)
    test("售后", "工单完成", "POST", f"/service/orders/{so_id}/complete", token=TOKEN,
        body={"result": "修复完成", "solution": "更换网线"})
    test("售后", "客户确认", "POST", f"/service/orders/{so_id}/confirm", token=TOKEN,
        body={"rating": 5, "comment": "服务很好"})

# ============== 8. 报销管理 ==============
print(f"\n{YELLOW}[8/15] 报销管理{RESET}")
test("报销", "我的报销", "GET", "/expenses/my", token=TOKEN)
test("报销", "报销列表", "GET", "/expenses", token=TOKEN, params={"per_page": 20})
test("报销", "报销统计", "GET", "/expenses/stats", token=TOKEN)
test("报销", "可报销项目", "GET", "/expenses/projects", token=TOKEN)
# 新建报销
if proj_id:
    ok, code, data = test("报销", "新建报销(测试)", "POST", "/expenses", token=TOKEN,
        body={"project_id": proj_id, "category": "交通", "amount": 320.50,
              "items": [{"category": "交通", "amount": 320.50, "description": "打车去客户现场"}],
              "occurred_at": "2026-06-22", "description": "打车去客户现场"},
        save_id="expense_id")

# ============== 9. 车辆管理 ==============
print(f"\n{YELLOW}[9/15] 车辆管理 (档案+油卡+保险+保养){RESET}")
test("车辆", "车辆列表", "GET", "/vehicles", token=TOKEN, params={"per_page": 20})
test("车辆", "车辆统计", "GET", "/vehicles/stats", token=TOKEN)
test("车辆", "油卡列表", "GET", "/fuel-cards", token=TOKEN)
test("车辆", "油卡充值记录", "GET", "/fuel-cards/recharges", token=TOKEN)
test("车辆", "油卡统计", "GET", "/fuel-cards/stats", token=TOKEN)
test("车辆", "保险记录", "GET", "/vehicles/insurances", token=TOKEN)
test("车辆", "保养记录", "GET", "/vehicles/maintenances", token=TOKEN)
test("车辆", "用车申请", "GET", "/vehicles/applies", token=TOKEN)
test("车辆", "车辆使用", "GET", "/vehicles/usage", token=TOKEN)
# 取一辆车
code, data, _ = c.request("GET", "/vehicles?per_page=1", token=TOKEN)
veh_id = None
if code == 200 and isinstance(data.get("data"), dict) and data["data"].get("data"):
    veh_id = data["data"]["data"][0]["id"]
if veh_id:
    test("车辆", "车辆详情", "GET", f"/vehicles/{veh_id}", token=TOKEN)
# 油卡
code, data, _ = c.request("GET", "/fuel-cards?per_page=1", token=TOKEN)
fc_id = None
if code == 200 and isinstance(data.get("data"), dict) and data["data"].get("data"):
    fc_id = data["data"]["data"][0]["id"]
if fc_id:
    test("车辆", "油卡充值", "POST", "/fuel-cards/recharges", token=TOKEN,
        body={"fuel_card_id": fc_id, "amount": 500, "remark": "压测充值"})

# ============== 10. 库存管理 ==============
print(f"\n{YELLOW}[10/15] 库存管理{RESET}")
test("库存", "物品列表", "GET", "/inventory", token=TOKEN, params={"per_page": 20})
test("库存", "库存统计", "GET", "/inventory/stats", token=TOKEN)
test("库存", "低库存预警", "GET", "/inventory/low-stock", token=TOKEN)
test("库存", "分类列表", "GET", "/inventory-categories", token=TOKEN)
test("库存", "分类树", "GET", "/inventory-categories/tree", token=TOKEN)
test("库存", "按分类查物品", "GET", "/inventory/items-by-category", token=TOKEN)

# ============== 11. 财务管理 ==============
print(f"\n{YELLOW}[11/15] 财务管理 (账户+应收/应付+发票){RESET}")
test("财务", "财务总览", "GET", "/finance/overview", token=TOKEN)
test("财务", "财务摘要", "GET", "/finance/summary", token=TOKEN)
test("财务", "账龄分析", "GET", "/finance/summary/aging", token=TOKEN)
test("财务", "现金流", "GET", "/finance/summary/cashflow", token=TOKEN)
test("财务", "账户列表", "GET", "/finance/accounts", token=TOKEN)
test("财务", "账户转账", "GET", "/finance/transfers", token=TOKEN)
test("财务", "发票列表", "GET", "/finance/invoices", token=TOKEN)
test("财务", "收款列表", "GET", "/finance/receipts", token=TOKEN)
test("财务", "应收列表", "GET", "/finance/receivables", token=TOKEN)
test("财务", "应付列表", "GET", "/finance/payables", token=TOKEN)
test("财务", "付款列表", "GET", "/finance/payments", token=TOKEN)
# 账户详情
code, data, _ = c.request("GET", "/finance/accounts?per_page=1", token=TOKEN)
acc_id = None
if code == 200 and isinstance(data.get("data"), dict) and data["data"].get("data"):
    acc_id = data["data"]["data"][0]["id"]
if acc_id:
    test("财务", "账户交易记录", "GET", f"/finance/accounts/{acc_id}/transactions", token=TOKEN)

# ============== 12. 网盘 ==============
print(f"\n{YELLOW}[12/15] 公司网盘{RESET}")
test("网盘", "文件夹列表", "GET", "/disk/folders", token=TOKEN)
test("网盘", "文件列表", "GET", "/disk/files", token=TOKEN)
ok, code, data = test("网盘", "新建文件夹", "POST", "/disk/folders", token=TOKEN,
    body={"name": "压测目录-2026", "parent_id": 0})

# ============== 13. 知识库 ==============
print(f"\n{YELLOW}[13/15] 知识库{RESET}")
test("知识库", "知识库分类", "GET", "/knowledge/categories", token=TOKEN)
test("知识库", "知识库文章", "GET", "/knowledge/articles", token=TOKEN, params={"per_page": 20})

# ============== 14. 消息中心 ==============
print(f"\n{YELLOW}[14/15] 消息中心{RESET}")
test("消息", "消息列表", "GET", "/notifications", token=TOKEN)
test("消息", "未读数", "GET", "/notifications/unread-count", token=TOKEN)
test("消息", "全部已读", "POST", "/notifications/mark-all-read", token=TOKEN)

# ============== 15. 审批 + 系统设置 ==============
print(f"\n{YELLOW}[15/15] 审批 + 系统设置 + 审计{RESET}")
test("审批", "审批中心", "GET", "/approvals/center", token=TOKEN)
test("审批", "审批统计", "GET", "/approvals/center/stats", token=TOKEN)
test("审批", "项目审批", "GET", "/approvals/project", token=TOKEN)
test("审批", "财务审批", "GET", "/approvals/finance", token=TOKEN)
test("审批", "运营审批", "GET", "/approvals/operation", token=TOKEN)
test("审批", "审批模板", "GET", "/approval-templates", token=TOKEN)

test("设置", "系统设置", "GET", "/settings", token=TOKEN)
test("设置", "端口配置", "GET", "/settings/port", token=TOKEN)
test("设置", "空闲配置", "GET", "/settings/idle-config", token=TOKEN)
test("审计", "系统日志", "GET", "/system-logs", token=TOKEN, params={"per_page": 20})
test("审计", "审计日志", "GET", "/audit-logs", token=TOKEN, params={"per_page": 20})
test("备份", "备份列表", "GET", "/backups", token=TOKEN)

# ============== 输出报告 ==============
print(f"\n\n{CYAN}{'='*70}{RESET}")
print(f"{CYAN}  压测报告{RESET}")
print(f"{CYAN}{'='*70}{RESET}\n")

ts = R.total_summary()
print(f"  总计: {ts['total']} 个测试 | {GREEN}通过 {ts['pass']}{RESET} | {YELLOW}警告 {ts['warn']}{RESET} | {RED}失败 {ts['fail']}{RESET}")
print()
for module in R.modules:
    s = R.module_summary(module)
    icon = f"{GREEN}✓{RESET}" if s['fail'] == 0 and s['warn'] == 0 else (f"{YELLOW}⚠{RESET}" if s['fail'] == 0 else f"{RED}✗{RESET}")
    print(f"  {icon} {s['module']:8s}  {s['total']:3d} 测试 | {GREEN}通过 {s['pass']}{RESET} | {YELLOW}警告 {s['warn']}{RESET} | {RED}失败 {s['fail']}{RESET}")

# 输出失败明细
print(f"\n{YELLOW}{'='*70}{RESET}")
print(f"{YELLOW}  失败明细{RESET}")
print(f"{YELLOW}{'='*70}{RESET}\n")
fail_count = 0
for module, tests in R.modules.items():
    for t in tests:
        if t['status'] == 'FAIL':
            fail_count += 1
            print(f"  {RED}✗{RESET} [{module}] {t['name']}")
            print(f"    {t['method']} {t['url']} → code={t['code']}")
            if t.get('response'):
                print(f"    response: {t['response'][:200]}")
            print()

if fail_count == 0:
    print(f"  {GREEN}无失败{RESET}")

# 落盘报告
report = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "summary": ts,
    "modules": {m: R.module_summary(m) for m in R.modules},
    "tests": R.modules,
    "created_ids": R.created_ids,
}
out_path = r"D:\work\website\OA\.workbuddy\stress_test_report.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\n  {GRAY}JSON 报告已保存: {out_path}{RESET}")
