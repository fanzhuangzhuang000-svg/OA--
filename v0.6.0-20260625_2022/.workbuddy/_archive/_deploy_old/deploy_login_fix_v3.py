import paramiko
import os
import time

# 172 服务器信息
host = '172.20.0.139'
username = 'nbcy'
password = 'admin123'
remote_web_dir = '/var/www/oa-web'
remote_api_dir = '/var/www/oa-api'
local_dist = r'D:\work\website\OA\pc-web\dist'

print('=== 部署前端到 172.20.0.139 ===\n')

# 连接服务器
print('1. 连接服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)
print('   ✅ 连接成功')

# 清空远程 web 目录（使用 sudo）
print('\n2. 清空远程 web 目录...')
stdin, stdout, stderr = ssh.exec_command(f'sudo rm -rf {remote_web_dir}/*')
stdout.read()
print('   ✅ 清空完成')

# 重新创建 web 目录
print('\n3. 创建 web 目录...')
stdin, stdout, stderr = ssh.exec_command(f'sudo mkdir -p {remote_web_dir}')
stdout.read()
print('   ✅ 目录创建完成')

# 上传 dist 文件到 /tmp
print('\n4. 上传前端文件到 /tmp...')
sftp = ssh.open_sftp()

# 先上传到 /tmp/oa-web
tmp_dir = '/tmp/oa-web'
stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {tmp_dir}')
stdout.read()

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

upload_dir(local_dist, tmp_dir)
sftp.close()
print('   ✅ 上传完成')

# 使用 sudo cp 复制到目标目录
print('\n5. 复制文件到 web 目录...')
stdin, stdout, stderr = ssh.exec_command(f'sudo cp -r {tmp_dir}/* {remote_web_dir}/')
stdout.read()
err = stderr.read().decode()
if err:
    print(f'   警告: {err[:200]}')

# 设置权限
print('\n6. 设置文件权限...')
stdin, stdout, stderr = ssh.exec_command(f'sudo chown -R www-data:www-data {remote_web_dir}')
stdout.read()
print('   ✅ 权限设置完成')

# 清理临时文件
print('\n7. 清理临时文件...')
stdin, stdout, stderr = ssh.exec_command(f'sudo rm -rf {tmp_dir}')
stdout.read()
print('   ✅ 清理完成')

# 重启 Nginx
print('\n8. 重启 Nginx...')
stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart nginx')
stdout.read()
print('   ✅ Nginx 重启完成')

# 上传密码更新脚本
print('\n9. 更新 admin 密码...')
sftp = ssh.open_sftp()
local_script = r'D:\work\website\OA\.workbuddy\update_admin_password.php'
remote_script = '/tmp/update_admin_password.php'
sftp.put(local_script, remote_script)
sftp.close()

# 运行密码更新脚本
stdin, stdout, stderr = ssh.exec_command(f'cd {remote_api_dir} && php {remote_script} 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
print(f'   输出: {output}')
if err:
    print(f'   错误: {err[:200]}')

# 删除临时脚本
stdin, stdout, stderr = ssh.exec_command(f'rm {remote_script}')
stdout.read()

ssh.close()

print('\n=== ✅ 部署完成 ===')
print('\n请测试:')
print('  1. 清除浏览器缓存 (Ctrl+F5)')
print('  2. 访问 http://172.20.0.139')
print('  3. 使用 admin / admin123 登录')
print('  4. 检查密码提示是否显示')
print('  5. 检查是否还有自动填充')
