#!/usr/bin/env python3
"""获取原始 route:list 输出并保存"""
import paramiko

HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    return client

def run(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err

def main():
    client = ssh_connect()
    
    print("📋 获取完整 route:list 输出...")
    code, out, err = run(client, "cd /var/www/oa-api && php artisan route:list 2>&1 | head -100", timeout=30)
    
    print(f"\n退出码: {code}")
    if err.strip():
        print(f"stderr:\n{err[:500]}")
    
    print(f"\nstdout (前 3000 字符):\n{out[:3000]}")
    
    # 保存完整输出
    with open("D:/work/website/OA/.workbuddy/_test/api_tests/route_list_raw.txt", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"\n✅ 完整输出已保存到: route_list_raw.txt")
    
    client.close()

if __name__ == "__main__":
    main()
