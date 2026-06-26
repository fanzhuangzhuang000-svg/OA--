#!/usr/bin/env python3
"""
修复152服务器 - 重新部署API

问题: 部署后PHP崩溃 (Target class [request] does not exist)
原因: sftp复制可能损坏文件
解决: 用tar打包传输，避免逐文件复制损坏
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
    print("  152服务器 - 重新部署API")
    print("=" * 60)

    # 1. 创建tar包
    print("\n[1/5] 创建tar包...")
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
        tar.add(API_DIR, arcname="pc-api")
    tar_buffer.seek(0)
    tar_data = tar_buffer.getvalue()
    print(f"  包大小: {len(tar_data)/1024/1024:.1f} MB")

    # 2. 上传tar包
    print("\n[2/5] 上传tar包...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PASS, timeout=60)

    sftp = ssh.open_sftp()
    sftp.putfo(io.BytesIO(tar_data), "/tmp/pc-api.tar.gz")
    sftp.close()
    print("  上传完成")

    # 3. 解压到目标目录
    print("\n[3/5] 解压到目标目录...")
    cmd = f"sudo rm -rf {REMOTE_API} && sudo mkdir -p {REMOTE_API} && sudo tar -xzf /tmp/pc-api.tar.gz -C /var/www/ && sudo mv /var/www/pc-api {REMOTE_API}"
    out, err = run_ssh(cmd)
    if err:
        print(f"  错误: {err}")
        return False
    print("  解压完成")

    # 4. 设置权限
    print("\n[4/5] 设置权限...")
    cmd = f"sudo chown -R www-data:www-data {REMOTE_API} && sudo chmod -R 755 {REMOTE_API}"
    out, err = run_ssh(cmd)
    print("  权限设置完成")

    # 5. 重启PHP-FPM
    print("\n[5/5] 重启PHP-FPM...")
    cmd = "sudo systemctl restart php8.3-fpm"
    out, err = run_ssh(cmd)
    print("  PHP-FPM重启完成")

    # 验证
    print("\n[验证] 测试API...")
    out, err = run_ssh(f"curl -s http://localhost:3001/api/employees -H 'Authorization: Bearer 418|kIDEl3MvD8BbCWH64GCfQfo6c2zSeWD4cBkgUJ5v422a9889' | head -c 200")
    print(f"  结果: {out[:200] if out else err[:200]}")

    print("\n✅ 部署完成!")
    return True

if __name__ == "__main__":
    try:
        deploy_api()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)