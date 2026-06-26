import paramiko

# 172 服务器信息
host = '172.20.0.139'
username = 'nbcy'
password = 'admin123'

print('=== 更新 admin 密码为 admin123 ===\n')

# 连接服务器
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)
print('✅ 连接成功')

# 方法1：使用 PHP 命令直接更新密码
print('\n方法1：使用 PHP 命令更新密码...')
php_code = '''
$password = password_hash('admin123', PASSWORD_DEFAULT);
echo $password;
'''
stdin, stdout, stderr = ssh.exec_command(f'php -r "{php_code}" 2>&1')
bcrypt_hash = stdout.read().decode().strip()
err = stderr.read().decode()
if err:
    print(f'  错误: {err[:200]}')
    
if bcrypt_hash and len(bcrypt_hash) > 20:
    print(f'  生成 bcrypt 哈希: {bcrypt_hash[:30]}...')
    
    # 使用 psql 更新密码
    print('\n方法2：使用 psql 更新数据库...')
    sql = f"UPDATE users SET password = '{bcrypt_hash}' WHERE username = 'admin';"
    stdin, stdout, stderr = ssh.exec_command(
        f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
    )
    output = stdout.read().decode()
    err = stderr.read().decode()
    print(f'  输出: {output}')
    if err:
        print(f'  错误: {err[:200]}')
else:
    print('  ❌ 生成 bcrypt 哈希失败')

# 方法3：使用 Laravel tinker 更新密码
print('\n方法3：使用 Laravel tinker 更新密码...')
stdin, stdout, stderr = ssh.exec_command(
    'cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="'
    "App\\Models\\User::where(\'username\', \'admin\')->first()->update([\'password\' => bcrypt(\'admin123\')]);'
    '" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'  输出: {output[:300]}')
if err:
    print(f'  错误: {err[:200]}')

ssh.close()

print('\n=== ✅ 密码更新完成 ===')
print('\n请测试:')
print('  1. 清除浏览器缓存 (Ctrl+F5)')
print('  2. 访问 http://172.20.0.139')
print('  3. 使用 admin / admin123 登录')
