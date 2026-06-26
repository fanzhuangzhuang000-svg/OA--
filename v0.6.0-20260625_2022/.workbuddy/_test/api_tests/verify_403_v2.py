"""扩展 403 验证 - opp/referrer/pool"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    return r.json()['data']['token'], r.json()['data']['user']

def sql(cmd):
    subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True)

token, me = login('admin', 'admin123')
h = {'Authorization': f'Bearer {token}'}
user_id = me['id']
print(f'admin id={user_id}')

# 测 opp
r = requests.get(f'{BASE}/sales/opps?per_page=1', headers=h, timeout=10)
opps = r.json().get('data', {}).get('data', [])
opp_id = opps[0]['id'] if opps else None
print(f'\n[opp {opp_id}]')
sql(f"UPDATE sales_opportunities SET sales_id = 99999 WHERE id = {opp_id};")
r = requests.put(f'{BASE}/sales/opps/{opp_id}', headers=h, json={'name': 'x'}, timeout=10)
print(f'  PUT(非自己): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
sql(f"UPDATE sales_opportunities SET sales_id = {user_id} WHERE id = {opp_id};")
r = requests.put(f'{BASE}/sales/opps/{opp_id}', headers=h, json={'name': 'x'}, timeout=10)
print(f'  PUT(自己):   HTTP {r.status_code} code={r.json().get("code")}')

# 测 referrer
r = requests.get(f'{BASE}/sales/referrers?per_page=1', headers=h, timeout=10)
refs = r.json().get('data', {}).get('data', [])
if refs:
    ref_id = refs[0]['id']
    print(f'\n[referrer {ref_id}]')
    sql(f"UPDATE referrers SET owner_id = 99999 WHERE id = {ref_id};")
    r = requests.put(f'{BASE}/sales/referrers/{ref_id}', headers=h, json={'name': 'x'}, timeout=10)
    print(f'  PUT(非自己): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
    sql(f"UPDATE referrers SET owner_id = {user_id} WHERE id = {ref_id};")
    r = requests.put(f'{BASE}/sales/referrers/{ref_id}', headers=h, json={'name': 'x'}, timeout=10)
    print(f'  PUT(自己):   HTTP {r.status_code} code={r.json().get("code")}')
else:
    print('\n[referrer] 无数据')

# 测 quote
r = requests.get(f'{BASE}/sales/quotes?per_page=1', headers=h, timeout=10)
quotes = r.json().get('data', {}).get('data', [])
if quotes:
    qid = quotes[0]['id']
    # 看 quote 的 owner 字段名
    print(f'\n[quote {qid}]')
    # 先看字段
    out = subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
        "\\d quotations"], capture_output=True, text=True)
    print('  schema 字段:', [l for l in out.stdout.split('\n') if 'owner' in l.lower() or 'sales' in l.lower()][:5])
    # 试 sales_id
    sql(f"UPDATE quotations SET sales_id = 99999 WHERE id = {qid};")
    r = requests.put(f'{BASE}/sales/quotes/{qid}/status', headers=h, json={'status': 'draft'}, timeout=10)
    print(f'  PUT status(非自己): HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
    sql(f"UPDATE quotations SET sales_id = {user_id} WHERE id = {qid};")
    r = requests.put(f'{BASE}/sales/quotes/{qid}/status', headers=h, json={'status': 'draft'}, timeout=10)
    print(f'  PUT status(自己):   HTTP {r.status_code} code={r.json().get("code")}')
else:
    print('\n[quote] 无数据')
