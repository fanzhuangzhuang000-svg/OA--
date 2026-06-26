import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')
for cmd in [
    'cd /var/www/oa-api && grep -E "login|register" routes/api.php | head -10',
    'cd /var/www/oa-api && cat app/Http/Controllers/Api/AuthController.php 2>/dev/null | head -80',
    'cd /var/www/oa-api && cat app/Http/Controllers/Api/Auth/LoginController.php 2>/dev/null | head -80',
]:
    si,so,se = ssh.exec_command(cmd)
    print('---', cmd[:60])
    print(so.read().decode() or se.read().decode())
ssh.close()
