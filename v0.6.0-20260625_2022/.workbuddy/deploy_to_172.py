"""
全量部署脚本 — 安防运维OA 部署到 172.20.0.139 (nbcy/admin123) - 测试平台
v0.3.7.8+ → 172.20.0.139 PG

使用: python .workbuddy/deploy_to_172.py [--skip-migrate] [--skip-seed] [--skip-web] [--skip-composer] [--no-clear] [--dry-run]

⚠️ 默认测试平台（2026-06-18 用户明确）：172 = 测试 (本地每次修改自动同步)
   152.136.115.121 = 展示平台，部署需用户明确允许
"""
import sys, os, time, argparse
import paramiko
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
LOCAL_WEB = r'D:\work\website\OA\pc-web\dist'
REMOTE_API = '/var/www/oa-api'
REMOTE_WEB = '/var/www/oa-web'

SKIP_DIRS = {'.git', 'vendor', 'node_modules', 'storage', '.workbuddy'}

def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    return ssh

def run(ssh, cmd, timeout=120, label='', echo=True):
    if label and echo:
        print(f'  [{label}] $ {cmd[:80]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    result = out or err
    if result:
        for line in result.split('\n')[:10]:
            print(f'    {line}')
    return out, err, rc

def sftp_upload_tree(ssh, local_root, remote_root):
    """递归上传目录，跳过 SKIP_DIRS"""
    sftp = ssh.open_sftp()
    n = 0
    for dirpath, dirnames, filenames in os.walk(local_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, local_root).replace('\\', '/')
        remote_dir = remote_root if rel == '.' else posixpath.join(remote_root, rel)
        
        try:
            sftp.stat(remote_dir)
        except IOError:
            run(ssh, f'mkdir -p {remote_dir}', echo=False)
        
        for fn in filenames:
            try:
                sftp.put(os.path.join(dirpath, fn), posixpath.join(remote_dir, fn))
                n += 1
                if n % 60 == 0:
                    print(f'    已上传 {n} 个文件...')
            except Exception as e:
                print(f'    [WARN] {fn}: {e}')
    sftp.close()
    return n

def sftp_put_text(ssh, remote_path, content):
    """写入文件内容"""
    sftp = ssh.open_sftp()
    with sftp.file(remote_path, 'w') as f:
        f.write(content)
    sftp.close()

# ====== 主流程 ======
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--skip-migrate', action='store_true')
    p.add_argument('--skip-seed', action='store_true')
    p.add_argument('--skip-web', action='store_true')
    p.add_argument('--skip-composer', action='store_true',
                        help='跳过 composer install (危险: 仅当 vendor 已存在且不变时使用)')
    p.add_argument('--no-clear', action='store_true',
                        help='不清空 REMOTE_API (保留 vendor/storage/.env, 只覆盖源文件)')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    
    ssh = ssh_connect()
    
    # ---- 1. 备份 ----
    ts = int(time.time())
    print(f'\n[1/7] 备份旧代码 → .bak.{ts}')
    run(ssh, f'sudo cp -r {REMOTE_API} {REMOTE_API}.bak.{ts} 2>/dev/null; echo DONE', label='backup api')
    run(ssh, f'sudo cp -r {REMOTE_WEB} {REMOTE_WEB}.bak.{ts} 2>/dev/null; echo DONE', label='backup web')
    
    # ---- 2. 清空 + chown (v0.3.15 加 --no-clear 保持 vendor/.env) ----
    print(f'\n[2/7] 清空旧文件，chown nbcy')
    if args.no_clear:
        print('  [v0.3.15] --no-clear 模式: 保留 vendor/storage/.env，只覆盖源文件')
        # 仅 chown 让 nbcy 可写（不删任何文件）
        run(ssh, f'sudo chown -R nbcy:nbcy {REMOTE_API}', echo=False)
    else:
        # 危险操作：全清空（保留 .bak.* 备份目录）
        run(ssh, f'sudo rm -rf {REMOTE_API}/* {REMOTE_API}/.* 2>/dev/null; echo DONE')
        run(ssh, f'sudo chown -R nbcy:nbcy {REMOTE_API}')
    
    # ---- 2.5. vendor 完整性预检 (v0.3.16 P0) ----
    if not args.dry_run and args.no_clear:
        out, err, rc = run(ssh, f'sudo test -d {REMOTE_API}/vendor && echo OK || echo MISSING', label='vendor 预检', echo=False)
        if 'OK' not in (out + err):
            print('  [WARN] vendor 不存在 --no-clear 模式自动转为全量部署')
            args.no_clear = False
        else:
            # 验证 composer.lock / autoload 完整
            out2, _, _ = run(ssh, f'sudo test -f {REMOTE_API}/vendor/autoload.php && echo OK || echo MISSING', label='autoload 预检', echo=False)
            if 'OK' not in out2:
                print('  [WARN] autoload.php 缺失 --no-clear 模式自动转全量部署')
                args.no_clear = False
            else:
                # 检查关键包（spatie/laravel-permission）是否实际加载
                out3, _, _ = run(ssh, f'sudo -u www-data php -r "require \'{REMOTE_API}/vendor/autoload.php\'; echo class_exists(\'Spatie\\\\Permission\\\\Models\\\\Role\') ? \\'ROLE_OK\\' : \\'ROLE_MISSING\';" 2>&1', label='spatie role check', echo=False)
                if 'ROLE_OK' in out3:
                    print('  [OK] vendor 完整 + autoload 完整 + spatie role 加载成功')
                else:
                    print(f'  [WARN] spatie role 加载失败: {out3[:200]}')
                    print('  [INFO] 建议: 去掉 --skip-composer 让它重装依赖')

    # ---- 3. 上传 API 代码 ----
    print(f'\n[3/7] 上传 API 代码 {LOCAL_API} → {REMOTE_API}')
    if args.dry_run:
        print('  (dry-run, skip)')
    else:
        n = sftp_upload_tree(ssh, LOCAL_API, REMOTE_API)
        print(f'  ✓ 上传完成: {n} 个文件')
    
    # ---- 4. 写 .env ----
    print(f'\n[4/7] 写入 .env (PG)')
    env = """APP_NAME="安防运维OA"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://172.20.0.139

LOG_CHANNEL=stack
LOG_LEVEL=debug

DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=security_oa
DB_USERNAME=oa_user
DB_PASSWORD=oa_pg_pwd_782997781

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120

SANCTUM_STATEFUL_DOMAINS=localhost,localhost:3000,172.20.0.139

MAIL_MAILER=smtp
MAIL_HOST=mailpit
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
"""
    if not args.dry_run:
        sftp_put_text(ssh, f'{REMOTE_API}/.env', env)
        # v0.3.16 P0: .env 默认 600，www-data 读不到导致所有 DB/cache 走默认 mysql
        run(ssh, f'sudo chmod 644 {REMOTE_API}/.env && sudo chown www-data:www-data {REMOTE_API}/.env', label='chmod .env')
        print('  ✓ .env 已写入 (chmod 644 + chown www-data)')
    
    # ---- 5. Composer install (v0.3.15 加 --skip-composer 保持 vendor) ----
    print(f'\n[5/7] Composer install (可能需 2-5 分钟)...')
    if args.skip_composer:
        print('  [v0.3.15] --skip-composer 模式: 跳过 composer install（依赖现有 vendor）')
    if not args.dry_run and not args.skip_composer:
        # 检查 composer 是否可用
        out, err, rc = run(ssh, 'which composer 2>/dev/null || echo NOT_FOUND', label='check composer')
        if 'NOT_FOUND' in (out + err):
            print('  [WARN] 服务器无 composer，尝试安装...')
            run(ssh, 'curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer 2>&1', timeout=180, label='install composer')
        
        out, err, rc = run(
            ssh,
            f'cd {REMOTE_API} && COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --optimize-autoloader 2>&1',
            timeout=300,
            label='composer install'
        )
        if rc == 0:
            print('  ✓ composer install 完成')
        elif args.no_clear:
            # v0.3.15 兼容性：--no-clear 模式下 vendor 已存在，autoload 仍可用
            print('  [WARN] composer install 失败 --no-clear 模式保证 fpm 仍可使用原 vendor')
        else:
            print(f'  [ERROR] composer install 失败 (rc={rc})')
            # 尝试单独跑看看
            out2, err2, _ = run(ssh, f'cd {REMOTE_API} && composer diagnose 2>&1 && composer install --no-dev -o 2>&1 | tail -30', timeout=300, label='composer retry')
    
    # ---- 6. 修正权限 ----
    print(f'\n[6/7] 修正权限为 www-data')
    if not args.dry_run:
        run(ssh, f'sudo chown -R www-data:www-data {REMOTE_API}')
        run(ssh, f'sudo chmod -R 755 {REMOTE_API}')
        # storage 和 cache 需要可写
        for d in ['storage', 'bootstrap/cache']:
            run(ssh, f'sudo chmod -R 775 {REMOTE_API}/{d}')
        run(ssh, f'sudo mkdir -p {REMOTE_API}/storage/framework/{{cache,sessions,views}}')
        run(ssh, f'sudo mkdir -p {REMOTE_API}/storage/logs')
        run(ssh, f'sudo mkdir -p {REMOTE_API}/storage/app/{{backups,public}}')
        run(ssh, f'sudo chown -R www-data:www-data {REMOTE_API}/storage {REMOTE_API}/bootstrap/cache')
        # 生成 APP_KEY
        run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan key:generate --force 2>&1', timeout=30, label='key:generate')
        # 清理缓存
        run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1', timeout=15)
        run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan route:clear 2>&1', timeout=15)
        print('  ✓ 权限修正完成')
    
    # ---- 7. Migrate + Seed + Restart ----
    print(f'\n[7/7] 数据库初始化 + 重启服务')
    if not args.dry_run:
        if not args.skip_migrate:
            print('  执行 php artisan migrate --force ...')
            out, err, rc = run(
                ssh,
                f'cd {REMOTE_API} && sudo -u www-data php artisan migrate --force 2>&1',
                timeout=120,
                label='migrate'
            )
            if rc == 0:
                print('  ✓ migrate 完成')
            else:
                print(f'  [WARN] migrate 可能有问题: {err[:200]}')
            
            # PG 新表授权
            run(ssh, 'sudo -u postgres psql -d security_oa -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oa_user" 2>&1', label='grant tables', echo=False)
            run(ssh, 'sudo -u postgres psql -d security_oa -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO oa_user" 2>&1', label='grant seqs', echo=False)
        
        if not args.skip_seed:
            print('  执行 php artisan db:seed ...')
            out, err, rc = run(
                ssh,
                f'cd {REMOTE_API} && sudo -u www-data php artisan db:seed --class=DatabaseSeeder --force 2>&1',
                timeout=60,
                label='DatabaseSeeder'
            )
            out2, err2, rc2 = run(
                ssh,
                f'cd {REMOTE_API} && sudo -u www-data php artisan db:seed --class=BusinessLogicTestDataSeeder --force 2>&1',
                timeout=180,
                label='BusinessSeeder'
            )
            if rc2 == 0:
                print('  ✓ seed 完成')
            else:
                print(f'  [WARN] BusinessLogicTestDataSeeder: {(out2 or err2)[:200]}')
        
        # Restart FPM
        run(ssh, 'sudo systemctl restart php8.3-fpm 2>&1', timeout=15, label='restart fpm')
        print('  ✓ php8.3-fpm 已重启')
    
    ssh.close()
    
    # ---- 前端 ----
    if not args.skip_web and not args.dry_run:
        print(f'\n[WEB] 上传前端 dist...')
        if not os.path.exists(LOCAL_WEB):
            print(f'  [ERROR] dist 目录不存在: {LOCAL_WEB}')
            print('  请先运行: cd pc-web && npm run build')
        else:
            ssh2 = ssh_connect()
            run(ssh2, f'sudo rm -rf {REMOTE_WEB}/* 2>/dev/null; echo DONE')
            run(ssh2, f'sudo chown -R nbcy:nbcy {REMOTE_WEB}')
            n = sftp_upload_tree(ssh2, LOCAL_WEB, REMOTE_WEB)
            run(ssh2, f'sudo chown -R www-data:www-data {REMOTE_WEB}')
            print(f'  ✓ 前端上传完成: {n} 个文件')
            ssh2.close()
    
    print('\n' + '='*50)
    print('部署完成!')
    print(f'  API:  http://172.20.0.139:3001/api')
    print(f'  Web:  http://172.20.0.139:3000')
    print('='*50)

if __name__ == '__main__':
    main()
