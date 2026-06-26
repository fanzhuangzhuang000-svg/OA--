"""Test C3: dashboard screen endpoint"""
import urllib.request, json, urllib.parse
BASE = 'http://172.20.0.139:3001'
def call(method, path, token=None, body=None):
    parts = urllib.parse.urlparse(path)
    encoded_path = urllib.parse.quote(parts.path, safe='/=&?')
    if parts.query:
        encoded_path += '?' + urllib.parse.quote(parts.query, safe='=&')
    url = f'{BASE}{encoded_path}'
    data = json.dumps(body).encode() if body is not None else None
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# Login
code, body = call('POST', '/api/auth/login', body={'username': 'admin', 'password': 'admin123'})
token = json.loads(body)['data']['token']
print(f'LOGIN: {code}')

# Get screen data
code, body = call('GET', '/api/dashboard/screen', token=token)
print(f'GET /api/dashboard/screen: {code}')
if code == 200:
    data = json.loads(body)['data']
    print('\n=== metrics ===')
    for m in data['metrics']:
        print(f'  {m["label"]}: {m["value"]} (trend {m["trend"]}%)')
    print('\n=== revenueChart (近 12 月) ===')
    for r in data['revenueChart']:
        print(f'  {r["month"]}: ¥{r["value"]} (h={r["height"]}%)')
    print('\n=== projectStatus ===')
    for s in data['projectStatus']:
        print(f'  {s["label"]}: {s["count"]} ({s["pct"]}%)')
    print('\n=== serviceMetrics ===')
    print(f'  {data["serviceMetrics"]}')
    print('\n=== todos ===')
    for t in data['todos']:
        print(f'  {t["label"]}: {t["count"]}')
else:
    print(body)
