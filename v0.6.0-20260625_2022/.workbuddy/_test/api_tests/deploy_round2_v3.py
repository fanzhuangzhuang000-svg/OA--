#!/usr/bin/env python3
"""
deploy_round2_v3.py — 第二轮优化部署（正确版本）
用法：python deploy_round2_v3.py
"""
import paramiko
import os
import tempfile
import time

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

def sftp_put(client, local_path, remote_path):
    """上传文件到远程（先 /tmp，再 sudo cp）"""
    sftp = client.open_sftp()
    tmp_path = f"/tmp/{os.path.basename(local_path)}"
    sftp.put(local_path, tmp_path)
    sftp.close()
    run(client, f"cp {tmp_path} {remote_path} && chown www-data:www-data {remote_path} && rm -f {tmp_path}", sudo=True)

def update_fpm_config(client):
    print("=== 更新 FPM 配置 ===")
    code, out, err = run(client, "cat /etc/php/8.3/fpm/pool.d/www.conf")
    if code != 0:
        print(f"  读取失败: {err}")
        return False
    lines = out.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("pm.max_children"):
            new_lines.append("pm.max_children = 80")
        elif line.startswith("pm.start_servers"):
            new_lines.append("pm.start_servers = 20")
        elif line.startswith("pm.min_spare_servers"):
            new_lines.append("pm.min_spare_servers = 10")
        elif line.startswith("pm.max_spare_servers"):
            new_lines.append("pm.max_spare_servers = 30")
        else:
            new_lines.append(line)
    new_conf = "\n".join(new_lines)
    # 写本地临时文件，然后上传
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".conf") as f:
        f.write(new_conf)
        tmp_local = f.name
    sftp = client.open_sftp()
    sftp.put(tmp_local, "/tmp/www.conf.new")
    sftp.close()
    os.unlink(tmp_local)
    run(client, "cp /tmp/www.conf.new /etc/php/8.3/fpm/pool.d/www.conf && rm -f /tmp/www.conf.new", sudo=True)
    # 验证
    _, out, _ = run(client, "grep -E 'pm\.(max_children|start_servers|min_spare|max_spare)' /etc/php/8.3/fpm/pool.d/www.conf")
    print(f"  验证:\n{out.strip()}")
    return True

def deploy_controllers(client):
    print("\n=== 部署 Controller 文件 ===")
    files = [
        r"app\Http\Controllers\Api\VehicleController.php",
        r"app\Http\Controllers\Api\EmployeeController.php",
        r"app\Http\Controllers\Api\CustomerController.php",
        r"app\Http\Controllers\Api\ProjectController.php",
    ]
    for rel in files:
        local = os.path.join(API_LOCAL, rel)
        remote = f"{API_REMOTE}/{rel}".replace("\\", "/")
        print(f"  {os.path.basename(rel)}...", end="")
        try:
            sftp_put(client, local, remote)
            print(" ✓")
        except Exception as e:
            print(f" ✗ {e}")

def restart_fpm(client):
    print("\n=== 重启 FPM ===")
    code, _, err = run(client, "systemctl restart php8.3-fpm", sudo=True)
    if code == 0:
        print("  FPM 重启成功")
        return True
    else:
        print(f"  FPM 重启失败: {err}")
        return False

def verify(client):
    print("\n=== 验证部署 ===")
    files = [
        "app/Http/Controllers/Api/VehicleController.php",
        "app/Http/Controllers/Api/EmployeeController.php",
        "app/Http/Controllers/Api/CustomerController.php",
        "app/Http/Controllers/Api/ProjectController.php",
    ]
    for rel in files:
        remote = f"{API_REMOTE}/{rel}"
        code, out, _ = run(client, f"grep -c 'Cache::' {remote}")
        if code == 0 and int(out.strip()) > 0:
            print(f"  ✓ {os.path.basename(rel)}")
        else:
            print(f"  ? {os.path.basename(rel)}")

def main():
    print("=== 第二轮优化部署开始 ===")
    client = ssh_connect()
    try:
        update_fpm_config(client)
        deploy_controllers(client)
        restart_fpm(client)
        time.sleep(3)
        verify(client)
        print("\n=== 部署完成，请运行性能测试 ===")
        print(r"  本地运行: python D:\work\website\OA\.workbuddy\_test\api_tests\11_perf_test.py")
    finally:
        client.close()

if __name__ == "__main__":
    main()
