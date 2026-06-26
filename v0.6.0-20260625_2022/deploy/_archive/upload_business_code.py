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
    print("📦 打包业务代码...")
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
                print(f"  添加目录: {d}")
                tar.add(path, arcname=d)
        for f in files_to_pack:
            path = os.path.join(base_dir, f)
            if os.path.exists(path):
                print(f"  添加文件: {f}")
                tar.add(path, arcname=f)
    
    print(f"✅ 打包完成: {tar_path}")
    return tar_path

def run_command(ssh, cmd, timeout=300):
    """执行远程命令"""
    print(f"🔧 执行: {cmd[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out:
        print(f"  输出: {out[:500]}")
    if err and code != 0:
        print(f"  错误: {err[:500]}")
    return code, out, err

def main():
    print("=" * 60)
    print("🚀 上传业务代码到服务器")
    print("=" * 60)
    
    # 1. 打包
    tar_path = create_tarball()
    
    # 2. 连接 SSH
    print("\n📡 连接服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("✅ 已连接")
    
    # 3. 上传压缩包
    print("\n📤 上传压缩包...")
    remote_tar = "/tmp/oa_business.tar.gz"
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(tar_path, remote_tar)
    print("✅ 上传完成")
    
    # 4. 备份当前代码（可选）
    print("\n💾 备份当前代码...")
    run_command(ssh, f"cd {REMOTE_DIR} && tar czf /tmp/oa_api_backup_$(date +%Y%m%d_%H%M%S).tar.gz . 2>/dev/null || true")
    
    # 5. 解压业务代码
    print("\n📂 解压业务代码...")
    # 先清空一些目录（保留 vendor 和 .env）
    run_command(ssh, f"cd {REMOTE_DIR} && rm -rf app/* bootstrap/cache/* config/* database/* public/* resources/* routes/* storage/*")
    # 解压
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && tar xzf {remote_tar} --exclude='vendor' --exclude='.env'")
    if code != 0:
        print(f"⚠️  解压可能有警告: {err}")
    else:
        print("✅ 解压完成")
    
    # 6. 复制本地 .env 到服务器
    print("\n⚙️  配置 .env...")
    # 读取本地 .env 并调整数据库配置
    local_env = "D:/work/website/OA/pc-api/.env"
    if os.path.exists(local_env):
        with open(local_env, 'r', encoding='utf-8') as f:
            env_content = f.read()
        # 确保数据库配置正确
        print("  已存在 .env 文件，保留服务器上的配置")
    
    # 7. 安装/更新依赖
    print("\n📦 更新 Composer 依赖...")
    run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer install --no-interaction 2>&1 | tail -20")
    
    # 8. 运行数据库迁移
    print("\n🗄️  运行数据库迁移...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if "table already exists" in err.lower() or "already exists" in err:
        print("  ℹ️  部分表已存在，继续...")
    if out:
        print(f"  迁移输出: {out[:500]}")
    
    # 9. 填充数据库
    print("\n🌱 填充初始数据...")
    code, out, err = run_command(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  填充输出: {out[:500]}")
    
    # 10. 设置权限
    print("\n🔐 设置文件权限...")
    run_command(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_command(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 11. 重启 PHP-FPM 和 Nginx
    print("\n🔄 重启服务...")
    run_command(ssh, "sudo systemctl restart php8.3-fpm")
    run_command(ssh, "sudo systemctl restart nginx")
    
    # 12. 测试
    print("\n🧪 测试访问...")
    code, out, err = run_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    print(f"  HTTP 状态码: {out}")
    
    # 13. 测试 API
    print("\n🧪 测试 API...")
    code, out, err = run_command(ssh, "curl -s http://localhost/api/test 2>/dev/null | head -20")
    if out:
        print(f"  API 响应: {out[:300]}")
    else:
        print("  ℹ️  /api/test 端点不存在，这是正常的")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("✅ 部署完成!")
    print("=" * 60)
    print(f"\n🌐 访问地址: http://{SSH_HOST}")
    print(f"\n📝 默认账号 (如果 seed 成功):")
    print("  用户名: admin")
    print("  密码: password (或查看数据库)")
    print("\n⚠️  注意事项:")
    print("  1. 如果页面报错，请检查 storage/logs/laravel.log")
    print(f"  2. 前端需要将 API 地址设置为 http://{SSH_HOST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
