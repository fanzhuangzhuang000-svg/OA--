import paramiko

host = '172.20.0.139'
user = 'nbcy'
pwd = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pwd, timeout=15)
print('SSH 连接成功')

# 上传 FinanceController.php
sftp = ssh.open_sftp()
local = 'D:/work/website/OA/pc-api/app/Http/Controllers/Api/FinanceController.php'
remote_tmp = '/tmp/FinanceController.php'
remote_target = '/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php'

print('上传 FinanceController.php...')
sftp.put(local.replace('\\', '/'), remote_tmp)
ssh.exec_command(f'sudo cp {remote_tmp} {remote_target} && sudo chown www-data:www-data {remote_target}')
print('上传完成')

# 清理路由缓存 + 重启 FPM
print('清理缓存 + 重启 FPM...')
cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan route:clear',
    'cd /var/www/oa-api && sudo -u www-data php artisan config:clear',
    'sudo systemctl restart php8.3-fpm',
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    print(f'  {cmd[:50]}: {out[:100]}')

# 验证：不传 supplier_id 创建应付
print('\n验证：不传 supplier_id 创建应付...')
test = """
token=$(curl -s -X POST http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

curl -s -X POST http://127.0.0.1/api/finance/payables \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"amount":99999,"due_date":"2026-09-01","notes":"验证supplier_id可选"}' 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(test, get_pty=True, timeout=20)
out = stdout.read().decode('utf-8', errors='replace')
print('结果:', out[:400])

sftp.close()
ssh.close()
print('\n完成')
