#!/usr/bin/env python3
"""安防运维OA - Laravel 后端部署脚本 v2"""

import paramiko
import os
import sys
import tarfile
import tempfile
import time

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
LOCAL_API = 'D:/work/website/OA/pc-api'
REMOTE_BASE = '/var/www/oa-api'

def log(msg):
    print(f"  {msg}")

def ssh_exec(ssh, cmd, desc='', sudo=False):
    """执行 SSH 命令"""
    full_cmd = f"sudo bash -c '{cmd}'" if sudo else cmd
    log(f"▶ {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(full_cmd, timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    exit_code = stdout.channel.recv_exit_status()
    if out.strip() and len(out.strip()) < 500:
        for line in out.strip().split('\n'):
            if line.strip():
                log(f"   {line[:120]}")
    if err.strip() and exit_code != 0:
        for line in err.strip().split('\n'):
            if line.strip():
                log(f"   ⚠️ {line[:120]}")
    if exit_code != 0:
        log(f"   ❌ 退出码 {exit_code}")
        return False, out, err
    return True, out, err

def ssh_exec_no_sudo(ssh, cmd, desc=''):
    """执行不需要 sudo 的命令"""
    log(f"▶ {desc or cmd[:60]}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    out = stdout.read().decode()
    err = stderr.read().decode()
    exit_code = stdout.channel.recv_exit_status()
    if out.strip() and len(out.strip()) < 500:
        for line in out.strip().split('\n'):
            if line.strip():
                log(f"   {line[:120]}")
    if err.strip() and exit_code != 0:
        for line in err.strip().split('\n'):
            if line.strip():
                log(f"   ⚠️ {line[:120]}")
    if exit_code != 0:
        log(f"   ❌ 退出码 {exit_code}")
        return False, out, err
    return True, out, err

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
        # Step 1: 安装 PHP 8.3（Ubuntu 24.04 默认）
        print("\n📦 步骤1: 安装 PHP 8.3...")
        ssh_exec(ssh, "apt update -qq", "更新软件包列表", sudo=True)
        php_pkgs = ("php php-fpm php-mysql php-mbstring php-xml php-curl "
                   "php-zip php-gd php-tokenizer php-fileinfo php-bcmath php-dom")
        ssh_exec(ssh, f"apt install -y -qq {php_pkgs}", f"安装 PHP 及扩展", sudo=True)
        ssh_exec(ssh, "php -v | head -1", "验证 PHP 版本", sudo=False)
        # 检查 php-fpm 服务名
        ok, out, _ = ssh_exec(ssh, "ls /etc/init.d/php*-fpm 2>/dev/null || echo 'not_found'", "检查 PHP-FPM", sudo=False)
        php_fpm_service = 'php8.3-fpm'  # 默认
        if out and '8.3' in out:
            php_fpm_service = 'php8.3-fpm'
        log(f"   PHP-FPM 服务名: {php_fpm_service}")

        # Step 2: 安装 Composer
        print("\n📦 步骤2: 安装 Composer...")
        cmd = "curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer"
        ssh_exec(ssh, cmd, "下载安装 Composer", sudo=True)
        ssh_exec(ssh, "composer --version", "验证 Composer", sudo=False)

        # Step 3: 创建项目目录
        print(f"\n📦 步骤3: 创建项目目录...")
        ssh_exec(ssh, f"mkdir -p {REMOTE_BASE}", sudo=True)
        ssh_exec(ssh, f"chown -R {USER}:{USER} /var/www", sudo=True)

        # Step 4: 打包并上传
        print("\n📦 步骤4: 打包并上传后端文件...")
        log("  打包中（排除 vendor/ node_modules/）...")
        tmp_tar = os.path.join(tempfile.gettempdir(), 'oa-api.tar.gz')
        with tarfile.open(tmp_tar, 'w:gz') as tar:
            for root, dirs, files in os.walk(LOCAL_API):
                dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git', 'storage/logs', 'storage/framework')]
                for file in files:
                    fpath = os.path.join(root, file)
                    arcname = os.path.relpath(fpath, os.path.dirname(LOCAL_API))
                    tar.add(fpath, arcname=arcname)
        log(f"  打包完成: {os.path.getsize(tmp_tar)//1024} KB")
        
        log("  上传中...")
        sftp = ssh.open_sftp()
        remote_tar = '/tmp/oa-api.tar.gz'
        sftp.put(tmp_tar, remote_tar)
        log("  上传完成！")
        os.remove(tmp_tar)

        # Step 5: 解压
        print(f"\n📦 步骤5: 解压文件...")
        ssh_exec(ssh, f"tar -xzf {remote_tar} -C /var/www/", "解压", sudo=True)
        ssh_exec(ssh, f"chown -R www-data:www-data {REMOTE_BASE}", sudo=True)
        ssh_exec(ssh, f"rm -f {remote_tar}", "删除临时文件", sudo=True)

        # Step 6: 安装 PHP 依赖
        print("\n📦 步骤6: 安装 PHP 依赖...")
        cmd = f"cd {REMOTE_BASE} && sudo -u www-data composer install --no-dev --optimize-autoloader 2>&1 | tail -3"
        ssh_exec(ssh, cmd, "Composer install", sudo=False)

        # Step 7: 配置 MySQL（使用 sudo mysql 免密登录）
        print("\n📦 步骤7: 配置 MySQL 数据库...")
        sq = f"""sudo mysql -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" """
        ssh_exec(ssh, sq, "创建数据库 oa_db", sudo=False)
        sq = f"""sudo mysql -e "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'OaPass123!';" """
        ssh_exec(ssh, sq, "创建用户 oa_user", sudo=False)
        sq = f"""sudo mysql -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" """
        ssh_exec(ssh, sq, "授权", sudo=False)
        sq = f"""sudo mysql -e "FLUSH PRIVILEGES;" """
        ssh_exec(ssh, sq, "刷新权限", sudo=False)

        # Step 8: 写入 .env
        print("\n📦 步骤8: 写入 .env 配置...")
        env_lines = [
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
        ]
        # 用 sftp 写入 .env
        env_content = '\n'.join(env_lines) + '\n'
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
            f.write(env_content)
            tmp_env = f.name
        sftp.put(tmp_env, f"{REMOTE_BASE}/.env")
        os.unlink(tmp_env)
        log("  .env 写入完成")
        
        # Step 9: 生成 APP_KEY 并运行迁移
        print("\n📦 步骤9: 生成 APP_KEY 并运行迁移...")
        ssh_exec(ssh, f"cd {REMOTE_BASE} && php artisan key:generate --force", "生成 APP_KEY", sudo=False)
        ssh_exec(ssh, f"cd {REMOTE_BASE} && php artisan migrate --force", "运行数据库迁移", sudo=False)
        ssh_exec(ssh, f"cd {REMOTE_BASE} && php artisan db:seed --force", "运行数据库种子", sudo=False)

        # Step 10: 配置 Nginx
        print("\n📦 步骤10: 配置 Nginx...")
        nginx_conf = f"""server {{
    listen 80;
    server_name 172.20.0.139;
    root {REMOTE_BASE}/public;
    index index.php index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}
    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }}
    location ~ /\\.(?!well-known).* {{
        deny all;
    }}
    error_log /var/log/nginx/oa-api_error.log;
    access_log /var/log/nginx/oa-api_access.log;
}}"""
        # 写入 nginx 配置
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
            f.write(nginx_conf)
            tmp_nginx = f.name
        sftp.put(tmp_nginx, '/tmp/oa-api-nginx.conf')
        os.unlink(tmp_nginx)
        ssh_exec(ssh, "cp /tmp/oa-api-nginx.conf /etc/nginx/sites-available/oa-api", "复制 Nginx 配置", sudo=True)
        ssh_exec(ssh, "ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api", "启用站点", sudo=True)
        ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default", "禁用默认站点", sudo=True)
        ssh_exec(ssh, "nginx -t", "测试 Nginx 配置", sudo=False)
        
        # Step 11: 启动服务
        print("\n📦 步骤11: 启动服务...")
        ssh_exec(ssh, f"systemctl start {php_fpm_service}", "启动 PHP-FPM", sudo=True)
        ssh_exec(ssh, f"systemctl enable {php_fpm_service}", "设置 PHP-FPM 开机启动", sudo=True)
        ssh_exec(ssh, "systemctl reload nginx", "重载 Nginx", sudo=True)
        
        # Step 12: 测试
        print("\n📦 步骤12: 测试部署...")
        ok, out, _ = ssh_exec(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/", "测试 HTTP 访问", sudo=False)
        log(f"   HTTP 状态码: {out.strip()}")
        
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
