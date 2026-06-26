"""
Deploy C1 backend to server (3 files)
"""
import paramiko, os

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
SRC = r'D:\work\website\OA\pc-api'
DST = '/var/www/oa-api'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS)
sftp = ssh.open_sftp()

files = [
    ('app/Http/Controllers/Api/RoleController.php', 'app/Http/Controllers/Api/RoleController.php'),
    ('database/seeders/PermissionRoleSeeder.php', 'database/seeders/PermissionRoleSeeder.php'),
    ('database/migrations/2026_06_16_160001_add_rbac_business_columns.php',
     'database/migrations/2026_06_16_160001_add_rbac_business_columns.php'),
]

# upload to /tmp first
for src_rel, dst_rel in files:
    src_path = os.path.join(SRC, src_rel)
    tmp_path = f'/tmp/c1_{os.path.basename(dst_rel)}'
    print(f'Uploading {src_rel} -> {tmp_path} ({os.path.getsize(src_path)}B)')
    sftp.put(src_path, tmp_path)
    # move to dst with sudo
    cmd = f'sudo -u www-data cp {tmp_path} {DST}/{dst_rel} && sudo chown www-data:www-data {DST}/{dst_rel} && echo OK'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'  deploy: {out} {err}')

# also upload updated api.php
api_php = os.path.join(SRC, 'routes', 'api.php')
sftp.put(api_php, '/tmp/c1_api.php')
cmd = f'sudo -u www-data cp /tmp/c1_api.php {DST}/routes/api.php && sudo chown www-data:www-data {DST}/routes/api.php && echo API-OK'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(f'api.php: {stdout.read().decode().strip()} {stderr.read().decode().strip()}')

sftp.close()
ssh.close()
