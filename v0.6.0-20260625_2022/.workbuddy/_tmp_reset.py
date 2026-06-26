import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)

# 用临时脚本方式执行（避免 Python 转义问题）
php_script = r"""<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
$users = App\Models\User::whereIn('username', ['admin', 'nbcy'])->get();
foreach ($users as $u) {
    $u->password = Illuminate\Support\Facades\Hash::make('admin123');
    $u->save();
    echo "Reset: " . $u->username . "\n";
}
echo "DONE\n";
"""
import io
sftp = ssh.open_sftp()
with sftp.file('/tmp/reset_pwd.php', 'w') as f:
    f.write(php_script)

si, so, se = ssh.exec_command('php /tmp/reset_pwd.php 2>&1', timeout=60)
out = so.read().decode('utf-8', 'replace').strip()
err = se.read().decode('utf-8', 'replace').strip()
rc = so.channel.recv_exit_status()
print('Reset:', rc)
print(out)
print('ERR:', err[:300])
ssh.exec_command('rm /tmp/reset_pwd.php')
sftp.close()
ssh.close()
