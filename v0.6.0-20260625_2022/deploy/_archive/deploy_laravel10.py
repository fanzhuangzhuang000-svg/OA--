#!/usr/bin/env python3
"""
在服务器上部署 Laravel 10（与业务代码匹配）
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
    tar_path = "D:/work/website/OA/deploy/oa_biz.tar.gz"
    
    dirs_to_pack = []
    base_dir = "D:/work/website/OA/pc-api"
    
    # 只打包业务代码目录
    for d in ['app/Http/Controllers/Api', 'app/Models', 'app/Services', 'app/Enums', 'config', 'database', 'routes', 'resources']:
        path = os.path.join(base_dir, d)
        if os.path.exists(path):
            arc = d.replace('\\', '/')
            print(f"  Adding: {arc}/")
            dirs_to_pack.append((d, arc))
    
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
            print(f"   OUT: {out[:400]}")
        if err and code != 0:
            print(f"   ERR (code {code}): {err[:400]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Deploying Laravel 10 + Business Code")
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
    
    # 3. 在服务器上创建 Laravel 10 项目
    print("\nCreating Laravel 10 project on server...")
    # 先删掉旧的（如果有）
    run_cmd(ssh, f"sudo rm -rf {REMOTE_DIR}")
    # 创建 Laravel 10 项目
    code, out, err = run_cmd(ssh, f"cd /var/www && sudo -u www-data composer create-project laravel/laravel:^10.0 oa-api 2>&1 | tail -30", timeout=180)
    if code != 0:
        print("ERROR: Failed to create Laravel 10 project!")
        print(f"STDERR: {err[:1000]}")
        ssh.close()
        return
    
    print("Laravel 10 project created!")
    
    # 4. 配置 .env
    print("\nConfiguring .env...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data cp .env.example .env")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan key:generate")
    
    # 5. 上传业务代码
    print("\nUploading business code...")
    remote_tar = "/tmp/oa_biz.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    # 6. 解压业务代码（覆盖默认文件）
    print("\nExtracting business code (overwriting defaults)...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"WARNING during extraction: {err[:500]}")
    else:
        print("Extraction complete!")
    
    # 7. 确保 storage 目录存在
    print("\nEnsuring storage directories exist...")
    for d in ['storage/logs', 'storage/framework/cache', 'storage/framework/sessions', 'storage/framework/views', 'storage/app/public', 'bootstrap/cache']:
        run_cmd(ssh, f"sudo -u www-data mkdir -p {REMOTE_DIR}/{d}")
    
    # 8. 安装依赖
    print("\nInstalling Composer dependencies...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -20", timeout=180)
    
    # 9. 配置数据库（需要先创建数据库）
    print("\nSetting up database...")
    # 从服务器读取 debian-sys-maint 凭证
    code, out, err = run_cmd(ssh, "sudo cat /etc/mysql/debian.cnf | grep -E 'user|password'", show_output=False)
    # 解析出 user 和 password
    lines = out.strip().split('\n')
    db_user = ''
    db_pass = ''
    for line in lines:
        if 'user' in line.lower() and '=' in line:
            db_user = line.split('=')[1].strip()
        if 'password' in line.lower() and '=' in line:
            db_pass = line.split('=')[1].strip()
    
    if db_user and db_pass:
        print(f"  DB admin user: {db_user}")
        # 创建数据库和用户
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE DATABASE IF NOT EXISTS oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE USER IF NOT EXISTS 'oa_user'@'localhost' IDENTIFIED BY 'oa_password';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>&1""")
        run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "FLUSH PRIVILEGES;" 2>&1""")
        
        # 更新 .env 数据库配置
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_DATABASE=.*/DB_DATABASE=oa_db/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_USERNAME=.*/DB_USERNAME=oa_user/' {REMOTE_DIR}/.env""")
        run_cmd(ssh, f"""sudo -u www-data sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=oa_password/' {REMOTE_DIR}/.env""")
    
    # 10. 运行迁移
    print("\nRunning migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration: {out[:500]}")
    if err and 'error' in err.lower():
        print(f"  Migration errors: {err[:500]}")
    
    # 11. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed: {out[:500]}")
    
    # 12. 设置权限
    print("\nSetting permissions...")
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 13. 重启服务
    print("\nRestarting services...")
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 14. 测试
    print("\nTesting HTTP access...")
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show_output=False)
    print(f"  HTTP Status: {out}")
    
    # 15. 查看路由
    print("\nChecking routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -50")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"  Routes:\n{out[:1500]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Deployment complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nDefault credentials (if seeded):")
    print("  Username: admin")
    print("  Password: password (check database if not working)")
    print("\nNext steps:")
    print(f"  1. Update frontend .env: VITE_API_BASE=http://{SSH_HOST}")
    print(f"  2. Test login at http://{SSH_HOST}/login")
    print("=" * 60)

if __name__ == "__main__":
    main()
