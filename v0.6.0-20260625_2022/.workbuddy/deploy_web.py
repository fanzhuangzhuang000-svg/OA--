import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.')

# 1) sftp 上传 dist/ (整体)
sftp = ssh.open_sftp()
local_dist = 'D:/work/website/OA/pc-web/dist'
remote_dist = '/tmp/oa-web-dist'

# 先清远程
try:
    ssh.exec_command('rm -rf /tmp/oa-web-dist')
except: pass

# 递归上传
def upload_dir(local, remote):
    sftp.mkdir(remote)
    for name in os.listdir(local):
        lp = os.path.join(local, name)
        rp = remote + '/' + name
        if os.path.isdir(lp):
            upload_dir(lp, rp)
        else:
            sftp.put(lp, rp)

upload_dir(local_dist, remote_dist)
sftp.close()
print('uploaded dist')

# 2) 替换 /var/www/oa-web
cmds = [
    'sudo rm -rf /var/www/oa-web',
    'sudo mkdir -p /var/www/oa-web',
    'sudo mv /tmp/oa-web-dist/* /var/www/oa-web/ 2>&1 | tail -2',
    'sudo mv /tmp/oa-web-dist/.[!.]* /var/www/oa-web/ 2>/dev/null',
    'sudo chown -R www-data:www-data /var/www/oa-web',
    'sudo rm -rf /tmp/oa-web-dist',
    'ls /var/www/oa-web | head -5',
    'ls /var/www/oa-web/assets | head -3',
]
for c in cmds:
    print('===', c)
    stdin, stdout, stderr = ssh.exec_command(c)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out.strip(): print(out.strip()[:200])
    if err.strip() and 'cannot' not in err.lower(): print('ERR:', err.strip()[:200])

# 3) reload php-fpm
print('\n=== reload php-fpm ===')
stdin, stdout, stderr = ssh.exec_command('sudo systemctl reload php8.3-fpm && echo "FPM reloaded"')
print(stdout.read().decode('utf-8', errors='ignore'))
print(stderr.read().decode('utf-8', errors='ignore'))

ssh.close()
print('\nDONE')
