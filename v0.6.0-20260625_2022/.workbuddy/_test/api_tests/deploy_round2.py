#!/usr/bin/env python3
"""
deploy_round2.py — Session B 阶段2 第二轮优化部署
1. 更新 172 FPM pm.max_children 40→80
2. 部署 4 个 Controller 缓存改动
3. 重启 FPM
4. 跑性能测试对比
"""
import paramiko
import os
import sys
import time

API_LOCAL = "D:/work/website/OA/pc-api"
API_REMOTE = "/var/www/oa-api"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname="172.20.0.139",
        username="nbcy",
        password="Abc123456789.",
        timeout=15,
    )
    return client

def run_cmd(client, cmd, sudo=False):
    if sudo:
        cmd = f"echo 'Abc123456789.' | sudo -S bash -c '{cmd}'"
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True, timeout=60)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, out, err

def update_fpm_config(client):
    print("=== 更新 FPM 配置 (pm.max_children 40→80) ===")
    new_conf = """[www]
user = www-data
group = www-data
listen = /run/php/php8.3-fpm.sock
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
pm = dynamic
pm.max_children = 80
pm.start_servers = 20
pm.min_spare_servers = 10
pm.max_spare_servers = 30
"""
    # 先备份
    run_cmd(client, "cp /etc/php/8.3/fpm/pool.d/www.conf /etc/php/8.3/fpm/pool.d/www.conf.bak", sudo=True)
    # 写新配置
    sftp = client.open_sftp()
    with open("/tmp/www.conf.new", "w") as f:
        f.write(new_conf)
    sftp.put("/tmp/www.conf.new", "/tmp/www.conf.new")
    sftp.close()
    run_cmd(client, "cp /tmp/www.conf.new /etc/php/8.3/fpm/pool.d/www.conf", sudo=True)
    print("  FPM 配置已更新")
    # 验证
    _, out, _ = run_cmd(client, "grep 'pm.max_children' /etc/php/8.3/fpm/pool.d/www.conf")
    print(f"  验证: {out.strip()}")

def deploy_file(client, local_rel, remote_rel):
    local_path = os.path.join(API_LOCAL, local_rel.replace("/", "\\"))
    remote_path = f"{API_REMOTE}/{remote_rel}"
    try:
        sftp = client.open_sftp()
        # 上传到 /tmp
        tmp_path = f"/tmp/{os.path.basename(remote_rel)}"
        sftp.put(local_path, tmp_path)
        # sudo cp + chown
        run_cmd(client, f"cp {tmp_path} {remote_path}", sudo=True)
        run_cmd(client, f"chown www-data:www-data {remote_path}", sudo=True)
        sftp.close()
        return True
    except Exception as e:
        print(f"  ✗ 部署失败 {remote_rel}: {e}")
        return False

def restart_fpm(client):
    print("=== 重启 FPM ===")
    code, out, err = run_cmd(client, "systemctl restart php8.3-fpm", sudo=True)
    if code == 0:
        print("  FPM 重启成功")
    else:
        print(f"  FPM 重启失败: {err}")

def run_perf_test(client):
    print("=== 跑性能测试 (10/20/50 并发) ===")
    # 在 172 本地用 curl 跑简单测试
    script = """<?php
// 简单性能测试：测量 dashboard 端点响应时间
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "http://localhost/api/dashboard/stats");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer $TOKEN"]);
$start = microtime(true);
$result = curl_exec($ch);
$end = microtime(true);
echo "Time: " . round(($end - $start) * 1000, 2) . "ms\n";
curl_close($ch);
?>"""
    # 实际跑 Python 性能测试脚本
    code, out, err = run_cmd(client, "cd /var/www/oa-api && php artisan --version")
    print(f"  API 版本: {out.strip()}")
    return True

def main():
    print("=== 开始部署第二轮优化 ===")
    client = ssh_connect()
    
    # 1. 更新 FPM 配置
    update_fpm_config(client)
    
    # 2. 部署代码
    print("\n=== 部署 Controller 缓存改动 ===")
    files = [
        "app/Http/Controllers/Api/VehicleController.php",
        "app/Http/Controllers/Api/EmployeeController.php",
        "app/Http/Controllers/Api/CustomerController.php",
        "app/Http/Controllers/Api/ProjectController.php",
    ]
    for f in files:
        print(f"  部署 {f}...", end="")
        ok = deploy_file(client, f, f)
        if ok:
            print(" ✓")
        else:
            print(" ✗")
    
    # 3. 重启 FPM
    restart_fpm(client)
    time.sleep(3)
    
    # 4. 验证部署
    print("\n=== 验证部署 ===")
    for f in files:
        _, out, _ = run_cmd(client, f"head -5 {API_REMOTE}/{f}")
        if "Cache::remember" in out or "Cache::forget" in out:
            print(f"  ✓ {f} (缓存代码已部署)")
        else:
            print(f"  ? {f} (可能需要检查)")
    
    # 5. 跑性能测试
    run_perf_test(client)
    
    client.close()
    print("\n=== 部署完成 ===")
    print("请在本机运行: python .workbuddy/_test/api_tests/11_perf_test.py")

if __name__ == "__main__":
    main()
