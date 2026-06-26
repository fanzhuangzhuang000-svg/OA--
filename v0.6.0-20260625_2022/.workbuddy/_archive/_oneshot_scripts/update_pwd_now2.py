import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

# 用 PHP 直接更新密码（写临时 PHP 文件到网站目录以外的安全位置）
php_code = """<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$user = App\Models\User::where('username','admin')->first();
if ($user) {
    $user->password = bcrypt('admin123');
    $user->save();
    echo 'OK: password updated for ' . $user->username;
} else {
    echo 'NOTFOUND';
}
"""
# 写到 /tmp（不需要 www-data 权限）
with open(r'D:\work\website\OA\.workbuddy\pwd_update.php', 'w') as f:
    f.write(php_code)

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\pwd_update.php', '/tmp/pwd_update.php')
sftp.close()

# 用 sudo 以 www-data 身份运行
stdin, stdout, stderr = ssh.exec_command('sudo php /tmp/pwd_update.php 2>&1 && sudo rm /tmp/pwd_update.php')
out = stdout.read().decode()
err = stderr.read().decode()
print('OUTPUT:', out)
if err.strip():
    print('STDERR:', err[:600])

ssh.close()
print('done')
