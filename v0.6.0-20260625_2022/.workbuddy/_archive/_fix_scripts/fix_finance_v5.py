"""彻底删残留的 2 行"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 删这两行
old = """        // 本月已批报销支出
            ->where('approved_at', '>=', now()->startOfMonth())
            ->sum('total_amount');
"""
if old in content:
    content = content.replace(old, '')
    print('✓ 删 3 行残渣')
else:
    print('⚠️ 未找到残渣')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'w') as f:
    f.write(content)
sftp.close()

# restart + test
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=15)
so.read()

import urllib.request, json
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
    print('overview HTTP', e.code, e.read().decode()[:300])
