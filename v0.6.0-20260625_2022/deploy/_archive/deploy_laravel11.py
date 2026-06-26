#!/usr/bin/env python3
"""
在服务器上部署 Laravel 11 + 业务代码
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
    
    # 只打包业务代码
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

def main():
    print("=" * 60)
    print("Deploying Laravel 11 + Business Code")
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
    
    # 3. 在服务器上创建 Laravel 11 项目
    print("\nCreating Laravel 11 project on server...")
    run_cmd(ssh, f"sudo rm -rf {REMOTE_DIR}")
    code, out, err = run_cmd(ssh, f"cd /var/www && sudo -u www-data composer create-project laravel/laravel oa-api 2>&1 | tail -30", timeout=180)
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
    # 6. 备份当前业务代码
    print("\nBacking up current business code...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && tar czf /tmp/oa_biz_backup_$(date +%Y%m%d_%H%M%S).tar.gz app/Http/Controllers/Api app/Models config database routes 2>/dev/null || true")
    
    # 7. 删除旧的业务代码（保留 Laravel 11 核心文件）
    print("\nRemoving old business code (keeping Laravel 11 core)...")
    # 只删除 Api 目录
    run_cmd(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/app/Http/Controllers/Api 2>/dev/null || true")
    # 删除旧的 Models（保留 User.php）
    run_cmd(ssh, f"sudo -u www-data find {REMOTE_DIR}/app/Models -name '*.php' ! -name 'User.php' -delete 2>/dev/null || true")
    # 删除旧的迁移和种子
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/database/migrations/*.php 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/database/seeders/*.php 2>/dev/null || true")
    # 删除旧的路由
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/routes/api.php 2>/dev/null || true")
    # 删除旧的配置（将被新配置覆盖）
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/config/cors.php 2>/dev/null || true")
    run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/config/sanctum.php 2>/dev/null || true")
    
    # 8. 解压新的业务代码
    print("\nExtracting new business code...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"WARNING during extraction: {err[:500]}")
    else:
        print("Extraction complete!")
    
    # 9. 安装依赖（包括 sanctum 和 spatie/laravel-permission）
    print("\nInstalling Composer dependencies (Laravel 11)...")
    # 先更新 composer.json 以确保依赖正确
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/"laravel\\/framework": "[^"]*"/"laravel\\/framework": "^11.0"/' {REMOTE_DIR}/composer.json""")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer update --no-interaction 2>&1 | tail -30", timeout=300)
    if code != 0:
        print(f"ERROR: Composer update failed!")
        print(f"STDERR: {err[:1000]}")
        ssh.close()
        return
    
    # 10. 配置数据库
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
        # 创建数据库和用户
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'oa_password';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "FLUSH PRIVILEGES;" 2>&1""")
        
        # 更新 .env
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_DATABASE=.*/DB_DATABASE=oa_db/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_USERNAME=.*/DB_USERNAME=oa_user/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=oa_password/' {REMOTE_DIR}/.env""")
    
    # 11. 运行迁移
    print("\nRunning migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration: {out[:800]}")
    if err and 'error' in err.lower():
        print(f"  Errors: {err[:800]}")
    
    # 12. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed: {out[:800]}")
    
    # 13. 设置权限
    print("\nSetting permissions...")
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 14. 重启服务
    print("\nRestarting services...")
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 15. 测试访问
    print("\nTesting HTTP access...")
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show_output=False)
    print(f"  HTTP Status: {out}")
    
    # 16. 查看路由
    print("\nChecking routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -60")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"  Routes:\n{out[:1500]}")
    else:
        print(f"  Error: {err[:800]}")
    
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
