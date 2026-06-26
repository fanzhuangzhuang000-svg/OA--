"""完整最终压力测试 - 全模块全端点"""
import urllib.request, urllib.error, json, os, re

# 登录
req = urllib.request.Request('http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
H = {'Authorization': f'Bearer {token}'}
BASE = 'http://172.20.0.139:3001/api'

def call(url, method='GET', data=None):
    try:
        r = urllib.request.Request(f'{BASE}{url}', headers=H, method=method)
        if data:
            r.data = json.dumps(data).encode()
            r.add_header('Content-Type', 'application/json')
        resp = urllib.request.urlopen(r, timeout=8)
        body = resp.read()
        try:
            return resp.status, json.loads(body)
        except:
            return resp.status, body[:200].decode(errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:150]
    except Exception as e:
        return 'EXC', str(e)[:100]

# 从 modules.ts 提取所有 URL
tests = set()
with open('pc-web/src/api/modules.ts', 'r', encoding='utf-8') as f:
    content = f.read()
for m in re.finditer(r"['\"`](/[a-z][a-z\-_/{}]+)['\"`]\s*[,)]", content):
    url = m.group(1)
    url = re.sub(r'/\$\{[^}]+\}', '/1', url)
    tests.add(url)

# 从 modules.ts 提取方法
methods = {}  # url -> method
# 简单识别: 在函数参数后面紧跟的是 get/post/put/delete
for m in re.finditer(r"\b(get|post|put|delete)\s*\(\s*['\"`](/[a-z][a-z\-_/{}]+)['\"`]", content):
    methods[m.group(2).replace('${id}', '1')] = m.group(1).upper()

ok, fail = [], []
for url in sorted(tests):
    method = methods.get(url, 'GET')
    code, body = call(url, method)
    if code == 200:
        ok.append((method, url))
    else:
        fail.append((method, url, code, body))

print(f'总端点数: {len(tests)}\n')
print(f'✅ OK: {len(ok)} ({len(ok)*100//len(tests)}%)')
print(f'❌ FAIL: {len(fail)}\n')

if fail:
    print('=== 失败列表 ===')
    for m, u, c, b in fail[:30]:
        print(f'  ❌ [{m} {c}] {u}')
        print(f'        {b[:100] if isinstance(b, str) else b}')
