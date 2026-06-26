import urllib.request, urllib.error, json
req = urllib.request.Request('http://172.20.0.139:3001/api/auth/login',
    data=json.dumps({'username':'admin','password':'admin123'}).encode(),
    headers={'Content-Type':'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
token = resp['data']['token']

# 用前端可能传的字段触发一次 invoices POST
data = {
    'invoice_no': 'TEST-001',
    'customer_id': 1,
    'amount': 1000.0,
    'tax_rate': 0.13,
    'type': 'sales',
    'status': 'draft',
}
r = urllib.request.Request('http://172.20.0.139:3001/api/finance/invoices',
    data=json.dumps(data).encode(),
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept': 'application/json'},
    method='POST')
try:
    print(urllib.request.urlopen(r, timeout=8).read().decode())
except urllib.error.HTTPError as e:
    print(f'[{e.code}]', e.read().decode()[:500])

# 然后看日志
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
stdin, stdout, stderr = ssh.exec_command('sudo tail -100 /var/www/oa-api/storage/logs/laravel.log | grep -A 5 -i "invoice\|error" | tail -40')
print('---LOG---')
print(stdout.read().decode())
ssh.close()
