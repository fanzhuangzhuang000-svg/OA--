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
print('✅ 连接成功\n')

# 在服务器上直接创建 PHP 脚本并运行
print('创建密码更新脚本...')
php_script = '''<?php
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
use App\Models\User;
$user = User::where('username', 'admin')->first();
if ($user) {
    $user->password = bcrypt('admin123');
    $user->save();
    echo "✅ 密码已更新为 admin123\n";
} else {
    echo "❌ 未找到 admin 用户\n";
}
'''

# 将脚本写入服务器
stdin, stdout, stderr = ssh.exec_command(
    f'cat > /tmp/update_pwd.php << \'EOF\'\n{php_script}EOF\n'
)
stdout.read()
err = stderr.read().decode()
if err:
    print(f'错误: {err[:200]}')

# 复制到 Laravel 目录
print('复制到 Laravel 目录...')
stdin, stdout, stderr = ssh.exec_command(
    'sudo cp /tmp/update_pwd.php /var/www/oa-api/ && sudo chown www-data:www-data /var/www/oa-api/update_pwd.php'
)
stdout.read()
err = stderr.read().decode()
if err:
    print(f'错误: {err[:200]}')

# 运行脚本
print('运行密码更新脚本...\n')
stdin, stdout, stderr = ssh.exec_command(
    'cd /var/www/oa-api && sudo -u www-data php update_pwd.php 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'输出: {output}')
if err:
    print(f'错误: {err[:300]}')

# 删除临时脚本
print('\n删除临时脚本...')
stdin, stdout, stderr = ssh.exec_command(
    'rm /tmp/update_pwd.php && rm /var/www/oa-api/update_pwd.php'
)
stdout.read()
print('✅ 删除完成')

ssh.close()

print('\n=== ✅ 密码更新完成 ===')
print('\n请测试:')
print('  1. 清除浏览器缓存 (Ctrl+F5)')
print('  2. 访问 http://172.20.0.139')
print('  3. 使用 admin / admin123 登录')
