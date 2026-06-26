#!/usr/bin/env python3
"""v3.9.0 阶段4c: 把 pc-api 业务代码覆盖到 laravel 模板上, 然后迁移 + seed
- /var/www/oa-api/ 是空的 Laravel 11 模板 (create-project 来的)
- /var/www/oa-api-bak/ 是之前上传的 pc-api 业务代码 (没 artisan)
- 合并策略: 把 oa-api-bak 里的 业务文件 复制到 oa-api, 不要覆盖 Laravel 模板的 artisan / bootstrap/cache / vendor
"""
import paramiko
import os
import posixpath

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = 'sudo'
LOCAL_ROOT = r'D:\work\website\OA\pc-api'
BAK_REMOTE = '/var/www/oa-api-bak'
API_REMOTE = '/var/www/oa-api'

def sftp_mkdir_p(sftp, path):
    parts = path.strip('/').split('/')
    cur = ''
    for p in parts:
        cur = f'{cur}/{p}'
        try:
            sftp.stat(cur)
        except IOError:
            try:
                sftp.mkdir(cur)
            except IOError: pass

def ssh_exec(ssh, cmd, timeout=300, show_tail=15):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    if show_tail and (out or err):
        for line in (out+err).strip().split('\n')[-show_tail:]:
            if line.strip(): print(f'    {line}')
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    sftp = ssh.open_sftp()
    print('✅ connected')

    # 1. chown -R ubuntu
    print('\n=== 1. chown -R ubuntu:ubuntu /var/www/oa-api ===')
    ssh_exec(ssh, f'{SUDO} chown -R ubuntu:ubuntu {API_REMOTE} {BAK_REMOTE}')

    # 2. 关键: 把 oa-api-bak 的 PG migrations 和业务代码 rsync 到 oa-api
    # 不要覆盖: vendor/ storage/ bootstrap/cache/ .env artisan  composer.json composer.lock
    print('\n=== 2. 用 rsync 把 oa-api-bak → oa-api (排除 vendor/storage/bootstrap/.env/artisan) ===')
    # 客户端 rsync 不一定装, 改用 cp -a + rm 排除
    # 用 find + cp 复杂, 干脆用 rsync
    rsync_cmd = (
        f'rsync -a --delete --exclude=vendor --exclude=storage --exclude=.env '
        f'--exclude=artisan --exclude=composer.lock '
        f'--exclude=node_modules --exclude=.git '
        f'{BAK_REMOTE}/ {API_REMOTE}/'
    )
    ssh_exec(ssh, rsync_cmd, timeout=120, show_tail=5)

    # 3. composer.json 合并: 我们的 composer.json 加 sanctum 和 spatie/laravel-permission
    #   create-project 装的 laravel/framework 11.x, 我们的也是 11.x, 但少 sanctum 和 spatie
    print('\n=== 3. composer require 装 sanctum + spatie/laravel-permission ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && composer require laravel/sanctum spatie/laravel-permission --no-interaction 2>&1', timeout=600, show_tail=10)

    # 4. 把 PG migrations 单独放回去 (rsync 不会带 migrations_pg/ 那个子目录)
    # 不, rsync --delete 会删 oa-api-bak 里的, 但 oa-api-bak 的 migrations 已经 mv 成 migrations_pg,
    # 然后 mv 成 migrations。所以 oa-api-bak 现在的 database/migrations 是 PG 版.
    print('\n=== 4. 验证 migrations ===')
    ssh_exec(ssh, f'ls {API_REMOTE}/database/migrations/ 2>&1 | wc -l', show_tail=2)
    ssh_exec(ssh, f'head -25 {API_REMOTE}/database/migrations/2024_01_01_000003_create_users_table.php', show_tail=20)

    # 5. 复制 .env (生产 PG)
    print('\n=== 5. 复制 .env ===')
    sftp.put(r'D:\work\website\OA\.workbuddy\newserver\env_production', f'{API_REMOTE}/.env')
    print('  ✅ .env')

    # 6. key:generate
    print('\n=== 6. php artisan key:generate ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan key:generate --force 2>&1', show_tail=5)

    # 7. storage 权限
    print('\n=== 7. storage 权限 ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && chmod -R 775 storage bootstrap/cache', show_tail=2)

    # 8. storage:link
    print('\n=== 8. php artisan storage:link ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan storage:link 2>&1', show_tail=3)

    # 9. publish sanctum + spatie
    print('\n=== 9. vendor:publish sanctum + spatie ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan vendor:publish --provider="Laravel\\Sanctum\\SanctumServiceProvider" --force 2>&1 | head -5', show_tail=5)
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan vendor:publish --provider="Spatie\\Permission\\PermissionServiceProvider" --force 2>&1 | head -5', show_tail=5)

    # 10. migrate
    print('\n=== 10. php artisan migrate --force ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan migrate --force 2>&1', timeout=300, show_tail=30)

    # 11. seed
    print('\n=== 11. php artisan db:seed --force ===')
    ssh_exec(ssh, f'cd {API_REMOTE} && php artisan db:seed --force 2>&1', timeout=120, show_tail=30)

    # 12. 缓存清理
    print('\n=== 12. 缓存清理 ===')
    for cmd in ['config:clear', 'route:clear', 'cache:clear', 'view:clear']:
        ssh_exec(ssh, f'cd {API_REMOTE} && php artisan {cmd} 2>&1', show_tail=2)

    # 13. chown 回 www-data
    print('\n=== 13. chown 回 www-data ===')
    ssh_exec(ssh, f'{SUDO} chown -R www-data:www-data {API_REMOTE}')

    # 14. 验证
    print('\n=== 14. 验证 DB ===')
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c '\\dt' 2>&1 | head -50", show_tail=40)
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c 'SELECT count(*) AS users FROM users; SELECT count(*) AS roles FROM roles; SELECT count(*) AS perms FROM permissions; SELECT count(*) AS perms_role FROM permission_role;' 2>&1 | head -10", show_tail=10)

    sftp.close()
    ssh.close()
    print('\n✅ 阶段4c 完成')

if __name__ == '__main__':
    main()
