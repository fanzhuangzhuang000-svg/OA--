#!/usr/bin/env python3
"""v0.3.18 全量幂等测试 — DELETE migrations 后 migrate 2 次"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

fn = '2026_06_20_000001_add_inventory_warnings.php'
sftp.put('pc-api/database/migrations/' + fn, f'/tmp/{fn}')
sftp.close()

cmds = [
    f'sudo -n cp /tmp/{fn} /var/www/oa-api/database/migrations/{fn}',
    f'sudo -n chown www-data:www-data /var/www/oa-api/database/migrations/{fn}',
    f'sudo -n chmod 644 /var/www/oa-api/database/migrations/{fn}',
    'sudo -n systemctl restart php8.3-fpm',
    "PGPASSWORD=$(sudo -n cat /var/www/oa-api/.env | grep DB_PASSWORD | cut -d= -f2 | tr -d '\\r') psql -U oa_user -d security_oa -h 127.0.0.1 -c 'DELETE FROM migrations' 2>&1 | tail -2",
    'cd /var/www/oa-api && sudo -n php artisan migrate --force 2>&1 | tail -8',
    'echo --- SECOND ---',
    'cd /var/www/oa-api && sudo -n php artisan migrate --force 2>&1 | tail -5',
    "PGPASSWORD=$(sudo -n cat /var/www/oa-api/.env | grep DB_PASSWORD | cut -d= -f2 | tr -d '\\r') psql -U oa_user -d security_oa -h 127.0.0.1 -tAc \"SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'\"",
]
for c in cmds:
    print('=' * 60)
    print(c[:100])
    stdin, stdout, stderr = ssh.exec_command(c, timeout=180)
    out = stdout.read().decode().strip()
    print(out[:1500])
ssh.close()
