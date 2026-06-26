"""把方法里的 \\Xxx 改成 \\App\\Models\\Xxx（完全限定）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'rb') as f:
    raw = f.read()
content = raw.decode('utf-8')

# 替换 4 个方法里的裸 \Xxx 为 \App\Models\Xxx
# 注意：只替换方法体里的（避免误伤顶部 use 语句）
# 用更精确的替换：定位 4 个新方法
import re

# 4 个新方法区域: todo() projectProgress() serviceStats() revenueTrend()
# 用正则匹配并替换方法体里的 \Xxx

# 简单做法：替换所有 \ExpenseClaim / \LeaveRequest / \ServiceOrder / \Receivable / \Project / \DB
# 但只在方法体里（前 5 个是 Model，\DB 是 Facade）

models = ['ExpenseClaim', 'LeaveRequest', 'ServiceOrder', 'Receivable', 'Project']
for m in models:
    # 替换 \m 为 \App\Models\m（不影响已经带 App\Models 的）
    content = re.sub(r'(?<!\\Models\\)\b\\' + m + r'\b', '\\\\App\\\\Models\\\\' + m, content)
# \DB 是 Facade，不动
# 但 \Illuminate\Http\Request 应该改 \Illuminate\Http\Request（已有完整路径）

# 但要小心：顶部 use 语句里的 \Xxx 不能改。看下 use 语句
# use App\Models\Xxx — 没有 \，所以不影响

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'w') as f:
    f.write(content)
sftp.close()
print('✓ 已替换 \\Xxx 为 \\App\\Models\\Xxx')

# 重启 + 测
import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=15):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

# 清缓存
run('cd /var/www/oa-api && sudo -u www-data php artisan config:clear 2>&1', t=15)
run('cd /var/www/oa-api && sudo -u www-data composer dump-autoload 2>&1 | tail -3', t=30)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

# 测 HTTP
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
for url in ['/api/dashboard/todo', '/api/dashboard/project-progress', '/api/dashboard/service-stats', '/api/dashboard/revenue-trend']:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')[:300]
            print(f'  [200] {url}: {body}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:200]}')

ssh2.close()
