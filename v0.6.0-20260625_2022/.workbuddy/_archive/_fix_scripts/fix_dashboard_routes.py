"""在 routes/api.php 加 4 个 dashboard 路由"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/routes/api.php', 'rb') as f:
    raw = f.read()

is_crlf = b'\r\n' in raw
nl = b'\r\n' if is_crlf else b'\n'
content = raw.decode('utf-8')

# 在 screen 路由后插入 4 个
old = "        Route::get('screen', [DashboardController::class, 'screen']);" + nl.decode('utf-8')
new_routes = old + (
    "        Route::get('todo', [DashboardController::class, 'todo']);" + nl.decode('utf-8') +
    "        Route::get('project-progress', [DashboardController::class, 'projectProgress']);" + nl.decode('utf-8') +
    "        Route::get('service-stats', [DashboardController::class, 'serviceStats']);" + nl.decode('utf-8') +
    "        Route::get('revenue-trend', [DashboardController::class, 'revenueTrend']);" + nl.decode('utf-8')
)

if old in content:
    content = content.replace(old, new_routes)
    with sftp.open('/var/www/oa-api/routes/api.php', 'w') as f:
        f.write(content)
    print('✓ 4 个路由已添加到 api.php')
else:
    print('❌ 找不到 screen 路由')

sftp.close()

# 清缓存 + 重启
import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=10):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

run('cd /var/www/oa-api && sudo -u www-data php artisan route:clear 2>&1', t=15)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

out = run("sudo -u www-data php /var/www/oa-api/artisan route:list 2>&1 | grep -i dashboard | head -10")
print('=== 路由 ===')
print(out)

# 测 4 个接口
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
            body = r.read().decode('utf-8')[:400]
            print(f'  [200] {url}: {body}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:200]}')

ssh2.close()
