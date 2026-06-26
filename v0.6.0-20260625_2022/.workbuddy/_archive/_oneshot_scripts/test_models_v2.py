"""通过 artisan tinker 测试模型"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/test_models.php', 'w') as f:
    f.write('''<?php
require __DIR__.'/../var/www/oa-api/vendor/autoload.php';
$app = require_once __DIR__.'/../var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

$models = ['ExpenseClaim','LeaveRequest','ServiceOrder','Receivable','Project','AttendanceRecord'];
foreach ($models as $m) {
    try {
        $cls = 'App\\\\Models\\\\' . $m;
        $c = $cls::count();
        echo "$m: $c\\n";
    } catch (Throwable $e) {
        echo "$m: ERR " . $e->getMessage() . "\\n";
    }
}
''')
sftp.close()

def run(cmd, t=15):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

# 跑测试
out = run('cd /var/www/oa-api && sudo -u www-data php /tmp/test_models.php 2>&1')
print('=== 模型测试（带 app context）===')
print(out)
