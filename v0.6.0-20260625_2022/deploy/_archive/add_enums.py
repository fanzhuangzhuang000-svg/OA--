#!/usr/bin/env python3
"""
添加 Enums/index.php 到 files autoload 并测试
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
        print(f"   OUT: {out[:600]}")
    if err and code != 0:
        print(f"   ERR: {err[:600]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Adding Enums/index.php to files autoload")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 修改权限并下载 composer.json
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/composer.json")
    sftp = ssh.open_sftp()
    local_file = "D:/work/website/OA/deploy/composer_server.json"
    sftp.get(f"{REMOTE_DIR}/composer.json", local_file)
    sftp.close()
    
    # 2. 修改
    with open(local_file, 'r') as f:
        data = json.load(f)
    
    files = data.get('autoload', {}).get('files', [])
    if "app/Enums/index.php" not in files:
        files.append("app/Enums/index.php")
        data['autoload']['files'] = files
        print("Added app/Enums/index.php to files autoload")
    
    # 检查是否还有 Services 目录
    code, out, err = run_cmd(ssh, f"ls {REMOTE_DIR}/app/Services/ 2>/dev/null || echo 'NO_DIR'")
    if 'NO_DIR' not in out:
        run_cmd(ssh, f"find {REMOTE_DIR}/app/Services -name '*.php' 2>/dev/null")
    
    with open(local_file, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # 3. 上传
    sftp = ssh.open_sftp()
    sftp.put(local_file, f"{REMOTE_DIR}/composer.json")
    sftp.close()
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/composer.json")
    
    # 4. dump-autoload
    print("\nRunning composer dump-autoload...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data composer dump-autoload -o 2>&1 | tail -10")
    
    # 5. 清除缓存
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 6. 权限和重启
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 7. 测试登录
    print("\nTesting login...")
    run_cmd(ssh, f"sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print(f"\nLogin response: {out[:500]}")
    
    # 8. 查看日志
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -50")
    
    # 9. 如果成功，测试更多 API
    if 'token' in out.lower() or 'user' in out.lower():
        print("\n✅ LOGIN WORKS!")
        try:
            import json as j
            resp = j.loads(out)
            token = resp.get('token', resp.get('data', {}).get('token', ''))
            if token:
                print(f"Token: {token[:50]}...")
                code, out2, err2 = run_cmd(ssh, f"""curl -s http://localhost/api/dashboard/stats -H 'Authorization: Bearer {token}' 2>&1""")
                print(f"Dashboard: {out2[:500]}")
        except:
            pass
    else:
        print("\n❌ Login still failing, checking log above")
    
    ssh.close()
    print(f"\nDone! URL: http://{SSH_HOST}")

if __name__ == "__main__":
    main()
