#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 v0.3.10 后端增量推送到 152"""
import os, subprocess
from deploy_credentials import get_ssh_credentials_152, connect_ssh

LOCAL = 'D:/work/website/OA'
STAGING = '/tmp/oa-staging'

def main():
    creds = get_ssh_credentials_152()
    ssh = connect_ssh(creds)

    # 1) 列变更 php
    out = subprocess.check_output(
        ['bash', '-c', f'find {LOCAL}/pc-api -name "*.php" -mtime -3 -not -path "*/vendor/*" -not -path "*/node_modules/*"'],
        shell=False
    ).decode().strip().split('\n')
    php_files = []
    for l in out:
        l = l.replace('\\', '/')
        if not l:
            continue
        rel = l.replace(LOCAL + '/', '')
        php_files.append(rel)
    print(f'[php] {len(php_files)} files')

    # 2) 加 migration (确认 5 个全在)
    for m in [
        'pc-api/database/migrations/2026_06_21_130000_add_party_fields_to_stock_records.php',
        'pc-api/database/migrations/2026_06_21_140000_add_logistics_to_stock_records.php',
        'pc-api/database/migrations/2026_06_22_000000_add_nullable_supplier_id_to_payables_table.php',
        'pc-api/database/migrations/2026_06_22_000001_add_idle_timeout_settings.php',
        'pc-api/database/migrations/2026_06_22_130000_create_process_tables.php',
    ]:
        if m not in php_files:
            php_files.append(m)
    print(f'[php+migration] {len(php_files)} files')

    # 3) sftp put
    sftp = ssh.open_sftp()
    ok = err = 0
    errs = []
    for rel in php_files:
        local = f'{LOCAL}/{rel}'.replace('\\', '/')
        remote = f'{STAGING}/{rel}'
        remote_dir = os.path.dirname(remote).replace('\\', '/')
        ssh.exec_command(f'mkdir -p {remote_dir}')
        try:
            sftp.put(local, remote)
            ok += 1
        except Exception as e:
            err += 1
            errs.append(f'{rel}: {e}')
    sftp.close()
    print(f'put ok={ok} err={err}')
    if errs:
        for e in errs[:5]:
            print('  ', e)

    # 4) rsync 到正式目录
    cmds = [
        f'sudo rm -rf {STAGING}/pc-api/storage {STAGING}/pc-api/bootstrap/cache {STAGING}/pc-api/vendor',
        f'sudo rsync -a {STAGING}/pc-api/ /var/www/oa-api/ 2>&1 | tail -3',
        'sudo chown -R www-data:www-data /var/www/oa-api/',
        'sudo find /var/www/oa-api -type d -exec chmod 755 {} \;',
        'sudo find /var/www/oa-api -type f -exec chmod 644 {} \;',
        'sudo chmod -R 775 /var/www/oa-api/storage /var/www/oa-api/bootstrap/cache',
        # 关键文件落地确认
        'ls -la /var/www/oa-api/app/Http/Controllers/Api/ApprovalCenterController.php',
        'ls -la /var/www/oa-api/database/migrations/2026_06_22_130000_create_process_tables.php',
        'ls -la /var/www/oa-api/app/Http/Middleware/AuditLogger.php /var/www/oa-api/app/Http/Middleware/ForceJsonResponse.php 2>&1',
    ]
    for c in cmds:
        print('---', c[:60])
        stdin, stdout, stderr = ssh.exec_command(c, timeout=120)
        out = stdout.read().decode(errors='ignore').strip()
        err = stderr.read().decode(errors='ignore').strip()
        if out: print(out)
        if err: print('ERR:', err[:300])

    # 5) 清理 staging
    ssh.exec_command(f'sudo rm -rf {STAGING}')
    ssh.close()
    print('\n✅ 后端代码推送完成')

if __name__ == '__main__':
    main()
