"""同步前端 dist 到 172.20.0.139"""
import paramiko
import os
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL = r'D:\work\website\OA\pc-web\dist'
REMOTE = '/var/www/oa-web'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

def run(cmd, t=60):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    return so.read().decode('utf-8', 'replace').strip()

# 备份旧前端
ts = int(__import__('time').time())
run(f'sudo cp -r {REMOTE} {REMOTE}.bak.{ts} 2>/dev/null || true')

# 清空
run(f'sudo rm -rf {REMOTE}/*')
run(f'sudo mkdir -p {REMOTE}')
run(f'sudo chown -R nbcy:nbcy {REMOTE}')

# 上传
sftp = ssh.open_sftp()
uploaded = 0
for dirpath, dirnames, filenames in os.walk(LOCAL):
    rel = os.path.relpath(dirpath, LOCAL).replace('\\', '/')
    remote_dir = posixpath.join(REMOTE, rel) if rel != '.' else REMOTE
    if rel != '.':
        try:
            sftp.stat(remote_dir)
        except IOError:
            run(f'mkdir -p {remote_dir}')
    for fn in filenames:
        local_fp = os.path.join(dirpath, fn)
        remote_fp = posixpath.join(remote_dir, fn)
        try:
            sftp.put(local_fp, remote_fp)
            uploaded += 1
        except Exception as e:
            print(f'  ERR: {fn}: {e}')
sftp.close()
print(f'上传完成: {uploaded} 个文件')

# 改 owner
run(f'sudo chown -R www-data:www-data {REMOTE}')

print('OK')
ssh.close()
