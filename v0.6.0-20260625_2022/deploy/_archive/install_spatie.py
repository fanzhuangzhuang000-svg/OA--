#!/usr/bin/env python3
"""
安装 spatie/laravel-permission 和所有缺失依赖
"""
import paramiko

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=300):
    print(f">> {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out and len(out.strip()) > 0:
        print(f"   OUT: {out[:600]}")
    if err and code != 0:
        print(f"   ERR: {err[:600]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Installing spatie/laravel-permission")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 安装 spatie/laravel-permission
    print("[1] Installing spatie/laravel-permission...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer require spatie/laravel-permission --no-interaction 2>&1 | tail -20", timeout=180)
    
    # 2. 发布配置
    print("\n[2] Publishing spatie/laravel-permission config...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan vendor:publish --provider='Spatie\\Permission\\PermissionServiceProvider' 2>&1 | tail -10")
    
    # 3. 清除缓存
    print("\n[3] Clearing caches...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 4. 设置权限
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    
    # 5. 重启
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 6. 测试
    print("\n[4] Testing login...")
    run_cmd(ssh, f"sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print(f"\n   Login response: {out[:500]}")
    
    # 7. 查看日志
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -50")
    
    # 8. 查看路由数
    print("\n[5] Route count...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | grep -c '|' || echo '0'")
    print(f"   Total routes: {out.strip()}")
    
    ssh.close()
    print(f"\nDone! URL: http://{SSH_HOST}")

if __name__ == "__main__":
    main()
