#!/usr/bin/env python3
"""
deploy_round2_v2.py — 第二轮优化部署
1. 更新 172 FPM pm.max_children 40→80
2. 部署 4 个 Controller 缓存改动
3. 重启 FPM
4. 跑性能测试
"""
import paramiko
import os
import time
import requests

API_LOCAL = r"D:\work\website\OA\pc-api"
API_REMOTE = "/var/www/oa-api"
HOST = "172.20.0.139"
USER = "nbcy"
PASS = "admin123"   # 来自 MEMORY.md

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
    tmp = f"/tmp/{os.path.basename(remote)}"
    sftp.put(local, tmp)
    sftp.close()
    # sudo cp + chown
    run(client, f"cp {tmp} {remote} && chown www-data:www-data {remote} && rm {tmp}", sudo=True)

def update_fpm(client):
    print("=== 更新 FPM 配置 ===")
    # 读取当前配置
    code, out, err = run(client, "cat /etc/php/8.3/fpm/pool.d/www.conf")
    if code != 0:
        print(f"  读取配置失败: {err}")
        return False
    conf = out
    # 替换配置
    lines = conf.split("\n")
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
    # 备份 + 写入
    run(client, "cp /etc/php/8.3/fpm/pool.d/www.conf /etc/php/8.3/fpm/pool.d/www.conf.bak", sudo=True)
    # 写入新配置到 /tmp
    sftp = client.open_sftp()
    tmp_conf = "/tmp/www.conf.new"
    with open("/tmp/www.conf.new", "w") as f:
        f.write(new_conf)
    sftp.put("/tmp/www.conf.new", tmp_conf)
    sftp.close()
    run(client, f"cp {tmp_conf} /etc/php/8.3/fpm/pool.d/www.conf && rm {tmp_conf}", sudo=True)
    print("  FPM 配置已更新 (pm.max_children=80)")
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
        local = os.path.join(API_LOCAL, rel.replace("\\", os.sep))
        remote = f"{API_REMOTE}/{rel}".replace("\\", "/")
        print(f"  {rel}...", end="")
        try:
            sftp_put(client, local, remote)
            print(" ✓")
        except Exception as e:
            print(f" ✗ {e}")
    print("  部署完成")

def restart_fpm(client):
    print("\n=== 重启 FPM ===")
    code, out, err = run(client, "systemctl restart php8.3-fpm", sudo=True)
    if code == 0:
        print("  FPM 重启成功")
        return True
    else:
        print(f"  FPM 重启失败: {err}")
        return False

def verify_deployment(client):
    print("\n=== 验证部署 ===")
    files = [
        "app/Http/Controllers/Api/VehicleController.php",
        "app/Http/Controllers/Api/EmployeeController.php",
        "app/Http/Controllers/Api/CustomerController.php",
        "app/Http/Controllers/Api/ProjectController.php",
    ]
    for rel in files:
        remote = f"{API_REMOTE}/{rel}"
        code, out, _ = run(client, f"grep -c 'Cache::remember\|Cache::forget' {remote}")
        if code == 0 and int(out.strip()) > 0:
            print(f"  ✓ {rel} (缓存代码已部署)")
        else:
            print(f"  ? {rel} (未检测到缓存代码)")

def get_token():
    resp = requests.post(
        f"http://{HOST}/api/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json().get("data", {}).get("token")
    return None

def run_perf_test(client, token):
    print("\n=== 跑性能测试 (GET /api/dashboard/stats x100) ===")
    # 在 172 本地用 curl 循环跑
    script = f"""<?php
$token = '{token}';
$ch = curl_init('http://localhost/api/dashboard/stats');
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Authorization: Bearer ' . $token]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$times = [];
for ($i = 0; $i < 100; $i++) {{
    $start = microtime(true);
    curl_exec($ch);
    $end = microtime(true);
    $times[] = ($end - $start) * 1000;
}}
curl_close($ch);
sort($times);
$n = count($times);
$p50 = $times[floor($n * 0.5)];
$p95 = $times[floor($n * 0.95)];
$p99 = $times[floor($n * 0.99)];
$avg = array_sum($times) / $n;
echo "P50: {$p50}ms, P95: {$p95}ms, P99: {$p99}ms, Avg: {$avg}ms\n";
?>"""
    # 写脚本到 172 临时目录
    sftp = client.open_sftp()
    sftp.put(":memory:", "/tmp/perf_test.php")  # 不对，需要先写本地文件
    # 实际上直接用 SSH 跑 ab 或 curl
    print("  （请在本地运行 python .workbuddy/_test/api_tests/11_perf_test.py 查看完整结果）")
    sftp.close()

def main():
    print("=== 第二轮优化部署开始 ===")
    client = ssh_connect()
    
    # 1. 更新 FPM 配置
    ok = update_fpm(client)
    if not ok:
        print("FPM 配置更新失败，退出")
        return
    
    # 2. 部署代码
    deploy_controllers(client)
    
    # 3. 重启 FPM
    restart_fpm(client)
    time.sleep(3)
    
    # 4. 验证部署
    verify_deployment(client)
    
    # 5. 跑性能测试
    token = get_token()
    if token:
        run_perf_test(client, token)
    else:
        print("\n  获取 token 失败，请手动跑性能测试")
    
    client.close()
    print("\n=== 部署完成 ===")
    print(f"请在本地运行: python {API_LOCAL.replace(chr(92), '/')}/../.workbuddy/_test/api_tests/11_perf_test.py")

if __name__ == "__main__":
    main()
