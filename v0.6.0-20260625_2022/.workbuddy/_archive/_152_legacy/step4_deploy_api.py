#!/usr/bin/env python3
"""v3.9.0 阶段4: 上传 oa-api + composer install + migrate + seed
- rsync 上传源码到 /var/www/oa-api
- 复制 .env 模板
- composer install
- php artisan key:generate
- php artisan migrate (走 migrations_pg 子目录)
- php artisan db:seed
- 修正 storage 目录权限
"""
import paramiko
import os
import posixpath
import shutil
import sys

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = 'sudo'
LOCAL_ROOT = r'D:\work\website\OA\pc-api'
REMOTE_ROOT = '/var/www/oa-api'

def ssh_exec(ssh, cmd, timeout=300, show_tail=5):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    if show_tail and (out or err):
        text = (out + err).strip()
        for line in text.split('\n')[-show_tail:]:
            print(f'    {line}')
    return out, err

def sftp_mkdir_p(sftp, remote_dir):
    """递归创建远程目录"""
    parts = remote_dir.strip('/').split('/')
    cur = ''
    for p in parts:
        cur = f'{cur}/{p}'
        try:
            sftp.stat(cur)
        except IOError:
            try:
                sftp.mkdir(cur)
            except IOError as e:
                # 已存在（并发）就忽略
                if 'exists' not in str(e).lower() and 'File exists' not in str(e):
                    raise

def sftp_upload_dir(sftp, local_dir, remote_dir, exclude_dirs=None, exclude_files=None):
    """递归上传目录"""
    exclude_dirs = exclude_dirs or ['.git', 'vendor', 'node_modules', '.workbuddy']
    exclude_files = exclude_files or []
    for root, dirs, files in os.walk(local_dir):
        # 跳过
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        rel = os.path.relpath(root, local_dir)
        if rel == '.':
            remote_root = remote_dir
        else:
            remote_root = posixpath.join(remote_dir, rel.replace('\\', '/'))
        sftp_mkdir_p(sftp, remote_root)
        for fn in files:
            if fn in exclude_files:
                continue
            local_path = os.path.join(root, fn)
            remote_path = posixpath.join(remote_root, fn).replace('\\', '/')
            try:
                sftp.put(local_path, remote_path)
            except IOError as e:
                if 'No such file' in str(e):
                    # 父目录未建, 试一次补建
                    parent = posixpath.dirname(remote_path)
                    sftp_mkdir_p(sftp, parent)
                    try:
                        sftp.put(local_path, remote_path)
                        continue
                    except Exception as e2:
                        print(f'    WARN retry fail: {local_path}: {e2}')
                else:
                    print(f'    WARN: {local_path} → {remote_path}: {e}')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    sftp = ssh.open_sftp()
    print('✅ connected')

    # 1. chown /var/www 给 ubuntu
    print('\n=== 1. chown /var/www 给 ubuntu ===')
    out, err = ssh_exec(ssh, f"{SUDO} chown -R ubuntu:ubuntu /var/www 2>&1", show_tail=3)
    ssh_exec(ssh, f"{SUDO} mkdir -p /var/www/oa-api 2>&1", show_tail=0)

    # 2. 上传源码
    print('\n=== 2. rsync 上传 oa-api (排除 vendor/.git) ===')
    # 用 paramiko sftp 避免依赖 rsync
    sftp_mkdir_p(sftp, REMOTE_ROOT)
    sftp_upload_dir(sftp, LOCAL_ROOT, REMOTE_ROOT)
    print('  ✅ 上传完成')

    # 3. 上传 .env
    print('\n=== 3. 上传 .env (生产 PostgreSQL 配置) ===')
    env_local = r'D:\work\website\OA\.workbuddy\newserver\env_production'
    # .env 之前被排除上传, 现在单独 sftp put
    try:
        sftp.put(env_local, f'{REMOTE_ROOT}/.env')
    except IOError as e:
        # .env 可能在上传目录里因为父目录没建
        if 'No such file' in str(e):
            sftp_mkdir_p(sftp, REMOTE_ROOT)
            sftp.put(env_local, f'{REMOTE_ROOT}/.env')
        else:
            raise
    print('  ✅ .env 上传')

    # 4. chown 给 www-data
    print('\n=== 4. chown /var/www/oa-api 给 www-data ===')
    out, err = ssh_exec(ssh, f"{SUDO} chown -R www-data:www-data {REMOTE_ROOT} 2>&1", show_tail=2)

    # 5. composer install
    print('\n=== 5. composer install (生产, 无 dev) ===')
    out, err = ssh_exec(ssh, f"cd {REMOTE_ROOT} && composer install --no-dev --optimize-autoloader --no-interaction 2>&1", timeout=600, show_tail=15)

    # 6. APP_KEY 生成
    print('\n=== 6. php artisan key:generate ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} -u www-data php artisan key:generate --force 2>&1", show_tail=5)

    # 7. 配置 migrations_pg 路径: 让 laravel 只跑 migrations_pg
    # 方案: 临时移走原 migrations, 只留 migrations_pg
    print('\n=== 7. 启用 migrations_pg (移走原 migrations) ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} mv database/migrations database/_migrations_mysql 2>&1", show_tail=3)
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} mv database/migrations_pg database/migrations 2>&1", show_tail=3)

    # 8. migrate
    print('\n=== 8. php artisan migrate --force ===')
    out, err = ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} -u www-data php artisan migrate --force 2>&1", timeout=180, show_tail=20)

    # 9. seed
    print('\n=== 9. php artisan db:seed --force ===')
    ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} -u www-data php artisan db:seed --force 2>&1", timeout=120, show_tail=15)

    # 10. cache
    print('\n=== 10. 清理 Laravel 缓存 ===')
    for cmd in ['config:clear', 'route:clear', 'cache:clear', 'view:clear']:
        ssh_exec(ssh, f"cd {REMOTE_ROOT} && {SUDO} -u www-data php artisan {cmd} 2>&1", show_tail=2)

    # 11. storage 权限
    print('\n=== 11. storage & bootstrap/cache 权限 ===')
    ssh_exec(ssh, f"{SUDO} chown -R www-data:www-data {REMOTE_ROOT}/storage {REMOTE_ROOT}/bootstrap/cache 2>&1", show_tail=2)
    ssh_exec(ssh, f"{SUDO} chmod -R 775 {REMOTE_ROOT}/storage {REMOTE_ROOT}/bootstrap/cache 2>&1", show_tail=2)

    # 12. 验证: 测连 + 查 users
    print('\n=== 12. 验证 migrate 成功 ===')
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c '\\dt' 2>&1 | head -20", show_tail=15)
    ssh_exec(ssh, f"PGPASSWORD='oa_pg_pwd_782997781' psql -h 127.0.0.1 -U oa_user -d security_oa -c 'SELECT count(*) FROM users;' 2>&1 | head -5", show_tail=5)

    sftp.close()
    ssh.close()
    print('\n✅ 阶段4完成')

if __name__ == '__main__':
    main()
