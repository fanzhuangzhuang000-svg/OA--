#!/usr/bin/env python3
"""
152服务器 - 完整部署API (修复 Concerns 缺失问题)

问题: 部署后缺少 Concerns 文件夹, 导致 PHP 崩溃
原因: tar 解压时只复制了部分目录
解决: 完整打包所有文件, 包括 app 下的所有子目录
"""
import paramiko
import tarfile
import os
import sys
import io
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
API_DIR = ROOT / "pc-api"

# 152服务器配置
HOST = "152.136.115.121"
USER = "ubuntu"
PASS = "Aa782997781."
REMOTE_API = "/var/www/oa-api"

def run_ssh(cmd):
    """执行SSH命令"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PASS, timeout=30)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    ssh.close()
    return out, err

def deploy_api():
    """部署API到152服务器"""
    print("=" * 60)
    print("  152服务器 - 完整部署API")
    print("=" * 60)

    # 1. 创建完整tar包 (包含所有文件)
    print("\n[1/6] 创建tar包...")
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
        # 添加整个 api 目录
        tar.add(API_DIR, arcname="pc-api")
    tar_buffer.seek(0)
    tar_data = tar_buffer.getvalue()
    print(f"  包大小: {len(tar_data)/1024/1024:.1f} MB")

    # 2. 上传tar包
    print("\n[2/6] 上传tar包...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PASS, timeout=60)

    sftp = ssh.open_sftp()
    sftp.putfo(io.BytesIO(tar_data), "/tmp/pc-api.tar.gz")
    sftp.close()
    print("  上传完成")

    # 3. 备份并替换
    print("\n[3/6] 备份并替换...")
    out, err = run_ssh(f"sudo mv {REMOTE_API} {REMOTE_API}-old-bak && sudo mkdir -p {REMOTE_API}")
    print("  ", out, err)

    # 4. 解压
    print("\n[4/6] 解压...")
    out, err = run_ssh(f"sudo tar -xzf /tmp/pc-api.tar.gz -C /var/www/ && sudo mv /var/www/pc-api {REMOTE_API}")
    print("  ", out, err)

    # 5. 设置权限
    print("\n[5/6] 设置权限...")
    out, err = run_ssh(f"sudo chown -R www-data:www-data {REMOTE_API} && sudo chmod -R 755 {REMOTE_API}")
    print("  权限设置完成")

    # 6. 重启PHP-FPM
    print("\n[6/6] 重启PHP-FPM...")
    out, err = run_ssh("sudo systemctl restart php8.3-fpm")
    print("  重启完成")

    # 验证
    print("\n[验证] 测试API...")
    out, err = run_ssh(f"cd {REMOTE_API} && sudo -u www-data php artisan route:list --path=api/login 2>&1 | head -5")
    print(f"  路由检查: {out[:300]}")

    print("\n✅ 部署完成!")
    return True

if __name__ == "__main__":
    try:
        deploy_api()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)