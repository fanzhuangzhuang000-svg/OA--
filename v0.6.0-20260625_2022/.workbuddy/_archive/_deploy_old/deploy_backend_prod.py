import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# 1. 备份当前后端代码
print('=== 1. 备份当前后端代码 ===')
cmd1 = 'cd /var/www && sudo cp -r oa-api oa-api-bak-$(date +%Y%m%d-%H%M) && echo "备份完成"'
stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True, timeout=60)
out1 = stdout.read().decode('utf-8', errors='replace')
print(out1[:200])

# 2. 上传后端代码打包文件
print('\n=== 2. 上传后端代码打包文件 ===')
sftp = ssh.open_sftp()
local_file = 'D:/work/website/OA/oa-api-code.tar.gz'
remote_tmp = '/tmp/oa-api-code.tar.gz'
print(f'上传 {local_file} -> {remote_tmp}...')
sftp.put(local_file.replace('\\', '/'), remote_tmp)
print('✅ 上传完成')

# 3. 解压代码文件（覆盖 app/, config/, routes/, database/, resources/, bootstrap/, public/）
print('\n=== 3. 解压代码文件 ===')
cmd3 = '''cd /var/www/oa-api && \
sudo tar -xzf /tmp/oa-api-code.tar.gz --overwrite && \
sudo chown -R www-data:www-data /var/www/oa-api/ && \
echo "解压完成"'''
stdin, stdout, stderr = ssh.exec_command(cmd3, get_pty=True, timeout=60)
out3 = stdout.read().decode('utf-8', errors='replace')
print(out3[:400])

# 4. 验证 .env 文件还在
print('\n=== 4. 验证 .env 文件 ===')
cmd4 = 'cat /var/www/oa-api/.env | grep -E "APP_ENV|APP_DEBUG|DB_DATABASE"'
stdin, stdout, stderr = ssh.exec_command(cmd4, get_pty=True, timeout=10)
out4 = stdout.read().decode('utf-8', errors='replace')
print(out4[:300])

# 5. 运行数据库迁移
print('\n=== 5. 运行数据库迁移 ===')
cmd5 = 'cd /var/www/oa-api && sudo -u www-data php artisan migrate --force 2>&1 | tail -20'
stdin, stdout, stderr = ssh.exec_command(cmd5, get_pty=True, timeout=60)
out5 = stdout.read().decode('utf-8', errors='replace')
print(out5[:400])

# 6. 重启 PHP-FPM
print('\n=== 6. 重启 PHP-FPM ===')
cmd6 = 'sudo systemctl restart php8.3-fpm && echo "重启完成"'
stdin, stdout, stderr = ssh.exec_command(cmd6, get_pty=True, timeout=15)
out6 = stdout.read().decode('utf-8', errors='replace')
print(out6[:200])

# 7. 验证 API 是否可用
print('\n=== 7. 验证 API 是否可用 ===')
import time
time.sleep(2)
cmd7 = 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/health 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd7, timeout=10)
http_code = stdout.read().decode().strip()
print(f'API 健康检查: HTTP {http_code}')

if http_code == '200':
    print('✅ 后端部署完成！API 已可用')
else:
    print('❌ API 不可用，请检查日志')

sftp.close()
ssh.close()
print('\n✅ 部署完成')
