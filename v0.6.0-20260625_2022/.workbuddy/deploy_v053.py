#!/usr/bin/env python3
"""
V0.5.3 增量部署到 117
- 推后端 (php-api/) 改动
- 推前端 dist/
- 备份 .env
- 跑 migration
- 重启 fpm
- 跑 smoke
"""
import os, sys, time, subprocess, base64
import paramiko
from pathlib import Path

HOST = '192.168.3.117'
USER = 'nbcy'
PWD  = 'admin123'
API  = 'http://192.168.3.117'

ROOT_LOCAL = Path(r'D:\work\website\OA')
API_LOCAL  = ROOT_LOCAL / 'pc-api'
WEB_LOCAL  = ROOT_LOCAL / 'pc-web'

REMOTE_API  = '/var/www/oa-api'
REMOTE_WEB  = '/var/www/oa-web'

def ssh():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PWD, timeout=10)
    return c

def run(c, cmd, echo=True, check=True):
    if echo: print(f'  $ {cmd[:120]}')
    stdin, stdout, stderr = c.exec_command(cmd, timeout=180)
    rc = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', 'ignore')
    err = stderr.read().decode('utf-8', 'ignore')
    if check and rc != 0:
        print(f'  ✗ rc={rc} stderr={err[:200]}')
        sys.exit(1)
    return rc, out, err

def upload(ssh_c, local, remote):
    """单文件上传 — 走 /tmp 暂存 + sudo cp (www-data 写权问题)"""
    sftp = ssh_c.open_sftp()
    tmp_remote = f'/tmp/v053_{int(time.time()*1000)}_{os.path.basename(local)}'
    try:
        sftp.put(str(local), tmp_remote)
    finally:
        sftp.close()
    # sudo cp 到目标
    parent = str(Path(remote).parent).replace('\\', '/')
    run(ssh_c, f'sudo mkdir -p {parent}', echo=False, check=False)
    run(ssh_c, f'sudo cp {tmp_remote} {remote}', echo=False)
    run(ssh_c, f'sudo chown www-data:www-data {remote}', echo=False)
    run(ssh_c, f'sudo chmod 644 {remote}', echo=False)
    run(ssh_c, f'rm -f {tmp_remote}', echo=False, check=False)

def upload_dir(ssh_c, local_dir, remote_dir, excludes=None):
    """目录上传 — 先全部 put 到 /tmp, 再 sudo cp -r 整树"""
    excludes = excludes or set()
    sftp = ssh_c.open_sftp()
    tmp_base = f'/tmp/v053_upload_{int(time.time()*1000)}'
    run(ssh_c, f'mkdir -p {tmp_base}', echo=False)
    try:
        for root, dirs, files in os.walk(local_dir):
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith('.')]
            rel = os.path.relpath(root, local_dir)
            if rel == '.':
                rdst = tmp_base
            else:
                rdst = f'{tmp_base}/{rel}'.replace('\\', '/')
            try:
                sftp.stat(rdst)
            except FileNotFoundError:
                run(ssh_c, f'mkdir -p {rdst}', echo=False, check=False)
            for f in files:
                if f in excludes or f.startswith('.'):
                    continue
                lp = os.path.join(root, f)
                rp = f'{rdst}/{f}'.replace('\\', '/')
                sftp.put(lp, rp)
    finally:
        sftp.close()
    # sudo cp -r 整树过去
    run(ssh_c, f'sudo mkdir -p {remote_dir}', echo=False, check=False)
    run(ssh_c, f'sudo cp -r {tmp_base}/. {remote_dir}/', echo=False)
    run(ssh_c, f'sudo chown -R www-data:www-data {remote_dir}', echo=False, check=False)
    run(ssh_c, f'rm -rf {tmp_base}', echo=False, check=False)

def main():
    print('='*60)
    print('  V0.5.3 增量部署到 117')
    print('='*60)
    c = ssh()

    # 1) 备份 .env
    print('\n[1] 备份 117 .env')
    run(c, f'sudo cp {REMOTE_API}/.env {REMOTE_API}/.env.bak.v053_$(date +%Y%m%d_%H%M%S)')

    # 2) 推后端增量
    print('\n[2] 推后端源码 (app/ + bootstrap/ + routes/ + database/migrations/ + database/seeders/)')
    for sub in ['app', 'bootstrap', 'routes', 'tests', 'config']:
        ld = API_LOCAL / sub
        if not ld.exists(): continue
        rd = f'{REMOTE_API}/{sub}'
        print(f'  → {sub}/')
        upload_dir(c, ld, rd, excludes={'vendor'})

    # 推 migrations 和 seeders
    print('  → database/migrations/')
    upload_dir(c, API_LOCAL / 'database' / 'migrations', f'{REMOTE_API}/database/migrations')
    print('  → database/seeders/')
    upload_dir(c, API_LOCAL / 'database' / 'seeders', f'{REMOTE_API}/database/seeders')

    # 3) 修 owner
    print('\n[3] chown')
    run(c, f'sudo chown -R www-data:www-data {REMOTE_API}/app {REMOTE_API}/bootstrap {REMOTE_API}/routes {REMOTE_API}/tests {REMOTE_API}/database', check=False)

    # 4) 推前端 dist
    print('\n[4] 推前端 dist/')
    web_dist = WEB_LOCAL / 'dist'
    if web_dist.exists():
        # 清空再推
        run(c, f'sudo rm -rf {REMOTE_WEB}/*')
        upload_dir(c, web_dist, REMOTE_WEB)
        run(c, f'sudo chown -R www-data:www-data {REMOTE_WEB}')

    # 5) 跑 migration (新加的 expires_at 字段)
    print('\n[5] 跑 migration')
    run(c, f'cd {REMOTE_API} && php artisan migrate --force 2>&1 | tail -20', echo=True)

    # 6) clear cache + restart
    print('\n[6] clear + restart')
    run(c, f'cd {REMOTE_API} && php artisan config:clear 2>&1')
    run(c, f'cd {REMOTE_API} && php artisan route:clear 2>&1')
    run(c, f'cd {REMOTE_API} && php artisan cache:clear 2>&1')
    run(c, 'sudo systemctl restart php8.5-fpm')

    # 7) smoke
    print('\n[7] smoke')
    time.sleep(2)
    smoke_script = ROOT_LOCAL / '.workbuddy' / 'smoke_v049.py'
    if smoke_script.exists():
        r = subprocess.run(['python', str(smoke_script)], capture_output=True, text=True, timeout=300)
        print(r.stdout[-2000:])
        if r.returncode != 0:
            print(f'  ✗ smoke 失败 rc={r.returncode}')
            sys.exit(1)
        print('  ✓ smoke pass')
    else:
        print('  ⚠ smoke_v049.py 不存在, 跳过')

    # 8) e2e 临时角色 (可选)
    print('\n[8] e2e 临时角色流程')
    e2e_script = ROOT_LOCAL / '.workbuddy' / 'e2e_v053_temporary.py'
    if e2e_script.exists():
        r = subprocess.run(['python', str(e2e_script)], capture_output=True, text=True, timeout=300)
        print(r.stdout[-2000:])
    else:
        print('  (e2e 脚本待写)')

    print('\n' + '='*60)
    print('  ✓ V0.5.3 部署完成')
    print('='*60)

if __name__ == '__main__':
    main()
