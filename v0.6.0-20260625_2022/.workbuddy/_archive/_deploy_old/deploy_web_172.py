import paramiko, os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

# 1) sftp 上传 dist
sftp = ssh.open_sftp()
local_dist = 'D:/work/website/OA/pc-web/dist'
remote_dist = '/tmp/oa-web-dist'

try:
    ssh.exec_command('rm -rf /tmp/oa-web-dist')
except: pass

def upload_dir(local, remote):
    try:
        sftp.mkdir(remote)
    except: pass
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
    'sudo chown -R nbcy:nbcy /var/www/oa-web',
    'sudo rm -rf /var/www/oa-web.bak',
    'sudo mv /var/www/oa-web /var/www/oa-web.bak',
    'sudo mkdir -p /var/www/oa-web',
    'sudo chown nbcy:nbcy /var/www/oa-web',
    'cp -r /tmp/oa-web-dist/. /var/www/oa-web/',
    'sudo chown -R www-data:www-data /var/www/oa-web',
    'sudo rm -rf /tmp/oa-web-dist',
    'ls /var/www/oa-web | head -5',
    'cat /var/www/oa-web/index.html | grep "assets/index"',
]
for c in cmds:
    print('===', c)
    stdin, stdout, stderr = ssh.exec_command(c)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out.strip(): print(out.strip()[:300])
    if err.strip() and 'cannot' not in err.lower(): print('ERR:', err.strip()[:300])

# 3) reload php-fpm
print('\n=== reload php-fpm ===')
stdin, stdout, stderr = ssh.exec_command('sudo systemctl reload php8.3-fpm && echo OK')
print(stdout.read().decode('utf-8', errors='ignore'))
print(stderr.read().decode('utf-8', errors='ignore'))

ssh.close()
print('\nDONE')
