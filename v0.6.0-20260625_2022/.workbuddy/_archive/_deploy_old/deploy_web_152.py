"""Deploy frontend to 152 server"""
import paramiko
import os
import posixpath
import sys

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
LOCAL_WEB = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'

print(f'连接 {HOST}...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

# 清空 web 目录
print(f'清空 {REMOTE_WEB}...')
stdin, stdout, stderr = ssh.exec_command(f'sudo rm -rf {REMOTE_WEB}/* 2>/dev/null; echo DONE')
print(stdout.read().decode())

print(f'上传前端文件 from {LOCAL_WEB}...')
sftp = ssh.open_sftp()
n = 0
for dirpath, dirnames, filenames in os.walk(LOCAL_WEB):
    dirnames[:] = [d for d in dirnames if d not in {'.git', 'node_modules'}]
    rel = os.path.relpath(dirpath, LOCAL_WEB).replace(os.sep, '/')
    remote_dir = REMOTE_WEB if rel == '.' else posixpath.join(REMOTE_WEB, rel)
    try:
        sftp.stat(remote_dir)
    except IOError:
        stdin, _, _ = ssh.exec_command(f'sudo mkdir -p {remote_dir}')
    for fn in filenames:
        local_path = os.path.join(dirpath, fn)
        try:
            sftp.put(local_path, posixpath.join(remote_dir, fn))
            n += 1
            if n % 100 == 0:
                print(f'已上传 {n} 个文件...')
        except Exception as e:
            print(f'[WARN] {fn}: {e}')
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f'sudo chown -R www-data:www-data {REMOTE_WEB}')
print(f'\n✓ 前端上传完成: {n} 个文件')
print('✓ 权限修正完成')
ssh.close()
print('✅ 前端部署完成!')