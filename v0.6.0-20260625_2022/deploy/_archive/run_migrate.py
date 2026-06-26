#!/usr/bin/env python3
"""
测试 Laravel DB 连接并运行迁移和填充
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
    print("Running Migrations and Seeding")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 清除缓存
    print("=" * 60)
    print("[1] Clearing caches...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan config:clear")
    
    # 2. 测试数据库连接 (用 migrate:status)
    print("\n" + "=" * 60)
    print("[2] Testing DB connection (migrate:status)...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate:status 2>&1 | head -20")
    
    if 'Access denied' in out or 'Access denied' in err:
        print("   ❌ DB connection FAILED!")
        return
    elif 'Ran' in out or 'Pending' in out or 'No' in out:
        print("   ✅ DB connection OK!")
    else:
        print(f"   Unknown status, checking further...")
    
    # 3. 运行迁移
    print("\n" + "=" * 60)
    print("[3] Running migrations...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    
    # 4. 填充数据库
    print("\n" + "=" * 60)
    print("[4] Seeding database...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    
    # 5. 设置权限
    print("\n" + "=" * 60)
    print("[5] Setting permissions...")
    print("=" * 60)
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 6. 重启服务
    print("\n" + "=" * 60)
    print("[6] Restarting services...")
    print("=" * 60)
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 7. 测试 HTTP
    print("\n" + "=" * 60)
    print("[7] Testing HTTP access...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", timeout=10)
    print(f"   HTTP Status: {out}")
    
    if out.strip() == "200":
        print("   ✅ SUCCESS!")
    else:
        # 查看日志
        print("\n   Checking logs...")
        run_cmd(ssh, f"tail -50 {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -50")
    
    # 8. 查看路由
    print("\n" + "=" * 60)
    print("[8] Checking routes...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -80")
    
    # 9. 检查用户数据
    print("\n" + "=" * 60)
    print("[9] Checking database tables...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SHOW TABLES FROM oa_db;" 2>&1 | tail -20""")
    if 'oa_db' in out:
        print(f"   Tables:\n{out[:2000]}")
    
    # 10. 查看管理员用户
    print("\n" + "=" * 60)
    print("[10] Checking admin user...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SELECT id, name, email FROM oa_db.users LIMIT 5;" 2>&1""")
    if 'id' in out:
        print(f"   Users:\n{out[:1000]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
