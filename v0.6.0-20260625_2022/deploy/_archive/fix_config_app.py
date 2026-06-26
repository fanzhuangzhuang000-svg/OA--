#!/usr/bin/env python3
"""
修复 config/app.php：移除所有 Laravel 11 不需要的 Service Provider 引用
"""
import paramiko
import re

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
REMOTE_DIR = "/var/www/oa-api"

def run_cmd(ssh, cmd, timeout=60):
    """执行命令"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    return code, out, err

def fix_config_app_php(ssh):
    """下载、修复、上传 config/app.php"""
    print("Fixing config/app.php for Laravel 11...")
    
    # 1. 读取远程文件
    sftp = ssh.open_sftp()
    remote_file = f"{REMOTE_DIR}/config/app.php"
    local_temp = "D:/work/website/OA/deploy/app_temp.php"
    
    print(f"  Downloading {remote_file}...")
    try:
        sftp.get(remote_file, local_temp)
    except Exception as e:
        print(f"  ERROR downloading: {e}")
        # 尝试用 sudo 读取
        code, out, err = run_cmd(ssh, f"sudo cat {remote_file}")
        if code == 0:
            with open(local_temp, 'w', encoding='utf-8') as f:
                f.write(out)
            print("  Downloaded via sudo cat")
        else:
            print(f"  ERROR: {err}")
            return False
    
    # 2. 读取文件内容
    with open(local_temp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"  File size: {len(content)} bytes")
    
    # 3. 修复 providers 数组
    # 在 Laravel 11 中，只有 AppServiceProvider 需要保留
    # 移除所有对其他 Provider 的引用
    
    # 方法：找到 'providers' 数组，只保留 AppServiceProvider
    # 匹配 'providers' => [ ... ]
    
    # 只删除包含以下 Provider 的行：
    # - AuthServiceProvider
    # - RouteServiceProvider  
    # - EventServiceProvider
    # - BroadcastServiceProvider (如果有)
    
    original_len = len(content)
    
    # 删除包含旧 Provider 的行（支持多行）
    lines_to_remove = [
        'AuthServiceProvider',
        'RouteServiceProvider',
        'EventServiceProvider',
        'BroadcastServiceProvider',
    ]
    
    lines = content.split('\n')
    new_lines = []
    removed = 0
    for line in lines:
        should_remove = False
        for provider in lines_to_remove:
            if provider in line:
                should_remove = True
                removed += 1
                break
        if not should_remove:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    print(f"  Removed {removed} lines referencing old providers")
    
    # 4. 写回本地文件
    with open(local_temp, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 5. 上传回服务器
    print(f"  Uploading fixed file...")
    # 先改权限以便写入
    run_cmd(ssh, f"sudo chown nbcy:nbcy {remote_file}")
    sftp.put(local_temp, remote_file)
    run_cmd(ssh, f"sudo chown www-data:www-data {remote_file}")
    
    print("  Fixed!")
    sftp.close()
    return True

def main():
    print("=" * 60)
    print("Fixing config/app.php for Laravel 11")
    print("=" * 60)
    
    # 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS)
    print("Connected!")
    
    # 修复
    success = fix_config_app_php(ssh)
    
    if success:
        # 清除配置缓存
        print("\nClearing config cache...")
        run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan config:clear")
        run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan cache:clear")
        run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan optimize:clear")
        
        # 测试
        print("\nTesting artisan...")
        code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan --version 2>&1")
        print(f"  Output: {out}")
        if err:
            print(f"  Error: {err[:500]}")
        
        # 测试路由
        print("\nTesting routes...")
        code, out, err = run_cmd(ssh, f"cd {REMOTE_DIR} && sudo -u www-data php artisan route:list 2>&1 | head -30")
        if 'Error' not in out and 'not found' not in out:
            print(f"  Routes:\n{out[:1000]}")
        else:
            print(f"  Error: {err[:1000]}")
        
        # 重启服务
        print("\nRestarting services...")
        run_cmd(ssh, "sudo systemctl restart php8.3-fpm")
        run_cmd(ssh, "sudo systemctl restart nginx")
        
        # 测试 HTTP
        print("\nTesting HTTP...")
        code, out, err = run_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/ 2>&1")
        print(f"  HTTP Status: {out}")
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("Fix complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
