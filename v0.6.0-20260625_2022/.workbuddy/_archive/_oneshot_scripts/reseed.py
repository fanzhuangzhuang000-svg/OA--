"""
Re-seed to restore super admin
"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
cmd = 'cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=PermissionRoleSeeder --force --no-interaction 2>&1 | tail -5'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
print('SEED:', stdout.read().decode())

# verify
cmd = 'mysql -uoa_user -poa_password oa_db -e "SELECT id,name FROM roles ORDER BY id;" 2>&1 | grep -v Warning'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
ssh.close()
