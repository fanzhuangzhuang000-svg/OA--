#!/usr/bin/env python3
"""
最终综合修复 - 使用远程命令精确修复
"""
import paramiko
import json

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=120, show=True):
    print(f">> {cmd[:100]}...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    if show:
        if out and len(out.strip()) > 0:
            print(f"   OUT: {out[:500]}")
        if err and code != 0:
            print(f"   ERR: {err[:500]}")
    return code, out, err

def fix_composer_json_files(ssh):
    """使用 jq 或 python 远程修改 composer.json"""
    print("\n" + "=" * 60)
    print("[1] Fixing composer.json - Adding files autoload via remote PHP...")
    print("=" * 60)
    
    # 使用远程 PHP 来修改 composer.json
    php_code = '''<?php
$json_path = "/var/www/oa-api/composer.json";
$content = file_get_contents($json_path);
$data = json_decode($content, true);

if (!isset($data['autoload']['files'])) {
    $data['autoload']['files'] = array(
        "app/Http/Controllers/Api/ModuleControllers.php",
        "app/Models/CoreModels.php",
        "app/Models/ProjectModels.php",
        "app/Models/ServiceModels.php",
        "app/Models/OtherModels.php"
    );
    file_put_contents($json_path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\\n");
    echo "OK: files autoload added";
} else {
    echo "OK: files autoload already exists";
}
?>
'''
    
    # 通过 artisan tinker 执行 PHP 代码（不行）
    # 直接写入一个临时 PHP 文件然后执行
    sftp = ssh.open_sftp()
    local_php = "D:/work/website/OA/deploy/fix_composer.php"
    with open(local_php, 'w') as f:
        f.write(php_code)
    sftp.put(local_php, "/tmp/fix_composer.php")
    run_cmd(ssh, f"sudo chown nbcy:nbcy /tmp/fix_composer.php")
    sftp.close()
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && php /tmp/fix_composer.php 2>&1")
    print(f"   Result: {out}")
    
    # 验证
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && php -r \"echo json_encode(json_decode(file_get_contents('composer.json'), true)['autoload']['files'] ?? 'NOT FOUND');\" 2>&1")
    print(f"   Files autoload: {out}")
    
    # 重新生成 autoload
    print("   Running composer dump-autoload...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer dump-autoload -o 2>&1 | tail -10")

def fix_env_cache(ssh):
    """确保 CACHE_DRIVER=file (使用远程 PHP)"""
    print("\n" + "=" * 60)
    print("[2] Fixing .env cache and session drivers...")
    print("=" * 60)
    
    php_code = '''<?php
$env_path = "/var/www/oa-api/.env";
$content = file_get_contents($env_path);

// 删除所有 CACHE_DRIVER 和 SESSION_DRIVER 行
$lines = explode("\\n", $content);
$new_lines = [];
foreach ($lines as $line) {
    if (strpos(trim($line), 'CACHE_DRIVER=') === 0) continue;
    if (strpos(trim($line), 'SESSION_DRIVER=') === 0) continue;
    $new_lines[] = $line;
}
$new_lines[] = "CACHE_DRIVER=file";
$new_lines[] = "SESSION_DRIVER=file";
$content = implode("\\n", $new_lines);
file_put_contents($env_path, $content);
echo "OK: CACHE_DRIVER=file, SESSION_DRIVER=file";
?>
'''
    
    sftp = ssh.open_sftp()
    local_php = "D:/work/website/OA/deploy/fix_env.php"
    with open(local_php, 'w') as f:
        f.write(php_code)
    sftp.put(local_php, "/tmp/fix_env.php")
    run_cmd(ssh, f"sudo chown nbcy:nbcy /tmp/fix_env.php")
    sftp.close()
    
    code, out, err = run_cmd(ssh, f"php /tmp/fix_env.php 2>&1")
    print(f"   Result: {out}")
    
    # 验证
    code, out, err = run_cmd(ssh, f"grep -E '^(CACHE|SESSION)_DRIVER' {REMOTE_DIR}/.env")
    
    # 修改文件权限
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/.env")

def create_cache_table(ssh):
    """创建 cache 表（作为备选方案）"""
    print("\n" + "=" * 60)
    print("[3] Creating cache table (backup plan)...")
    print("=" * 60)
    
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && php artisan make:migration create_cache_table --table=cache 2>&1 || true")
    if 'created' in out.lower():
        run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1 | tail -5")
    else:
        print("   Skipping (migration might already exist)")

def main():
    print("=" * 60)
    print("FINAL COMPREHENSIVE FIX")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("\nConnected!")
    
    # 1. 修复 composer.json files autoload
    fix_composer_json_files(ssh)
    
    # 2. 修复 .env cache driver
    fix_env_cache(ssh)
    
    # 3. 创建 cache 表（备用）
    create_cache_table(ssh)
    
    # 4. 清除所有缓存
    print("\n" + "=" * 60)
    print("[4] Clearing all caches...")
    print("=" * 60)
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
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
    
    # 7. 测试路由
    print("\n" + "=" * 60)
    print("[7] Checking routes...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -100")
    
    # 8. 测试 API
    print("\n" + "=" * 60)
    print("[8] Testing API endpoints...")
    print("=" * 60)
    
    # Test root
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1", timeout=10)
    print(f"   GET / : {out[:200]}")
    
    # Test login
    print("\n   Testing login...")
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""", timeout=10)
    print(f"   POST /api/auth/login: {out[:500]}")
    
    # 9. 查看最新日志
    print("\n" + "=" * 60)
    print("[9] Latest error log...")
    print("=" * 60)
    code, out, err = run_cmd(ssh, f"tail -30 {REMOTE_DIR}/storage/logs/laravel.log 2>&1")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nURL: http://{SSH_HOST}")
    print(f"API: http://{SSH_HOST}/api")
    print("=" * 60)

if __name__ == "__main__":
    main()
