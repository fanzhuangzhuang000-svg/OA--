#!/usr/bin/env python3
"""V0.5.5.2 + V0.5.6 — 完整部署脚本"""
import os
import sys
from pathlib import Path
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PASS = 'nbcy@117'
REMOTE_BASE = '/tmp/oa-deploy'
LOCAL_BASE = r'D:\work\website\OA'

# 配置 sync dirs/files
SYNC = {
    'pc-api': {
        'local': f'{LOCAL_BASE}/pc-api',
        'remote': '/tmp/oa-deploy/pc-api',
        'exclude': ['vendor', 'node_modules', '.git', 'storage/logs', 'storage/framework/cache/data', '.phpunit.cache'],
        'suffix': 'api',
    },
    'pc-web': {
        'local': f'{LOCAL_BASE}/pc-web/dist',
        'remote': '/tmp/oa-deploy/pc-web-dist',
        'exclude': [],
        'suffix': 'web',
    },
}

def ssh_connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=10)
    return c

def run(c, cmd, timeout=120):
    print(f'  $ {cmd[:80]}')
    si, so, se = c.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', errors='replace')
    err = se.read().decode('utf-8', errors='replace')
    rc = so.channel.recv_exit_status()
    if rc != 0:
        print(f'  ! exit {rc}: {err[-200:]}')
    return rc, out, err

def upload_dir(ssh_c, local_dir, remote_dir, excludes):
    """SFTP 增量推送: local → /tmp/"""
    sftp = ssh_c.open_sftp()
    excludes = set(excludes or [])
    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in excludes and not d.startswith('.')]
        rel = os.path.relpath(root, local_dir)
        rdst = remote_dir if rel == '.' else f'{remote_dir}/{rel}'.replace('\\', '/')
        try: sftp.stat(rdst)
        except FileNotFoundError: run(ssh_c, f'mkdir -p {rdst}')
        for f in files:
            if f in excludes or f.startswith('.'): continue
            lp = os.path.join(root, f)
            rp = f'{rdst}/{f}'.replace('\\', '/')
            sftp.put(lp, rp)
    sftp.close()

def main():
    print(f'=== V0.5.5.2 + V0.5.6 部署 {HOST} ===')
    c = ssh_connect()
    try:
        # 1) 推代码
        print('[1] 推送代码到 /tmp')
        for label, cfg in SYNC.items():
            print(f'  pushing {label}...')
            run(c, f'rm -rf {cfg["remote"]}')
            run(c, f'mkdir -p {cfg["remote"]}')
            upload_dir(c, cfg['local'], cfg['remote'], cfg['exclude'])

        # 2) 复制到 web 目录
        print('[2] 复制到 /var/www/')
        run(c, 'sudo cp -r /tmp/oa-deploy/pc-api/* /var/www/oa-api/ && sudo chown -R www-data:www-data /var/www/oa-api')
        run(c, 'sudo cp -r /tmp/oa-deploy/pc-web-dist/* /var/www/oa-web/ && sudo chown -R www-data:www-data /var/www/oa-web')

        # 3) 跑 migration
        print('[3] 跑新 migration')
        run(c, 'cd /var/www/oa-api && sudo -u www-data php artisan migrate --force')

        # 4) 清缓存
        print('[4] 清缓存')
        run(c, 'cd /var/www/oa-api && sudo -u www-data php artisan config:clear && sudo -u www-data php artisan route:clear && sudo -u www-data php artisan cache:clear')

        # 5) 重启 fpm
        print('[5] 重启 php-fpm')
        run(c, 'sudo systemctl restart php8.5-fpm')

        # 6) 烟囱
        print('[6] 健康检查')
        run(c, 'curl -s -o /dev/null -w "api=%{http_code}\\n" http://127.0.0.1:8081/api/auth/me')
        run(c, 'curl -s -o /dev/null -w "web=%{http_code}\\n" http://127.0.0.1/')

        print('=== 部署完成 ===')
    finally:
        c.close()

if __name__ == '__main__':
    main()
