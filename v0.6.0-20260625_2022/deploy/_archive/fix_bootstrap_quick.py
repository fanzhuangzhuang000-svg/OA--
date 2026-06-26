#!/usr/bin/env python3
"""
快速修复 bootstrap/app.php 中的 api_prefix 错误
"""
import paramiko

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=60):
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
    print("Fixing bootstrap/app.php - Removing api_prefix...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!\n")
    
    # 下载
    sftp = ssh.open_sftp()
    local_temp = "D:/work/website/OA/deploy/bootstrap_app_temp.php"
    sftp.get(f"{REMOTE_DIR}/bootstrap/app.php", local_temp)
    
    with open(local_temp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Current:\n{content[:400]}")
    
    # 移除 api_prefix 行
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if 'api_prefix' not in line:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nFixed:\n{content[:400]}")
    
    # 上传
    run_cmd(ssh, f"sudo chown nbcy:nbcy {REMOTE_DIR}/bootstrap/app.php")
    sftp.put(local_temp, f"{REMOTE_DIR}/bootstrap/app.php")
    run_cmd(ssh, f"sudo chown www-data:www-data {REMOTE_DIR}/bootstrap/app.php")
    sftp.close()
    
    # 验证
    print("\nVerifying...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan --version 2>&1")
    print(f"\nArtisan version: {out.strip()}")
    
    # 运行迁移
    print("\nRunning migrations...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan migrate --force 2>&1")
    
    # 填充
    print("\nSeeding...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan db:seed --force 2>&1")
    
    # 清除缓存
    print("\nClearing cache...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
    
    # 重启
    run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
    run_cmd(ssh, "sudo systemctl restart nginx")
    
    # 测试
    print("\nTesting HTTP...")
    code, out, err = run_cmd(ssh, "curl -s http://localhost/ 2>&1", timeout=10)
    print(f"   Response: {out[:300]}")
    
    code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1", timeout=10)
    print(f"   HTTP Status: {out}")
    
    # 查看路由
    print("\nRoutes...")
    code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -80")
    
    # 查看用户
    print("\nUsers...")
    code, out, err = run_cmd(ssh, """sudo mysql -u debian-sys-maint -p'FLMoJ1vJcWhapbMF' -e "SELECT id, name, email, username FROM oa_db.users;" 2>&1""")
    
    ssh.close()
    
    print(f"\nDone! URL: http://{SSH_HOST}")

if __name__ == "__main__":
    main()
