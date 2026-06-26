"""直接 hardcode 替换方法体里的 \\Xxx"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'rb') as f:
    content = f.read().decode('utf-8')

# 简单直接替换（不影响顶部 use）
# 因为顶部 use App\Models\Xxx 后面没空格没反斜杠
# 方法体里都是 \Xxx::
replacements = [
    ('\\ExpenseClaim::', '\\App\\Models\\ExpenseClaim::'),
    ('\\LeaveRequest::', '\\App\\Models\\LeaveRequest::'),
    ('\\ServiceOrder::', '\\App\\Models\\ServiceOrder::'),
    ('\\Receivable::', '\\App\\Models\\Receivable::'),
    ('\\Project::', '\\App\\Models\\Project::'),
    ('\\AttendanceRecord::', '\\App\\Models\\AttendanceRecord::'),
    ('\\Certificate::', '\\App\\Models\\Certificate::'),
    ('\\Customer::', '\\App\\Models\\Customer::'),
    ('\\EmployeeProfile::', '\\App\\Models\\EmployeeProfile::'),
    ('\\InventoryItem::', '\\App\\Models\\InventoryItem::'),
    ('\\MaintenanceContract::', '\\App\\Models\\MaintenanceContract::'),
    ('\\Vehicle::', '\\App\\Models\\Vehicle::'),
]

count = 0
for old, new in replacements:
    n = content.count(old)
    if n > 0:
        content = content.replace(old, new)
        count += n
        print(f'  {old} → {new}: {n} 处')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'w') as f:
    f.write(content)
print(f'✓ 替换 {count} 处')

# 重启 + 测
import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=15):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

run('cd /var/www/oa-api && sudo -u www-data composer dump-autoload 2>&1 | tail -3', t=30)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

# 测 HTTP
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
for url in ['/api/dashboard/todo', '/api/dashboard/project-progress', '/api/dashboard/service-stats', '/api/dashboard/revenue-trend', '/api/dashboard/stats']:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')[:300]
            print(f'  [200] {url}: {body}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:200]}')

ssh2.close()
