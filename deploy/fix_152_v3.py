#!/usr/bin/env python3
"""
152服务器 - 正确部署API (修复路径问题)

问题: tar打包后解压路径错误，导致文件放错位置
原因: pc-api作为根目录打包，需要解压到/var/www/
解决: 解压后移动文件到正确位置
"""
import tarfile
import os
import sys
import io
import shutil
from pathlib import Path
from deploy_credentials import get_ssh_credentials_152, connect_ssh

ROOT = Path(__file__).parent.parent.resolve()
API_DIR = ROOT / "pc-api"

REMOTE_API = "/var/www/oa-api"

def run_ssh(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

def deploy_api():
    print("=" * 60)
    print("  152服务器 - 正确部署API (修复路径)")
    print("=" * 60)

    creds = get_ssh_credentials_152()

    # 1. 打包
    print("\n[1/5] 打包...")
    shutil.make_archive('/tmp/pc-api', 'gztar', API_DIR)
    print(f"  完成")

    # 2. 上传
    print("\n[2/5] 上传...")
    ssh = connect_ssh(creds)
    sftp = ssh.open_sftp()
    sftp.put('/tmp/pc-api.tar.gz', '/tmp/pc-api.tar.gz')
    sftp.close()
    print("  上传完成")

    # 3. 解压到临时目录
    print("\n[3/5] 解压...")
    out, err = run_ssh(ssh, "sudo mkdir -p /tmp/api-extract && sudo tar -xzf /tmp/pc-api.tar.gz -C /tmp/api-extract/")
    print("  解压完成")

    # 4. 移动到正确位置
    print("\n[4/5] 移动文件...")
    out, err = run_ssh(ssh, f"sudo rm -rf {REMOTE_API}-old && sudo mv {REMOTE_API} {REMOTE_API}-old && sudo mv /tmp/api-extract/pc-api {REMOTE_API}")
    print("  移动完成")

    # 5. 权限和重启
    print("\n[5/5] 权限+重启...")
    out, err = run_ssh(ssh, f"sudo chown -R www-data:www-data {REMOTE_API} && sudo chmod -R 755 {REMOTE_API} && sudo systemctl restart php8.3-fpm")
    print("  完成")

    # 验证
    print("\n[验证] 测试...")
    out, err = run_ssh(ssh, f"cd {REMOTE_API} && sudo -u www-data php artisan route:list --path=api/login 2>&1 | head -3")
    print(f"  结果: {out}")

    ssh.close()
    print("\n✅ 部署完成!")
    return True

if __name__ == "__main__":
    try:
        deploy_api()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
