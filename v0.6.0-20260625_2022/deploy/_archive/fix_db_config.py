#!/usr/bin/env python3
"""
修复 .env 中的数据库配置（sqlite -> mysql）
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
        print(f"   OUT: {out[:500]}")
    if err and code != 0:
        print(f"   ERR (code {code}): {err[:500]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Fixing .env: sqlite -> mysql")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 修复 .env 数据库配置
    print("[" + "=" * 60)
    print("Step 1: Fixing .env database config...")
    print("=" * 60)
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_CONNECTION=.*/DB_CONNECTION=mysql/' {REMOTE_DIR}/.env""")
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_HOST=.*/DB_HOST=127.0.0.1/' {REMOTE_DIR}/.env""")
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_PORT=.*/DB_PORT=3306/' {REMOTE_DIR}/.env""")
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_DATABASE=.*/DB_DATABASE=oa_db/' {REMOTE_DIR}/.env""")
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_USERNAME=.*/DB_USERNAME=oa_user/' {REMOTE_DIR}/.env""")
    run_cmd(ssh, f"""sudo -u www-data sed -i 's/^DB_PASSWORD=.*/DB_PASSWORD=oa_password/' {REMOTE_DIR}/.env""")
    
    # 验证配置
    print("\nVerifying .env...")
    run_cmd(ssh, f"grep -E '^DB_' {REMOTE_DIR}/.env")
    
    # 2. 清除所有缓存
    print("\n" + "=" * 60)
    print("Step 2: Clearing all caches...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan config:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan cache:clear")
    
    # 3. 测试数据库连接
    print("\n" + "=" * 60)
    print("Step 3: Testing database connection...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"""cd {REMOTE_DIR} && sudo -u www-data php -r "try {{ new PDO('mysql:host=127.0.0.1;dbname=oa_db', 'oa_user', 'oa_password'); echo 'DB OK'; }} catch (Exception e) {{ echo 'DB ERROR: ' . e->getMessage(); }}" 2>&1""")
    
    # 4. 运行迁移
    print("\n" + "=" * 60)
    print("Step 4: Running migrations...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"  Migration output:\n{out[:1000]}")
    if err and 'Error' in err:
        print(f"  Migration errors:\n{err[:1000]}")
    
    # 5. 填充数据库
    print("\n" + "=" * 60)
    print("Step 5: Seeding database...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"  Seed output:\n{out[:1000]}")
    
    # 6. 重启服务
    print("\n" + "=" * 60)
    print("Step 6: Restarting services...")
    print("=" * 60)
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 7. 测试 HTTP 访问
    print("\n" + "=" * 60)
    print("Step 7: Testing HTTP access...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", timeout=10)
    print(f"  HTTP Status: {out}")
    
    # 8. 查看路由
    print("\n" + "=" * 60)
    print("Step 8: Checking routes...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -80")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"  Routes:\n{out[:3000]}")
    else:
        print(f"  Error or no routes: {err[:1000]}")
    
    # 9. 查看最新日志
    print("\n" + "=" * 60)
    print("Step 9: Checking latest Laravel log...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"tail -30 {REMOTE_DIR}/storage/logs/laravel.log 2>&1")
    if out:
        print(f"  Log:\n{out[:2000]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Fix complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("\nIf still 500, check:")
    print(f"  1. {REMOTE_DIR}/storage/logs/laravel.log")
    print(f"  2. sudo tail -50 /var/log/nginx/error.log")
    print("=" * 60)

if __name__ == "__main__":
    main()
