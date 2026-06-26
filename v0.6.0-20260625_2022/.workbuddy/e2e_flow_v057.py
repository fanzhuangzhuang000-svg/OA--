"""V0.5.7 端到端业务流程测试 — 4 大核心 flow
实际端点：
  - /api/work-orders/{id}/{assign|start|resolve|cancel}
  - /api/repair-orders/{id}/{in-repair|repaired|ship-back|ship-out|close}
  - /api/sales/leads (POST), /api/sales/leads/{lead}/status (PATCH), /api/sales/leads/{lead}/convert-to-opp
  - /api/sales/opps (POST), /api/sales/opps/{opp}/stage (PATCH)
  - /api/expenses (POST), /api/expenses/{claim}/approve
"""
import requests
import time
import sys

API = 'http://192.168.3.117'
PASS = 0
FAIL = 0
def check(name, ok, detail=''):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  ✓ {name}')
    else:
        FAIL += 1
        print(f'  ✗ {name} {detail}')

def login(u):
    r = requests.post(f'{API}/api/auth/login', json={'username':u,'password':'admin123'}, timeout=10)
    if r.status_code == 200 and r.json().get('code') == 0:
        return r.json()['data']['token']
    return None

T_admin = login('admin1')
T_sales = login('sales_yang')
T_fin   = login('fin_wu')
T_tech  = login('tech_qian')

H = lambda T: {'Authorization': f'Bearer {T}'}

# ===== Flow 1: 维修 =====
print('\n=== Flow 1: 客户报修 → 维修工单 → 维修完成 ===')
r = requests.post(f'{API}/api/repair-orders', headers=H(T_admin), json={
    'customer_id': 1, 'contact_name': 'E2E客户', 'contact_phone': '13900000001',
    'equipment_brand': '海康', 'equipment_model': 'DS-E2E',
    'fault_description': 'E2E 维修流程测试',
    'method_type': 'paid_repair', 'parts_cost': 200, 'labor_cost': 100, 'shipping_cost': 50,
}, timeout=10)
d = r.json()
check('1.1 客户报修', d.get('code') == 0, str(d)[:80])
repair_id = d['data']['id'] if d.get('code') == 0 else None
repair_code = d['data']['code'] if d.get('code') == 0 else None

r = requests.post(f'{API}/api/work-orders', headers=H(T_tech), json={
    'customer_id': 1, 'project_id': 72,
    'fault_description': '工单维修', 'priority': 'high',
    'contact_name': 'E2E客户', 'contact_phone': '13900000001',
    'service_type': 'on_site',
}, timeout=10)
d = r.json()
check('1.2 维修工单', d.get('code') == 0, str(d)[:80])
wo_id = d['data']['id'] if d.get('code') == 0 else None

