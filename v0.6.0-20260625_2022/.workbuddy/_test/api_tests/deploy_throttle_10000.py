#!/usr/bin/env python3
"""deploy_throttle_10000.py — 临时部署 throttle=10000 到 172"""
import paramiko, os

API_LOCAL = r"D:\work\website\OA\pc-api"
API_REMOTE = "/var/www/oa-api"
HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
    return client

def run(client, cmd, sudo=False, timeout=30):
    if sudo:
        cmd = f"echo '{PASS}' | sudo -S bash -c '{cmd}'"
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    return code, out, err

def sftp_put(client, local, remote):
    sftp = client.open_sftp()
    tmp = f"/tmp/{os.path.basename(local)}"
    sftp.put(local, tmp)
    sftp.close()
    run(client, f"cp {tmp} {remote} && chown www-data:www-data {remote} && rm -f {tmp}", sudo=True)

def main():
    client = ssh_connect()
    print("=== 部署 AppServiceProvider.php (throttle=10000) ===")
    local = os.path.join(API_LOCAL, "app/Providers/AppServiceProvider.php")
    remote = f"{API_REMOTE}/app/Providers/AppServiceProvider.php"
    sftp_put(client, local, remote)
    print("  部署完成，重启 FPM...")
    code, out, err = run(client, "systemctl restart php8.3-fpm", sudo=True)
    if code == 0:
        print("  FPM 重启成功")
    else:
        print(f"  FPM 重启失败: {err}")
    client.close()

if __name__ == "__main__":
    main()
