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

# 拿到真实存在的ID
s, data = get('/projects')
real_pid = data['data']['data'][0]['id'] if data.get('data',{}).get('data') else None
print(f'真实项目ID: {real_pid}')

s, data = get('/expenses')
real_eid = data['data']['data'][0]['id'] if data.get('data',{}).get('data') else None
print(f'真实报销ID: {real_eid}')

s, data = get('/inventory')
real_iid = data['data']['data'][0]['id'] if data.get('data',{}).get('data') else None
print(f'真实库存ID: {real_iid}')

s, data = get('/vehicles')
real_vid = data['data']['data'][0]['id'] if data.get('data',{}).get('data') else None
print(f'真实车辆ID: {real_vid}')

# 重新测试detail接口
print('\n=== 用真实ID重测 ===')
tests = [
    f'/projects/{real_pid}',
    f'/projects/{real_pid}/tracking',
    f'/expenses/{real_eid}',
    f'/inventory/{real_iid}',
    f'/vehicles/{real_vid}',
    f'/vehicles/{real_vid}/insurances',
    f'/vehicles/{real_vid}/maintenances',
]
for url in tests:
    code, body = get(url)
    status = '✅' if code == 200 else '❌'
    print(f'  {status} [{code}] {url}')
