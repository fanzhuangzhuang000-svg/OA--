#!/usr/bin/env python3
"""
修复 Laravel 11 路由加载问题
Laravel 11 使用 bootstrap/app.php 来加载路由，而不是 RouteServiceProvider
"""
import paramiko
import os

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

def check_and_fix_routing(ssh):
    """检查并修复 Laravel 11 路由配置"""
    print("\n" + "=" * 60)
    print("Checking Laravel 11 routing configuration...")
    print("=" * 60)
    
    # 1. 检查 bootstrap/app.php
    print("\n[1] Checking bootstrap/app.php...")
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/bootstrap/app.php")
    
    if 'withRouting' not in out:
        print("  WARNING: withRouting() not found in bootstrap/app.php!")
        print("  Laravel 11 requires withRouting() to load routes.")
    else:
        print("  OK: withRouting() found")
    
    # 2. 检查 routes/api.php 是否存在
    print("\n[2] Checking routes/api.php...")
    code, out, err = run_cmd(ssh, f"test -f {REMOTE_DIR}/routes/api.php && echo 'EXISTS' || echo 'MISSING'")
    if "MISSING" in out:
        print("  ERROR: routes/api.php is missing!")
    else:
        print("  OK: routes/api.php exists")
        # 查看内容
        run_cmd(ssh, f"head -20 {REMOTE_DIR}/routes/api.php")
    
    # 3. 检查 routes/web.php
    print("\n[3] Checking routes/web.php...")
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/routes/web.php")
    
    # 4. 修复 bootstrap/app.php（如果需要）
    print("\n[4] Ensuring bootstrap/app.php has withRouting()...")
    # 下载 bootstrap/app.php
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/bootstrap_app_temp.php"
    
    try:
        sftp.get(f"{REMOTE_DIR}/bootstrap/app.php", local_temp)
        
        with open(local_temp, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 withRouting
        if 'withRouting' not in content:
            print("  Adding withRouting() to bootstrap/app.php...")
            # 在 return $app; 之前添加 withRouting
            content = content.replace(
                'return $app;',
                """    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withExceptions()
    ->withMiddleware()
    ->withCommands()
    ->run();

return $app;"""
            )
            
            with open(local_temp, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 上传
            run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/bootstrap/app.php")
            sftp.put(local_temp, f"{REMOTE_DIR}/bootstrap/app.php")
            run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/bootstrap/app.php")
            print("  Fixed!")
        else:
            print("  OK: withRouting() already present")
    
    except Exception as e:
        print(f"  ERROR: {e}")
    
    sftp.close()

def check_database_config(ssh):
    """检查数据库配置"""
    print("\n" + "=" * 60)
    print("Checking database configuration...")
    print("=" * 60)
    
    # 检查 .env 数据库配置
    print("\n[1] Checking .env database config...")
    code, out, err = run_cmd(ssh, f"grep -E '^DB_' {REMOTE_DIR}/.env")
    
    # 测试数据库连接
    print("\n[2] Testing database connection...")
    code, out, err = run_cmd(ssh, f"""cd {REMOTE_DIR} && sudo -u www-data php -r "try {{ pdo = new PDO('mysql:host=localhost;dbname=oa_db', 'oa_user', 'oa_password'); echo 'DB OK'; }} catch (Exception e) {{ echo 'DB ERROR: ' . e->getMessage(); }}" 2>&1""")
    
    # 检查数据库是否存在
    print("\n[3] Checking if database exists...")
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SHOW DATABASES LIKE 'oa_db';" 2>&1""")
    
    # 检查迁移是否运行
    print("\n[4] Checking migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate:status 2>&1 | head -30")

def clear_all_caches(ssh):
    """清除所有缓存"""
    print("\n" + "=" * 60)
    print("Clearing all caches...")
    print("=" * 60)
    
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan config:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan view:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan cache:clear")
    
    # 重启服务
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")

def main():
    print("=" * 60)
    print("Fixing Laravel 11 Routing + Database Issues")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 修复路由配置
    check_and_fix_routing(ssh)
    
    # 2. 检查数据库配置
    check_database_config(ssh)
    
    # 3. 清除缓存
    clear_all_caches(ssh)
    
    # 4. 测试路由
    print("\n" + "=" * 60)
    print("Testing routes after fix...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -50")
    
    # 5. 测试 HTTP
    print("\n" + "=" * 60)
    print("Testing HTTP access...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show_output=False)
    print(f"  HTTP Status: {out}")
    
    # 6. 查看最新日志
    print("\n" + "=" * 60)
    print("Latest Laravel log entries...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"tail -30 {REMOTE_DIR}/storage/logs/laravel.log 2>&1")
    
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
