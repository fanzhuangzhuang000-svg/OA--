import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

# 写 PHP 脚本到 /tmp
php = '''<?php
require '/var/www/oa-api/vendor/autoload.php';
$app = require '/var/www/oa-api/bootstrap/app.php';
$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);
$kernel->bootstrap();
echo 'CONST: ' . (defined('App\\Models\\Supplier::STATUS_ACTIVE') ? App\\Models\\Supplier::STATUS_ACTIVE : 'NO_CONST') . "\\n";
echo 'AGING METHOD: ' . (method_exists('App\\Http\\Controllers\\Api\\LedgerController', 'agingByModel') ? 'YES' : 'NO') . "\\n";
// 查 LedgerController aging 方法内容
$ref = new ReflectionMethod('App\\Http\\Controllers\\Api\\LedgerController', 'agingByModel');
$lines = file($ref->getFileName());
$start = $ref->getStartLine();
echo 'AGING BODY: ' . trim($lines[$start + 1] ?? '') . "\\n";
'''

with sftp.file('/tmp/check_const.php', 'w') as f:
    f.write(php)

si, so, se = ssh.exec_command('php /tmp/check_const.php 2>&1', timeout=30)
print('output:')
print(so.read().decode('utf-8', 'replace'))
print('err:', so.read().decode('utf-8', 'replace'))
sftp.close()
ssh.close()
