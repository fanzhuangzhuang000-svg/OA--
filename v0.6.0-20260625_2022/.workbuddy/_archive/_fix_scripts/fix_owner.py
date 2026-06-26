import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')
si,so,se = ssh.exec_command('ls -la /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php')
print('OWNER:', so.read().decode())
si,so,se = ssh.exec_command('sudo -n chown nbcy:nbcy /var/www/oa-api/app/Http/Controllers/Api/DashboardController.php && echo OK_NB')
print('chown nbcy:', so.read().decode(), se.read().decode())
ssh.close()
