import paramiko, sys
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')
import importlib.util
spec = importlib.util.spec_from_file_location('deploy', r'D:\work\website\OA\.workbuddy\deploy_to_172.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ssh = m.ssh_connect()
sftp = ssh.open_sftp()
LOCAL = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api'
files = [
    'AuthController.php',
    'DashboardController.php',
    'InventoryCategoryController.php',
    'PurchasePaymentRequestController.php',
    'EmployeeController.php',
]
for f in files:
    local = LOCAL + '\\' + f
    tmp = '/tmp/' + f
    remote = '/var/www/oa-api/app/Http/Controllers/Api/' + f
    sftp.put(local, tmp)
    print(f'已上传: {f}')
sftp.close()
names = ' '.join(f.replace('.php', '') for f in files)
cmd = f"""for f in {names}; do
  sudo cp /tmp/$f.php /var/www/oa-api/app/Http/Controllers/Api/$f.php
  sudo chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/$f.php
done && sudo systemctl restart php8.3-fpm && echo DEPLOY_OK"""
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())
print('ERR:', se.read().decode()[:500])
ssh.close()
