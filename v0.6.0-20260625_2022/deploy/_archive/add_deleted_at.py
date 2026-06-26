#!/usr/bin/env python3
"""
添加 deleted_at 列并测试登录
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
        print(f"   OUT: {out[:600]}")
    if err and code != 0:
        print(f"   ERR: {err[:600]}")
    return code, out, err

def main():
    print("=" * 60)
    print("Adding deleted_at column to users table")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 查看 users 表结构
    print("[1] Current users table structure...")
    run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "DESCRIBE oa_db.users;" 2>&1""")
    
    # 2. 查看 User 模型
    print("\n[2] User model...")
    run_cmd(ssh, f"cat {REMOTE_DIR}/app/Models/User.php 2>&1 | head -30")
    
    # 3. 添加 deleted_at 列
    print("\n[3] Adding deleted_at column...")
    run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "ALTER TABLE oa_db.users ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL AFTER password;" 2>&1""")
    
    # 4. 验证
    print("\n[4] Verifying...")
    run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "DESCRIBE oa_db.users;" 2>&1""")
    
    # 5. 清除缓存
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 6. 设置权限并重启
    run_cmd(ssh, f"sudo chown -R www-data:www-data {REMOTE_DIR}")
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 7. 测试登录
    print("\n[5] Testing login...")
    run_cmd(ssh, f"sudo truncate -s 0 {REMOTE_DIR}/storage/logs/laravel.log")
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print(f"\n   Login response: {out[:500]}")
    
    # 8. 查看日志（如果有错误）
    code, out, err = run_cmd(ssh, f"cat {REMOTE_DIR}/storage/logs/laravel.log 2>&1 | head -50")
    
    # 9. 如果成功，测试 dashboard
    if '"token"' in out or '"user"' in out:
        print("\n[6] Login successful! Testing dashboard...")
        # 提取 token
        import json
        try:
            resp = json.loads(out)
            token = resp.get('token', resp.get('data', {}).get('token', ''))
            if token:
                code, out2, err2 = run_cmd(ssh, f"""curl -s http://localhost/api/dashboard/stats -H 'Authorization: Bearer {token}' -H 'Accept: application/json' 2>&1""")
                print(f"   Dashboard: {out2[:500]}")
        except:
            pass
    
    ssh.close()
    print(f"\nDone! URL: http://{SSH_HOST}")

if __name__ == "__main__":
    main()
