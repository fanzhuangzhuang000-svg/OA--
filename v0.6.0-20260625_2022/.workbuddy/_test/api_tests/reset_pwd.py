import paramiko, sys
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')
import importlib.util
spec = importlib.util.spec_from_file_location('deploy', r'D:\work\website\OA\.workbuddy\deploy_to_172.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ssh = m.ssh_connect()

# 重置 admin (id=1) 密码
si, so, se = ssh.exec_command(
    'cd /var/www/oa-api && php -r "require \\"vendor/autoload.php\\"; $app = require \\"bootstrap/app.php\\"; $app->make(\\\\Illuminate\\\\Contracts\\\\Console\\\\Kernel::class)->bootstrap(); '
    '$u = \\App\\Models\\User::find(1); $u->password = bcrypt(\\"admin123\\"); $u->save(); echo \\"OK user=".$u->username."\\n"; '
    '$u2 = \\App\\Models\\User::where(\\"username\\",\\"nbcy\\")->first(); if($u2){$u2->password=bcrypt(\\"admin123\\"); $u2->save(); echo \\"OK nbcy\\n";}"',
    timeout=30
)
out = so.read().decode('utf-8', errors='replace')
err = se.read().decode('utf-8', errors='replace')
print('OUT:', out)
print('ERR:', err)
ssh.close()
