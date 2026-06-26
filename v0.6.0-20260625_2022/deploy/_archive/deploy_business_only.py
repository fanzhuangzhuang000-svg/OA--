#!/usr/bin/env python3
"""
正确的部署方式：保留 Laravel 骨架，只覆盖业务代码
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
    """只打包业务代码（不包含 Laravel 骨架文件）"""
    print("Packing business code only...")
    tar_path = "D:/work/website/OA/deploy/oa_business_only.tar.gz"
    
    # 只打包这些目录的内容
    dirs_to_pack = [
        ('app', 'app'),
        ('config', 'config'),
        ('database', 'database'),
        ('resources', 'resources'),
        ('routes', 'routes'),
    ]
    
    with tarfile.open(tar_path, "w:gz") as tar:
        base_dir = "D:/work/website/OA/pc-api"
        for src, arc in dirs_to_pack:
            path = os.path.join(base_dir, src)
            if os.path.exists(path):
                print(f"  Adding: {src}/")
                tar.add(path, arcname=arc)
        
        # 打包 public 目录（但保留 .htaccess 等）
        public_path = os.path.join(base_dir, 'public')
        if os.path.exists(public_path):
            print("  Adding: public/")
            tar.add(public_path, arcname='public')
    
    print(f"Package created: {tar_path} ({os.path.getsize(tar_path)} bytes)")
    return tar_path

def run_command(ssh, cmd, timeout=300, sudo=False):
    """执行远程命令"""
    if sudo:
        # 包装为 sudo bash -c
        escaped = cmd.replace("'", "'\"'\"'")
        cmd = f"sudo bash -c '{escaped}'"
    
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
    print("Deploying business code (keeping Laravel skeleton)")
    print("=" * 60)
    
    # 1. 打包业务代码
    tar_path = create_business_tarball()
    
    # 2. 连接 SSH
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 3. 检查远程 Laravel 项目状态
    print("\nChecking remote Laravel project...")
    code, out, err = run_command(ssh, f"ls -la {REMOTE_DIR}/artisan 2>/dev/null && echo 'EXISTS' || echo 'MISSING'")
    if "MISSING" in out:
        print("  ERROR: artisan file missing! Need to recreate Laravel project.")
        print("  Running: composer create-project laravel/laravel oa-api-temp...")
        run_command(ssh, f"cd /var/www && sudo -u www-data composer create-project laravel/laravel oa-api-temp 2>&1 | tail -20")
        run_command(ssh, f"sudo mv {REMOTE_DIR} {REMOTE_DIR}.bak.$(date +%s)")
        run_command(ssh, f"sudo mv /var/www/oa-api-temp {REMOTE_DIR}")
        run_command(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    
    # 4. 上传业务代码包
    print("\nUploading business code package...")
    remote_tar = "/tmp/oa_business_only.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    # 5. 备份当前业务代码
    print("\nBacking up current business code...")
    run_command(ssh, f"cd {REMOTE_DIR} && tar czf /tmp/oa_business_backup_$(date +%Y%m%d_%H%M%S).tar.gz app config database resources routes 2>/dev/null || true")
    
    # 6. 清空业务目录（保留 Laravel 核心文件）
    print("\nCleaning old business code...")
    for d in ['app/Http/Controllers', 'app/Models', 'app/Providers', 'config', 'database/migrations', 'database/seeders', 'resources', 'routes']:
        run_command(ssh, f"sudo -u www-data rm -rf {REMOTE_DIR}/{d}/* 2>/dev/null || true")
    
    # 7. 解压新业务代码
    print("\nExtracting new business code...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"  Warning: {err[:300]}")
    else:
        print("  Extraction complete!")
    
    # 8. 确保 .env 存在并配置
    print("\nChecking .env configuration...")
    code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/.env && echo 'OK' || echo 'MISSING'")
    if "MISSING" in out:
        run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data cp .env.example .env")
        run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan key:generate")
    
    # 9. 安装依赖
    print("\nInstalling/updating Composer dependencies...")
    run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -20", timeout=180)
    
    # 10. 运行迁移
    print("\nRunning database migrations...")
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
    
    # 14. 测试访问
    print("\nTesting HTTP access...")
    code, out, err = run_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    print(f"  HTTP Status: {out}")
    
    # 15. 测试 API 路由
    print("\nTesting API routes...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -40")
    if out:
        print(f"  Routes:\n{out[:800]}")
    
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
