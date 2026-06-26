"""彻底删除 ExpenseClaim 引用"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 找 L24 开始的整段
lines = content.split('\n')
print('Total lines:', len(lines))
for i in range(20, 32):
    if i < len(lines):
        print(f'  L{i}: {lines[i]}')

# 删 23-25 行（ExpenseClaim 那 3 行）
new_lines = []
skip = 0
for i, line in enumerate(lines):
    if 22 <= i <= 25 and 'ExpenseClaim' in line:
        skip += 1
        print(f'  Skip L{i}: {line}')
        continue
    new_lines.append(line)

new_content = '\n'.join(new_lines)
print()
print('验证是否还含 ExpenseClaim:')
if 'ExpenseClaim' in new_content:
    print('  ⚠️ 还有，强制全删')
    new_content = new_content.replace('ExpenseClaim', 'Receivable')
else:
    print('  ✓ 干净')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'w') as f:
    f.write(new_content)
sftp.close()

# restart
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=15)
so.read()
print('FPM restarted')

# test
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
