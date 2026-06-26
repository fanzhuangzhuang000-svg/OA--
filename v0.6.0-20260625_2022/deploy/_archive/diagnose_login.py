#!/usr/bin/env python3
"""
检查登录 API 的具体错误，并创建缺失的表
"""
import paramiko

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=120):
    print(f">> {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if out and len(out.strip()) > 0:
        print(f"   OUT: {out[:800]}")
    if err and code != 0:
        print(f"   ERR: {err[:800]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Diagnosing Login API Error")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 清空日志
    run_cmd(ssh, f"sudo -u www-data truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log 2>/dev/null || sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/storage/logs/laravel.log")
    
    # 2. 触发登录请求
    print("\n" + "=" * 60)
    print("Triggering login request...")
    print("=" * 60)
    run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    
    # 3. 查看日志
    print("\n" + "=" * 60)
    print("Error log...")
    print("=" * 60)
    run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -100")
    
    # 4. 检查 AuthController
    print("\n" + "=" * 60)
    print("Checking AuthController...")
    print("=" * 60)
    run_cmd(ssh, f"head -50 {REMOTE_DIR}/app/Http/Controllers/Api/ModuleControllers.php 2>&1")
    
    # 5. 创建 cache 和 sessions 表（使用 PHP artisan）
    print("\n" + "=" * 60)
    print("Creating missing tables via artisan...")
    print("=" * 60)
    # 创建 cache 表迁移
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan make:migration create_cache_table 2>&1 | tail -5")
    # 运行迁移
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1 | tail -10")
    
    # 6. 再次清除缓存
    print("\n" + "=" * 60)
    print("Clearing caches again...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 7. 设置权限
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 8. 再次测试
    print("\n" + "=" * 60)
    print("Testing login again...")
    print("=" * 60)
    run_cmd(ssh, f"sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    run_cmd(ssh, """curl -sv -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print("\nLog after login:")
    run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -80")
    
    ssh.close()
    print(f"\nDone!")

if __name__ == "__main__":
    main()
