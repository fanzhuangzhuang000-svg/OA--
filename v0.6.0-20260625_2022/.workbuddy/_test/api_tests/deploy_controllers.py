#!/usr/bin/env python3
"""部署修复后的 VehicleController 和 InventoryController 到 172"""
import paramiko, sys, os
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')
import importlib.util
spec = importlib.util.spec_from_file_location('deploy', r'D:\work\website\OA\.workbuddy\deploy_to_172.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ssh = m.ssh_connect()
sftp = ssh.open_sftp()

files = [
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\VehicleController.php',
     '/var/www/oa-api/app/Http/Controllers/Api/VehicleController.php'),
    (r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\InventoryController.php',
     '/var/www/oa-api/app/Http/Controllers/Api/InventoryController.php'),
]

for local, remote in files:
    fname = os.path.basename(local)
    tmp = '/tmp/' + fname
    print(f"📤 上传 {fname} ...")
    sftp.put(local, tmp)
    cmd = f"sudo cp {tmp} {remote} && sudo chown www-data:www-data {remote}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err: print(f"  STDERR: {err[:100]}")
    print(f"  ✅ {fname} 已部署")

sftp.close()
# 重启 PHP-FPM
print("\n🔄 重启 php8.3-fpm ...")
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart php8.3-fpm && echo DONE')
print(stdout.read().decode())
ssh.close()
print("\n✅ 完成")
