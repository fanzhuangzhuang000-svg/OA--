#!/usr/bin/env python3
"""
上传并运行全面业务流转测试脚本到 172 服务器
"""
import paramiko
import sys
import time

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"
LOCAL_SCRIPT = r"D:\work\website\OA\.workbuddy\_test\api_tests\13_full_business_flow_test.py"
REMOTE_SCRIPT = "/tmp/13_full_business_flow_test.py"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"🔌 连接 {HOST}...")
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    print("  ✅ SSH 连接成功")
    return client

def upload(client, local, remote):
    print(f"📤 上传脚本: {local} → {remote}")
    sftp = client.open_sftp()
    sftp.put(local, remote)
    sftp.close()
    print("  ✅ 上传完成")

def run(client, cmd, timeout=120):
    print(f"🚀 执行: {cmd[:80]}")
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err

def main():
    client = ssh_connect()
    
    # 1. 检查 requests 库
    print("\n📦 检查 requests 库...")
    code, out, err = run(client, "python3 -c 'import requests; print(requests.__version__)'")
    if code != 0:
        print("  ⚠️ requests 未安装，正在安装...")
        code2, out2, err2 = run(client, "pip3 install requests -q", timeout=60)
        if code2 != 0:
            print(f"  ❌ 安装失败: {err2}")
            return
        print("  ✅ requests 安装完成")
    else:
        print(f"  ✅ requests 已安装: {out.strip()}")
    
    # 2. 上传测试脚本
    upload(client, LOCAL_SCRIPT, REMOTE_SCRIPT)
    
    # 3. 运行测试
    print("\n" + "="*60)
    print("🚀 运行全面业务流转测试...")
    print("="*60)
    code, out, err = run(client, f"cd /tmp && python3 {REMOTE_SCRIPT}", timeout=120)
    
    print("\n" + "="*60)
    print("📋 测试结果输出:")
    print("="*60)
    print(out)
    if err.strip():
        print("\n⚠️ 错误输出:")
        print(err)
    
    print(f"\n退出码: {code}")
    
    # 4. 下载测试结果（如果有报告文件）
    print("\n📥 检查测试报告文件...")
    code2, out2, err2 = run(client, f"ls -la /tmp/phase3_*_report.md 2>/dev/null || echo 'NO_REPORT'")
    if "NO_REPORT" not in out2:
        print("  发现报告文件:")
        print(out2)
    
    client.close()
    print("\n✅ 完成")
    return code

if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
