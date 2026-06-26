#!/usr/bin/env python3
"""v3.9.0 阶段4b: 修正 oa-api 部署 - 修权限 + composer + migrate + seed
- 先 chown -R 给 ubuntu
- composer install
- 移走原 migrations, 启用 migrations_pg
- key:generate
- migrate --seed
- 改回 www-data
"""
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = 'sudo'
REMOTE_ROOT = '/var/www/oa-api'

def ssh_exec(ssh, cmd, timeout=600, show_tail=15):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    if show_tail and (out or err):
        text = (out + err).strip()
        for line in text.split('\n')[-show_tail:]:
            print(f'    {line}')
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    print('✅ connected')

    # 1. chown 给 ubuntu
    print('\n=== 1. chown -R ubuntu:ubuntu /var/www/oa-api ===')
    ssh_exec(ssh, f"{SUDO} chown -R ubuntu:ubuntu {REMOTE_ROOT}", show_tail=3)

    # 2. composer install (用户级, 不需要 sudo)
    print('\n=== 2. composer install --no-dev ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && composer install --no-dev --optimize-autoloader --no-interaction 2>&1", timeout=600, show_tail=10)

    # 3. 启用 PG migrations: 原 migrations 改名 _mysql_bak, migrations_pg → migrations
    print('\n=== 3. 启用 migrations_pg ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT}/database && mv migrations _migrations_mysql && mv migrations_pg migrations 2>&1", show_tail=3)
    ssh_exec(ssh, f"ls {REMOTE_ROOT}/database/migrations/ | head -5", show_tail=5)

    # 4. key:generate
    print('\n=== 4. php artisan key:generate ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && php artisan key:generate --force 2>&1", show_tail=3)

    # 5. storage 权限
    print('\n=== 5. storage 权限 ===')
    ssh_exec(ssh, f"chmod -R 775 storage bootstrap/cache 2>&1", show_tail=2)

    # 6. migrate
    print('\n=== 6. php artisan migrate --force ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && php artisan migrate --force 2>&1", timeout=180, show_tail=20)

    # 7. seed
    print('\n=== 7. php artisan db:seed --force ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && php artisan db:seed --force 2>&1", timeout=120, show_tail=20)

    # 8. 缓存
    print('\n=== 8. 清缓存 ===')
    for cmd in ['config:clear', 'route:clear', 'cache:clear', 'view:clear']:
        ssh_exec(ssh, f"cd {REMOTE_ROOT} && php artisan {cmd} 2>&1", show_tail=2)

    # 9. 改回 www-data
    print('\n=== 9. chown 回 www-data ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} chown -R www-data:www-data . 2>&1", show_tail=2)

    # 10. 验证
    print('\n=== 10. 验证 DB ===')
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c '\\dt' 2>&1 | head -10", show_tail=10)
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c 'SELECT count(*) AS users FROM users; SELECT count(*) AS roles FROM roles; SELECT count(*) AS perms FROM permissions;' 2>&1 | head -10", show_tail=10)

    ssh.close()
    print('\n✅ 阶段4b 完成')

if __name__ == '__main__':
    main()
