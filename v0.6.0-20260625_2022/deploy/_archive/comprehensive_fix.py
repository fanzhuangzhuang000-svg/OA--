#!/usr/bin/env python3
"""
一次性修复所有问题：
1. 删除冲突的 Laravel 默认迁移
2. 修复 bootstrap/app.php 添加 API 路由
3. 清空数据库并重新运行迁移
4. 填充数据库
5. 测试
"""
import paramiko
import os

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
        print(f"   OUT: {out[:600]}")
    if err and code != 0:
        print(f"   ERR: {err[:600]}")
    return code, out, err

def fix_bootstrap_app(ssh):
    """修复 bootstrap/app.php 添加 API 路由"""
    print("\n" + "=" * 60)
    print("[1] Fixing bootstrap/app.php - Adding API routes...")
    print("=" * 60)
    
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/bootstrap_app_temp.php"
    
    # 下载
    sftp.get(f"{REMOTE_DIR}/bootstrap/app.php", local_temp)
    
    with open(local_temp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"   Current content preview:\n   {content[:300]}")
    
    # 检查是否已有 api: 参数
    if 'api:' in content:
        print("   Already has api: route, skipping")
        sftp.close()
        return
    
    # 在 withRouting 中添加 api: 参数
    # 替换: web: __DIR__.'/../routes/web.php',
    # 为:   web: __DIR__.'/../routes/web.php',\n        api: __DIR__.'/../routes/api.php',
    
    old = "web: __DIR__.'/../routes/web.php',"
    new = "web: __DIR__.'/../routes/web.php',\n        api: __DIR__.'/../routes/api.php',\n        api_prefix: 'api',"
    
    if old in content:
        content = content.replace(old, new)
        print("   Added api route!")
    else:
        print("   WARNING: Could not find expected pattern")
    
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 上传
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/bootstrap/app.php")
    sftp.put(local_temp, f"{REMOTE_DIR}/bootstrap/app.php")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/bootstrap/app.php")
    
    print("   bootstrap/app.php fixed!")
    sftp.close()

def remove_conflicting_migrations(ssh):
    """删除与业务代码冲突的 Laravel 默认迁移"""
    print("\n" + "=" * 60)
    print("[2] Removing conflicting Laravel default migrations...")
    print("=" * 60)
    
    # Laravel 11 默认的迁移文件（与我们的冲突）
    conflicting = [
        '0001_01_01_000000_create_users_table.php',
        '0001_01_01_000001_create_cache_table.php',
        '0001_01_01_000002_create_jobs_table.php',
        '0001_01_01_000000_create_personal_access_tokens_table.php',
    ]
    
    code, out, err = run_cmd(ssh, f"ls {REMOTE_DIR}/database/migrations/")
    
    for f in conflicting:
        run_cmd(ssh, f"sudo -u www-data rm -f {REMOTE_DIR}/database/migrations/{f} 2>/dev/null || true")
        print(f"   Removed: {f}")
    
    # 查看剩余的迁移文件
    print("\n   Remaining migrations:")
    run_cmd(ssh, f"ls {REMOTE_DIR}/database/migrations/")

def drop_and_migrate(ssh):
    """清空数据库并重新运行迁移"""
    print("\n" + "=" * 60)
    print("[3] Dropping all tables and re-running migrations...")
    print("=" * 60)
    
    # 获取 MySQL admin 凭证
    code, out, err = run_cmd(ssh, "sudo cat /etc/mysql/debian.cnf | grep -E 'user|password'")
    lines = out.strip().split('\n')
    db_user = ''
    db_pass = ''
    for line in lines:
        if 'user' in line.lower() and '=' in line:
            db_user = line.split('=')[1].strip()
        if 'password' in line.lower() and '=' in line:
            db_pass = line.split('=')[1].strip()
    
    # 删除并重新创建数据库
    print("\n   Recreating database oa_db...")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "DROP DATABASE IF EXISTS oa_db;" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "CREATE DATABASE oa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'localhost';" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "GRANT ALL PRIVILEGES ON oa_db.* TO 'oa_user'@'127.0.0.1';" 2>&1""")
    run_cmd(ssh, f"""sudo mysql -u {db_user} -p'{db_pass}' -e "FLUSH PRIVILEGES;" 2>&1""")
    
    # 清除迁移记录
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate:reset --force 2>&1 || true")
    
    # 运行所有迁移
    print("\n   Running fresh migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    
    if 'FAIL' in out:
        print(f"\n   ⚠️ Some migrations failed!")
    else:
        print(f"\n   ✅ All migrations completed!")

def seed_database(ssh):
    """填充数据库"""
    print("\n" + "=" * 60)
    print("[4] Seeding database...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    
    if out:
        print(f"   Seed output:\n{out[:1500]}")

def fix_session_driver(ssh):
    """修改 session driver 为 file（避免数据库 session 问题）"""
    print("\n" + "=" * 60)
    print("[5] Fixing session driver (file instead of database)...")
    print("=" * 60)
    
    # 下载 .env
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/.env.temp"
    sftp.get(f"{REMOTE_DIR}/.env", local_temp)
    
    with open(local_temp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith('SESSION_DRIVER='):
            new_lines.append('SESSION_DRIVER=file\n')
        elif line.startswith('CACHE_DRIVER='):
            new_lines.append('CACHE_DRIVER=file\n')
        else:
            new_lines.append(line)
    
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/.env")
    sftp.put(local_temp, f"{REMOTE_DIR}/.env")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/.env")
    
    print("   Session driver set to 'file'")
    sftp.close()

def final_test(ssh):
    """最终测试"""
    print("\n" + "=" * 60)
    print("[6] Final testing...")
    print("=" * 60)
    
    # 清除缓存
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    
    # 设置权限
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 重启服务
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 测试 HTTP
    print("\n   Testing HTTP...")
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1", timeout=10)
    print(f"   Response: {out[:200]}")
    
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", timeout=10)
    print(f"   HTTP Status: {out}")
    
    # 测试 API
    print("\n   Testing API...")
    code, out, err = run_cmd(ssh, "curl -s http://localhost/api/health 2>&1 | head -5", timeout=10)
    print(f"   API Response: {out[:200]}")
    
    # 查看路由
    print("\n   Checking routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -60")
    if out and 'Error' not in out:
        print(f"   Routes:\n{out[:3000]}")
    
    # 查看表
    print("\n   Database tables...")
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SHOW TABLES FROM oa_db;" 2>&1""")
    
    # 查看用户
    print("\n   Users...")
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SELECT id, name, email, username FROM oa_db.users;" 2>&1""")

def main():
    print("=" * 60)
    print("COMPREHENSIVE FIX - All Issues")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 修复 bootstrap/app.php
    fix_bootstrap_app(ssh)
    
    # 2. 删除冲突的迁移
    remove_conflicting_migrations(ssh)
    
    # 3. 修改 session driver
    fix_session_driver(ssh)
    
    # 4. 清空数据库并重新迁移
    drop_and_migrate(ssh)
    
    # 5. 填充数据库
    seed_database(ssh)
    
    # 6. 最终测试
    final_test(ssh)
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print(f"API: http://{SSH_HOST}/api")
    print("\nDefault credentials (if seeded):")
    print("  Username: admin")
    print("  Password: password")
    print("=" * 60)

if __name__ == "__main__":
    main()
