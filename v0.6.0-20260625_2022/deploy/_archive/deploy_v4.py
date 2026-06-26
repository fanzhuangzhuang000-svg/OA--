#!/usr/bin/env python3
"""安防运维OA - 部署脚本 v4（修复 MySQL 访问）"""
import paramiko, os, sys, tarfile, tempfile

HOST, USER, PASS = '172.20.0.139', 'nbcy', 'admin123'
LOCAL_API = 'D:/work/website/OA/pc-api'
REMOTE_BASE = '/var/www/oa-api'

def log(m): print(f"  {m}")

def run(ssh, cmd, desc='', sudo=True):
    full = f"sudo bash -c '{cmd}'" if sudo else cmd
    log(f"▶ {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(full, timeout=300)
    out, err = stdout.read().decode(), stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    for l in (out+err).split('\n'):
        l = l.strip()
        if l: log(f"   {l[:150]}")
    return code == 0, out, err

def main():
    print("🚀 部署安防运维OA到 172.20.0.139...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)
    print("✅ SSH 连接成功")
    sftp = ssh.open_sftp()

    # 读取 debian-sys-maint 密码
    log("▶ 读取 MySQL debian-sys-maint 密码...")
    with sftp.open('/etc/mysql/debian.cnf', 'r') as f:
        cnf = f.read()
    import re
    dm_user = re.search(r'user\s*=\s*(\S+)', cnf)
    dm_pass = re.search(r'password\s*=\s*(\S+)', cnf)
    if dm_user and dm_pass:
        dm_user, dm_pass = dm_user.group(1), dm_pass.group(1)
        log(f"   debian-sys-maint 用户: {dm_user}")
    else:
        log("   ❌ 无法读取 debian.cnf")
        sys.exit(1)

    mysql_base = f"mysql -u {dm_user} -p'{dm_pass}'"

    # Step 1: 清理并创建目录
    print(f"\n📦 步骤1: 准备目录...")
    run(ssh, f"rm -rf {REMOTE_BASE}", "删除旧目录")
    run(ssh, f"mkdir -p {REMOTE_BASE}", "创建目录")
    run(ssh, f"chown -R {USER}:{USER} /var/www", "设置权限")

    # Step 2: 打包上传
    print("\n📦 步骤2: 打包上传...")
    log("  打包中...")
    tmp_tar = os.path.join(tempfile.gettempdir(), 'oa-api.tar.gz')
    with tarfile.open(tmp_tar, 'w:gz') as tar:
        base_dir = os.path.dirname(LOCAL_API)
        for root, dirs, files in os.walk(LOCAL_API):
            dirs[:] = [d for d in dirs if d not in ('vendor','node_modules','.git')]
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, base_dir)
                tar.add(fp, arcname=arc)
    log(f"  打包完成: {os.path.getsize(tmp_tar)//1024} KB")
    sftp.put(tmp_tar, '/tmp/oa-api.tar.gz')
    log("  上传完成")

    # Step 3: 解压
    print("\n📦 步骤3: 解压...")
    run(ssh, "tar -xzf /tmp/oa-api.tar.gz -C /var/www/", "解压")
    # 检查解压后的目录名
    ok, out, _ = run(ssh, f"ls -d /var/www/pc-api 2>/dev/null && echo FOUND || echo NOTFOUND", "检查目录")
    if 'FOUND' in out:
        run(ssh, f"cp -r /var/www/pc-api/* {REMOTE_BASE}/", "复制文件")
        run(ssh, f"rm -rf /var/www/pc-api", "清理临时目录")
    run(ssh, f"chown -R www-data:www-data {REMOTE_BASE}", "设置 www-data 权限")
    run(ssh, "rm -f /tmp/oa-api.tar.gz", "删除临时文件")
    os.remove(tmp_tar)

    # Step 4: Composer install
    print("\n📦 步骤4: 安装依赖...")
    cmd = f"cd {REMOTE_BASE} && sudo -u www-data composer install --no-dev --optimize-autoloader 2>&1 | tail -10"
    run(ssh, cmd, "Composer install")

    # Step 5: MySQL 建库建用户
    print("\n📦 步骤5: 配置 MySQL...")
    for sql, desc in [
        ("CREATE DATABASE IF NOT EXISTS oa_db CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci", "创建数据库"),
        ("CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'OaPass123!'", "创建用户"),
        ("GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost'", "授权"),
        ("FLUSH PRIVILEGES", "刷新权限"),
    ]:
        q = sql.replace("'", "'\''")
        run(ssh, f"{mysql_base} -e \"{q}\"", desc, sudo=False)

    # Step 6: 写入 .env
    print("\n📦 步骤6: 写入 .env...")
    env_content = "\n".join([
        "APP_NAME=安防运维OA", "APP_ENV=production", "APP_KEY=",
        "APP_DEBUG=false", "APP_URL=http://172.20.0.139", "",
        "DB_CONNECTION=mysql", "DB_HOST=127.0.0.1", "DB_PORT=3306",
        "DB_DATABASE=oa_db", "DB_USERNAME=oa_user", "DB_PASSWORD=OaPass123!",
    ]) + "\n"
    encoded = __import__('base64').b64encode(env_content.encode()).decode()
    run(ssh, f"echo '{encoded}' | base64 -d | sudo tee {REMOTE_BASE}/.env > /dev/null", "写入 .env")
    run(ssh, f"chown www-data:www-data {REMOTE_BASE}/.env", "设置权限")

    # Step 7: 生成 KEY + 迁移
    print("\n📦 步骤7: 数据库迁移...")
    run(ssh, f"cd {REMOTE_BASE} && php artisan key:generate --force", "生成 APP_KEY")
    run(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force", "运行迁移")
    run(ssh, f"cd {REMOTE_BASE} && php artisan db:seed --force", "运行种子")

    # Step 8: Nginx 配置
    print("\n📦 步骤8: 配置 Nginx...")
    nginx_conf = """server {
    listen 80;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php;
    location / { try_files $uri $uri/ /index.php?$query_string; }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
    location ~ /\.(?!well-known).* { deny all; }
}"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
        f.write(nginx_conf); tn = f.name
    sftp.put(tn, '/tmp/oa-api-nginx.conf')
    os.unlink(tn)
    run(ssh, "cp /tmp/oa-api-nginx.conf /etc/nginx/sites-available/oa-api", "复制配置", sudo=True)
    run(ssh, "ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api", "启用站点", sudo=True)
    run(ssh, "rm -f /etc/nginx/sites-enabled/default", "禁用默认", sudo=True)
    run(ssh, "sudo nginx -t", "测试配置", sudo=False)

    # Step 9: 启动服务
    print("\n📦 步骤9: 启动服务...")
    run(ssh, "systemctl start php8.3-fpm", "启动 PHP-FPM", sudo=True)
    run(ssh, "systemctl enable php8.3-fpm", "设置开机启动", sudo=True)
    run(ssh, "sudo nginx -s reload 2>/dev/null || sudo systemctl reload nginx", "重载 Nginx", sudo=False)

    # Step 10: 测试
    print("\n📦 步骤10: 测试...")
    _, out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/", "测试访问")
    log(f"   HTTP 状态码: {out.strip()}")

    sftp.close(); ssh.close()
    print(f"\n🎉 部署完成！")
    print(f"🌐 http://172.20.0.139")
    print(f"📡 http://172.20.0.139/api")
    print(f"\n默认账号: admin/admin123 | manager/123456 | user/123456")

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback; traceback.print_exc()
