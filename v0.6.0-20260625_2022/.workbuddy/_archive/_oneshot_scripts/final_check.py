import urllib.request, urllib.error, json
req = urllib.request.Request('http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']

# 之前500的 invoices 创建
data = {'invoice_no': 'TEST-002', 'customer_id': 1, 'amount': 1000.0, 'tax_rate': 0.13, 'type': 'sales', 'status': 'draft'}
r = urllib.request.Request('http://172.20.0.139:3001/api/finance/invoices',
    data=json.dumps(data).encode(),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    method='POST')
try:
    print('INVOICE POST:', urllib.request.urlopen(r, timeout=8).read().decode()[:200])
except urllib.error.HTTPError as e:
    print(f'INVOICE POST [{e.code}]:', e.read().decode()[:200])
