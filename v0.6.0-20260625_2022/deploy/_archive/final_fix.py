#!/usr/bin/env python3
"""
最终修复：
1. 在 composer.json 中添加 files autoload（解决 PSR-4 问题）
2. 确保 CACHE_DRIVER=file
3. 重新测试
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

def fix_composer_json(ssh):
    """在 composer.json 中添加 files autoload"""
    print("\n" + "=" * 60)
    print("[1] Fixing composer.json - Adding files autoload...")
    print("=" * 60)
    
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/composer_temp.json"
    sftp.get(f"{REMOTE_DIR}/composer.json", local_temp)
    
    with open(local_temp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 如果已经有 files autoload，跳过
    if '"files"' in content:
        print("   Already has files autoload, skipping")
        sftp.close()
        return
    
    # 添加 files autoload
    # 在 "autoload" -> "psr-4" 后面添加 "files"
    old = '''"autoload": {
        "psr-4": {
            "App\\\\": "app/"
        }
    }'''
    
    new = '''"autoload": {
        "psr-4": {
            "App\\\\": "app/"
        },
        "files": [
            "app/Http/Controllers/Api/ModuleControllers.php",
            "app/Models/CoreModels.php",
            "app/Models/ProjectModels.php",
            "app/Models/ServiceModels.php",
            "app/Models/OtherModels.php"
        ]
    }'''
    
    if old in content:
        content = content.replace(old, new)
        print("   Added files autoload!")
    else:
        print("   WARNING: Could not find expected autoload pattern")
        print(f"   Content preview: {content[:500]}")
    
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.write(content)
    
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/composer.json")
    sftp.put(local_temp, f"{REMOTE_DIR}/composer.json")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/composer.json")
    sftp.close()
    
    # 重新生成 autoload
    print("\n   Running composer dump-autoload...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer dump-autoload 2>&1")
    print("   Done!")

def fix_env(ssh):
    """确保 CACHE_DRIVER=file"""
    print("\n" + "=" * 60)
    print("[2] Ensuring CACHE_DRIVER=file in .env...")
    print("=" * 60)
    
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/.env.temp"
    sftp.get(f"{REMOTE_DIR}/.env", local_temp)
    
    with open(local_temp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    found_cache = False
    found_session = False
    
    for line in lines:
        if line.startswith('CACHE_DRIVER='):
            new_lines.append('CACHE_DRIVER=file\n')
            found_cache = True
        elif line.startswith('SESSION_DRIVER='):
            new_lines.append('SESSION_DRIVER=file\n')
            found_session = True
        else:
            new_lines.append(line)
    
    # 如果没有找到，在末尾添加
    if not found_cache:
        new_lines.append('CACHE_DRIVER=file\n')
    if not found_session:
        new_lines.append('SESSION_DRIVER=file\n')
    
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/.env")
    sftp.put(local_temp, f"{REMOTE_DIR}/.env")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/.env")
    sftp.close()
    print("   CACHE_DRIVER and SESSION_DRIVER set to 'file'!")

def main():
    print("=" * 60)
    print("FINAL FIX - PSR-4 + Cache Driver")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 修复 composer.json
    fix_composer_json(ssh)
    
    # 2. 修复 .env
    fix_env(ssh)
    
    # 3. 清除缓存
    print("\n" + "=" * 60)
    print("[3] Clearing caches...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    
    # 4. 设置权限
    print("\n" + "=" * 60)
    print("[4] Setting permissions...")
    print("=" * 60)
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 5. 重启服务
    print("\n" + "=" * 60)
    print("[5] Restarting services...")
    print("=" * 60)
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 6. 测试路由
    print("\n" + "=" * 60)
    print("[6] Checking routes...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -100")
    if out and 'Error' not in out and 'not found' not in out:
        print(f"   Routes:\n{out[:5000]}")
    
    # 7. 测试 API
    print("\n" + "=" * 60)
    print("[7] Testing API endpoints...")
    print("=" * 60)
    
    # Test root
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1", timeout=10)
    print(f"   GET / : {out[:300]}")
    
    # Test login
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' 2>&1""", timeout=10)
    print(f"   POST /api/auth/login: {out[:500]}")
    
    # Test dashboard
    code, out, err = run_cmd(ssh, """curl -s http://localhost/api/dashboard/stats 2>&1""", timeout=10)
    print(f"   GET /api/dashboard/stats: {out[:500]}")
    
    # 8. HTTP Status
    print("\n" + "=" * 60)
    print("[8] HTTP Status check...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", timeout=10)
    print(f"   HTTP Status: {out}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)
    print(f"\n🌐 URL: http://{SSH_HOST}")
    print(f"📖 API: http://{SSH_HOST}/api")
    print("\n👤 Default credentials:")
    print("   Username: admin")
    print("   Password: admin123 (or check database)")
    print("=" * 60)

if __name__ == "__main__":
    main()
