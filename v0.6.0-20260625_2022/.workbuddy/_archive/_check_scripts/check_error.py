"""查最新错误"""
import paramiko
import re
import urllib.request, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace')
    return out

# 清空日志
run('sudo truncate -s 0 /var/www/oa-api/storage/logs/laravel.log', t=5)

# 触发一次
import urllib.error
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

try:
    req = urllib.request.Request('http://172.20.0.139:3000/api/finance/overview', headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=10) as r:
        print('overview:', r.read().decode())
except urllib.error.HTTPError as e:
    print('overview HTTP', e.code, e.read().decode())

# 看错误
out = run('sudo cat /var/www/oa-api/storage/logs/laravel.log 2>/dev/null')
errors = re.findall(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] production\.ERROR: (.+?)(?=\s*\{|\s*$)', out, re.MULTILINE)
print('\n最近错误:')
for ts, err in errors:
    print(f'  [{ts}] {err[:300]}')
