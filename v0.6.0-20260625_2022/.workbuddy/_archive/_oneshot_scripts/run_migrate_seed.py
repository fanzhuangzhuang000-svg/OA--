import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')

# 跑 migration + seeder，全部 sudo -u www-data 因为 www-data 是 owner
cmds = [
    # 先清 opcache
    'cd /var/www/oa-api && sudo -u www-data php artisan optimize:clear 2>&1 | tail -5',
    # 跑 migration（看输出）
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate --no-interaction 2>&1 | tail -10',
    # 跑 seeder
    'cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=PermissionRoleSeeder --no-interaction 2>&1 | tail -10',
    # 验证
    'mysql -uoa_user -poa_password oa_db -e "SELECT COUNT(*) AS perms FROM permissions; SELECT id,name,color FROM roles;" 2>&1 | grep -v Warning',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c, timeout=60)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'> {c}\n  {out}\n  ERR={err}')

ssh.close()
