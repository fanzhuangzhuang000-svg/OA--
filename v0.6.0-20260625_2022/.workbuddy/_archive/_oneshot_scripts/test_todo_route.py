"""直接路由到 DashboardController@todo 看错误"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/test_route.php', 'w') as f:
    f.write('''<?php
require __DIR__.'/../var/www/oa-api/vendor/autoload.php';
$app = require_once __DIR__.'/../var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

try {
    $controller = new App\\Http\\Controllers\\Api\\DashboardController();
    $result = $controller->todo();
    echo "OK: " . $result->getContent() . "\\n";
} catch (Throwable $e) {
    echo "ERR: " . $e->getMessage() . "\\n";
    echo "FILE: " . $e->getFile() . ":" . $e->getLine() . "\\n";
    echo "TRACE: " . substr($e->getTraceAsString(), 0, 1500) . "\\n";
}
''')
sftp.close()

def run(cmd, t=15):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

# 清日志
run('sudo truncate -s 0 /var/www/oa-api/storage/logs/laravel.log', t=5)

# 跑
out = run('cd /var/www/oa-api && sudo -u www-data php /tmp/test_route.php 2>&1')
print('=== 直接调 todo ===')
print(out)

print()
out = run('sudo tail -3 /var/www/oa-api/storage/logs/laravel.log 2>/dev/null | head -c 2000')
print('=== laravel.log ===')
print(out)
