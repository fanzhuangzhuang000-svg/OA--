import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
stdin, stdout, stderr = ssh.exec_command('sudo grep -B 1 -A 10 "finance/invoices" /var/www/oa-api/storage/logs/laravel.log | tail -40')
print(stdout.read().decode())
ssh.close()
