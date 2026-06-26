"""用前端真实URL（按modules.ts定义）+ 数据库真实ID 测试"""
import urllib.request, urllib.error, json, os, re

req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
H = {'Authorization': f'Bearer {token}'}
BASE = 'http://172.20.0.139:3001/api'

def call(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'{BASE}{url}', headers=H), timeout=8)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return 'EXC', str(e)[:150]

# 从 api/modules.ts 提取所有真实函数调用
tests = set()
with open('pc-web/src/api/modules.ts', 'r', encoding='utf-8') as f:
    content = f.read()
for m in re.finditer(r"['\"`](/[a-z][a-z\-_/{}]+)['\"`]\s*[,)]", content):
    url = m.group(1)
    url = re.sub(r'/\$\{[^}]+\}', '/1', url)  # 用1代替{id}
    tests.add(url)

print(f'从 modules.ts 提取的API数: {len(tests)}\n')

ok, fail = [], []
for url in sorted(tests):
    code, body = call(url)
    if code == 200:
        ok.append(url)
        print(f'  ✅ [{code}] {url}')
    else:
        fail.append((url, code, body))
        print(f'  ❌ [{code}] {url}')

print(f'\n=== OK: {len(ok)} / FAIL: {len(fail)} ===')