# 工单状态推进: pending → assign → start → resolve
if wo_id:
    r = requests.post(f'{API}/api/work-orders/{wo_id}/assign', headers=H(T_tech),
                      json={'engineer_id': 4, 'note': 'E2E 指派'}, timeout=10)  # tech_qian
    check('1.3 工单指派', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/work-orders/{wo_id}/start', headers=H(T_tech), timeout=10)
    check('1.4 开始维修', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/work-orders/{wo_id}/resolve', headers=H(T_tech),
                      json={'result_notes': '已修复', 'parts_cost': 200, 'labor_cost': 100,
                            'customer_signature': 'data:image/png;base64,iVBORw0K'}, timeout=10)
    check('1.5 完成维修', r.json().get('code') == 0, str(r.json())[:80])

# 返修单状态推进
if repair_id:
    # 状态机: received → sent_for_repair → in_repair → repaired → sent_back → closed
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/ship-out', headers=H(T_tech),
                      json={'sender_name': '客户', 'sender_address': '北京',
                            'receiver_name': '厂家A', 'receiver_address': '上海',
                            'carrier': '顺丰', 'tracking_no': 'SF0001'}, timeout=10)
    check('1.6 寄修中', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/in-repair', headers=H(T_tech),
                      json={'engineer_id': 4, 'note': '开始维修'}, timeout=10)
    check('1.7 维修中', r.json().get('code') == 0, str(r.json())[:80])
    # 创建维修方式记录 (标记修好必填)
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/methods', headers=H(T_tech),
                      json={'method_type': 'paid_repair', 'actual_cost': 350, 'note': 'E2E维修方式'}, timeout=10)
    check('1.7a 维修方式', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/repaired', headers=H(T_tech), timeout=10)
    check('1.8 已修好', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/ship-back', headers=H(T_tech),
                      json={'sender_name': '厂家A', 'sender_address': '上海',
                            'receiver_name': '客户', 'receiver_address': '北京',
                            'carrier': '顺丰', 'tracking_no': 'SF12345'}, timeout=10)
    check('1.9 已回寄', r.json().get('code') == 0, str(r.json())[:80])
    r = requests.post(f'{API}/api/repair-orders/{repair_id}/close', headers=H(T_tech), timeout=10)
    check('1.10 返修关闭', r.json().get('code') == 0, str(r.json())[:80])

# 客户公开查询
if repair_code:
    time.sleep(1)
    r = requests.get(f'{API}/api/portal/repair',
                     params={'code': repair_code, 'phone_suffix': '0001'}, timeout=10)
    check('1.11 客户查询返修', r.status_code == 200, f'status={r.status_code} body={r.text[:100]}')

# ===== Flow 2: 销售 =====
print('\n=== Flow 2: 线索 → 商机 ===')
r = requests.post(f'{API}/api/sales/leads', headers=H(T_sales), json={
    'customer_id': 1, 'source': 'online',
    'contact_name': 'E2E销售', 'contact_phone': '13900000002',
    'requirement': 'E2E 销售流程测试',
    'estimated_amount': 100000,
}, timeout=10)
d = r.json()
check('2.1 创建线索', d.get('code') == 0, str(d)[:100])
lead_id = d['data']['id'] if d.get('code') == 0 else None

# 推进 status (PATCH /api/sales/leads/{id}/status)
if lead_id:
    r = requests.patch(f'{API}/api/sales/leads/{lead_id}/status', headers=H(T_sales),
                       json={'status':'qualified'}, timeout=10)
    check('2.2 线索合格', r.json().get('code') == 0, str(r.json())[:100])
    # 转换商机
    r = requests.post(f'{API}/api/sales/leads/{lead_id}/convert-to-opp', headers=H(T_sales),
                      json={'name': 'E2E商机-' + str(lead_id), 'estimated_amount': 100000,
                            'sales_id': 3, 'presale_id': 4}, timeout=10)
    check('2.3 线索转商机', r.json().get('code') == 0, str(r.json())[:100])

# 单独建一个商机
r = requests.post(f'{API}/api/sales/opps', headers=H(T_sales), json={
    'customer_id': 1, 'name': 'E2E 商机测试', 'estimated_amount': 200000,
    'probability': 60, 'sales_id': 3, 'presale_id': 4,
    'expected_sign_date': '2026-08-30',
}, timeout=10)
d = r.json()
check('2.4 创建商机', d.get('code') == 0, str(d)[:100])
opp_id = d['data']['id'] if d.get('code') == 0 else None
if opp_id:
    r = requests.post(f'{API}/api/sales/opps/{opp_id}/mark-won', headers=H(T_sales),
                      json={'contract_amount': 200000, 'signed_at': '2026-06-25'}, timeout=10)
    check('2.5 商机成交', r.json().get('code') == 0, str(r.json())[:100])

# ===== Flow 3: 财务 =====
print('\n=== Flow 3: 报销 → 审批 ===')
r = requests.post(f'{API}/api/expenses', headers=H(T_fin), json={
    'category': 'travel', 'total_amount': 1500, 'project_id': 72,
    'description': 'E2E 报销测试',
    'claim_no': f'EX-E2E-{int(time.time())}',
    'items': [{'item_type': 'flight', 'amount': 800, 'description': '机票'},
              {'item_type': 'hotel', 'amount': 700, 'description': '酒店'}],
}, timeout=10)
d = r.json()
check('3.1 创建报销', d.get('code') == 0, str(d)[:100])
ec_id = d['data']['id'] if d.get('code') == 0 else None

if ec_id:
    r = requests.put(f'{API}/api/expenses/{ec_id}', headers=H(T_fin),
                     json={'status':'pending'}, timeout=10)
    check('3.2 提交审批', r.json().get('code') == 0, str(r.json())[:100])
    r = requests.post(f'{API}/api/expenses/{ec_id}/approve', headers=H(T_admin),
                      json={'action':'approved', 'comment':'E2E 同意'}, timeout=10)
    check('3.3 审批通过', r.json().get('code') == 0, str(r.json())[:100])

# ===== Flow 4: 看板与统计 =====
print('\n=== Flow 4: 看板与统计端点 ===')
r = requests.get(f'{API}/api/dashboard/widget/all', headers=H(T_admin), timeout=10)
check('4.1 Dashboard widget all', r.status_code == 200)
r = requests.get(f'{API}/api/dashboard/maintenance-stats', headers=H(T_admin), timeout=10)
check('4.2 maintenance-stats', r.status_code == 200)
r = requests.get(f'{API}/api/repair-cost/overview', headers=H(T_admin), timeout=10)
check('4.3 repair-cost overview', r.status_code == 200)
r = requests.get(f'{API}/api/dict/kinds', headers=H(T_admin), timeout=10)
check('4.4 dict kinds', r.status_code == 200)
r = requests.get(f'{API}/api/admin/monitor/metrics', headers=H(T_admin), timeout=10)
check('4.5 monitor metrics', r.status_code == 200)

# 报表
print(f'\n{"="*60}')
print(f'  E2E 业务流程: 通过 {PASS} / 失败 {FAIL}')
print(f'{"="*60}')
sys.exit(0 if FAIL == 0 else 1)
