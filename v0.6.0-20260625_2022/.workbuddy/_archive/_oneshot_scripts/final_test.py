"""最终压力测试 - 用前端真实URL + 数据库已有ID"""
import urllib.request, urllib.error, json, os, re

# 登录
req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
H = {'Authorization': f'Bearer {token}'}
BASE = 'http://172.20.0.139:3001/api'

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'{BASE}{url}', headers=H), timeout=8)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:150]
    except Exception as e:
        return 'EXC', str(e)[:100]

# 1. 列出所有前端真实调用的API
def extract_apis():
    apis = set()
    for root, dirs, files in os.walk('pc-web/src'):
        for fn in files:
            if not fn.endswith(('.ts', '.vue', '.js')):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                for m in re.finditer(r"['\"`](/[a-z][a-z\-_/]+)['\"`]", content):
                    api = m.group(1)
                    # 排除 vue/组件路径
                    if any(api.startswith(p) for p in ['/assets', '/img', '/static', '/src/', '/views/', '/components/', '/router/', '/layout', '/@/', '/node_modules']):
                        continue
                    if '_id' in api or 'WIDTH' in api or 'HEIGHT' in api:
                        continue
                    apis.add(api)
            except:
                pass
    return apis

# 2. 提取后端定义的路由
def extract_backend_routes():
    routes = {}
    with open('pc-api/routes/api.php', 'r', encoding='utf-8') as f:
        for line in f:
            m = re.search(r"Route::(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", line)
            if m:
                method = m.group(1).upper()
                path = m.group(2).rstrip('/')
                base = re.sub(r'/\{[^}]+\}', '/{id}', path)
                routes.setdefault(base, set()).add(method)
    return routes

apis = extract_apis()
backend = extract_backend_routes()

print(f'前端真实调用: {len(apis)}')
print(f'后端定义路由: {len(backend)}')

# 3. 找出前端调用但后端未定义
missing = []
for api in sorted(apis):
    # 标准化为 base path
    norm = api
    # 把 {id} 占位
    norm = re.sub(r'/\$\{[^}]+\}', '/{id}', norm)
    norm = re.sub(r'/\d+', '/{id}', norm)
    
    # 检查是否有匹配
    found = False
    for bp in backend.keys():
        # 完全匹配或带 {id}
        if norm == bp or norm.rstrip('/{id}') == bp.rstrip('/{id}'):
            found = True
            break
        # 前缀匹配
        if norm.startswith(bp.split('{id}')[0]):
            found = True
            break
    if not found:
        missing.append(api)

print(f'\n=== 前端调用但后端路由缺失: {len(missing)} ===')
for m in sorted(set(missing))[:50]:
    print(f'  {m}')
