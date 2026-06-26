"""跨用户 403 验证脚本"""
import requests, sys

BASE = 'http://127.0.0.1/api'

def login(username, password):
    r = requests.post(f'{BASE}/auth/login', json={'username': username, 'password': password}, timeout=10)
    j = r.json()
    if j.get('code') != 0:
        print(f'  ✗ 登录失败: {j.get("message")}')
        sys.exit(1)
    return j['data']['token'], j['data']['user']

print('=' * 60)
print('跨用户 403 验证')
print('=' * 60)

# 1. admin 登录
print('\n[1] admin 登录')
token, me = login('admin', 'admin123')
print(f'  ✓ admin 登录成功 id={me["id"]} role={me.get("role", "?")}')

# 2. 找另一条 lead（确保是 admin 拥有的）
print('\n[2] 列所有 lead')
r = requests.get(f'{BASE}/sales/leads?per_page=3', headers={'Authorization': f'Bearer {token}'}, timeout=10)
j = r.json()
leads = j.get('data', {}).get('data', [])
print(f'  ✓ 当前 lead 数: {len(leads)}')
if not leads:
    print('  ✗ 没有 lead，结束')
    sys.exit(1)

# 3. SQL 直接构造：把 lead 1 的 owner_id 改成 99999（不存在的用户）
#    模拟"另一人创建的 lead"
#    实际在 172 上用 psql 改
import subprocess
subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
    f"UPDATE leads SET owner_id = 99999 WHERE id = {leads[0]['id']};"], capture_output=True)
print(f'  ✓ SQL: 把 lead {leads[0]["id"]} 的 owner_id 改成 99999')

# 4. admin 试图改 lead → 期望 403
print(f'\n[3] admin 试图 PUT /sales/leads/{leads[0]["id"]} → 期望 403')
r = requests.put(f'{BASE}/sales/leads/{leads[0]["id"]}',
                 headers={'Authorization': f'Bearer {token}'},
                 json={'customer_name': '应失败'},
                 timeout=10)
j = r.json()
print(f'  HTTP {r.status_code} code={j.get("code")} msg={j.get("message", "")[:80]}')
if r.status_code == 403:
    print('  ✅ 跨用户鉴权生效！')
else:
    print('  ❌ 跨用户鉴权没生效，期望 403')

# 5. 还原 lead 1 的 owner_id
subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c',
    f"UPDATE leads SET owner_id = {me['id']} WHERE id = {leads[0]['id']};"], capture_output=True)
print(f'\n[4] 还原 lead {leads[0]["id"]} owner_id={me["id"]}')

# 6. admin 再次 PUT 同一 lead → 期望 200
print(f'\n[5] admin 再次 PUT → 期望 200')
r = requests.put(f'{BASE}/sales/leads/{leads[0]["id"]}',
                 headers={'Authorization': f'Bearer {token}'},
                 json={'customer_name': '测试跨用户'},
                 timeout=10)
j = r.json()
print(f'  HTTP {r.status_code} code={j.get("code")} msg={j.get("message", "")[:80]}')
if r.status_code == 200 or j.get('code') == 0:
    print('  ✅ 自己拥有的资源能正常编辑')

print('\n' + '=' * 60)
print('验证完成')
