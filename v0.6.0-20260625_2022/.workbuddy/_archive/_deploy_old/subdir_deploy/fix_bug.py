#!/usr/bin/env python3
"""部署修复后的后端代码"""
import paramiko
import os

host = '152.136.115.121'
user = 'ubuntu'
pw = 'Aa782997781.'

base = r'D:\work\website\OA'

files = [
    (os.path.join(base, 'pc-api/app/Http/Controllers/Api/ProjectController.php'),
    '/var/www/oa-api/app/Http/Controllers/Api/ProjectController.php'),
    (os.path.join(base, 'pc-api/app/Http/Controllers/Api/VehicleController.php'),
    '/var/www/oa-api/app/Http/Controllers/Api/VehicleController.php'),
    (os.path.join(base, 'pc-api/app/Http/Controllers/Api/ExpenseController.php'),
    '/var/www/oa-api/app/Http/Controllers/Api/ExpenseController.php'),
    (os.path.join(base, 'pc-api/app/Http/Controllers/Api/InventoryController.php'),
    '/var/www/oa-api/app/Http/Controllers/Api/InventoryController.php'),
    (os.path.join(base, 'pc-api/app/Http/Controllers/Api/ServiceController.php'),
    '/var/www/oa-api/app/Http/Controllers/Api/ServiceController.php'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pw)

for local, remote in files:
    name = os.path.basename(remote)
    sftp = ssh.open_sftp()
    sftp.put(local, '/tmp/' + name)
    sftp.close()
    ssh.exec_command(f'sudo cp /tmp/{name} {remote} && sudo chown www-data:www-data {remote} && sudo rm /tmp/{name}')
    print(f'Uploaded: {name}')

ssh.exec_command('sudo systemctl restart php8.3-fpm')
print('PHP-FPM restarted')
ssh.close()
print('Done!')