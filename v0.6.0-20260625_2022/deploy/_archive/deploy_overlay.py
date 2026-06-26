#!/usr/bin/env python3
"""
正确的部署方式：
1. 保留服务器上的 Laravel 骨架（AppServiceProvider.php, Controller.php 等）
2. 只覆盖业务代码文件
3. 不删除 Laravel 核心文件
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
    """只打包业务代码（不包 Laravel 核心文件）"""
    print("Packing business code (business logic only)...")
    tar_path = "D:/work/website/OA/deploy/oa_business_logic.tar.gz"
    
    # 只打包业务代码目录
    dirs_to_pack = []
    
    # app/Http/Controllers/Api/ - API 控制器
    api_ctrl = "D:/work/website/OA/pc-api/app/Http/Controllers/Api"
    if os.path.exists(api_ctrl):
        dirs_to_pack.append(('app/Http/Controllers/Api', 'app/Http/Controllers/Api'))
    
    # app/Models/ - 模型
    models_dir = "D:/work/website/OA/pc-api/app/Models"
    if os.path.exists(models_dir):
        dirs_to_pack.append(('app/Models', 'app/Models'))
    
    # app/Services/ - 服务类（如果存在）
    services_dir = "D:/work/website/OA/pc-api/app/Services"
    if os.path.exists(services_dir):
        dirs_to_pack.append(('app/Services', 'app/Services'))
    
    # app/Enums/ - 枚举类（如果存在）
    enums_dir = "D:/work/website/OA/pc-api/app/Enums"
    if os.path.exists(enums_dir):
        dirs_to_pack.append(('app/Enums', 'app/Enums'))
    
    # config/ - 配置文件
    config_dir = "D:/work/website/OA/pc-api/config"
    if os.path.exists(config_dir):
        dirs_to_pack.append(('config', 'config'))
    
    # database/ - 迁移和种子
    db_dir = "D:/work/website/OA/pc-api/database"
    if os.path.exists(db_dir):
        dirs_to_pack.append(('database', 'database'))
    
    # routes/ - 路由
    routes_dir = "D:/work/website/OA/pc-api/routes"
    if os.path.exists(routes_dir):
        dirs_to_pack.append(('routes', 'routes'))
    
    # resources/ - 视图（如果有）
    res_dir = "D:/work/website/OA/pc-api/resources"
    if os.path.exists(res_dir):
        dirs_to_pack.append(('resources', 'resources'))
    
    if not dirs_to_pack:
        print("ERROR: No business code found!")
        return None
    
    with tarfile.open(tar_path, "w:gz") as tar:
        base_dir = "D:/work/website/OA/pc-api"
        for src, arc in dirs_to_pack:
            path = os.path.join(base_dir, src)
            print(f"  Adding: {src}/")
            tar.add(path, arcname=arc)
    
    size = os.path.getsize(tar_path)
    print(f"Package created: {tar_path} ({size} bytes)")
    return tar_path

def run_command(ssh, cmd, timeout=300):
    """执行远程命令"""
    print(f"Executing: {cmd[:90]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out and len(out.strip()) > 0:
        print(f"  Output: {out[:400]}")
    if err and code != 0:
        print(f"  Error (code {code}): {err[:400]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Deploying: Keep Laravel skeleton + overlay business code")
    print("=" * 60)
    
    # 1. 打包业务代码
    tar_path = create_business_tarball()
    if not tar_path:
        print("Aborting.")
        return
    
    # 2. 连接 SSH
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 3. 确保服务器上有完整的 Laravel 项目
    print("\nChecking remote Laravel project integrity...")
    code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/app/Providers/AppServiceProvider.php && echo 'OK' || echo 'MISSING'")
    if "MISSING" in out:
        print("  Laravel core files missing, recreating project...")
        run_command(ssh, f"cd /var/www && sudo -u www-data composer create-project laravel/laravel oa-api-new 2>&1 | tail -10")
        run_command(ssh, f"sudo mv {REMOTE_DIR} {REMOTE_DIR}.bak.$(date +%s)")
        run_command(ssh, f"sudo mv /var/www/oa-api-new {REMOTE_DIR}")
        run_command(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    
    # 4. 备份当前业务代码
    print("\nBacking up current business code...")
    run_command(ssh, f"cd {REMOTE_DIR} && tar czf /tmp/oa_biz_backup_$(date +%Y%m%d_%H%M%S).tar.gz app/Http/Controllers/Api app/Models config/database.php config/cors.php routes/api.php database 2>/dev/null || true")
    
    # 5. 删除旧的业务代码文件（但保留 Laravel 核心）
    print("\nRemoving old business code files (keeping Laravel core)...")
    # 只删除 Api 控制器
    run_command(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/app/Http/Controllers/Api/* 2>/dev/null || true")
    # 删除旧的 Model 文件（但保留 User.php 如果它存在）
    run_command(ssh, f"sudo -u www-data find {REMOTE_DIR}/app/Models -name '*.php' ! -name 'User.php' -delete 2>/dev/null || true")
    # 删除旧的迁移文件
    run_command(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/database/migrations/*.php 2>/dev/null || true")
    # 删除旧的种子文件
    run_command(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/database/seeders/*.php 2>/dev/null || true")
    # 删除旧的路由文件
    run_command(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/routes/api.php 2>/dev/null || true")
    
    # 6. 上传并解压新的业务代码
    print("\nUploading business code...")
    remote_tar = "/tmp/oa_business_logic.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    print("\nExtracting business code (overlay)...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"  Warning: {err[:500]}")
    else:
        print("  Extraction complete!")
    
    # 7. 确保 Laravel 核心文件存在
    print("\nVerifying Laravel core files...")
    core_files = [
        'app/Providers/AppServiceProvider.php',
        'app/Providers/AuthServiceProvider.php',
        'app/Providers/RouteServiceProvider.php',
        'app/Http/Controllers/Controller.php',
        'app/Http/Kernel.php',
        'app/Http/Middleware/RedirectIfAuthenticated.php',
    ]
    for f in core_files:
        code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/{f} && echo 'OK' || echo 'MISSING: {f}'")
        if "MISSING" in out:
            print(f"  WARNING: {f} is missing!")
    
    # 8. 配置 .env
    print("\nChecking .env...")
    code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/.env && echo 'OK' || echo 'MISSING'")
    if "MISSING" in out:
        run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data cp .env.example .env")
        run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan key:generate")
    
    # 9. 安装依赖
    print("\nInstalling Composer dependencies...")
    run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -20", timeout=180)
    
    # 10. 运行迁移
    print("\nRunning migrations...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration: {out[:500]}")
    
    # 11. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed: {out[:500]}")
    
    # 12. 设置权限
    print("\nSetting permissions...")
    run_command(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_command(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 13. 重启服务
    print("\nRestarting services...")
    run_command(ssh, "sudo systemctl restart php8.3-fpm")
    run_command(ssh, "sudo systemctl restart nginx")
    
    # 14. 测试
    print("\nTesting HTTP access...")
    code, out, err = run_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1")
    print(f"  HTTP Status: {out}")
    
    # 15. 查看路由
    print("\nChecking routes...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -50")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"  Routes:\n{out[:1000]}")
    else:
        print(f"  Error checking routes: {err[:500]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Deployment complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nDefault credentials (if seeded):")
    print("  Username: admin")
    print("  Password: password")
    print("\nNext steps:")
    print(f"  1. Update frontend API URL to http://{SSH_HOST}")
    print("  2. Test login at http://172.20.0.139/login")
    print("=" * 60)

if __name__ == "__main__":
    main()
