#!/usr/bin/env python3
"""
检查 Laravel 日志并诊断 500 错误
"""
import paramiko

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=60):
    """执行命令"""
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
    print("Diagnosing Laravel 500 Error")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 检查 .env 配置
    print("=" * 60)
    print("[1] Checking .env configuration...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/.env | grep -E '^[^#]'_PASSWORD' | head -20")
    
    # 2. 检查存储目录权限
    print("\n" + "=" * 60)
    print("[2] Checking storage permissions...")
    print("=" * 60)
    run_cmd(ssh, f"ls -la {REMOTE_DIR}/storage/logs/")
    run_cmd(ssh, f"ls -la {REMOTE_DIR}/bootstrap/cache/")
    
    # 3. 检查日志文件
    print("\n" + "=" * 60)
    print("[3] Checking Laravel log...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"test -f {REMOTE_DIR}/storage/logs/laravel.log && echo 'EXISTS' || echo 'NOT FOUND'")
    if "EXISTS" in out:
        run_cmd(ssh, f"tail -50 {REMOTE_DIR}/storage/logs/laravel.log")
    else:
        print("  Log file not found, checking for errors with artisan...")
        run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan serve --port=9000 2>&1 &")
        import time
        time.sleep(2)
        run_cmd(ssh, "curl -s http://localhost:9000/ 2>&1 | head -100")
    
    # 4. 手动触发一个请求来捕获错误
    print("\n" + "=" * 60)
    print("[4] Testing with artisan route:list...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -50")
    
    # 5. 检查 PHP 错误日志
    print("\n" + "=" * 60)
    print("[5] Checking PHP error log...")
    print("=" * 60)
    run_cmd(ssh, "sudo tail -50 /var/log/php8.3-fpm.log 2>/dev/null || echo 'Not found'")
    run_cmd(ssh, "sudo tail -50 /var/log/nginx/error.log 2>/dev/null | head -50")
    
    # 6. 尝试直接运行 artisan 来查看错误
    print("\n" + "=" * 60)
    print("[6] Testing artisan tinker...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan tinker --execute='echo 123' 2>&1")
    
    # 7. 检查 composer 依赖是否正确安装
    print("\n" + "=" * 60)
    print("[7] Checking vendor directory...")
    print("=" * 60)
    run_cmd(ssh, f"ls -la {REMOTE_DIR}/vendor/autoload.php 2>/dev/null && echo 'EXISTS' || echo 'MISSING'")
    run_cmd(ssh, f"ls -la {REMOTE_DIR}/vendor/laravel/ 2>/dev/null | head -10")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Diagnosis complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
