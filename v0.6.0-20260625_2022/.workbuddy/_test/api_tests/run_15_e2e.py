#!/usr/bin/env python3
"""上传 15_e2e_full_flow.py 到 172 并执行"""
import paramiko, sys

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

LOCAL  = r"D:\work\website\OA\.workbuddy\_test\api_tests\15_e2e_full_flow_v3.py"
REMOTE = "/tmp/15_e2e_full_flow_v3.py"

print(f"🔗 连接 {HOST} ...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

print(f"📤 上传脚本 ...")
sftp.put(LOCAL, REMOTE)
print(f"   ✅ 已上传到 {REMOTE}")
sftp.close()

print(f"\n🚀 执行端到端测试（可能需要 1~2 分钟）...\n")
stdin, stdout, stderr = client.exec_command(
    f"python3 {REMOTE} 2>&1", timeout=180
)

# 实时输出
import select
while True:
    r = select.select([stdout.channel], [], [], 2.0)[0]
    if r:
        chunk = stdout.channel.recv(4096).decode("utf-8", errors="replace")
        if not chunk:
            break
        print(chunk, end="")
    if stdout.channel.exit_status_ready():
        break

# 读剩余
remainder = stdout.read().decode("utf-8", errors="replace")
if remainder:
    print(remainder, end="")

err = stderr.read().decode("utf-8", errors="replace").strip()
if err:
    print(f"\n⚠️  stderr:\n{err[:500]}")

code = stdout.channel.recv_exit_status()
print(f"\n{'='*60}")
print(f"退出码: {code}  {'✅ 全部通过' if code == 0 else '❌ 有失败'}")
print('='*60)
client.close()
sys.exit(code)
