#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推送前端 dist 到 152"""
import paramiko, os

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'
STAGING = '/tmp/oa-web-staging'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PWD, timeout=15)

    # 1) 清空 staging
    ssh.exec_command(f'sudo rm -rf {STAGING} && sudo mkdir -p {STAGING} && sudo chown ubuntu:ubuntu {STAGING}')

    # 2) sftp put 整个 dist
    sftp = ssh.open_sftp()
    file_count = 0
    for root, dirs, files in os.walk(LOCAL_DIST):
        for f in files:
            local = os.path.join(root, f).replace('\\', '/')
            rel = os.path.relpath(local, LOCAL_DIST).replace('\\', '/')
            remote = f'{STAGING}/{rel}'
            rdir = os.path.dirname(remote).replace('\\', '/')
            ssh.exec_command(f'mkdir -p {rdir}')
            sftp.put(local, remote)
            file_count += 1
    sftp.close()
    print(f'put {file_count} files')

    # 3) 备份 + rsync + chown
    cmds = [
        # 备份当前 oa-web (为了万一回滚)
        f'sudo mv {REMOTE_WEB} {REMOTE_WEB}.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true',
        f'sudo mkdir -p {REMOTE_WEB}',
        f'sudo rsync -a {STAGING}/ {REMOTE_WEB}/ 2>&1 | tail -3',
        f'sudo chown -R www-data:www-data {REMOTE_WEB}',
        f'sudo chmod 755 {REMOTE_WEB}',
        # 关键文件落地确认
        f'ls -la {REMOTE_WEB}/index.html',
        f'ls {REMOTE_WEB}/assets/ | wc -l',
        # 清理 staging
        f'sudo rm -rf {STAGING}',
    ]
    for c in cmds:
        print('---', c[:60])
        stdin, stdout, stderr = ssh.exec_command(c, timeout=120)
        out = stdout.read().decode(errors='ignore').strip()
        err = stderr.read().decode(errors='ignore').strip()
        if out: print(out)
        if err: print('ERR:', err[:300])
    ssh.close()
    print('\n✅ 前端 dist 推送完成')

if __name__ == '__main__':
    main()
