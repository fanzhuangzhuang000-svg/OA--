"""战败复活验证"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    return r.json()['data']['token']

def sql(cmd):
    subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True)

token = login('admin', 'admin123')
h = {'Authorization': f'Bearer {token}'}

# 拿一个不是 admin 的 opp 改 lost
r = requests.get(f'{BASE}/sales/opps?per_page=1', headers=h, timeout=10)
opps = r.json().get('data', {}).get('data', [])
oid = opps[0]['id']
print(f'测试 opp_id={oid}')
sql(f"UPDATE opportunities SET stage='lost', lost_reason='other', sales_id=72 WHERE id={oid};")

# admin 复活 (sales_id=72 不是 admin) → 应 403
r = requests.post(f'{BASE}/sales/opps/{oid}/revive', headers=h, timeout=10)
print(f"admin revive (别人商机): HTTP {r.status_code} code={r.json().get('code')} msg={r.json().get('message','')[:60]}")

# 把 sales_id 改成 admin，stage 还是 lost，再试 → 中间件放行，但 oppsRevive 自己检查 role → admin 应该放行
sql(f"UPDATE opportunities SET stage='lost', sales_id=1 WHERE id={oid};")
r = requests.post(f'{BASE}/sales/opps/{oid}/revive', headers=h, timeout=10)
print(f"admin revive (自己商机): HTTP {r.status_code} code={r.json().get('code')} msg={r.json().get('message','')[:60]}")

# 还原 lost
sql(f"UPDATE opportunities SET stage='lost' WHERE id={oid};")
