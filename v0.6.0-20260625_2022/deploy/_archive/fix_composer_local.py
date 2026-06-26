#!/usr/bin/env python3
"""
下载 composer.json 到本地修改，然后上传
"""
import paramiko
import json

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
        print(f"   OUT: {out[:500]}")
    if err and code != 0:
        print(f"   ERR: {err[:500]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Fix: Download composer.json locally, edit, upload")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 临时修改文件权限为 nbcy
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/composer.json")
    
    # 2. 下载
    print("\n[1] Downloading composer.json...")
    sftp = ssh.open_sftp()
    local_file = "D:/work/website/OA/deploy/composer_server.json"
    sftp.get(f"{REMOTE_DIR}/composer.json", local_file)
    sftp.close()
    
    # 3. 读取并修改
    print("\n[2] Editing composer.json...")
    with open(local_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   Current autoload: {json.dumps(data.get('autoload', {}), indent=2)[:300]}")
    
    # 添加 files autoload
    if 'files' not in data.get('autoload', {}):
        data['autoload']['files'] = [
            "app/Http/Controllers/Api/ModuleControllers.php",
            "app/Models/CoreModels.php",
            "app/Models/ProjectModels.php",
            "app/Models/ServiceModels.php",
            "app/Models/OtherModels.php"
        ]
        print("   Added files autoload!")
    else:
        print("   files autoload already exists")
    
    # 保存
    with open(local_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # 4. 上传
    print("\n[3] Uploading fixed composer.json...")
    sftp = ssh.open_sftp()
    sftp.put(local_file, f"{REMOTE_DIR}/composer.json")
    sftp.close()
    
    # 5. 恢复权限
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/composer.json")
    
    # 6. 验证
    print("\n[4] Verifying...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && php -r \"echo json_encode(json_decode(file_get_contents('composer.json'), true)['autoload']['files']);\" 2>&1")
    print(f"   files autoload: {out}")
    
    # 7. dump-autoload
    print("\n[5] Running composer dump-autoload...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer dump-autoload -o 2>&1 | tail -10")
    
    # 8. 创建 cache 表（通过 SQL）
    print("\n[6] Creating cache table via SQL...")
    cache_sql = """
    CREATE TABLE IF NOT EXISTS cache (
        `key` varchar(255) NOT NULL PRIMARY KEY,
        `value` mediumtext NOT NULL,
        `expiration` int NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    run_cmd(ssh, f"""sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "USE oa_db; {cache_sql}" 2>&1""")
    
    # 9. 创建 sessions 表
    print("\n[7] Creating sessions table via SQL...")
    sessions_sql = """
    CREATE TABLE IF NOT EXISTS sessions (
        `id` varchar(255) NOT NULL PRIMARY KEY,
        `user_id` bigint unsigned NULL,
        `ip_address` varchar(45) NULL,
        `user_agent` text NULL,
        `payload` longtext NOT NULL,
        `last_activity` int NOT NULL,
        INDEX sessions_user_id_index (user_id),
        INDEX sessions_last_activity_index (last_activity)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    run_cmd(ssh, f"""sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "USE oa_db; {sessions_sql}" 2>&1""")
    
    # 10. 清除缓存
    print("\n[8] Clearing caches...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 11. 设置权限
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, f"sudo chmod -R 755 {REMOTE_DIR}/storage {REMOTE_DIR}/bootstrap/cache")
    
    # 12. 重启
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 13. 测试路由
    print("\n[9] Testing routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -80")
    
    # 14. 测试 API
    print("\n[10] Testing API...")
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1", timeout=10)
    print(f"   GET / : {out[:200]}")
    
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""", timeout=10)
    print(f"   POST /api/auth/login: {out[:500]}")
    
    ssh.close()
    
    print(f"\nDone! URL: http://{SSH_HOST}")

if __name__ == "__main__":
    main()
