import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')
for cmd in [
    'cd /var/www/oa-api && php artisan tinker --execute="echo json_encode(App\\Models\\User::where(\\"id\\",1)->first([\\"id\\",\\"username\\",\\"email\\",\\"name\\"])->toArray());"',
]:
    si,so,se = ssh.exec_command(cmd)
    print(so.read().decode() or se.read().decode())
ssh.close()
