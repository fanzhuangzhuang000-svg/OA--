"""真实跨用户 403 全面验证 (v4)
用 lisi (id=72) 创建 lead/opp/quote/referrer，然后 admin (id=1) 试图改 → 期望 403
"""
import requests, subprocess, time

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0:
        raise SystemExit(f'登录失败: {j.get("message")}')
    return j['data']['token'], j['data']['user']

def sql(cmd):
    subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True)

# lisi 密码是什么? 看下 seed
out = subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
    "SELECT u.id, u.username, u.email FROM users u WHERE u.username IN ('lisi', 'sales_chen', 'sales_yang')"],
    capture_output=True, text=True)
print('用户查询:', out.stdout)

# 用 admin 和 lisi 验证
admin_token, admin = login('admin', 'admin123')
print(f'\nadmin id={admin["id"]}')

# 1) lead: 把一条 lead 的 owner_id 改 72
print('\n[1] lead')
r = requests.get(f'{BASE}/sales/leads?per_page=1', headers={'Authorization': f'Bearer {admin_token}'}, timeout=10)
lead_id = r.json()['data']['data'][0]['id']
sql(f"UPDATE leads SET owner_id = 72 WHERE id = {lead_id};")
r = requests.put(f'{BASE}/sales/leads/{lead_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'customer_name': 'admin改了别人的'}, timeout=10)
print(f'  admin PUT(别人 lead {lead_id}): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
assert r.status_code == 403, f'期望 403 实际 {r.status_code}'
# 还原
sql(f"UPDATE leads SET owner_id = 1 WHERE id = {lead_id};")
r = requests.put(f'{BASE}/sales/leads/{lead_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'customer_name': 'admin自己的'}, timeout=10)
print(f'  admin PUT(自己 lead {lead_id}): HTTP {r.status_code} code={r.json().get("code")}')

# 2) opp
print('\n[2] opp')
r = requests.get(f'{BASE}/sales/opps?per_page=1', headers={'Authorization': f'Bearer {admin_token}'}, timeout=10)
opp_id = r.json()['data']['data'][0]['id']
sql(f"UPDATE opportunities SET sales_id = 72 WHERE id = {opp_id};")
r = requests.put(f'{BASE}/sales/opps/{opp_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'name': 'admin改了别人的'}, timeout=10)
print(f'  admin PUT(别人 opp {opp_id}): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
assert r.status_code == 403
sql(f"UPDATE opportunities SET sales_id = 1 WHERE id = {opp_id};")
r = requests.put(f'{BASE}/sales/opps/{opp_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'name': 'admin自己的'}, timeout=10)
print(f'  admin PUT(自己 opp {opp_id}): HTTP {r.status_code} code={r.json().get("code")}')

# 3) referrer
print('\n[3] referrer')
r = requests.get(f'{BASE}/sales/referrers?per_page=1', headers={'Authorization': f'Bearer {admin_token}'}, timeout=10)
ref_id = r.json()['data']['data'][0]['id']
sql(f"UPDATE referrers SET owner_id = 72 WHERE id = {ref_id};")
r = requests.put(f'{BASE}/sales/referrers/{ref_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'name': 'admin改了别人的'}, timeout=10)
print(f'  admin PUT(别人 ref {ref_id}): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
assert r.status_code == 403
sql(f"UPDATE referrers SET owner_id = 1 WHERE id = {ref_id};")
r = requests.put(f'{BASE}/sales/referrers/{ref_id}', headers={'Authorization': f'Bearer {admin_token}'}, json={'name': 'admin自己的'}, timeout=10)
print(f'  admin PUT(自己 ref {ref_id}): HTTP {r.status_code} code={r.json().get("code")}')

# 4) quote
print('\n[4] quote')
r = requests.get(f'{BASE}/sales/quotes?per_page=1', headers={'Authorization': f'Bearer {admin_token}'}, timeout=10)
qid = r.json()['data']['data'][0]['id']
# quote 28 created_by=72 (lisi). admin 改应 403
r = requests.put(f'{BASE}/sales/quotes/{qid}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={'status': 'draft'}, timeout=10)
print(f'  admin PUT(别人 quote {qid}): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
assert r.status_code == 403
# 改成自己 (admin=1)
sql(f"UPDATE quotations SET created_by = 1 WHERE id = {qid};")
r = requests.put(f'{BASE}/sales/quotes/{qid}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={'status': 'draft'}, timeout=10)
print(f'  admin PUT(自己 quote {qid}): HTTP {r.status_code} code={r.json().get("code")}')

print('\n=== 全部 4 模块跨用户 403 验证通过 ✅ ===')
