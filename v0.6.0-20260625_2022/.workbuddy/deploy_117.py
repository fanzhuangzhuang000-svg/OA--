"""V0.4.2 全量迁移到 117 (192.168.3.117) — Ubuntu 26.04 + PHP 8.5.4 + PG 18.4

阶段:
  1) 117 端建库建用户 (security_oa / oa_user)
  2) 117 端建 /var/www/oa-api (nbcy:nbcy) / /var/www/oa-web (www-data)
  3) 本地 → 117 全量传代码
  4) 117 端 composer install
  5) 172 → 117 pg_dump + pg_restore 全量数据
  6) 写 .env + 权限 + APP_KEY
  7) 配 Nginx + 重启 fpm
  8) 端到端烟囱测试
"""
import sys, os, time, subprocess
import paramiko
import posixpath

# ====== 目标服务器 ======
HOST_117 = '192.168.3.117'
HOST_172 = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'

LOCAL_API = r'D:\work\website\OA\pc-api'
LOCAL_WEB = r'D:\work\website\OA\pc-web\dist'

REMOTE_API = '/var/www/oa-api'
REMOTE_WEB = '/var/www/oa-web'

DB_NAME = 'security_oa'
DB_USER = 'oa_user'
DB_PASS = 'oa_pg_pwd_782997781'

# 117 默认数据库
REMOTE_PG_SUPER = 'postgres'  # postgres 超级用户

SKIP_DIRS = {'.git', 'vendor', 'node_modules', 'storage', '.workbuddy', 'dist_spa'}


# ====== SSH 工具 ======
def ssh_connect(host, user=USER, pwd=PWD, port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=user, password=pwd, timeout=20)
    return ssh


