#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V0.4.7 安全收口 - PHP 端 3 个修改 + 2 个新 -> 117"""
import os
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASSWORD = 'admin123'

LOCAL_BASE = r'D:\work\website\OA\pc-api'
REMOTE_BASE = '/var/www/oa-api'

# 1 新文件
NEW_FILES = [
    ('tests/Unit/Scopes/AuthScopeTest.php', 'tests/Unit/Scopes/AuthScopeTest.php'),
    ('tests/Unit/Scopes/DataScopeTest.php', 'tests/Unit/Scopes/DataScopeTest.php'),
]

# 6 改文件
MODIFIED_FILES = [
    'app/Scopes/DataScope.php',                              # 加 logDeniedAccess
    'app/Http/Controllers/Api/Concerns/HandlesDataScope.php', # 重写 findScoped + respondNotFound
    'app/Http/Controllers/Api/DashboardController.php',      # 加 isFull 标志 + cache 按 user
    'app/Http/Controllers/Api/InventoryController.php',      # batchExport 加 scope_all 校验
    'app/Http/Controllers/Api/WarrantyController.php',       # 用 trait, show 区分 404/403
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=20)
sftp = ssh.open_sftp()

print('=== [1/4] 上传新文件 ===')
for local_rel, remote_rel in NEW_FILES:
    local_path = os.path.join(LOCAL_BASE, local_rel)
    tmp = '/tmp/v047_new_' + remote_rel.replace('/', '_')
    sftp.put(local_path, tmp)
    print(f'  ✓ {local_rel}')

print('=== [2/4] 上传修改的文件 ===')
for rel in MODIFIED_FILES:
    local_path = os.path.join(LOCAL_BASE, rel)
    tmp = '/tmp/v047_mod_' + rel.replace('/', '_')
    sftp.put(local_path, tmp)
    print(f'  ✓ {rel}')
sftp.close()

print('=== [3/4] sudo cp ===')
for local_rel, remote_rel in NEW_FILES:
    tmp = '/tmp/v047_new_' + remote_rel.replace('/', '_')
    target = REMOTE_BASE + '/' + remote_rel
    target_dir = os.path.dirname(target)
    cmd = f'sudo -n mkdir -p {target_dir} && sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}'
    si, so, se = ssh.exec_command(cmd)
    so.read(); se.read()
    rc = si.channel.recv_exit_status()
    if rc != 0: print(f'  ✗ {remote_rel}')
    else: print(f'  ✓ {remote_rel}')

for rel in MODIFIED_FILES:
    tmp = '/tmp/v047_mod_' + rel.replace('/', '_')
    target = REMOTE_BASE + '/' + rel
    cmd = f'sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}'
    si, so, se = ssh.exec_command(cmd)
    so.read(); se.read()
    rc = si.channel.recv_exit_status()
    if rc != 0: print(f'  ✗ {rel}')
    else: print(f'  ✓ {rel}')

print('=== [4/4] restart php-fpm ===')
cmd = 'sudo -n systemctl restart php8.5-fpm && sleep 2 && sudo -n systemctl is-active php8.5-fpm'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

ssh.close()
