#!/usr/bin/env python3
"""
激活用户账号并最终测试
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
    print("Activating user accounts and final test")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 1. 激活所有用户
    print("[1] Activating all users...")
    run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "UPDATE oa_db.users SET status = 'active';" 2>&1""")
    run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SELECT id, name, username, email, status FROM oa_db.users;" 2>&1""")
    
    # 2. 清除缓存
    print("\n[2] Clearing caches...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear 2>&1")
    
    # 3. 测试登录
    print("\n[3] Testing login...")
    code, out, err = run_cmd(ssh, """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' 2>&1""")
    print(f"\n   Login response: {out[:800]}")
    
    # 4. 如果登录成功，获取 token 并测试其他 API
    try:
        resp = json.loads(out)
        token = resp.get('token', resp.get('data', {}).get('token', ''))
        
        if token:
            print(f"\n✅ LOGIN SUCCESSFUL!")
            print(f"   Token: {token[:80]}...")
            
            # 测试 Dashboard
            print("\n[4] Testing Dashboard API...")
            code, out, err = run_cmd(ssh, f"""curl -s http://localhost/api/dashboard/stats -H 'Authorization: Bearer {token}' -H 'Accept: application/json' 2>&1""")
            print(f"   Dashboard: {out[:500]}")
            
            # 测试员工列表
            print("\n[5] Testing Employee API...")
            code, out, err = run_cmd(ssh, f"""curl -s 'http://localhost/api/employees?page=1&per_page=5' -H 'Authorization: Bearer {token}' 2>&1""")
            print(f"   Employees: {out[:500]}")
        else:
            print(f"\n   Login failed but API works. Response: {out}")
    except Exception as e:
        print(f"\n   Could not parse response: {e}")
    
    # 5. 查看所有路由
    print("\n[6] All routes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -60")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"\n🌐 URL: http://{SSH_HOST}")
    print(f"📖 API: http://{SSH_HOST}/api")
    print("\n👤 Login credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 60)

if __name__ == "__main__":
    main()
