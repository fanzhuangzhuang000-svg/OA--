#!/usr/bin/env python3
"""
上传业务代码到远程服务器并运行迁移
"""
import paramiko
import os
import tarfile
from scp import SCPClient

# SSH 配置
SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def create_tarball():
    """打包业务代码"""
    print("Packing business code...")
    tar_path = "D:/work/website/OA/deploy/oa_business.tar.gz"
    
    # 要打包的目录
    dirs_to_pack = ['app', 'bootstrap', 'config', 'database', 'public', 'resources', 'routes', 'storage']
    # 要打包的文件
    files_to_pack = ['composer.json', '.env.example', '.gitignore']
    
    with tarfile.open(tar_path, "w:gz") as tar:
        base_dir = "D:/work/website/OA/pc-api"
        for d in dirs_to_pack:
            path = os.path.join(base_dir, d)
            if os.path.exists(path):
                print(f"  Adding directory: {d}")
                tar.add(path, arcname=d)
        for f in files_to_pack:
            path = os.path.join(base_dir, f)
            if os.path.exists(path):
                print(f"  Adding file: {f}")
                tar.add(path, arcname=f)
    
    print(f"Package created: {tar_path}")
    return tar_path

def run_command(ssh, cmd, timeout=300):
    """执行远程命令"""
    print(f"Executing: {cmd[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out:
        print(f"  Output: {out[:500]}")
    if err and code != 0:
        print(f"  Error: {err[:500]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Uploading business code to server")
    print("=" * 60)
    
    # 1. 打包
    tar_path = create_tarball()
    
    # 2. 连接 SSH
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 3. 上传压缩包
    print("\nUploading package...")
    remote_tar = "/tmp/oa_business.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    # 4. 备份当前代码
    print("\nBacking up current code...")
    run_command(ssh, f"cd {REMOTE_DIR} && tar czf /tmp/oa_api_backup_$(date +%Y%m%d_%H%M%S).tar.gz . 2>/dev/null || true")
    
    # 5. 解压业务代码
    print("\nExtracting business code...")
    # 先清空一些目录（保留 vendor 和 .env）
    run_command(ssh, f"cd {REMOTE_DIR} && rm -rf app/* bootstrap/cache/* config/* database/* public/* resources/* routes/* storage/*")
    # 解压
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && tar xzf {remote_tar} --exclude='vendor' --exclude='.env'")
    if code != 0:
        print(f"Warning during extraction: {err}")
    else:
        print("Extraction complete!")
    
    # 6. 确保 .env 存在
    print("\nChecking .env file...")
    code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/.env && echo 'EXISTS' || echo 'MISSING'")
    if "MISSING" in out:
        print("  .env not found, creating from .env.example...")
        run_command(ssh, f"cd {REMOTE_DIR} && cp .env.example .env")
        # 生成 APP_KEY
        run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan key:generate")
    
    # 7. 安装/更新依赖
    print("\nUpdating Composer dependencies...")
    run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -20")
    
    # 8. 运行数据库迁移
    print("\nRunning database migrations...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration output: {out[:500]}")
    
    # 9. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed output: {out[:500]}")
    
    # 10. 设置权限
    print("\nSetting file permissions...")
    run_command(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_command(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 11. 重启 PHP-FPM 和 Nginx
    print("\nRestarting services...")
    run_command(ssh, "sudo systemctl restart php8.3-fpm")
    run_command(ssh, "sudo systemctl restart nginx")
    
    # 12. 测试
    print("\nTesting access...")
    code, out, err = run_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    print(f"  HTTP Status: {out}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Deployment complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nDefault credentials (if seed ran successfully):")
    print("  Username: admin")
    print("  Password: password")
    print("\nNotes:")
    print("  1. Check storage/logs/laravel.log if there are errors")
    print(f"  2. Frontend should use API URL: http://{SSH_HOST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
