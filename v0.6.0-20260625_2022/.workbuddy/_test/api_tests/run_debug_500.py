#!/usr/bin/env python3
"""上传 debug_500.py 到 172 并执行"""
import paramiko, sys

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

LOCAL  = r"D:\work\website\OA\.workbuddy\_test\api_tests\debug_500.py"
REMOTE = "/tmp/debug_500.py"

print(f"🔗 连接 {HOST} ...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

print(f"📤 上传脚本 ...")
sftp.put(LOCAL, REMOTE)
print(f"   ✅ 已上传到 {REMOTE}")
sftp.close()

print(f"\n🚀 执行 debug_500.py ...\n")
stdin, stdout, stderr = client.exec_command(
    f"python3 {REMOTE} 2>&1", timeout=60
)

# 实时输出
import select
while True:
    r = select.select([stdout.channel], [], [], 3.0)[0]
    if r:
        chunk = stdout.channel.recv(4096).decode("utf-8", errors="replace")
        if not chunk:
            break
        print(chunk, end="")
    if stdout.channel.exit_status_ready():
        break

remainder = stdout.read().decode("utf-8", errors="replace")
if remainder:
    print(remainder, end="")

err = stderr.read().decode("utf-8", errors="replace").strip()
if err:
    print(f"\n⚠️  stderr:\n{err[:500]}")

code = stdout.channel.recv_exit_status()
print(f"\n{'='*60}")
print(f"退出码: {code}")
print('='*60)
client.close()
sys.exit(code)
