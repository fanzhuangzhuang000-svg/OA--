"""推 pc-web dist 到 117"""
import os, paramiko, time

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'
LOCAL = r'D:\work\website\OA\pc-web\dist'
REMOTE = '/var/www/oa-web'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
sftp = ssh.open_sftp()

# tar 压缩
import subprocess
tar_local = '/tmp/pc-web-v044.tar.gz'
if os.path.exists(tar_local):
    os.remove(tar_local)
subprocess.run(['tar', '-czf', tar_local, '-C', LOCAL, '.'], check=True)
print(f'local tar: {os.path.getsize(tar_local)} bytes')

# 上传
sftp.put(tar_local, '/tmp/pc-web-v044.tar.gz')
print('uploaded')

# 远程解压
cmds = [
    'sudo -n rm -rf /var/www/oa-web/*',
    'sudo -n mkdir -p /var/www/oa-web',
    'sudo -n tar -xzf /tmp/pc-web-v044.tar.gz -C /var/www/oa-web',
    'sudo -n chown -R www-data:www-data /var/www/oa-web',
    'sudo -n systemctl reload nginx',
]
for cmd in cmds:
    si, so, se = ssh.exec_command(cmd, timeout=60)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    print(f'  $ {cmd[:60]}... rc={rc} {err[:100]}')

print('done')
ssh.close()
