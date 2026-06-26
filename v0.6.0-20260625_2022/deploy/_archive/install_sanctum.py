#!/usr/bin/env python3
"""
安装 Laravel Sanctum 并测试登录
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
    print("Installing Laravel Sanctum")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 安装 Sanctum
    print("=" * 60)
    print("[1] Installing laravel/sanctum...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer require laravel/sanctum --no-interaction 2>&1 | tail -20", timeout=180)
    
    # 2. 发布 Sanctum 配置
    print("\n" + "=" * 60)
    print("[2] Publishing Sanctum config...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan sanctum:install 2>&1 | tail -10")
    
    # 3. 清除缓存
    print("\n" + "=" * 60)
    print("[3] Clearing caches...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 4. 设置权限
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    
    # 5. 重启服务
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 6. 清空日志并测试
    print("\n" + "=" * 60)
    print("[4] Testing login...")
    print("=" * 60)
    run_cmd(ssh, f"sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print(f"\n   Login response: {out[:500]}")
    
    # 7. 查看日志（如果有错误）
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -50")
    
    # 8. 测试其他 API
    print("\n" + "=" * 60)
    print("[5] Testing other API endpoints...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1")
    print(f"   GET / : {out[:200]}")
    
    # 查看路由数量
    print("\n" + "=" * 60)
    print("[6] Route count...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list --count 2>&1")
    print(f"   {out[:300]}")
    
    ssh.close()
    
    print(f"\nDone! URL: http://{SSH_HOST}")
    print(f"API: http://{SSH_HOST}/api")

if __name__ == "__main__":
    main()
