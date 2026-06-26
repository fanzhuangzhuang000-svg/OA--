"""修复顶部 use 的重复 App\\Models\\"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'rb') as f:
    content = f.read().decode('utf-8')

# 修复 use 行：'use App\\Models\\App\\Models\\Xxx' → 'use App\\Models\\Xxx'
fixes = [
    ('use App\\Models\\App\\Models\\ExpenseClaim;', 'use App\\Models\\ExpenseClaim;'),
    ('use App\\Models\\App\\Models\\LeaveRequest;', 'use App\\Models\\LeaveRequest;'),
    ('use App\\Models\\App\\Models\\Project;', 'use App\\Models\\Project;'),
    ('use App\\Models\\App\\Models\\Receivable;', 'use App\\Models\\Receivable;'),
    ('use App\\Models\\App\\Models\\ServiceOrder;', 'use App\\Models\\ServiceOrder;'),
]
for old, new in fixes:
    n = content.count(old)
    if n > 0:
        content = content.replace(old, new)
        print(f'  {old} → {new}: {n}')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'w') as f:
    f.write(content)
print('✓ use 已修复')

# 重启
import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=15):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

run('cd /var/www/oa-api && sudo -u www-data composer dump-autoload 2>&1 | tail -2', t=30)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

# 测所有 dashboard 接口
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
print('\n=== 测 5 个 dashboard 接口 ===')
for url in [
    '/api/dashboard/stats',
    '/api/dashboard/recent-projects',
    '/api/dashboard/recent-service-orders',
    '/api/dashboard/screen',
    '/api/dashboard/todo',
    '/api/dashboard/project-progress',
    '/api/dashboard/service-stats',
    '/api/dashboard/revenue-trend',
]:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')[:200]
            print(f'  [200] {url}: {body}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:150]}')

ssh2.close()
