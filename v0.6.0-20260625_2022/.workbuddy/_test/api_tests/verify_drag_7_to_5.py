import requests, subprocess, json

# 1) 登录
r = requests.post('http://127.0.0.1/api/auth/login', json={'username':'admin','password':'admin123'})
print(f'login: HTTP {r.status_code} code={r.json().get("code")}')
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

# 2) 拿 new 状态的 lead
r2 = requests.get('http://127.0.0.1/api/sales/leads', headers=h, params={'per_page': 10, 'status': 'new'})
leads = r2.json().get('data', {}).get('data', [])
print(f'new leads: {len(leads)}')
if not leads:
    print('没有 new 状态,跳过测试')
    exit(0)

# 3) 测试 7 段看板值拖动
lid = leads[0]['id']
print(f'\n测试 lead id={lid}')

tests = [
    ('negotiating', 'qualified'),   # 期望归一
    ('proposal', 'qualified'),      # 期望归一
    ('won', 'converted'),           # 期望归一
    ('lost', 'discarded'),          # 期望归一
    ('contacted', 'contacting'),    # 期望归一
    ('qualified', 'qualified'),     # 直接
    ('new', 'new'),                 # 边界: 自身
]
for board_val, expected_db in tests:
    # 状态机自身限制: 同一 lead 没法重置, 改用 SQL 直重置
    import subprocess
    subprocess.run(['psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
                    f"UPDATE leads SET status='new' WHERE id={lid};"],
                   env={'PGPASSWORD': 'oapass', 'PATH': '/usr/bin:/usr/local/bin'},
                   capture_output=True, text=True)
    r3 = requests.patch(f'http://127.0.0.1/api/sales/leads/{lid}/status', headers=h, json={'status': board_val})
    code = r3.json().get('code')
    db = r3.json().get('data', {}).get('status', '?') if code == 0 else '-'
    msg = r3.json().get('message', '')[:50] if code != 0 else ''
    mark = '✅' if code == 0 and db == expected_db else '❌'
    print(f'  {mark} PATCH {board_val:12s} → HTTP {r3.status_code} code={code} db={db} (期望 {expected_db}) {msg}')
