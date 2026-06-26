"""部署 P1 修复: project board + expense item_date 兜底"""
import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()
# 先传到 /tmp 再 sudo cp 过去
FILES = [
    (r'D:\work\website\OA\pc-api\routes\api.php', 'api.php'),
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\ProjectController.php', 'ProjectController.php'),
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\ExpenseController.php', 'ExpenseController.php'),
]
for local, name in FILES:
    sftp.put(local, f'/tmp/{name}')
sftp.close()
cmds = [
    'sudo cp /tmp/api.php /var/www/oa-api/routes/api.php',
    'sudo cp /tmp/ProjectController.php /var/www/oa-api/app/Http/Controllers/Api/ProjectController.php',
    'sudo cp /tmp/ExpenseController.php /var/www/oa-api/app/Http/Controllers/Api/ExpenseController.php',
    'sudo chown www-data:www-data /var/www/oa-api/routes/api.php /var/www/oa-api/app/Http/Controllers/Api/ProjectController.php /var/www/oa-api/app/Http/Controllers/Api/ExpenseController.php',
    'cd /var/www/oa-api && sudo -u www-data php artisan route:clear',
    'sudo systemctl restart php8.3-fpm',
]
for cmd in cmds:
    si,so,se = ssh.exec_command(cmd, timeout=30)
    out = so.read().decode('utf-8','replace').strip()
    err = se.read().decode('utf-8','replace').strip()
    print(f'  $ {cmd[:80]}')
    if out: print(f'    {out[:200]}')
    if err: print(f'    ERR: {err[:200]}')
time.sleep(2)
# 验证
si,so,se = ssh.exec_command('curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1:3001/api/auth/login', timeout=15)
login = so.read().decode()
import json
token = json.loads(login)['data']['token']
for ep in ['/api/projects/board']:
    si,so,se = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1:3001{ep}', timeout=15)
    print(f'  GET {ep}: {so.read().decode().strip()}')
si,so,se = ssh.exec_command(f'curl -s -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "Accept: application/json" -d \'{{"category":"测试","items":[{{"amount":10}}]}}\' http://127.0.0.1:3001/api/expenses', timeout=15)
print(f'  POST /api/expenses (item_date缺省): {so.read().decode().strip()[:200]}')
ssh.close()
print('  ✓ 部署完成')
