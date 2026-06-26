import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

# 更新 admin 密码
cmd = """cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="User::where('username','admin')->first()->update(['password'=>bcrypt('admin123')]);" """
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()

print('OUTPUT:', out)
if err:
    print('ERROR:', err[:500])

# 验证
stdin2, stdout2, stderr2 = ssh.exec_command(
    'cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="echo User::where(\'username\',\'admin\')->first()?->username;"'
)
print('VERIFY:', stdout2.read().decode())

ssh.close()
print('done')
