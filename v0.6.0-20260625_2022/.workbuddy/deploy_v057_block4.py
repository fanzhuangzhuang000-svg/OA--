#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.5.7 块4 部署脚本 - 维修成本归集 (117 服务器)
- 推送 1 service + 1 controller + 1 dashboard + routes/api.php
- 重建 web dist (MaintenanceWidget + RepairCostReport + router)
- optimize:clear + restart fpm
- 烟囱: 5 cost 端点 + dashboard widget
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

# 推送的 API 文件
API_FILES = [
    'app/Services/RepairCostStat.php',
    'app/Http/Controllers/Api/RepairCostSummaryController.php',
    'app/Http/Controllers/Api/DashboardController.php',
    'routes/api.php',
]

# 推送的 web 文件
WEB_FILES = [
    'src/views/dashboard/components/MaintenanceWidget.vue',
    'src/views/finance/RepairCostReport.vue',
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
    print('V0.5.7 块4 部署 - 维修成本归集 (117)')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=30)
    sftp = ssh.open_sftp()

    # [1] 上传 API 文件
    print(f'\n[1/7] 上传 API {len(API_FILES)} 文件到 /tmp ...')
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

    # [2] 上传 web 文件
    print(f'\n[2/7] 上传 web {len(WEB_FILES)} 文件到 /tmp ...')
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

    # [3] sudo cp API 文件 + chown
    print('\n[3/7] sudo cp API + chown ...')
    for rel in API_FILES:
        name = os.path.basename(rel)
        target = f'{REMOTE_API}/{rel}'
        run_remote(ssh, f'sudo -n cp /tmp/{name} {target}', timeout=15)
    run_remote(ssh, f'sudo -n chown -R www-data:www-data {REMOTE_API}/app/Http/Controllers/Api {REMOTE_API}/app/Services {REMOTE_API}/routes', timeout=15)

    # [4] sudo cp web 文件
    print('\n[4/7] sudo cp web 源文件 ...')
    # 源文件不直接用 (要 build), 但保留作回滚备份
    for rel in WEB_FILES:
        name = os.path.basename(rel)
        target = f'{REMOTE_WEB}/src/{rel.replace("src/", "")}'
        run_remote(ssh, f'sudo -n cp /tmp/web_{name} {target}', timeout=15)
    run_remote(ssh, f'sudo -n chown -R www-data:www-data {REMOTE_WEB}/src/views/dashboard {REMOTE_WEB}/src/views/finance {REMOTE_WEB}/src/router', timeout=15)

    # [5] 跑 vite build 生成 dist
    print('\n[5/7] 本地 vite build + 上传 dist ...')
    import subprocess
    build = subprocess.run(
        ['cmd', '/c', 'cd /d D:\\work\\website\\OA\\pc-web && npm run build 2>&1'],
        capture_output=True, text=True, timeout=300
    )
    print(f'  build returncode={build.returncode}')
    if build.returncode != 0:
        print(f'  STDOUT: {build.stdout[-1500:]}')
        print(f'  STDERR: {build.stderr[-500:]}')
    # 上传整个 dist (含 hash 化的 js/css)
    dist_dir = os.path.join(LOCAL_WEB, 'dist')
    if not os.path.exists(dist_dir):
        print('  ✗ dist 目录不存在')
    else:
        run_remote(ssh, f'sudo -n rm -rf {REMOTE_WEB}/dist/assets_tmp', timeout=15)
        # 用 rsync 风格, 简化: rm dist/assets + put 新文件
        # 先列本地文件
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, dist_dir).replace('\\', '/')
                if rel.startswith('assets/'):
                    target = f'{REMOTE_WEB}/dist/{rel}'
                    tmp = f'/tmp/dist_{os.path.basename(f)}'
                    sftp.put(fp, tmp)
                    run_remote(ssh, f'sudo -n cp {tmp} {target} && sudo -n chown www-data:www-data {target}', timeout=15)
        # 单独处理 index.html
        idx = os.path.join(dist_dir, 'index.html')
        if os.path.exists(idx):
            sftp.put(idx, '/tmp/dist_index.html')
            run_remote(ssh, f'sudo -n cp /tmp/dist_index.html {REMOTE_WEB}/dist/index.html && sudo -n chown www-data:www-data {REMOTE_WEB}/dist/index.html', timeout=15)
        print('  ✓ dist 已上传')

    # [6] optimize:clear + restart fpm
    print('\n[6/7] optimize:clear + restart fpm + 清 cache ...')
    run_remote(ssh, f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan optimize:clear 2>&1 | tail -5', timeout=60)
    run_remote(ssh, 'sudo -n systemctl restart php8.5-fpm 2>&1', timeout=30)
    time.sleep(2)
    run_remote(ssh, 'sudo -n systemctl status php8.5-fpm 2>&1 | head -3', timeout=10)
    run_remote(ssh, "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -2", timeout=15)

    # [7] 烟囱: 5 cost 端点 + dashboard widget + 路由
    print('\n[7/7] 烟囱测试 ...')
    out, _ = run_remote(ssh, '''curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin1","password":"admin123"}' ''', timeout=15)
    import re
    m = re.search(r'"token":"([^"]+)"', out)
    if not m:
        print('  ✗ 登录失败')
        sftp.close(); ssh.close(); return 1
    token = m.group(1)
    print(f'  ✓ token = {token[:30]}...')

    smoke_apis = [
        ('GET', '/api/repair-cost/overview'),
        ('GET', '/api/repair-cost/by-month?months=6'),
        ('GET', '/api/repair-cost/by-project'),
        ('GET', '/api/repair-cost/by-customer'),
        ('GET', '/api/repair-cost/by-method'),
        ('GET', '/api/dashboard/maintenance-stats'),
        ('GET', '/finance/repair-cost'),  # 前端 SPA 路由
    ]
    for m_, p in smoke_apis:
        # /finance/repair-cost 走 nginx (前端), 其他走 oa-api
        if p.startswith('/finance/'):
            url = f'http://127.0.0.1{p}'
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {url}"
        else:
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1{p} -H 'Authorization: Bearer {token}'"
        out, _ = run_remote(ssh, cmd, timeout=10)
        code = out.strip()
        ok = code in ('200', '302')
        print(f'  {"✓" if ok else "✗"} {m_} {p} -> {code}')

    # 检查路由注册
    out, _ = run_remote(ssh, "cd /var/www/oa-api && sudo -n php -d opcache.enable=0 artisan route:list --path=repair-cost 2>&1 | head -10", timeout=15)
    print(out[:1500])

    sftp.close()
    ssh.close()
    print('\n✅ V0.5.7 块4 部署完成')
    return 0

if __name__ == '__main__':
    sys.exit(main())
