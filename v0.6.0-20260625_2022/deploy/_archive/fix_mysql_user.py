#!/usr/bin/env python3
"""
修复 MySQL 用户和权限问题
"""
import paramiko

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=60, show=True):
    """执行命令"""
    if show:
        print(f">> {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if show:
        if out and len(out.strip()) > 0:
            print(f"   OUT: {out[:500]}")
        if err and code != 0:
            print(f"   ERR (code {code}): {err[:500]}")
    return code, out, err

def get_mysql_admin(ssh):
    """获取 MySQL admin 凭证"""
    code, out, err = run_cmd(ssh, "sudo cat /etc/mysql/debian.cnf | grep -E 'user|password'", show=False)
    lines = out.strip().split('\n')
    db_user = ''
    db_pass = ''
    for line in lines:
        if 'user' in line.lower() and '=' in line:
            db_user = line.split('=')[1].strip()
        if 'password' in line.lower() and '=' in line:
            db_pass = line.split('=')[1].strip()
    return db_user, db_pass

def fix_mysql_user(ssh, db_user, db_pass):
    """修复 MySQL 用户"""
    print("\n" + "=" * 60)
    print("Fixing MySQL user 'oa_user'...")
    print("=" * 60)
    
    # 1. 检查用户是否存在
    print("\n[1] Checking if user 'oa_user' exists...")
    code, out, err = run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "SELECT User, Host FROM mysql.user WHERE User='oa_user';" 2>&1""")
    
    if 'oa_user' in out:
        print("   User 'oa_user' exists")
    else:
        print("   User 'oa_user' does NOT exist, creating...")
    
    # 2. 删除旧用户（如果有）
    print("\n[2] Dropping old user (if exists)...")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "DROP USER IF EXISTS 'oa_user'@'localhost';" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "DROP USER IF EXISTS 'oa_user'@'127.0.0.1';" 2>&1""")
    
    # 3. 创建新用户（同时支持 localhost 和 127.0.0.1）
    print("\n[3] Creating user 'oa_user'...")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE USER 'oa_user'@'localhost' IDENTIFIED BY 'oa_password';" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE USER 'oa_user'@'127.0.0.1' IDENTIFIED BY 'oa_password';" 2>&1""")
    
    # 4. 授予权限
    print("\n[4] Granting privileges...")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'127.0.0.1';" 2>&1""")
    
    # 5. 刷新权限
    print("\n[5] Flushing privileges...")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "FLUSH PRIVILEGES;" 2>&1""")
    
    # 6. 验证
    print("\n[6] Verifying...")
    code, out, err = run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "SELECT User, Host FROM mysql.user WHERE User='oa_user';" 2>&1""")
    
    # 7. 测试连接
    print("\n[7] Testing connection as 'oa_user'...")
    code, out, err = run_cmd(ssh, f"""sudo mysql -u oa_user -p'oa_password' -e "SELECT 1;" 2>&1""")
    if "1" in out:
        print("   ✅ Connection successful!")
        return True
    else:
        print(f"   ❌ Connection failed: {err[:300]}")
        return False

def test_laravel_db(ssh):
    """测试 Laravel 数据库连接"""
    print("\n" + "=" * 60)
    print("Testing Laravel database connection...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan tinker --execute='try {{ DB::connection()->getPdo(); echo \"DB OK\"; }} catch (Exception e) {{ echo \"DB ERROR: \" . e->getMessage(); }}' 2>&1")
    
    if 'DB OK' in out:
        print("\n   ✅ Laravel can connect to database!")
        return True
    else:
        print(f"\n   ❌ Laravel cannot connect:")
        print(f"   {out[:800]}")
        return False

def migrate_and_seed(ssh):
    """运行迁移和填充"""
    print("\n" + "=" * 60)
    print("Running migrations...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    if out:
        print(f"\n   Migration:\n{out[:1000]}")
    
    print("\n" + "=" * 60)
    print("Seeding database...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    if out:
        print(f"\n   Seed:\n{out[:1000]}")

def restart_services(ssh):
    """重启服务"""
    print("\n" + "=" * 60)
    print("Restarting services...")
    print("=" * 60)
    
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")

def test_http(ssh):
    """测试 HTTP 访问"""
    print("\n" + "=" * 60)
    print("Testing HTTP access...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show=False)
    print(f"\n   HTTP Status: {out}")
    
    if out.strip() == "200":
        print("   ✅ HTTP 200 OK!")
        return True
    else:
        print(f"   ❌ HTTP {out.strip()}")
        # 查看日志
        code, out, err = run_cmd(ssh, f"tail -30 {REMOTE_DIR}/storage/logs/laravel.log 2>&1")
        return False

def main():
    print("=" * 60)
    print("Fixing MySQL User for Laravel")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 获取 MySQL admin 凭证
    print("\n" + "=" * 60)
    print("Getting MySQL admin credentials...")
    print("=" * 60)
    db_user, db_pass = get_mysql_admin(ssh)
    
    if not db_user or not db_pass:
        print("   ❌ ERROR: Cannot get MySQL admin credentials!")
        ssh.close()
        return
    
    print(f"   MySQL admin user: {db_user}")
    
    # 2. 修复 MySQL 用户
    success = fix_mysql_user(ssh, db_user, db_pass)
    
    if success:
        # 3. 测试 Laravel 数据库连接
        db_ok = test_laravel_db(ssh)
        
        if db_ok:
            # 4. 运行迁移
            migrate_and_seed(ssh)
            
            # 5. 重启服务
            restart_services(ssh)
            
            # 6. 测试 HTTP
            test_http(ssh)
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Fix complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
