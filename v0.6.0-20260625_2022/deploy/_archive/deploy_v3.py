#!/usr/bin/env python3
"""安防运维OA - Laravel 后端部署脚本 v3"""

import paramiko
import os
import sys
import tarfile
import tempfile

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
LOCAL_API = 'D:/work/website/OA/pc-api'
REMOTE_BASE = '/var/www/oa-api'

def log(msg):
    print(f"  {msg}")

def ssh_cmd(ssh, cmd, desc='', sudo=False):
    """执行命令，返回 (ok, stdout)"""
    full = f"sudo bash -c '{cmd}'" if sudo else cmd
    log(f"▶ {desc or cmd[:70]}")
    stdin, stdout, stderr = ssh.exec_command(full, timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out.strip() and len(out.strip()) < 400:
        for ln in out.strip().split('\n'):
            if ln.strip():
                log(f"   {ln[:150]}")
    if err.strip() and code != 0:
        for ln in err.strip().split('\n'):
            if ln.strip():
                log(f"   ⚠️ {ln[:150]}")
    if code != 0:
        log(f"   ❌ 退出码 {code}")
    return code == 0, out.strip(), err.strip()

def mysql_cmd(ssh, sql, desc):
    """执行 MySQL 命令（尝试多种方式）"""
    # 方式1: sudo mysql（auth_socket）
    log(f"▶ MySQL: {desc}")
    stdin, stdout, stderr = ssh.exec_command(f"sudo mysql -u root -e \"{sql}\"", timeout=30)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if code == 0:
        log(f"   ✅ sudo mysql 成功")
        return True
    # 方式2: mysql -u root -p
    log(f"   尝试密码登录...")
    stdin, stdout, stderr = ssh.exec_command(f"mysql -u root -p'admin123' -e \"{sql}\" 2>&1", timeout=30)
    out2 = stdout.read().decode()
    err2 = stderr.read().decode()
    code2 = stdout.channel.recv_exit_status()
    if code2 == 0:
        log(f"   ✅ 密码登录成功")
        return True
    log(f"   ❌ MySQL 操作失败: {err[:200]}")
    return False

def main():
    print("🚀 开始部署安防运维OA后端到 172.20.0.139...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS, timeout=15)
        print("✅ SSH 连接成功")
    except Exception as e:
        print(f"❌ SSH 连接失败: {e}")
        sys.exit(1)

    try:
        sftp = ssh.open_sftp()

        # Step 1: 确认 PHP 已安装
        print("\n📦 步骤1: 确认 PHP...")
        ssh_cmd(ssh, "php -v | head -1", "PHP 版本", sudo=False)

        # Step 2: 确认 Composer
        print("\n📦 步骤2: 确认 Composer...")
        ssh_cmd(ssh, "composer --version", "Composer 版本", sudo=False)

        # Step 3: 清理旧目录并创建新目录
        print(f"\n📦 步骤3: 准备目录 {REMOTE_BASE}...")
        ssh_cmd(ssh, f"rm -rf {REMOTE_BASE}", "删除旧目录", sudo=True)
        ssh_cmd(ssh, f"mkdir -p {REMOTE_BASE}", "创建目录", sudo=True)
        ssh_cmd(ssh, f"chown -R {USER}:{USER} {REMOTE_BASE}", "设置权限", sudo=True)

        # Step 4: 打包并上传
        print("\n📦 步骤4: 打包并上传...")
        log("  打包中（排除 vendor/ node_modules/）...")
        tmp_tar = os.path.join(tempfile.gettempdir(), 'oa-api.tar.gz')
        with tarfile.open(tmp_tar, 'w:gz') as tar:
            # 切换工作目录，使 tar 内的路径为相对路径
            base_dir = os.path.dirname(LOCAL_API)
            for root, dirs, files in os.walk(LOCAL_API):
                dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git', '__pycache__')]
                for file in files:
                    fpath = os.path.join(root, file)
                    arcname = os.path.relpath(fpath, base_dir)
                    tar.add(fpath, arcname=arcname)
        log(f"  打包完成: {os.path.getsize(tmp_tar)//1024} KB")
        log("  上传中...")
        sftp.put(tmp_tar, '/tmp/oa-api.tar.gz')
        log("  上传完成！")
        os.remove(tmp_tar)

        # Step 5: 解压到正确位置
        print(f"\n📦 步骤5: 解压文件...")
        # tar 包顶层目录是 pc-api，解压后移动到 oa-api
        ssh_cmd(ssh, f"tar -xzf /tmp/oa-api.tar.gz -C {REMOTE_BASE}/..", "解压", sudo=True)
        # 如果解压出来是 pc-api 目录，重命名为 oa-api
        ssh_cmd(ssh, f"ls {REMOTE_BASE}/../pc-api >/dev/null 2>&1 && mv {REMOTE_BASE}/../pc-api/* {REMOTE_BASE}/ || echo 'already in place'", "移动文件", sudo=True)
        ssh_cmd(ssh, f"chown -R www-data:www-data {REMOTE_BASE}", "设置 www-data 权限", sudo=True)
        ssh_cmd(ssh, f"rm -f /tmp/oa-api.tar.gz", "删除临时文件", sudo=True)
        ssh_cmd(ssh, f"ls {REMOTE_BASE}/composer.json >/dev/null 2>&1 && echo 'composer.json found'", "验证文件", sudo=False)

        # Step 6: Composer install
        print(f"\n📦 步骤6: 安装 PHP 依赖...")
        cmd = f"cd {REMOTE_BASE} && sudo -u www-data composer install --no-dev --optimize-autoloader 2>&1 | tail -5"
        ssh_cmd(ssh, cmd, "Composer install", sudo=False)

        # Step 7: MySQL 配置
        print("\n📦 步骤7: 配置 MySQL 数据库...")
        mysql_cmd(ssh, "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci", "创建数据库 oa_db")
        mysql_cmd(ssh, "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'OaPass123!'", "创建用户")
        mysql_cmd(ssh, "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost'", "授权")
        mysql_cmd(ssh, "FLUSH PRIVILEGES", "刷新权限")

        # Step 8: 写入 .env（在 chown 之前写，或者用 sudo 写）
        print("\n📦 步骤8: 写入 .env...")
        env_content = "\n".join([
            "APP_NAME=安防运维OA",
            "APP_ENV=production",
            "APP_KEY=",
            "APP_DEBUG=false",
            "APP_URL=http://172.20.0.139",
            "",
            "DB_CONNECTION=mysql",
            "DB_HOST=127.0.0.1",
            "DB_PORT=3306",
            "DB_DATABASE=oa_db",
            "DB_USERNAME=oa_user",
            "DB_PASSWORD=OaPass123!",
            "",
            "SANCTUM_STATEFUL_DOMAINS=172.20.0.139",
            "",
            "CACHE_DRIVER=file",
            "QUEUE_CONNECTION=sync",
            "SESSION_DRIVER=file",
        ]) + "\n"
        # 用 sudo tee 写入（绕过权限问题）
        import base64
        encoded = base64.b64encode(env_content.encode()).decode()
        ssh_cmd(ssh, f"echo '{encoded}' | base64 -d | sudo tee {REMOTE_BASE}/.env > /dev/null", "写入 .env", sudo=False)
        ssh_cmd(ssh, f"chown www-data:www-data {REMOTE_BASE}/.env", "设置 .env 权限", sudo=True)

        # Step 9: 生成 APP_KEY + 迁移
        print("\n📦 步骤9: 数据库迁移...")
        ssh_cmd(ssh, f"cd {REMOTE_BASE} && php artisan key:generate --force", "生成 APP_KEY", sudo=False)
        ssh_cmd(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force", "运行迁移", sudo=False)
        ssh_cmd(ssh, f"cd {REMOTE_BASE} && php artisan db:seed --force", "运行种子", sudo=False)

        # Step 10: Nginx 配置
        print("\n📦 步骤10: 配置 Nginx...")
        nginx_conf = r"""server {
    listen 80;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
    location ~ /\.(?!well-known).* {
        deny all;
    }
}"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
            f.write(nginx_conf)
            tmp_nginx = f.name
        sftp.put(tmp_nginx, '/tmp/oa-api-nginx.conf')
        os.unlink(tmp_nginx)
        ssh_cmd(ssh, "cp /tmp/oa-api-nginx.conf /etc/nginx/sites-available/oa-api", "复制 Nginx 配置", sudo=True)
        ssh_cmd(ssh, "ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api", "启用站点", sudo=True)
        ssh_cmd(ssh, "rm -f /etc/nginx/sites-enabled/default", "禁用默认站点", sudo=True)
        ssh_cmd(ssh, "nginx -t", "测试 Nginx 配置", sudo=False)

        # Step 11: 启动服务
        print("\n📦 步骤11: 启动服务...")
        ssh_cmd(ssh, "systemctl start php8.3-fpm", "启动 PHP-FPM", sudo=True)
        ssh_cmd(ssh, "systemctl enable php8.3-fpm", "设置开机启动", sudo=True)
        ssh_cmd(ssh, "systemctl reload nginx", "重载 Nginx", sudo=True)

        # Step 12: 测试
        print("\n📦 步骤12: 测试...")
        ok, out, _ = ssh_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/", "测试 HTTP")
        log(f"   HTTP 状态码: {out}")

        sftp.close()
        ssh.close()

        print(f"\n🎉 部署完成！")
        print(f"🌐 访问地址: http://172.20.0.139")
        print(f"📡 API 地址: http://172.20.0.139/api")
        print(f"\n📋 默认账号:")
        print(f"   管理员: admin / admin123")
        print(f"   经理:   manager / 123456")
        print(f"   员工:   user / 123456")

    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
