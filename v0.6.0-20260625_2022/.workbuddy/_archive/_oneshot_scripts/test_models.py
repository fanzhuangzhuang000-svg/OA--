"""测各模型的 count()"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/test_models.php', 'w') as f:
    f.write('''<?php
$models = [
    'App\\Models\\ExpenseClaim',
    'App\\Models\\LeaveRequest',
    'App\\Models\\ServiceOrder',
    'App\\Models\\Receivable',
    'App\\Models\\Project',
    'App\\Models\\AttendanceRecord',
];
foreach ($models as $m) {
    try {
        $c = $m::count();
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

out = run('cd /var/www/oa-api && sudo -u www-data php /tmp/test_models.php 2>&1')
print('=== 模型测试 ===')
print(out)

# 测 Project::take(5) -> get
sftp = ssh.open_sftp()
with sftp.file('/tmp/test2.php', 'w') as f:
    f.write('''<?php
try {
    $list = \\App\\Models\\Project::orderBy('updated_at', 'desc')->take(5)->get(['id','name','stage','progress','end_date']);
    echo "Project list count: " . $list->count() . "\\n";
} catch (Throwable $e) {
    echo "Project list ERR: " . $e->getMessage() . "\\n";
}
''')
sftp.close()

out = run('cd /var/www/oa-api && sudo -u www-data php /tmp/test2.php 2>&1')
print('=== Project list ===')
print(out)
