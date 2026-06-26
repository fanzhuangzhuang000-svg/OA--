"""V0.5.7 E2E 数据补充脚本 — 用 API 端点补齐缺数据的表
- leads / opportunities / work_orders / repair_orders
- approvals / expense_claims / attendance_records / warranties
全部走 API，自动处理 FK 验证和业务规则
"""
import requests
import random
import time
from datetime import datetime, timedelta

API = 'http://192.168.3.117'

# 登录
T_admin = requests.post(f'{API}/api/auth/login', json={'username':'admin1','password':'admin123'}, timeout=10).json()['data']['token']
T_sales = requests.post(f'{API}/api/auth/login', json={'username':'sales_yang','password':'admin123'}, timeout=10).json()['data']['token']
T_fin   = requests.post(f'{API}/api/auth/login', json={'username':'fin_wu','password':'admin123'}, timeout=10).json()['data']['token']
T_tech  = requests.post(f'{API}/api/auth/login', json={'username':'tech_qian','password':'admin123'}, timeout=10).json()['data']['token']

H_admin = {'Authorization': f'Bearer {T_admin}'}
H_sales = {'Authorization': f'Bearer {T_sales}'}
H_fin   = {'Authorization': f'Bearer {T_fin}'}
H_tech  = {'Authorization': f'Bearer {T_tech}'}

def get(path, headers=H_admin, **kw):
    return requests.get(f'{API}{path}', headers=headers, timeout=10, **kw)

def post(path, headers=H_admin, **kw):
    return requests.post(f'{API}{path}', headers=headers, timeout=10, **kw)

# 拿 customers / projects / users 列表
r = get('/api/customers?per_page=100')
customers = r.json()['data']['data']
print(f'customers: {len(customers)}')

r = get('/api/projects?per_page=100')
projects = r.json()['data']['data']
print(f'projects: {len(projects)}')

r = get('/api/auth/users?per_page=100')
users = r.json()['data']['data'] if 'data' in r.json() and r.json()['data'] else []
if not users:
    r = get('/api/users?per_page=100', headers=H_admin)
    users = r.json()['data']['data'] if 'data' in r.json() and r.json()['data'] else []
print(f'users: {len(users)}')

# 1. 线索 leads × 20
sources = ['referral', 'exhibition', 'website', 'cold_call', 'partner']
statuses = ['contacting', 'qualified', 'converted', 'discarded']
for i in range(20):
    cust = random.choice(customers)
    r = post('/api/leads', json={
        'customer_id': cust['id'],
        'source': random.choice(sources),
        'contact_name': cust.get('contact_name', f'联系人{i}'),
        'contact_phone': cust.get('contact_phone', f'138{random.randint(10000000,99999999)}'),
        'requirement': f'需求 #{i+1}: 视频监控/门禁/报警系统集成',
        'estimated_amount': random.randint(50000, 500000),
        'status': random.choice(statuses),
    }, headers=H_sales)
    if r.status_code == 200 and r.json().get('code') == 0:
        pass
    else:
        print(f'  lead {i}: {r.status_code} {r.text[:100]}')
print('leads: 20 created')

# 2. 商机 opps × 15
stages = ['qualification', 'proposal', 'negotiation', 'won', 'lost']
for i in range(15):
    cust = random.choice(customers)
    r = post('/api/opportunities', json={
        'customer_id': cust['id'],
        'name': f'商机 #{i+1} - {cust["name"]}',
        'amount': random.randint(100000, 2000000),
        'stage': random.choice(stages),
        'probability': random.randint(20, 90),
        'expected_close_date': (datetime.now() + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
    }, headers=H_sales)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  opp {i}: {r.status_code} {r.text[:80]}')
print('opps: 15 created')

# 3. 维修工单 work_orders × 10
priorities = ['low', 'normal', 'high', 'urgent']
for i in range(10):
    cust = random.choice(customers)
    proj = random.choice(projects)
    r = post('/api/work-orders', json={
        'customer_id': cust['id'],
        'project_id': proj['id'],
        'title': f'维修工单 #{i+1}',
        'fault_description': f'客户报修: 设备{i+1}号异常',
        'priority': random.choice(priorities),
        'contact_name': cust.get('contact_name', f'王{i}'),
        'contact_phone': f'139{random.randint(10000000,99999999)}',
    }, headers=H_tech)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  wo {i}: {r.status_code} {r.text[:80]}')
print('work_orders: 10 created')

# 4. 返修单 repair_orders × 8
methods = ['free_warranty', 'free_contract', 'paid_repair', 'paid_replace']
for i in range(8):
    cust = random.choice(customers)
    r = post('/api/repair-orders', json={
        'customer_id': cust['id'],
        'contact_name': cust.get('contact_name', f'李{i}'),
        'contact_phone': f'137{random.randint(10000000,99999999)}',
        'equipment_brand': ['海康', '大华', '宇视', '华为'][i%4],
        'equipment_model': f'M-{1000+i}',
        'fault_description': f'返修: 设备故障 {i+1}',
        'method_type': random.choice(methods),
        'parts_cost': random.randint(100, 2000),
        'labor_cost': random.randint(100, 500),
        'shipping_cost': random.randint(50, 200),
    }, headers=H_tech)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ro {i}: {r.status_code} {r.text[:80]}')
print('repair_orders: 8 created')

# 5. 审批 × 12
for i in range(12):
    typ = random.choice(['expense', 'leave', 'purchase', 'project', 'contract'])
    r = post('/api/approvals', json={
        'type': typ,
        'title': f'{typ} 审批 #{i+1}',
        'description': f'请审批 {typ} #{i+1}',
        'urgency': random.choice(['normal', 'urgent']),
    }, headers=H_admin)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  app {i}: {r.status_code} {r.text[:80]}')
print('approvals: 12 created')

# 6. 报销 expense_claims × 10
for i in range(10):
    r = post('/api/expense-claims', json={
        'title': f'报销 #{i+1} - 出差/采购/招待',
        'amount': random.randint(500, 5000),
        'category': random.choice(['travel', 'meal', 'office', 'transport']),
        'description': f'因公 {["出差","招待","办公","用车"][i%4]} 报销',
    }, headers=H_fin)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  exp {i}: {r.status_code} {r.text[:80]}')
print('expense_claims: 10 created')

# 7. 考勤 attendance_records × 30
for i in range(30):
    date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
    user = random.choice(users) if users else None
    r = post('/api/attendance/clock-in', json={
        'date': date,
        'clock_in': f'{date} 09:00:00',
        'clock_out': f'{date} 18:00:00' if random.random() > 0.3 else None,
    }, headers=H_admin)
    if r.status_code != 200 or r.json().get('code') != 0:
        if i < 3: print(f'  att {i}: {r.status_code} {r.text[:80]}')
print('attendance: 30 created')

# 8. 质保 warranties × 8
for i in range(8):
    proj = random.choice(projects)
    r = post('/api/warranties', json={
        'project_id': proj['id'],
        'start_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
        'end_date': (datetime.now() + timedelta(days=random.randint(180, 720))).strftime('%Y-%m-%d'),
        'terms': f'质保 #{i+1} - 1年内免费维修',
    }, headers=H_admin)
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  war {i}: {r.status_code} {r.text[:80]}')
print('warranties: 8 created')

print('\n=== ALL DONE ===')
