#!/usr/bin/env python3
"""
部署 Laravel 11 + 业务代码，然后修复 config/app.php
"""
import paramiko
import os
import tarfile
from scp import SCPClient

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def create_business_tarball():
    """打包业务代码"""
    print("Packing business code...")
    tar_path = "D:/work/website/OA/deploy/oa_biz_l11.tar.gz"
    
    base_dir = "D:/work/website/OA/pc-api"
    dirs_to_pack = []
    
    for d in ['app/Http/Controllers/Api', 'app/Models', 'app/Services', 'app/Enums', 'config', 'database', 'routes', 'resources']:
        path = os.path.join(base_dir, d)
        if os.path.exists(path):
            print(f"  Adding: {d}/")
            dirs_to_pack.append((d, d.replace('\\', '/')))
    
    if not dirs_to_pack:
        print("ERROR: No business code found!")
        return None
    
    with tarfile.open(tar_path, "w:gz") as tar:
        for src, arc in dirs_to_pack:
            path = os.path.join(base_dir, src)
            tar.add(path, arcname=arc)
    
    size = os.path.getsize(tar_path)
    print(f"Package created: {tar_path} ({size} bytes)")
    return tar_path

def run_cmd(ssh, cmd, timeout=300, show_output=True):
    """执行远程命令"""
    print(f">> {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if show_output:
        if out and len(out.strip()) > 0:
            print(f"   OUT: {out[:500]}")
        if err and code != 0:
            print(f"   ERR (code {code}): {err[:500]}")
    return code, out, err

def fix_config_app_php(ssh):
    """修复 config/app.php 使其兼容 Laravel 11"""
    print("\nFixing config/app.php for Laravel 11...")
    
    # 读取远程的 config/app.php
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/config/app.php", show_output=False)
    
    if 'AuthServiceProvider' in out or 'RouteServiceProvider' in out:
        print("  Found old providers, removing them...")
        # 使用 sed 删除包含这两个 Provider 的行
        run_cmd(ssh, f"""sudo -u www-data sed -i '/AuthServiceProvider/d' {REMOTE_DIR}/config/app.php""")
        run_cmd(ssh, f"""sudo -u www-data sed -i '/RouteServiceProvider/d' {REMOTE_DIR}/config/app.php""")
        print("  Fixed!")

def main():
    print("=" * 60)
    print("Deploying Laravel 11 + Business Code (Fixed)")
    print("=" * 60)
    
    # 1. 打包
    tar_path = create_business_tarball()
    if not tar_path:
        return
    
    # 2. 连接
    print("\nConnecting...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 3. 创建 Laravel 11 项目
    print("\nCreating Laravel 11 project...")
    run_cmd(ssh, f"sudo rm -rf {REMOTE_DIR}")
    code, out, err = run_cmd(ssh, f"cd /var/www && sudo -u www-data composer create-project laravel/laravel oa-api 2>&1 | tail -20", timeout=180)
    if code != 0:
        print("ERROR: Failed to create Laravel 11 project!")
        ssh.close()
        return
    print("Laravel 11 project created!")
    
    # 4. 配置 .env
    print("\nConfiguring .env...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data cp .env.example .env")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan key:generate")
    
    # 5. 上传业务代码
    print("\nUploading business code...")
    remote_tar = "/tmp/oa_biz_l11.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    # 6. 删除旧的业务代码（保留 Laravel 11 核心）
    print("\nRemoving old business code...")
    run_cmd(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/app/Http/Controllers/Api 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data find {REMOTE_DIR}/app/Models -name '*.php' ! -name 'User.php' -delete 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/database/migrations/* 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/database/seeders/* 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/routes/api.php 2>/dev/null || true")
    
    # 7. 解压业务代码
    print("\nExtracting business code...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"WARNING: {err[:500]}")
    else:
        print("Extraction complete!")
    
    # 8. 修复 config/app.php（关键步骤！）
    fix_config_app_php(ssh)
    
    # 9. 确保 storage 目录存在
    print("\nEnsuring storage directories...")
    for d in ['storage/logs', 'storage/framework/cache', 'storage/framework/sessions', 'storage/framework/views', 'storage/app/public', 'bootstrap/cache']:
        run_cmd(ssh, f"sudo -u www-data mkdir -p {REMOTE_DIR}/{d}")
    
    # 10. 安装依赖
    print("\nInstalling Composer dependencies...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer update --no-interaction 2>&1 | tail -30", timeout=300)
    if code != 0:
        print(f"ERROR: Composer update failed!")
        print(f"STDERR: {err[:2000]}")
        ssh.close()
        return
    
    # 11. 配置数据库
    print("\nSetting up database...")
    code, out, err = run_cmd(ssh, "sudo cat /etc/mysql/debian.cnf | grep -E 'user|password'", show_output=False)
    lines = out.strip().split('\n')
    db_user = ''
    db_pass = ''
    for line in lines:
        if 'user' in line.lower() and '=' in line:
            db_user = line.split('=')[1].strip()
        if 'password' in line.lower() and '=' in line:
            db_pass = line.split('=')[1].strip()
    
    if db_user and db_pass:
        print(f"  DB admin: {db_user}")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'oa_password';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "FLUSH PRIVILEGES;" 2>&1""")
        
        # 更新 .env
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_DATABASE=.*/DB_DATABASE=oa_db/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_USERNAME=.*/DB_USERNAME=oa_user/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=oa_password/' {REMOTE_DIR}/.env""")
    
    # 12. 运行迁移
    print("\nRunning migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration: {out[:800]}")
    if err and 'error' in err.lower():
        print(f"  Errors: {err[:800]}")
    
    # 13. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed: {out[:800]}")
    
    # 14. 设置权限
    print("\nSetting permissions...")
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 15. 重启服务
    print("\nRestarting services...")
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 16. 测试
    print("\nTesting HTTP access...")
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show_output=False)
    print(f"  HTTP Status: {out}")
    
    # 17. 查看路由
    print("\nChecking routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -60")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"  Routes:\n{out[:2000]}")
    else:
        print(f"  Error: {err[:1000]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Deployment complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nDefault credentials (if seeded):")
    print("  Username: admin")
    print("  Password: password")
    print("\nNext steps:")
    print(f"  1. Update frontend .env: VITE_API_BASE=http://{SSH_HOST}")
    print(f"  2. Test login at http://{SSH_HOST}/login")
    print("=" * 60)

if __name__ == "__main__":
    main()
