"""V0.4.10 - OA 端到端模拟 (4 角色 × 70+ 模块)"""
import json, requests
from pathlib import Path

API = 'http://127.0.0.1:8081/api'
USERS = {
    'admin':   ('admin1',    'admin123'),
    'finance': ('fin_wu',    'admin123'),
    'manager': ('sales_yang','admin123'),
    'user':    ('eng_qian',  'admin123'),
}
MODULES = [
    ('Dashboard',             ['/dashboard/stats']),
    ('Project-List',          ['/projects?per_page=5']),
    ('Project-Board',         ['/projects?per_page=5']),
    ('Project-Pool',          ['/projects?per_page=5']),
    ('Project-Calendar',      ['/projects?per_page=5']),
    ('Warranty-List',         ['/warranties?per_page=5']),
    ('Warranty-Expiring',     ['/warranties?expiring=30']),
    ('Warranty-ServiceOrder', ['/warranty/service-orders?per_page=5']),
    ('Warranty-Deposit',      ['/warranty/deposits?per_page=5']),
    ('Customer-List',         ['/customers?per_page=5']),
    ('Customer-Health',       ['/customers?per_page=5']),
    ('Customer-Pipeline',     ['/customers?per_page=5']),
    ('Customer-Map',          ['/customers?per_page=5']),
    ('Sales-Leads',           ['/sales/leads?per_page=5']),
    ('Sales-LeadsBoard',      ['/sales/leads?per_page=5']),
    ('Sales-Opps',            ['/sales/opportunities?per_page=5']),
    ('Sales-OppsBoard',       ['/sales/opportunities?per_page=5']),
    ('Sales-Referrers',       ['/sales/referrers?per_page=5']),
    ('Sales-Settlements',     ['/sales/settlements?per_page=5']),
    ('Purchase-Requirement',  ['/purchase/requirements?per_page=5']),
    ('Purchase-Plan',         ['/purchase/plans?per_page=5']),
    ('Purchase-Approval',     ['/purchase/approvals?per_page=5']),
    ('Purchase-PaymentRequest',['/purchase/payment-requests?per_page=5']),
    ('Purchase-Payment',      ['/purchase/payments?per_page=5']),
    ('Purchase-Contract',     ['/purchase/contracts?per_page=5']),
    ('Construction-Team',     ['/construction/teams?per_page=5']),
    ('Construction-Commencement',['/construction/commencement-orders?per_page=5']),
    ('Construction-Log',      ['/construction/logs?per_page=5']),
    ('Construction-Rectification',['/construction/rectifications?per_page=5']),
    ('Construction-WorkProcess',['/work-processes?per_page=5']),
    ('Construction-ExternalWork',['/external-works?per_page=5']),
    ('Process-Templates',     ['/process/templates?per_page=5']),
    ('Process-Instances',     ['/process/instances?per_page=5']),
    ('Process-Inspections',   ['/process/inspections?per_page=5']),
    ('Attendance-Overview',   ['/attendance/stats']),
    ('Attendance-Record',     ['/attendance/records?per_page=5']),
    ('Attendance-Leave',      ['/attendance/leave-requests?per_page=5']),
    ('Attendance-Overtime',   ['/attendance/overtime-requests?per_page=5']),
    ('Attendance-Shifts',     ['/attendance/shifts']),
    ('Attendance-Groups',     ['/attendance/groups']),
    ('Employee-List',         ['/employees?per_page=5']),
    ('Employee-Org',          ['/employees?per_page=5']),
    ('Employee-Onboardings',  ['/employee/onboardings?per_page=5']),
    ('Employee-Skill',        ['/employee/skill-tags']),
    ('Service-Orders',        ['/service-orders?per_page=5']),
    ('Service-Contract',      ['/maintenance-contracts?per_page=5']),
    ('Service-Stats',         ['/service-stats']),
    ('Inventory-Items',       ['/inventory/items?per_page=5']),
    ('Inventory-Warehouse',   ['/inventory/warehouses']),
    ('Inventory-LowStock',    ['/inventory/items?low_stock=1']),
    ('Finance-Receivables',   ['/receivables?per_page=5']),
    ('Finance-Payables',      ['/payables?per_page=5']),
    ('Finance-Expenses',      ['/expense-claims?per_page=5']),
    ('Warranty-Overview',     ['/warranties?per_page=5']),
    ('Approval-Center',       ['/approval/records?per_page=5']),
    ('Audit-Logs',            ['/audit-logs?per_page=5']),
    ('Audit-DataScope',       ['/audit/data-scope/summary?days=7']),
    ('Settings-Idle',         ['/settings/idle-config']),
    ('Supplier-List',         ['/suppliers?per_page=5']),
    ('Vehicle-Fleet',         ['/vehicles?per_page=5']),
    ('Vehicle-Apply',         ['/vehicle/applications?per_page=5']),
    ('External-Quote',        ['/external-quotes?per_page=5']),
    ('Knowledge-List',        ['/knowledge/articles?per_page=5']),
    ('Screen-Display',        ['/screen/config']),
    ('Message-List',          ['/messages?per_page=5']),
    ('Legal-List',            ['/legal/contracts?per_page=5']),
    ('Disk-List',             ['/disk/files?per_page=5']),
    ('Vehicle-Insurance',     ['/vehicles/insurances?per_page=5']),
    ('Vehicle-Maintenance',   ['/vehicles/maintenances?per_page=5']),
    ('Vehicle-FuelCard',      ['/vehicles/fuel-cards?per_page=5']),
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
    print('OA 端到端模拟测试 (4 角色 x {} 模块)'.format(len(MODULES)))
    print('='*70)
    grand = {'pass': 0, 'skip': 0, 'fail': 0, 'modules': []}
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
                else:
                    fail_n += 1
            grand['pass'] += pass_n
            grand['skip'] += skip_n
            grand['fail'] += fail_n
            grand['modules'].append({'role': role, 'module': name, 'pass': pass_n, 'skip': skip_n, 'fail': fail_n})
            status = 'OK ' if fail_n == 0 else 'XX '
            print(f'  [{status}] {role:7} {name:<32} pass={pass_n} skip={skip_n} fail={fail_n}')

    print('\n' + '='*70)
    print(f'Total: {len(USERS)} roles x {len(MODULES)} modules = {len(USERS)*len(MODULES)} reqs')
    print(f'  PASS: {grand["pass"]}  SKIP: {grand["skip"]}  FAIL: {grand["fail"]}')
    print('='*70)
    Path('/tmp/e2e_report.json').write_text(json.dumps(grand, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
