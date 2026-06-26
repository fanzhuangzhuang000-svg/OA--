#!/usr/bin/env python3
"""
V0.5.4 增量部署到 117
- 推后端 (php-api/) 改动
- 推前端 dist/
- clear + restart
- 跑 smoke
"""
import os, sys, time, subprocess
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

def upload_dir(ssh_c, local_dir, remote_dir, excludes=None):
    excludes = excludes or set()
    sftp = ssh_c.open_sftp()
    tmp_base = f'/tmp/v054_upload_{int(time.time()*1000)}'
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
    run(ssh_c, f'sudo mkdir -p {remote_dir}', echo=False, check=False)
    run(ssh_c, f'sudo cp -r {tmp_base}/. {remote_dir}/', echo=False)
    run(ssh_c, f'sudo chown -R www-data:www-data {remote_dir}', echo=False, check=False)
    run(ssh_c, f'rm -rf {tmp_base}', echo=False, check=False)

def main():
    print('='*60)
    print('  V0.5.4 增量部署到 117')
    print('='*60)
    c = ssh()

    # 1) 推后端
    print('\n[1] 推后端 app/ + routes/')
    for sub in ['app', 'routes']:
        ld = API_LOCAL / sub
        if not ld.exists(): continue
        rd = f'{REMOTE_API}/{sub}'
        print(f'  → {sub}/')
        upload_dir(c, ld, rd, excludes={'vendor'})

    # 2) 推前端
    print('\n[2] 推前端 dist/')
    web_dist = WEB_LOCAL / 'dist'
    if web_dist.exists():
        run(c, f'sudo rm -rf {REMOTE_WEB}/*')
        upload_dir(c, web_dist, REMOTE_WEB)
        run(c, f'sudo chown -R www-data:www-data {REMOTE_WEB}')

    # 3) clear + restart
    print('\n[3] clear + restart')
    run(c, f'cd {REMOTE_API} && php artisan config:clear 2>&1')
    run(c, f'cd {REMOTE_API} && php artisan route:clear 2>&1')
    run(c, f'cd {REMOTE_API} && php artisan cache:clear 2>&1')
    run(c, 'sudo systemctl restart php8.5-fpm')

    # 4) smoke
    print('\n[4] smoke')
    time.sleep(2)
    smoke_script = ROOT_LOCAL / '.workbuddy' / 'smoke_v049.py'
    if smoke_script.exists():
        r = subprocess.run(['python', str(smoke_script)], capture_output=True, text=True, timeout=300)
        print(r.stdout[-2000:])
        if r.returncode != 0:
            print(f'  ✗ smoke 失败 rc={r.returncode}')
            sys.exit(1)
        print('  ✓ smoke pass')

    # 5) 烟囱 V0.5.4 新端点
    print('\n[5] 烟囱 V0.5.4 新端点')
    e2e_v054 = ROOT_LOCAL / '.workbuddy' / 'e2e_v054.py'
    if e2e_v054.exists():
        r = subprocess.run(['python', str(e2e_v054)], capture_output=True, text=True, timeout=300)
        print(r.stdout[-2000:])

    print('\n' + '='*60)
    print('  ✓ V0.5.4 部署完成')
    print('='*60)

if __name__ == '__main__':
    main()
