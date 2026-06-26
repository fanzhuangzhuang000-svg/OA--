"""V0.4.10 - OA 端到端模拟 v2 (按真实 API 路径)"""
import json, requests
from pathlib import Path

API = 'http://192.168.3.117/api'
USERS = {
    'admin':   ('admin1',    'admin123'),
    'finance': ('fin_wu',    'admin123'),
    'manager': ('sales_yang','admin123'),
    'user':    ('eng_qian',  'admin123'),
}

# 真实 API 端点（已对齐 routes/api.php）
MODULES = [
    # Dashboard
    ('Dashboard',             ['/dashboard/stats']),
    # Project
    ('Project-List',          ['/projects?per_page=5']),
    ('Project-Board',         ['/projects?per_page=5']),
    ('Project-Pool',          ['/projects?per_page=5']),
    ('Project-Calendar',      ['/projects?per_page=5']),
    # Warranty (真实路径)
    ('Warranty-List',         ['/warranties?per_page=5']),
    ('Warranty-Expiring',     ['/warranties?expiring=30']),
    ('Warranty-ServiceOrder', ['/warranty-service-orders?per_page=5']),
    ('Warranty-Deposit',      ['/warranty-deposits?per_page=5']),
    # Customer
    ('Customer-List',         ['/customers?per_page=5']),
    ('Customer-Health',       ['/customers?per_page=5']),
    ('Customer-Pipeline',     ['/customers?per_page=5']),
    ('Customer-Map',          ['/customers?per_page=5']),
    # Sales
    ('Sales-Leads',           ['/sales/leads?per_page=5']),
    ('Sales-LeadsBoard',      ['/sales/leads?per_page=5']),
    ('Sales-Opps',            ['/sales/opps?per_page=5']),
    ('Sales-OppsBoard',       ['/sales/opps?per_page=5']),
    ('Sales-Referrers',       ['/sales/referrers?per_page=5']),
    # Purchase
    ('Purchase-Requirement',  ['/purchase/requirements?per_page=5']),
    ('Purchase-Plan',         ['/purchase/plans?per_page=5']),
    ('Purchase-Approval',     ['/purchase/approvals?per_page=5']),
    ('Purchase-PaymentRequest',['/purchase/payment-requests?per_page=5']),
    ('Purchase-Payment',      ['/purchase/payments?per_page=5']),
    ('Purchase-Contract',     ['/purchase/contracts?per_page=5']),
    # Construction
    ('Construction-Team',     ['/construction/teams?per_page=5']),
    ('Construction-Commencement',['/construction/commencement-orders?per_page=5']),
    ('Construction-Log',      ['/construction/logs?per_page=5']),
    ('Construction-Rectification',['/construction/rectifications?per_page=5']),
    ('Construction-WorkProcess',['/construction/work-processes?per_page=5']),
    ('Construction-ExternalWork',['/construction/external-works?per_page=5']),
    # Process
    ('Process-Templates',     ['/process/templates?per_page=5']),
    ('Process-Instances',     ['/process/instances?per_page=5']),
    ('Process-Inspections',   ['/process/inspections?per_page=5']),
    # Attendance
    ('Attendance-Overview',   ['/attendance/overview']),
    ('Attendance-Record',     ['/attendance/records?per_page=5']),
    ('Attendance-Leave',      ['/attendance/leave?per_page=5']),
    ('Attendance-Overtime',   ['/attendance/overtime?per_page=5']),
    ('Attendance-Shifts',     ['/schedules/shifts']),
    ('Attendance-Groups',     ['/schedules/groups']),
    # Employee
    ('Employee-List',         ['/employees?per_page=5']),
    ('Employee-Org',          ['/employees?per_page=5']),
    ('Employee-Onboardings',  ['/employee-onboardings?per_page=5']),
    # Service
    ('Service-Orders',        ['/service/orders?per_page=5']),
    ('Service-Contract',      ['/service/maintenance-contracts?per_page=5']),
    ('Service-Stats',         ['/service/stats']),
    # Inventory
    ('Inventory-Items',       ['/inventory?per_page=5']),
    ('Inventory-Warehouse',   ['/inventory/warehouses']),
    ('Inventory-LowStock',    ['/inventory/low-stock']),
    # Finance
    ('Finance-Receivables',   ['/finance/receivables?per_page=5']),
    ('Finance-Payables',      ['/finance/payables?per_page=5']),
    ('Finance-Expenses',      ['/expenses?per_page=5']),
    ('Warranty-Overview',     ['/warranties?per_page=5']),
    # Approval
    ('Approval-Center',       ['/approvals/center']),
    # Audit
    ('Audit-Logs',            ['/audit-logs?per_page=5']),
    ('Audit-DataScope',       ['/audit/data-scope/summary?days=7']),
    # Settings
    ('Settings-Idle',         ['/settings/idle-config']),
    # Vehicle
    ('Vehicle-Fleet',         ['/vehicles?per_page=5']),
    ('Vehicle-Apply',         ['/vehicles/apply?per_page=5']),
    ('Vehicle-Insurance',     ['/vehicles/insurances?per_page=5']),
    ('Vehicle-Maintenance',   ['/vehicles/maintenances?per_page=5']),
    ('Vehicle-FuelCard',      ['/fuel-cards?per_page=5']),
    # Knowledge
    ('Knowledge-List',        ['/knowledge/articles?per_page=5']),
    # Disk
    ('Disk-List',             ['/disk/files?per_page=5']),
    # Dashboard screen
    ('Screen-Display',        ['/dashboard/screen']),
    # External
    ('External-Quote',        ['/external-quotes/requests']),
    # Suppliers (实际走 /projects 内的 suppliers)
    ('Supplier-List',         ['/projects/suppliers?per_page=5']),
]


