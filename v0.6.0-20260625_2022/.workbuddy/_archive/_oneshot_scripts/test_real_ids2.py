import urllib.request, urllib.error, json

req = urllib.request.Request(
    'http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'}
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']
H = {'Authorization': f'Bearer {token}'}

def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'http://172.20.0.139:3001/api{url}', headers=H), timeout=8)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:100]

# 直接看响应结构
for url in ['/projects', '/expenses', '/inventory', '/vehicles', '/finance/accounts']:
    code, body = get(url)
    if code == 200:
        print(f'{url}: type={type(body["data"]).__name__}')
        if isinstance(body['data'], list):
            print(f'  列表长度: {len(body["data"])}, 第一项: {body["data"][0] if body["data"] else "空"}')
        elif isinstance(body['data'], dict):
            print(f'  keys: {list(body["data"].keys())[:8]}')
            if 'data' in body['data']:
                items = body['data']['data']
                print(f'  data长度: {len(items) if items else 0}')
                if items and len(items) > 0:
                    print(f'  第一项ID: {items[0].get("id")}')
    else:
        print(f'{url}: [{code}]')
