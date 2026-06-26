"""
V1.1 前端部署 → 172.20.0.139
"""
import os, sys
import paramiko

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL = r'D:\work\website\OA\pc-web\dist'
REMOTE = '/var/www/oa-web'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
print(f'[SSH] {HOST} connected')

# 1) rsync via sftp - delete remote first to avoid stale
si, so, se = ssh.exec_command(f'sudo rm -rf {REMOTE} && sudo mkdir -p {REMOTE} && sudo chown -R {USER}:{USER} {REMOTE}')
so.read()
print(f'[CLEAN] {REMOTE}')

sftp = ssh.open_sftp()
n = 0
for dp, dns, fns in os.walk(LOCAL):
    rel = os.path.relpath(dp, LOCAL).replace('\\', '/')
    rdir = f'{REMOTE}/{rel}' if rel != '.' else REMOTE
    try:
        sftp.stat(rdir)
    except IOError:
        sftp.mkdir(rdir)
    for fn in fns:
        lp = os.path.join(dp, fn).replace('\\', '/')
        rp = f'{rdir}/{fn}'
        sftp.put(lp, rp)
        n += 1
sftp.close()
print(f'[SFTP] uploaded {n} files')

# 2) chown www-data
si, so, se = ssh.exec_command(f'sudo chown -R www-data:www-data {REMOTE}')
so.read()
print(f'[CHOWN] www-data')

# 3) reload nginx (静态资源不需要 fpm restart)
si, so, se = ssh.exec_command('sudo nginx -s reload')
so.read()
print(f'[NGINX] reload')

# 4) verify
import time; time.sleep(2)
for ep in ['/api/process/industries', '/api/process/templates']:
    cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:3001{ep}"
    si, so, se = ssh.exec_command(cmd)
    out = so.read().decode().strip()
    print(f'[VERIFY] {ep} → {out}')

ssh.close()
print('done')