#!/usr/bin/env python3
"""
修复权限问题并正确部署业务代码
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
    """打包业务代码（不包含 vendor 和 .env）"""
    print("Packing business code (without vendor and .env)...")
    tar_path = "D:/work/website/OA/deploy/oa_business_v2.tar.gz"
    
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

def run_command(ssh, cmd, timeout=300, use_sudo=False):
    """执行远程命令"""
    if use_sudo:
        # 如果是需要 sudo 的命令，包装一下
        cmd = f"sudo bash -c '{cmd.replace(chr(39), chr(39)+chr(92)+chr(92)+chr(39)+chr(39))}'"
    
    print(f"Executing: {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out and len(out.strip()) > 0:
        print(f"  Output: {out[:300]}")
    if err and code != 0:
        print(f"  Error: {err[:300]}")
    return code, out, err

def run_sudo_command(ssh, cmd, timeout=300):
    """执行需要 sudo 的命令（正确处理）"""
    print(f"Executing (sudo): {cmd[:100]}...")
    # 使用 sudo bash -c 来执行复杂命令
    escaped_cmd = cmd.replace("'", "'\"'\"'")
    full_cmd = f"sudo bash -c '{escaped_cmd}'"
    stdin, stdout, stderr = ssh.exec_command(full_cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out and len(out.strip()) > 0:
        print(f"  Output: {out[:300]}")
    if err and code != 0:
        print(f"  Error: {err[:300]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Fixing permissions and deploying business code")
    print("=" * 60)
    
    # 1. 打包
    tar_path = create_tarball()
    
    # 2. 连接 SSH
    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 3. 临时更改目录所有者为 nbcy（这样才能上传和解压）
    print("\nChanging ownership to nbcy for upload...")
    run_sudo_command(ssh, f"chown -R nbcy:nbcy {REMOTE_DIR}")
    
    # 4. 上传压缩包
    print("\nUploading package...")
    remote_tar = "/tmp/oa_business_v2.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("Upload complete!")
    
    # 5. 清空目标目录中的旧代码（保留 vendor、.env、node_modules）
    print("\nCleaning old code...")
    # 使用 find 删除，但保留特定文件和目录
    cleanup_cmd = f"""
    cd {REMOTE_DIR} && 
    find . -mindepth 1 -maxdepth 1 ! -name 'vendor' ! -name '.env' ! -name 'node_modules' ! -name '.git' ! -name 'storage' -exec rm -rf {{}} +
    """
    run_command(ssh, cleanup_cmd)
    
    # 创建 storage 目录（如果不存在）
    run_command(ssh, f"mkdir -p {REMOTE_DIR}/storage/logs")
    run_command(ssh, f"mkdir -p {REMOTE_DIR}/storage/framework/cache")
    run_command(ssh, f"mkdir -p {REMOTE_DIR}/storage/framework/sessions")
    run_command(ssh, f"mkdir -p {REMOTE_DIR}/storage/framework/views")
    run_command(ssh, f"mkdir -p {REMOTE_DIR}/storage/app/public")
    
    # 6. 解压新代码
    print("\nExtracting new code...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && tar xzf {remote_tar} 2>&1")
    if code != 0:
        print(f"Warning during extraction: {err[:500]}")
    else:
        print("Extraction complete!")
    
    # 7. 确保 .env 存在
    print("\nChecking .env file...")
    code, out, err = run_command(ssh, f"test -f {REMOTE_DIR}/.env && echo 'EXISTS' || echo 'MISSING'")
    if "MISSING" in out:
        print("  .env not found, creating from .env.example...")
        run_command(ssh, f"cd {REMOTE_DIR} && cp .env.example .env")
        # 生成 APP_KEY
        run_command(ssh, f"cd {REMOTE_DIR} && php artisan key:generate 2>&1 | head -5")
    
    # 8. 改回所有权给 www-data
    print("\nChanging ownership back to www-data...")
    run_sudo_command(ssh, f"chown -R www-data:www-data {REMOTE_DIR}")
    run_sudo_command(ssh, f"chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 9. 安装/更新依赖（作为 www-data 用户）
    print("\nUpdating Composer dependencies...")
    run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -10")
    
    # 10. 运行数据库迁移
    print("\nRunning database migrations...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration output: {out[:500]}")
    
    # 11. 填充数据库
    print("\nSeeding database...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed output: {out[:500]}")
    
    # 12. 重启服务
    print("\nRestarting services...")
    run_sudo_command(ssh, "systemctl restart php8.3-fpm")
    run_sudo_command(ssh, "systemctl restart nginx")
    
    # 13. 测试
    print("\nTesting access...")
    code, out, err = run_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    print(f"  HTTP Status: {out}")
    
    # 14. 检查路由是否生效
    print("\nChecking routes...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -30")
    if out:
        print(f"  Routes: {out[:500]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Deployment complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nDefault credentials (if seed ran successfully):")
    print("  Username: admin")
    print("  Password: password (or check database)")
    print("\nNext steps:")
    print("  1. Update frontend .env to point to http://172.20.0.139")
    print("  2. Test login functionality")
    print("=" * 60)

if __name__ == "__main__":
    main()
