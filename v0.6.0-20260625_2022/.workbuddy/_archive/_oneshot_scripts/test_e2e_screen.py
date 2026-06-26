"""
C3 E2E: login -> 通过 nginx 调 /api/dashboard/screen -> 保存 sample
"""
import json, urllib.request

API = 'http://172.20.0.139:3000'

# 1) login
body = json.dumps({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request(f'{API}/api/auth/login', data=body,
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read().decode())
token = data['data']['token']
print('TOKEN:', token[:25], '...')

# 2) GET /api/dashboard/screen
req = urllib.request.Request(f'{API}/api/dashboard/screen',
    headers={'Accept': 'application/json', 'Authorization': f'Bearer {token}'})
resp = urllib.request.urlopen(req, timeout=15)
body = json.loads(resp.read().decode())
print('code:', body.get('code'), 'message:', body.get('message'))
if body.get('code') == 0:
    d = body['data']
    print('metrics count:', len(d['metrics']))
    print('revenueChart count:', len(d['revenueChart']))
    print('projectStatus count:', len(d['projectStatus']))
    print('serviceMetrics:', d['serviceMetrics'])
    print('todos count:', len(d['todos']))
    with open(r'D:\work\website\OA\.workbuddy\screen_api_sample.json', 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False, indent=2)
    print('saved sample to screen_api_sample.json')
