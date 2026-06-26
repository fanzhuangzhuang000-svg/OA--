import paramiko

# 172 服务器信息
host = '172.20.0.139'
username = 'nbcy'
password = 'admin123'
remote_api_dir = '/var/www/oa-api'

print('=== 更新 admin 密码 ===\n')

# 连接服务器
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)
print('✅ 连接成功')

# 上传密码更新脚本到 Laravel 项目目录
print('\n上传密码更新脚本...')
sftp = ssh.open_sftp()
local_script = r'D:\work\website\OA\.workbuddy\update_admin_password.php'
remote_script = f'{remote_api_dir}/update_admin_password.php'
sftp.put(local_script, remote_script)
sftp.close()
print('✅ 上传完成')

# 运行密码更新脚本
print('\n运行密码更新脚本...')
stdin, stdout, stderr = ssh.exec_command(
    f'cd {remote_api_dir} && sudo -u www-data php update_admin_password.php 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'输出: {output}')
if err:
    print(f'错误: {err[:300]}')

# 删除临时脚本
print('\n删除临时脚本...')
stdin, stdout, stderr = ssh.exec_command(f'rm {remote_script}')
stdout.read()
print('✅ 删除完成')

ssh.close()

print('\n=== ✅ 密码更新完成 ===')
print('\n请测试:')
print('  1. 清除浏览器缓存 (Ctrl+F5)')
print('  2. 访问 http://172.20.0.139')
print('  3. 使用 admin / admin123 登录')
print('  4. 检查密码提示是否显示')
print('  5. 检查是否还有自动填充')
