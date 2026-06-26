"""块六验证"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0: raise SystemExit(f'login fail: {j.get("message")}')
    return j['data']['token']

def sql(cmd):
    return subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True).stdout

admin_token = login('admin', 'admin123')
h = {'Authorization': f'Bearer {admin_token}'}

print('=' * 60)
print('块六 完整流程验证')
print('=' * 60)

# 1. mark-won opp 112
print('\n[1] oppsMarkWon opp=112 contract=100000')
r = requests.post(f'{BASE}/sales/opps/112/mark-won', headers=h, json={
    'contract_amount': 100000,
    'signed_at': '2026-06-23',
}, timeout=10)
print(f'HTTP {r.status_code} code={r.json().get("code")}')
if r.status_code != 200:
    print('msg:', r.json().get('message', '')[:100])

# 2. 看自动建的 settlement
print('\n[2] 自动建 settlement?')
out = sql("SELECT id, opportunity_id, referrer_id, amount, status FROM referral_settlements;")
print(out)

# 解析 sid
import re
# 从 pg 输出 '1 | 112 | 2 | 4200.00 | pending' 找 id 列
match = re.search(r'^\s*(\d+)\s*\|\s*112', out, re.MULTILINE)
sid = int(match.group(1)) if match else None
print(f'parsed sid={sid}')

if sid:
    # 3. 列表
    print('\n[3] GET /referral-settlements')
    r = requests.get(f'{BASE}/sales/referral-settlements', headers=h, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} total={r.json().get("data", {}).get("total", "?")}')

    # 4. stats
    print('\n[4] GET /referral-settlements/stats')
    r = requests.get(f'{BASE}/sales/referral-settlements/stats', headers=h, timeout=10)
    print(f'HTTP {r.status_code} data={r.json().get("data")}')

    # 5. 详情
    print(f'\n[5] GET /referral-settlements/{sid}')
    r = requests.get(f'{BASE}/sales/referral-settlements/{sid}', headers=h, timeout=10)
    d = r.json().get('data', {})
    print(f'HTTP {r.status_code} amount={d.get("amount")} status={d.get("status")} ref={d.get("referrer", {}).get("name")}')

    # 6. 审核
    print(f'\n[6] POST /{sid}/approve')
    r = requests.post(f'{BASE}/sales/referral-settlements/{sid}/approve', headers=h, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} status={r.json().get("data", {}).get("status")}')

    # 7. 发放
    print(f'\n[7] POST /{sid}/pay')
    r = requests.post(f'{BASE}/sales/referral-settlements/{sid}/pay', headers=h, json={
        'payment_no': f'TEST-PAY-{sid}',
        'payment_voucher': f'disk/sales/referral/2026/06/test-{sid}.pdf',
    }, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} status={r.json().get("data", {}).get("status")} paid_at={r.json().get("data", {}).get("paid_at")}')

    # 8. 验证 total_commission 累加
    print(f'\n[8] referrer.total_commission')
    out = sql("SELECT id, name, total_commission FROM referrers WHERE id = 2;")
    print(out)

print('\n=== 块六核心 7 项验证完成 ===')
