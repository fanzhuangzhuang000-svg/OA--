import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# 1. 备份当前前端文件
print('=== 1. 备份当前前端文件 ===')
cmd1 = 'cd /var/www && sudo cp -r oa-web oa-web-bak-$(date +%Y%m%d-%H%M) && echo "备份完成"'
stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True, timeout=30)
out1 = stdout.read().decode('utf-8', errors='replace')
print(out1[:200])

# 2. 上传前端打包文件
print('\n=== 2. 上传前端打包文件 ===')
sftp = ssh.open_sftp()
local_file = 'D:/work/website/OA/oa-web-dist.tar.gz'
remote_tmp = '/tmp/oa-web-dist.tar.gz'
print(f'上传 {local_file} -> {remote_tmp}...')
sftp.put(local_file.replace('\\', '/'), remote_tmp)
print('✅ 上传完成')

# 3. 清空 oa-web 目录并解压
print('\n=== 3. 解压前端文件 ===')
cmd3 = 'cd /var/www/oa-web && sudo rm -rf * && sudo tar -xzf /tmp/oa-web-dist.tar.gz --strip-components=1 && sudo chown -R www-data:www-data /var/www/oa-web/ && echo "解压完成"'
stdin, stdout, stderr = ssh.exec_command(cmd3, get_pty=True, timeout=30)
out3 = stdout.read().decode('utf-8', errors='replace')
print(out3[:300])

# 4. 验证前端文件
print('\n=== 4. 验证前端文件 ===')
cmd4 = 'ls -lh /var/www/oa-web/ 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd4, get_pty=True, timeout=10)
out4 = stdout.read().decode('utf-8', errors='replace')
print(out4[:400])

sftp.close()
ssh.close()
print('\n✅ 前端部署完成')
