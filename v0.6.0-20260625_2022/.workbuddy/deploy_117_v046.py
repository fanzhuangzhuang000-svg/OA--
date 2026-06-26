#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V0.4.6 B 数据权限: PHP 端 4 个新文件 + 8 个 Model 修改 -> 117"""
import os
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASSWORD = 'admin123'

LOCAL_BASE = r'D:\work\website\OA\pc-api'
REMOTE_BASE = '/var/www/oa-api'

# 4 个新文件
NEW_FILES = [
    ('app/Concerns/HasDataScope.php',                 'app/Concerns/HasDataScope.php'),
    ('app/Scopes/DataScope.php',                      'app/Scopes/DataScope.php'),
    ('app/Support/AuthScope.php',                     'app/Support/AuthScope.php'),
    ('app/Http/Controllers/Api/Concerns/HandlesDataScope.php', 'app/Http/Controllers/Api/Concerns/HandlesDataScope.php'),
]

# 7 个修改的 Model (本地 -> 远端)
MODIFIED_FILES = [
    'app/Models/ProjectModels.php',
    'app/Models/ConstructionLog.php',
    'app/Models/CustomerReceivable.php',
    'app/Models/Rectification.php',
    'app/Models/Warranty.php',
    'app/Models/WarrantyServiceOrder.php',
    'app/Models/WarrantyDeposit.php',
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=20)
sftp = ssh.open_sftp()

# 1. 上传新文件到 /tmp
print('=== [1/4] 上传新文件 ===')
for local_rel, remote_rel in NEW_FILES:
    local_path = os.path.join(LOCAL_BASE, local_rel)
    tmp = '/tmp/b_v046_' + remote_rel.replace('/', '_')
    sftp.put(local_path, tmp)
    print(f'  ✓ {local_rel}')

# 2. 上传修改的 Model
print('=== [2/4] 上传修改的 Model ===')
for rel in MODIFIED_FILES:
    local_path = os.path.join(LOCAL_BASE, rel)
    tmp = '/tmp/b_v046_mod_' + rel.replace('/', '_')
    sftp.put(local_path, tmp)
    print(f'  ✓ {rel}')
sftp.close()

# 3. sudo cp 新文件到 oa-api
print('=== [3/4] sudo cp 新文件 ===')
for local_rel, remote_rel in NEW_FILES:
    tmp = '/tmp/b_v046_' + remote_rel.replace('/', '_')
    target = REMOTE_BASE + '/' + remote_rel
    target_dir = os.path.dirname(target)
    cmd = f'sudo -n mkdir -p {target_dir} && sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}'
    si, so, se = ssh.exec_command(cmd)
    so.read(); se.read()  # 排空
    if si.channel.recv_exit_status() != 0:
        print(f'  ✗ {remote_rel}')
    else:
        print(f'  ✓ {remote_rel}')

# 4. sudo cp 修改的 Model
print('=== [4/4] sudo cp 修改的 Model ===')
for rel in MODIFIED_FILES:
    tmp = '/tmp/b_v046_mod_' + rel.replace('/', '_')
    target = REMOTE_BASE + '/' + rel
    cmd = f'sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}'
    si, so, se = ssh.exec_command(cmd)
    so.read(); se.read()
    if si.channel.recv_exit_status() != 0:
        print(f'  ✗ {rel}')
    else:
        print(f'  ✓ {rel}')

# 5. 重建 autoload (新加了 3 个目录)
print('=== [5/5] composer dump-autoload ===')
cmd = 'cd /var/www/oa-api && sudo -n -u www-data composer dump-autoload --no-dev --no-scripts 2>&1 | tail -5'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

# 6. 清 opcache (V0.4.4 验证过 reload 不清, 必须 restart)
print('=== restart php-fpm (清 opcache) ===')
cmd = 'sudo -n systemctl restart php8.5-fpm && sleep 2 && sudo -n systemctl is-active php8.5-fpm'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

# 7. 烟囱自检: 用 artisan tinker 验证 scope 已挂
print('=== 自检: scope 已注册? ===')
cmd = 'cd /var/www/oa-api && sudo -n -u www-data php artisan tinker --execute="echo \\App\\Models\\Project::query()->toSql();" 2>&1 | tail -3'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

ssh.close()