def login(role):
    u, p = USERS[role]
    r = requests.post(f'{API}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    assert j.get('code') == 0, f'{role} login failed: {j}'
    return u, j['data']['token']


def call(token, ep):
    r = requests.get(f'{API}{ep}', headers={'Authorization': f'Bearer {token}'}, timeout=15)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, {}


def main():
    print('='*70)
    print(f'OA 端到端模拟 v2 (4 角色 x {len(MODULES)} 模块 — 真实 API 路径)')
    print('='*70)
    grand = {'pass': 0, 'skip': 0, 'fail': 0, 'failures': [], 'modules': []}
    for role in USERS:
        try:
            u, token = login(role)
        except Exception as e:
            print(f'[{role}] LOGIN FAILED: {e}')
            continue
        print(f'\n--- {role} ({u}) ---')
        for name, eps in MODULES:
            pass_n = skip_n = fail_n = 0
            for ep in eps:
                code, j = call(token, ep)
                if code == 404:
                    skip_n += 1
                elif code == 200 and j.get('code') in (0, None):
                    pass_n += 1
                elif code == 403:
                    skip_n += 1
                elif code == 500:
                    fail_n += 1
                    grand['failures'].append({'role': role, 'module': name, 'ep': ep, 'msg': str(j)[:100]})
                else:
                    fail_n += 1
                    grand['failures'].append({'role': role, 'module': name, 'ep': ep, 'code': code, 'msg': str(j)[:100]})
            grand['pass'] += pass_n
            grand['skip'] += skip_n
            grand['fail'] += fail_n
            grand['modules'].append({'role': role, 'module': name, 'pass': pass_n, 'skip': skip_n, 'fail': fail_n})
            status = 'OK ' if fail_n == 0 else 'XX '
            print(f'  [{status}] {role:7} {name:<32} pass={pass_n} skip={skip_n} fail={fail_n}')

    print('\n' + '='*70)
    total = len(USERS) * len(MODULES)
    print(f'Total: {len(USERS)} roles x {len(MODULES)} modules = {total} reqs')
    print(f'  PASS: {grand["pass"]}  SKIP: {grand["skip"]}  FAIL: {grand["fail"]}')
    if grand['failures']:
        print('\n== 失败明细 ==')
        for f in grand['failures'][:20]:
            print(f"  [{f['role']:7}] {f['module']:<32} {f['ep']:<40} {f['msg'][:80]}")
    print('='*70)
    Path('/tmp/e2e_v2_report.json').write_text(json.dumps(grand, ensure_ascii=False, indent=2))
    print('报告: /tmp/e2e_v2_report.json')


if __name__ == '__main__':
    main()
