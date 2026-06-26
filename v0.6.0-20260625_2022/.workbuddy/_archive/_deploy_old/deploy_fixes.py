"""部署修复到172服务器"""
import paramiko, os, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

sftp = ssh.open_sftp()

# 上传修改的文件
files_to_upload = [
    'pc-api/routes/api.php',
    'pc-api/app/Http/Controllers/Api/AttendanceController.php',
    'pc-api/app/Http/Controllers/Api/CustomerController.php',
    'pc-api/app/Http/Controllers/Api/FinanceController.php',
    'pc-api/app/Http/Controllers/Api/PurchaseLogisticsController.php',
]

for f in files_to_upload:
    if not os.path.exists(f):
        print(f'NOT FOUND: {f}')
        continue
    basename = os.path.basename(f)
    remote_tmp = f'/tmp/{basename}'
    print(f'Uploading {f} -> {remote_tmp} ...')
    sftp.put(f, remote_tmp)
    # 用 sudo 复制到目标位置
    target = f'/var/www/oa-api/{f.replace("pc-api/", "")}'
    cmd = f'sudo cp {remote_tmp} {target} && sudo chown www-data:www-data {target} && sudo rm -f {remote_tmp}'
    ssh.exec_command(cmd)
    
print('\nFiles uploaded. Now clearing routes cache...')
ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan route:clear && sudo systemctl restart php8.3-fpm')

# 验证
import time
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://localhost:3001/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\'')
out = stdout.read().decode()
print(f'\nLogin test: {out[:200]}')

sftp.close()
ssh.close()
print('\n✅ Deployment complete')
