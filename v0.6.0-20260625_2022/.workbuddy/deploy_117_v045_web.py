#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V0.4.5 前端 dist 推 117"""
import os
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASSWORD = 'admin123'
LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=20)
sftp = ssh.open_sftp()

# 1. 上传 dist 到 /tmp/dist_*
print('=== [1/3] 上传 dist 到 /tmp ===')
uploaded = 0
for root, dirs, files in os.walk(LOCAL_DIST):
    for f in files:
        local_path = os.path.join(root, f)
        rel = os.path.relpath(local_path, LOCAL_DIST).replace(os.sep, '/')
        tmp_path = '/tmp/dist_' + rel.replace('/', '_')
        sftp.put(local_path, tmp_path)
        uploaded += 1
print(f'  ✓ {uploaded} 文件')
sftp.close()

# 2. sudo cp 到 /var/www/oa-web
print('=== [2/3] sudo cp 到 /var/www/oa-web ===')
for root, dirs, files in os.walk(LOCAL_DIST):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), LOCAL_DIST).replace(os.sep, '/')
        tmp_path = '/tmp/dist_' + rel.replace('/', '_')
        target = REMOTE_WEB + '/' + rel
        target_dir = os.path.dirname(target).replace('\\', '/')
        cmd = f'sudo -n mkdir -p {target_dir} && sudo -n cp {tmp_path} {target}'
        si, so, se = ssh.exec_command(cmd)
        so.read()

# chown + clear
ssh.exec_command(f'sudo -n chown -R www-data:www-data {REMOTE_WEB}')
ssh.exec_command(f'sudo -n rm -rf /tmp/dist_*')
print('  ✓ 复制完成')

# 3. 验证
print('=== [3/3] 验证 ===')
si, so, se = ssh.exec_command(f'sudo -n ls {REMOTE_WEB}/ | head -5')
print('  顶层:')
print(so.read().decode().rstrip().replace('\n', '\n  '))
si, so, se = ssh.exec_command(f'sudo -n ls {REMOTE_WEB}/assets/ | wc -l')
print(f'  assets 数量: {so.read().decode().strip()}')
si, so, se = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/')
print(f'  HTTP / -> {so.read().decode()}')

ssh.close()
print('✅ 推送完成')
