import paramiko
import os
import time

# 172 服务器信息
host = '172.20.0.139'
username = 'nbcy'
password = 'admin123'
remote_web_dir = '/var/www/oa-web'
local_dist = r'D:\work\website\OA\pc-web\dist'

print('=== 部署前端到 172.20.0.139 ===\n')

# 连接服务器
print('1. 连接服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)
print('   ✅ 连接成功')

# 上传 dist 目录下的所有文件
print('\n2. 上传前端文件...')
sftp = ssh.open_sftp()

# 递归上传目录
def upload_dir(local_path, remote_path):
    for item in os.listdir(local_path):
        local_item = os.path.join(local_path, item)
        remote_item = remote_path + '/' + item
        if os.path.isdir(local_item):
            try:
                sftp.mkdir(remote_item)
            except:
                pass
            upload_dir(local_item, remote_item)
        else:
            sftp.put(local_item, remote_item)
            print(f'   上传: {item}')

upload_dir(local_dist, remote_web_dir)
sftp.close()
print('   ✅ 上传完成')

# 设置权限
print('\n3. 设置文件权限...')
stdin, stdout, stderr = ssh.exec_command(f'sudo chown -R www-data:www-data {remote_web_dir}')
stdout.read()
print('   ✅ 权限设置完成')

# 重启 Nginx
print('\n4. 重启 Nginx...')
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart nginx')
stdout.read()
print('   ✅ Nginx 重启完成')

# 更新 admin 密码
print('\n5. 更新 admin 用户密码...')
stdin, stdout, stderr = ssh.exec_command(
    "cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute=\"\\$user = App\Models\User::where('username', 'admin')->first(); if (\\$user) { \\$user->password = bcrypt('admin123'); \\$user->save(); echo 'Password updated'; } else { echo 'User not found'; }\" 2>&1"
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'   输出: {output}')
if err:
    print(f'   错误: {err[:200]}')

ssh.close()

print('\n=== ✅ 部署完成 ===')
print('\n请测试:')
print('  1. 清除浏览器缓存 (Ctrl+F5)')
print('  2. 访问 http://172.20.0.139')
print('  3. 使用 admin / admin123 登录')
print('  4. 检查密码提示是否显示')
print('  5. 检查是否还有自动填充')
