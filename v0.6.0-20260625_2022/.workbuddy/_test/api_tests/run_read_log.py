#!/usr/bin/env python3
"""上传并执行 read_laravel_log.py 到 172"""
import paramiko
from pathlib import Path

SSH_HOST = "172.20.0.139"
SSH_USER = "nbcy"
SSH_PASS = "admin123"
SSH_PORT = 22

LOCAL_SCRIPT = r"D:\work\website\OA\.workbuddy\_test\api_tests\read_laravel_log.py"
REMOTE_SCRIPT = "/tmp/read_laravel_log.py"

def main():
    print(f"🔗 连接 {SSH_HOST} ...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    print("✅ 已连接")

    # 上传脚本
    print(f"📤 上传脚本 ...")
    sftp = client.open_sftp()
    sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
    sftp.close()
    print(f"   ✅ 已上传到 {REMOTE_SCRIPT}")

    # 执行
    print(f"\n🚀 执行脚本（读取 laravel.log）...\n")
    print("=" * 60)
    
    stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_SCRIPT}", timeout=120)
    for line in stdout:
        print(line.rstrip())
    err_out = stderr.read().decode('utf-8', errors='replace')
    if err_out:
        print("STDERR:", err_out[:500])

    print("=" * 60)
    print("✅ 完成")
    client.close()

if __name__ == "__main__":
    main()
