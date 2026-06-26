import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 上传正确的配置文件
print('=== 1. 上传 Nginx 配置 ===')
sftp = ssh.open_sftp()
local = 'D:/work/website/OA/.workbuddy/nginx/oa-api.conf'
sftp.put(local.replace('\\', '/'), '/tmp/oa-api.conf')
print('✅ 配置文件已上传到 /tmp/oa-api.conf')

# 2. 清理 sites-enabled/ 目录
print('\n=== 2. 清理旧配置 ===')
cmds = [
    'sudo rm -f /etc/nginx/sites-enabled/oa-api.bak',
    'sudo rm -f /etc/nginx/sites-enabled/default',
    'sudo cp /tmp/oa-api.conf /etc/nginx/sites-available/oa-api',
    'sudo ln -sf /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api',
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=10)
    out = stdout.read().decode('utf-8', errors='replace')
    if out.strip():
        print(out[:200])

# 3. 测试 Nginx 配置
print('\n=== 3. 测试 Nginx 配置 ===')
stdin, stdout, stderr = ssh.exec_command('sudo nginx -t 2>&1', get_pty=True, timeout=10)
test_out = stdout.read().decode('utf-8', errors='replace')
print(test_out[:400])

if 'syntax is ok' in test_out.lower() or 'test is successful' in test_out.lower():
    print('✅ Nginx 配置测试通过')
    
    # 4. 重启 Nginx
    print('\n=== 4. 重启 Nginx ===')
    ssh.exec_command('sudo systemctl restart nginx', get_pty=True, timeout=15)
    
    # 5. 验证 80 端口
    print('\n=== 5. 验证 80 端口 ===')
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/health 2>&1',
        timeout=10
    )
    http_code = stdout.read().decode().strip()
    print(f'API 健康检测: HTTP {http_code}')
    
    if http_code == '200':
        print('✅ Nginx 配置完成！API 现已通过 80 端口访问')
    else:
        print('❌ API 不可达，请检查配置')
else:
    print('❌ Nginx 配置测试失败')
    stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-enabled/oa-api 2>&1', get_pty=True, timeout=10)
    print(stdout.read().decode()[:600])

sftp.close()
ssh.close()
print('\n完成')
