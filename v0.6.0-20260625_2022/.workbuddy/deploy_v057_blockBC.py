#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.5.7 块B+C 部署脚本 - 数据字典 + 系统监控 (117 服务器)
- 推送 1 migration + 1 model + 2 controller + routes/api.php
- 推送前端 SystemDict.vue + SystemMonitor.vue + router
- optimize:clear + restart fpm
- 烟囱: 7 dict 端点 + 6 monitor 端点
"""
import os
import sys
import paramiko
import time

HOST = '192.168.3.117'
USER = 'nbcy'
PASSWORD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
LOCAL_WEB = r'D:\work\website\OA\pc-web'
REMOTE_API = '/var/www/oa-api'
REMOTE_WEB = '/var/www/oa-web'

API_FILES = [
    'database/migrations/2026_06_25_000026_create_system_dicts_table.php',
    'app/Models/SystemDict.php',
    'app/Http/Controllers/Api/SystemDictController.php',
    'app/Http/Controllers/Api/SystemMonitorController.php',
    'routes/api.php',
]

WEB_FILES = [
    'src/views/settings/SystemDict.vue',
    'src/views/settings/SystemMonitor.vue',
    'src/router/index.ts',
]

def run_remote(ssh, cmd, timeout=60):
    print(f'  $ {cmd[:120]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    if out: print(out[:2000])
    if err and 'WARN' not in err: print(f'  STDERR: {err[:500]}')
    return out, err

def main():
    print('=' * 60)
    print('V0.5.7 块B+C 部署 - 数据字典 + 系统监控 (117)')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=30)
    sftp = ssh.open_sftp()

    # [1] API
    print(f'\n[1/6] 上传 API {len(API_FILES)} 文件到 /tmp ...')
    for rel in API_FILES:
        local = os.path.join(LOCAL_API, rel).replace('\\', '/')
        name = os.path.basename(rel)
        remote_tmp = f'/tmp/{name}'
        if not os.path.exists(local):
            print(f'  ✗ {name} - 本地不存在')
            continue
        sftp.put(local, remote_tmp)
        size = os.path.getsize(local)
        print(f'  ✓ {name} ({size}B)')

    # [2] Web
    print(f'\n[2/6] 上传 web {len(WEB_FILES)} 文件到 /tmp ...')
    for rel in WEB_FILES:
        local = os.path.join(LOCAL_WEB, rel).replace('\\', '/')
        name = os.path.basename(rel)
        remote_tmp = f'/tmp/web_{name}'
        if not os.path.exists(local):
            print(f'  ✗ {name} - 本地不存在')
            continue
        sftp.put(local, remote_tmp)
        size = os.path.getsize(local)
        print(f'  ✓ {name} ({size}B)')

    # [3] sudo cp API + chown
    print('\n[3/6] sudo cp API+web + chown ...')
    for rel in API_FILES:
        name = os.path.basename(rel)
        target = f'{REMOTE_API}/{rel}'
        run_remote(ssh, f'sudo -n cp /tmp/{name} {target}', timeout=15)
    run_remote(ssh, f'sudo -n chown -R www-data:www-data {REMOTE_API}/app/Http/Controllers/Api {REMOTE_API}/app/Models {REMOTE_API}/app/Services {REMOTE_API}/database/migrations {REMOTE_API}/routes', timeout=15)

    for rel in WEB_FILES:
        name = os.path.basename(rel)
        target = f'{REMOTE_WEB}/src/{rel.replace("src/", "")}'
        run_remote(ssh, f'sudo -n cp /tmp/web_{name} {target}', timeout=15)
    run_remote(ssh, f'sudo -n chown -R www-data:www-data {REMOTE_WEB}/src/views/settings {REMOTE_WEB}/src/router', timeout=15)

    # [4] 跑 migration
    print('\n[4/6] 跑 migration ...')
    run_remote(ssh, f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan migrate --force 2>&1 | tail -10', timeout=120)

    # [5] vite build
    print('\n[5/6] 本地 vite build + 上传 dist ...')
    import subprocess
    build = subprocess.run(
        ['cmd', '/c', 'cd /d D:\\work\\website\\OA\\pc-web && npm run build 2>&1'],
        capture_output=True, text=True, timeout=300
    )
    print(f'  build returncode={build.returncode}')
    if build.returncode != 0:
        print(f'  STDERR: {build.stderr[-1000:]}')
    dist_dir = os.path.join(LOCAL_WEB, 'dist')
    if os.path.exists(dist_dir):
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, dist_dir).replace('\\', '/')
                if rel.startswith('assets/'):
                    target = f'{REMOTE_WEB}/dist/{rel}'
                    tmp = f'/tmp/dist_{os.path.basename(f)}'
                    sftp.put(fp, tmp)
                    run_remote(ssh, f'sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}', timeout=15)
        idx = os.path.join(dist_dir, 'index.html')
        if os.path.exists(idx):
            sftp.put(idx, '/tmp/dist_index.html')
            run_remote(ssh, f'sudo -n cp /tmp/dist_index.html {REMOTE_WEB}/dist/index.html && sudo -n chown www-data:www-data {REMOTE_WEB}/dist/index.html', timeout=15)
        print('  ✓ dist 已上传')

    # [6] optimize:clear + restart fpm + smoke
    print('\n[6/6] optimize:clear + restart fpm + 烟囱 ...')
    run_remote(ssh, f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan optimize:clear 2>&1 | tail -5', timeout=60)
    run_remote(ssh, 'sudo -n systemctl restart php8.5-fpm 2>&1', timeout=30)
    time.sleep(2)
    run_remote(ssh, "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -1", timeout=10)

    out, _ = run_remote(ssh, '''curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin1","password":"admin123"}' ''', timeout=15)
    import re
    m = re.search(r'"token":"([^"]+)"', out)
    if not m:
        print('  ✗ 登录失败')
        sftp.close(); ssh.close(); return 1
    token = m.group(1)
    print(f'  ✓ token = {token[:30]}...')

    smoke = [
        ('GET', '/api/dict/kinds'),
        ('GET', '/api/dict/grouped'),
        ('GET', '/api/dict'),
        ('GET', '/api/admin/monitor/metrics'),
        ('GET', '/api/admin/monitor/disk'),
        ('GET', '/api/admin/monitor/db'),
        ('GET', '/api/admin/monitor/services'),
        ('GET', '/api/admin/monitor/errors'),
        ('GET', '/api/admin/monitor/backups'),
        ('GET', '/settings/dict'),
        ('GET', '/settings/monitor'),
    ]
    for m_, p in smoke:
        if p.startswith('/settings/'):
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1{p}"
        else:
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1{p} -H 'Authorization: Bearer {token}'"
        out, _ = run_remote(ssh, cmd, timeout=10)
        code = out.strip()
        ok = code in ('200', '302')
        print(f'  {"✓" if ok else "✗"} {m_} {p} -> {code}')

    out, _ = run_remote(ssh, "cd /var/www/oa-api && sudo -n php -d opcache.enable=0 artisan route:list --path=dict 2>&1 | head -15", timeout=15)
    print(out[:1500])
    out, _ = run_remote(ssh, "cd /var/www/oa-api && sudo -n php -d opcache.enable=0 artisan route:list --path=admin/monitor 2>&1 | head -15", timeout=15)
    print(out[:1500])

    sftp.close()
    ssh.close()
    print('\n✅ V0.5.7 块B+C 部署完成')
    return 0

if __name__ == '__main__':
    sys.exit(main())