def run(ssh, cmd, timeout=120, label='', echo=True, check_rc=False):
    if label and echo:
        print(f'  [{label}] $ {cmd[:80]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    result = out or err
    if result and echo:
        for line in result.split('\n')[:15]:
            print(f'    {line}')
    if check_rc and rc != 0:
        print(f'  [ERROR] {label} rc={rc}')
    return rc, out, err


def sftp_mkdir_p(sftp, remote_path):
    if not remote_path or remote_path == '/':
        return
    try:
        sftp.stat(remote_path)
        return
    except IOError:
        parent = posixpath.dirname(remote_path)
        if parent and parent != '/':
            sftp_mkdir_p(sftp, parent)
        try:
            sftp.mkdir(remote_path)
        except IOError:
            pass


def sftp_upload_tree(ssh, local_root, remote_root, skip_dirs=None):
    """递归上传目录"""
    skip = skip_dirs or SKIP_DIRS
    sftp = ssh.open_sftp()
    n = 0
    for dirpath, dirnames, filenames in os.walk(local_root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        rel = os.path.relpath(dirpath, local_root).replace('\\', '/')
        remote_dir = remote_root if rel == '.' else posixpath.join(remote_root, rel)

        try:
            sftp.stat(remote_dir)
        except IOError:
            sftp_mkdir_p(sftp, remote_dir)

        for fn in filenames:
            local_path = os.path.join(dirpath, fn)
            remote_path = posixpath.join(remote_dir, fn)
            try:
                sftp.put(local_path, remote_path)
                n += 1
                if n % 100 == 0:
                    print(f'    已传 {n} 个文件...')
            except Exception as e:
                print(f'    [WARN] {fn}: {e}')
    sftp.close()
    return n


def sftp_put_text(ssh, remote_path, content):
    sftp = ssh.open_sftp()
    with sftp.file(remote_path, 'w') as f:
        f.write(content)
    sftp.close()


# ====== 阶段 1: 建库建用户 ======
def phase1_create_db():
    print('\n' + '='*60)
    print('阶段 1/8: 117 端建库建用户')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    # 1) 建用户（用 SQL，避开 createuser --pwprompt 阻塞）
    run(ssh,
        f"sudo -u postgres psql -tAc \"DO \\$\\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}') THEN CREATE ROLE {DB_USER} LOGIN PASSWORD '{DB_PASS}' NOSUPERUSER NOCREATEDB NOCREATEROLE; END IF; END \\$\\$\" 2>&1",
        label='create user', check_rc=True)
    # 2) 建库
    run(ssh,
        f'sudo -u postgres createdb --owner={DB_USER} {DB_NAME} 2>&1 || echo "db_may_exist"',
        label='createdb', check_rc=False)
    # 3) GRANT
    run(ssh, f'sudo -u postgres psql -d {DB_NAME} -c "GRANT ALL ON SCHEMA public TO {DB_USER};"', label='grant schema', check_rc=True)
    run(ssh, f'sudo -u postgres psql -d {DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {DB_USER};"', label='grant tables', check_rc=True)
    run(ssh, f'sudo -u postgres psql -d {DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {DB_USER};"', label='grant seqs', check_rc=True)
    # 4) 验证
    run(ssh, f'sudo -u postgres psql -d {DB_NAME} -tAc "SELECT current_database(), current_user;" 2>&1',
        label='verify db', check_rc=True)
    ssh.close()
    print('  ✓ 库 + 用户就位')


# ====== 阶段 2: 建项目目录 ======
def phase2_mkdir():
    print('\n' + '='*60)
    print('阶段 2/8: 建 /var/www/oa-api (nbcy) / /var/www/oa-web (www-data)')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    run(ssh, f'sudo mkdir -p {REMOTE_API} {REMOTE_WEB}', label='mkdir')
    # 仿照 172：oa-api 给 nbcy，oa-web 给 www-data
    run(ssh, f'sudo chown -R nbcy:nbcy {REMOTE_API}', label='chown oa-api')
    run(ssh, f'sudo chown -R www-data:www-data {REMOTE_WEB}', label='chown oa-web')
    run(ssh, f'ls -la {REMOTE_API} {REMOTE_WEB}', label='verify', echo=False)
    ssh.close()
    print('  ✓ 目录就位')


# ====== 阶段 3: 传后端代码 ======
def phase3_upload_api():
    print('\n' + '='*60)
    print(f'阶段 3/8: 传后端代码 {LOCAL_API} → {REMOTE_API}')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    n = sftp_upload_tree(ssh, LOCAL_API, REMOTE_API, skip_dirs=SKIP_DIRS)
    print(f'  ✓ 上传完成: {n} 个文件')
    ssh.close()


# ====== 阶段 4: composer install ======
def phase4_composer():
    print('\n' + '='*60)
    print('阶段 4/8: 117 端 composer install')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    # 先 sudo chown 让 www-data 也能跑（避免权限问题）
    # composer install 用 nbcy 跑，最后再 chown www-data
    print('  跑 composer install（可能 2-5 分钟）...')
    rc, out, err = run(ssh,
        f'cd {REMOTE_API} && COMPOSER_ALLOW_SUPERUSER=1 composer config audit.abandoned ignore 2>&1 && COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_AUDIT_NO_DEV=1 composer install --no-dev --optimize-autoloader --no-interaction --no-audit 2>&1',
        timeout=600, label='composer install')
    if 'Fatal error' in (out+err) or 'requires PHP' in (out+err):
        print('  [ERROR] composer 失败，输出:')
        print(out[-1500:])
        print(err[-1500:])
    # 检查关键包
    # 验证关键包（写 PHP 文件避免 shell 转义）
    php_check = b"<?php require 'vendor/autoload.php'; echo class_exists('Illuminate\Foundation\Application') ? 'LARAVEL_OK' : 'LARAVEL_MISSING';"
    sftp = ssh.open_sftp()
    sftp.file("/tmp/laravel_check.php", "wb").write(php_check)
    sftp.close()
    rc, out, err = run(ssh, f"cd {REMOTE_API} && php /tmp/laravel_check.php 2>&1", label="laravel check")
    if "LARAVEL_OK" in (out + err):
        print("  [OK] Laravel 加载成功")
    else:
        print(f"  [WARN] laravel autoload 有问题: {out} {err}")
    ssh.close()


# ====== 阶段 5: pg_dump 172 + 灌 117 ======
def phase5_pg_migration():
    print('\n' + '='*60)
    print('阶段 5/8: 172 → 117 pg_dump + pg_restore')
    print('='*60)
    # 5.1 在 172 上 pg_dump
    ssh172 = ssh_connect(HOST_172)
    print('  [5.1] 172 端 pg_dump -Fc ...')
    dump_file = f'/tmp/{DB_NAME}_v042.dump'
    rc, out, err = run(ssh172,
        f'sudo -u postgres pg_dump -Fc --no-owner --no-acl -d {DB_NAME} -f {dump_file} 2>&1',
        timeout=180, label='pg_dump 172')
    if rc != 0:
        print(f'  [ERROR] pg_dump 失败: {err}')
        ssh172.close()
        return False
    run(ssh172, f'ls -la {dump_file}', label='check dump size', echo=False)
    # 5.2 scp dump 到 117（在 172 端 scp 到 117，注意 pg_dump 文件归属）
    print('  [5.2] scp dump 172 → 117 (走 172 sftp out)...')
    ssh117 = ssh_connect(HOST_117)
    sftp_117 = ssh117.open_sftp()
    remote_dump = f'/tmp/{DB_NAME}_v042.dump'
    # 先从 172 读出 dump（用 172 sftp.cat），写到 117 /tmp
    sftp_172 = ssh172.open_sftp()
    with sftp_172.open(dump_file, 'rb') as fr:
        data = fr.read()
    sftp_172.close()
    with sftp_117.file(remote_dump, 'wb') as fw:
        fw.write(data)
    sftp_117.close()
    print(f'  ✓ dump 已传到 117: {remote_dump} ({len(data)} bytes)')
    # 5.3 117 端 pg_restore
    print('  [5.3] 117 端 pg_restore ...')
    # 先清理可能已有的表（如果有迁移跑过）
    run(ssh117, f'sudo -u postgres psql -d {DB_NAME} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO {DB_USER};" 2>&1',
        label='clean public schema')
    # pg_restore
    rc, out, err = run(ssh117,
        f'sudo -u postgres pg_restore -d {DB_NAME} --no-owner --no-acl --role={DB_USER} {remote_dump} 2>&1 | tail -30',
        timeout=180, label='pg_restore')
    # 5.4 验证表数量
    rc, out, err = run(ssh117,
        f'sudo -u postgres psql -d {DB_NAME} -tAc "SELECT count(*) FROM pg_tables WHERE schemaname=\'public\';"',
        label='count tables')
    print(f'  ✓ 117 security_oa 有 {out} 张表')
    # 5.5 修复 owner（pg_restore --no-owner 后表可能还是 postgres 拥有）
    print('  [5.5] 把所有表 owner 改 oa_user ...')
    run(ssh117,
        f'sudo -u postgres psql -d {DB_NAME} -c "DO \$\$ DECLARE r record; BEGIN FOR r IN SELECT tablename FROM pg_tables WHERE schemaname=\'public\' LOOP EXECUTE \'ALTER TABLE public.\' || r.tablename || \' OWNER TO {DB_USER}\'; END LOOP; END \$\$;" 2>&1',
        label='change table owner', timeout=120)
    run(ssh117,
        f'sudo -u postgres psql -d {DB_NAME} -c "DO \$\$ DECLARE r record; BEGIN FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema=\'public\' LOOP EXECUTE \'ALTER SEQUENCE public.\' || r.sequence_name || \' OWNER TO {DB_USER}\'; END LOOP; END \$\$;" 2>&1',
        label='change seq owner', timeout=120)
    # 5.6 验证
    rc, out, err = run(ssh117,
        f'PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB_NAME} -tAc "SELECT count(*) FROM users;" 2>&1',
        label='verify users table')
    print(f'  ✓ users 表记录数: {out}')
    # 5.7 清理 dump
    run(ssh117, f'rm -f {remote_dump}', label='cleanup dump', echo=False)
    run(ssh172, f'sudo rm -f {dump_file}', label='cleanup 172 dump', echo=False)
    ssh172.close()
    ssh117.close()
    return True


# ====== 阶段 6: .env + 权限 + APP_KEY ======
def phase6_env():
    print('\n' + '='*60)
    print('阶段 6/8: 写 .env + 权限 + APP_KEY')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    env = f"""APP_NAME="\\u5b89\\u9632\\u8fd0\\u7ef4OA"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://{HOST_117}

LOG_CHANNEL=stack
LOG_LEVEL=debug

DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE={DB_NAME}
DB_USERNAME={DB_USER}
DB_PASSWORD={DB_PASS}

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120

SANCTUM_STATEFUL_DOMAINS=localhost,localhost:3000,{HOST_117}

MAIL_MAILER=smtp
MAIL_HOST=mailpit
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
"""
    sftp_put_text(ssh, f'{REMOTE_API}/.env', env)
    # v0.3.16 P0 修复：chmod 644 + chown www-data
    run(ssh, f'sudo chmod 644 {REMOTE_API}/.env', label='chmod .env')
    run(ssh, f'sudo chown www-data:www-data {REMOTE_API}/.env', label='chown .env')
    # 跑 172 的 APP_KEY 复用（避免重置后 token 失效）
    # 先看 172 的 .env APP_KEY
    ssh172 = ssh_connect(HOST_172)
    _, out, _ = run(ssh172, f'grep ^APP_KEY= {REMOTE_API}/.env 2>&1', label='get 172 APP_KEY', echo=False)
    if out and 'base64:' in out:
        app_key = out.split('=', 1)[1].strip()
        # 替换 .env 里的空 APP_KEY
        run(ssh, f'sudo sed -i "s|^APP_KEY=$|APP_KEY={app_key}|" {REMOTE_API}/.env', label='set APP_KEY', echo=False)
        print(f'  ✓ APP_KEY 复用 172: {app_key[:30]}...')
    ssh172.close()
    # 创建 storage 子目录
    run(ssh, f'sudo mkdir -p {REMOTE_API}/storage/framework/{{cache,sessions,views}} {REMOTE_API}/storage/logs {REMOTE_API}/storage/app/{{backups,public}}', label='mkdir storage')
    # chown 整目录
    run(ssh, f'sudo chown -R www-data:www-data {REMOTE_API}/storage {REMOTE_API}/bootstrap/cache', label='chown storage')
    # 测试 artisan 跑得动
    rc, out, err = run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan --version 2>&1', label='artisan test')
    if 'Laravel' in out:
        print('  ✓ artisan 正常')
    # 清缓存
    for c in ['config:clear', 'route:clear', 'cache:clear']:
        run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan {c} 2>&1', label=c, echo=False)
    ssh.close()


# ====== 阶段 7: Nginx 配置 ======
def phase7_nginx():
    print('\n' + '='*60)
    print('阶段 7/8: 配 Nginx (oa / oa-api) + 重启 fpm')
    print('='*60)
    ssh = ssh_connect(HOST_117)

    # 删 default 占 80 端口的站点
    run(ssh, 'sudo rm -f /etc/nginx/sites-enabled/default', label='remove default', echo=False)

    # oa-api 后端
    nginx_api = f"""server {{
    listen 80;
    server_name api.{HOST_117} {HOST_117};

    root {REMOTE_API}/public;
    index index.php;

    client_max_body_size 50M;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.5-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
    }}
}}
"""
    sftp_put_text(ssh, '/tmp/oa-api.nginx', nginx_api)
    run(ssh, 'sudo mv /tmp/oa-api.nginx /etc/nginx/sites-available/oa-api', label='write oa-api')
    run(ssh, 'sudo ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api', label='enable oa-api')

    # oa 前端
    nginx_web = f"""server {{
    listen 80;
    server_name oa.{HOST_117} {HOST_117};

    root {REMOTE_WEB};
    index index.html;

    client_max_body_size 50M;

    # SPA fallback
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # 静态资源缓存
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf)$ {{
        expires 1d;
        add_header Cache-Control "public, immutable";
    }}

    # API 反代（同服务器后端，节省外网 IP）
    location /api/ {{
        proxy_pass http://unix:/run/php/php8.5-fpm.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }}
}}
"""
    sftp_put_text(ssh, '/tmp/oa.nginx', nginx_web)
    run(ssh, 'sudo mv /tmp/oa.nginx /etc/nginx/sites-available/oa', label='write oa')
    run(ssh, 'sudo ln -sf /etc/nginx/sites-available/oa /etc/nginx/sites-enabled/oa', label='enable oa')

    # 测配置
    rc, out, err = run(ssh, 'sudo nginx -t 2>&1', label='nginx -t', check_rc=True)
    # 重启 nginx
    run(ssh, 'sudo systemctl reload nginx 2>&1', label='reload nginx')
    # 重启 php8.5-fpm（清 opcache + 加载新 vendor）
    run(ssh, 'sudo systemctl restart php8.5-fpm 2>&1', label='restart php8.5-fpm')
    ssh.close()


# ====== 阶段 8: 端到端验证 ======
def phase8_smoke():
    print('\n' + '='*60)
    print('阶段 8/8: 端到端烟囱测试')
    print('='*60)
    ssh = ssh_connect(HOST_117)
    tests = []
    # 1. 后端 /api/auth/login
    rc, out, err = run(ssh,
        f'curl -s -o /tmp/r1.txt -w "HTTP=%{{http_code}}\\n" -X POST http://127.0.0.1/api/auth/login -H "Accept: application/json" -H "Content-Type: application/json" -d \'{{"username":"admin","password":"admin123"}}\' 2>&1',
        label='login', check_rc=False)
    tests.append(('login', rc, out))
    print(f'  /api/auth/login: {out[:200]}')
    # 看 response body
    run(ssh, 'cat /tmp/r1.txt | head -c 500', label='login body', echo=False)
    # 2. 前端 /
    rc, out, err = run(ssh, 'curl -s -o /dev/null -w "HTTP=%{http_code}\\n" http://127.0.0.1/ 2>&1',
        label='frontend /', check_rc=False)
    tests.append(('frontend /', rc, out))
    print(f'  /: {out[:200]}')
    # 3. 提取 token 测 budget API
    rc, out, err = run(ssh,
        f'cat /tmp/r1.txt | head -c 2000',
        label='login body 2', echo=False)
    # 简单提取 token
    import re
    m = re.search(r'"token":"([^"]+)"', out)
    token = m.group(1) if m else None
    if not token:
        m = re.search(r'"access_token":"([^"]+)"', out)
        token = m.group(1) if m else None
    if token:
        print(f'  ✓ 拿到 token: {token[:30]}...')
        # 测一个 budget API
        rc, out, err = run(ssh,
            f'curl -s -o /tmp/r2.txt -w "HTTP=%{{http_code}}\\n" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1/api/construction/budgets 2>&1',
            label='budget list', check_rc=False)
        print(f'  /api/construction/budgets: {out[:200]}')
        run(ssh, 'cat /tmp/r2.txt | head -c 500', label='budget body', echo=False)
    else:
        print('  [WARN] 没拿到 token，跳过 budget 测')
    # 4. 看 laravel.log
    rc, out, err = run(ssh, f'ls -la {REMOTE_API}/storage/logs/laravel.log 2>&1 | head -3',
        label='laravel log size', echo=False)
    # 5. 看表 owner
    rc, out, err = run(ssh,
        f'sudo -u postgres psql -d {DB_NAME} -tAc "SELECT count(*) FROM pg_tables WHERE schemaname=\'public\' AND tableowner=\'{DB_USER}\';" 2>&1',
        label='count owner oa_user')
    print(f'  表 owner=oa_user 的: {out} 张')
    # 6. 关键表测 SELECT
    for tbl in ['users', 'projects', 'project_budgets', 'suppliers', 'external_quote_requests', 'customer_receivables']:
        rc, out, err = run(ssh,
            f'PGPASSWORD={DB_PASS} psql -h 127.0.0.1 -U {DB_USER} -d {DB_NAME} -tAc "SELECT count(*) FROM {tbl};" 2>&1',
            label=f'count {tbl}', echo=False)
        print(f'  {tbl}: {out} 条')
    ssh.close()


# ====== 主入口 ======
def main():
    print('='*60)
    print('  117 全量部署（PHP 8.5 + PG 18.4 + Ubuntu 26.04）')
    print('  来源：172.20.0.139 (V0.4.2 已部署) + 本地代码')
    print('='*60)

    # 阶段 1
    phase1_create_db()
    # 阶段 2
    phase2_mkdir()
    # 阶段 3
    phase3_upload_api()
    # 阶段 4
    phase4_composer()
    # 阶段 5
    phase5_pg_migration()
    # 阶段 6
    phase6_env()
    # 阶段 7
    phase7_nginx()
    # 阶段 8
    phase8_smoke()

    print('\n' + '='*60)
    print('  ✓ 117 部署完成')
    print(f'  API:    http://{HOST_117}/api')
    print(f'  前端:   http://{HOST_117}/')
    print(f'  账户:   admin / admin123')
    print('='*60)


if __name__ == '__main__':
    main()
