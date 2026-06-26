#!/usr/bin/env python3
"""上传并运行 14_full_flow_v2.py 到 172"""
import paramiko
import sys

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"
LOCAL = r"D:\work\website\OA\.workbuddy\_test\api_tests\14_full_flow_v5.py"
REMOTE = "/tmp/14_full_flow_v5.py"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    print("✅ SSH 连接成功")
    return client

def main():
    client = ssh_connect()

    # 上传
    print(f"📤 上传测试脚本...")
    sftp = client.open_sftp()
    sftp.put(LOCAL, REMOTE)
    sftp.close()
    print("  ✅ 上传完成")

    # 运行（阻塞读取完整输出）
    print("\n" + "="*60)
    print("🚀 运行全面业务流转测试 v2...")
    print("="*60)
    stdin, stdout, stderr = client.exec_command(
        f"cd /tmp && python3 {REMOTE}",
        get_pty=True, timeout=180
    )
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()

    print(out)
    if err.strip():
        print("\n⚠️ stderr:")
        print(err)

    print(f"\n退出码: {code}")
    client.close()
    return code

if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
