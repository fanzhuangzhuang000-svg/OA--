#!/usr/bin/env python3
"""
直接修复 .env 文件（使用 Python 而不是 sed）
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

def fix_env_file(ssh):
    """使用 Python 直接修复 .env 文件"""
    print("\n" + "=" * 60)
    print("Fixing .env file (using Python)...")
    print("=" * 60)
    
    env_path = f"{REMOTE_DIR}/.env"
    
    # 1. 下载 .env 文件
    print("\n[1] Downloading .env...")
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/.env.temp"
    
    try:
        sftp.get(env_path, local_temp)
        print(f"   Downloaded to {local_temp}")
    except Exception as e:
        print(f"   ERROR: {e}")
        # 尝试用 sudo cat 读取
        code, out, err = run_cmd(ssh, f"sudo cat {env_path}", show=False)
        if code == 0:
            with open(local_temp, 'w', encoding='utf-8') as f:
                f.write(out)
            print("   Downloaded via sudo cat")
        else:
            print(f"   ERROR: {err}")
            return False
    
    # 2. 读取并修复
    print("\n[2] Reading and fixing .env...")
    with open(local_temp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 要设置的配置
    config = {
        'APP_ENV': 'production',
        'APP_DEBUG': 'false',
        'APP_URL': 'http://172.20.0.139',
        'DB_CONNECTION': 'mysql',
        'DB_HOST': '127.0.0.1',
        'DB_PORT': '3306',
        'DB_DATABASE': 'oa_db',
        'DB_USERNAME': 'oa_user',
        'DB_PASSWORD': 'oa_password',
    }
    
    # 更新或添加配置
    updated = set()
    new_lines = []
    
    for line in lines:
        line = line.rstrip('\n')
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in config:
                new_lines.append(f"{key}={config[key]}\n")
                updated.add(key)
            else:
                new_lines.append(line + '\n')
        else:
            new_lines.append(line + '\n')
    
    # 添加缺失的配置
    for key, value in config.items():
        if key not in updated:
            new_lines.append(f"{key}={value}\n")
            print(f"   Added: {key}={value}")
    
    # 3. 写回本地文件
    print("\n[3] Writing fixed .env...")
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"   File size: {len(new_lines)} lines")
    
    # 4. 上传回服务器
    print("\n[4] Uploading fixed .env...")
    run_cmd(ssh, f"sudo chown nbcy:nbcy {env_path}")
    sftp.put(local_temp, env_path)
    run_cmd(ssh, f"sudo chown www-data:www-data {env_path}")
    run_cmd(ssh, f"sudo chmod 644 {env_path}")
    
    print("   Uploaded!")
    sftp.close()
    
    # 5. 验证
    print("\n[5] Verifying .env...")
    code, out, err = run_cmd(ssh, f"grep -E '^DB_' {env_path}")
    
    return True

def test_database(ssh):
    """测试数据库连接"""
    print("\n" + "=" * 60)
    print("Testing database connection...")
    print("=" * 60)
    
    # 使用 artisan 测试
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan tinker --execute='try {{ DB::connection()->getPdo(); echo \"DB OK\"; }} catch (Exception e) {{ echo \"DB ERROR: \" . e->getMessage(); }}' 2>&1")
    
    if 'DB OK' in out:
        print("\n   ✅ Database connection successful!")
        return True
    else:
        print(f"\n   ❌ Database connection failed!")
        if err:
            print(f"   Error: {err[:500]}")
        return False

def clear_caches(ssh):
    """清除所有缓存"""
    print("\n" + "=" * 60)
    print("Clearing all caches...")
    print("=" * 60)
    
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan config:clear")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan cache:clear")

def run_migrations(ssh):
    """运行数据库迁移"""
    print("\n" + "=" * 60)
    print("Running migrations...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    
    if out:
        print(f"\n   Migration output:\n{out[:1000]}")
    
    if err and 'error' in err.lower():
        print(f"\n   Migration errors:\n{err[:1000]}")

def main():
    print("=" * 60)
    print("Fixing .env and Testing Database")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 修复 .env
    success = fix_env_file(ssh)
    
    if success:
        # 2. 清除缓存
        clear_caches(ssh)
        
        # 3. 测试数据库连接
        db_ok = test_database(ssh)
        
        if db_ok:
            # 4. 运行迁移
            run_migrations(ssh)
            
            # 5. 重启服务
            print("\n" + "=" * 60)
            print("Restarting services...")
            print("=" * 60)
            run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
            run_cmd(ssh, "sudo systemctl restart nginx")
            
            # 6. 测试 HTTP
            print("\n" + "=" * 60)
            print("Testing HTTP access...")
            print("=" * 60)
            code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", show=False)
            print(f"\n   HTTP Status: {out}")
            
            # 7. 查看路由
            print("\n" + "=" * 60)
            print("Checking routes...")
            print("=" * 60)
            code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -80")
            if out and 'Error' not in out:
                print(f"\n   Routes:\n{out[:2000]}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Fix complete!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
