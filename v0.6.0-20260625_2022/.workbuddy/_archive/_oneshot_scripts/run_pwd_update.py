import paramiko, getpass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 用密码认证（paramiko 不读 SSH config，不受公钥偏好影响）
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 用 Laravel 的 php 命令直接更新密码
cmd = (
    "cd /var/www/oa-api && "
    "sudo -u www-data php -r "
    "'require \"vendor/autoload.php\"; "
    "$app = require \"bootstrap/app.php\"; "
    "$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); "
    "$u = App\\Models\\User::where(\"username\",\"admin\")->first(); "
    "if($u){$u->password = bcrypt(\"admin123\"); $u->save(); echo \"OK:".$u->username;}"
    "' 2>&1"
)
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print("OUTPUT:", out)
if err.strip():
    print("STDERR:", err[:600])

ssh.close()
print("done")
