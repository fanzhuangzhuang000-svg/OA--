"""
Sync server controllers -> local + cleanup ModuleControllers
Bypasses Git Bash Python path issue by cd-ing into target dir.
"""
import paramiko, os, hashlib, io

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
REMOTE = '/var/www/oa-api/app/Http/Controllers/Api'
LOCAL = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api'

os.chdir(LOCAL)  # change to target dir so open() works

def md5(b):
    return hashlib.md5(b).hexdigest()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS)
sftp = ssh.open_sftp()

attrs = sftp.listdir_attr(REMOTE)
pulled, skipped, failed = [], [], []
for a in sorted(attrs, key=lambda x: x.filename):
    name = a.filename
    if not name.endswith('.php'):
        continue
    with sftp.open(f'{REMOTE}/{name}', 'rb') as f:
        srv = f.read()
    srv_md5 = md5(srv)

    local_path = f'{LOCAL}/{name}'
    if os.path.exists(local_path):
        with open(local_path, 'rb') as f:
            loc = f.read()
        loc_md5 = md5(loc)
        if srv_md5 == loc_md5:
            skipped.append(f'{name} (same)')
            continue
    # write
    try:
        with open(local_path, 'wb') as f:
            f.write(srv)
        pulled.append(f'{name} ({len(srv)}B)')
    except Exception as e:
        failed.append(f'{name}: {e}')

# remove ModuleControllers.php
mc = f'{LOCAL}/ModuleControllers.php'
if os.path.exists(mc):
    os.remove(mc)
    print('REMOVED ModuleControllers.php')

sftp.close()
ssh.close()

print(f'PULLED: {len(pulled)}')
for p in pulled: print(f'  + {p}')
print(f'SKIPPED: {len(skipped)}')
for s in skipped: print(f'  = {s}')
if failed:
    print('FAILED:')
    for f in failed: print(f'  ! {f}')
