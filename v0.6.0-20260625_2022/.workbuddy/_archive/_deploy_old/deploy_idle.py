"""Deploy pc-web dist to 172 server"""
import os
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
sftp = ssh.open_sftp()

local_dir = r'D:\work\website\OA\pc-web\dist'
remote_dir = '/tmp/oa_dist'
target_dir = '/var/www/oa-web'

# Cleanup and create remote tmp
ssh.exec_command(f'rm -rf {remote_dir} && mkdir -p {remote_dir}')

# Upload all files
file_count = 0
for root, dirs, files in os.walk(local_dir):
    for f in files:
        local_path = os.path.join(root, f)
        rel = os.path.relpath(local_path, local_dir).replace(os.sep, '/')
        remote_path = f'{remote_dir}/{rel}'
        # ensure parent dir
        remote_parent = os.path.dirname(remote_path).replace(os.sep, '/')
        ssh.exec_command(f'mkdir -p {remote_parent}')
        sftp.put(local_path, remote_path)
        file_count += 1

print(f'[1] Uploaded: {file_count} files')
sftp.close()

# Deploy - 用 cp 同步内容,先清空目标再复制
deploy_cmds = [
    f'sudo rm -rf {target_dir}/*',
    f'sudo cp -r {remote_dir}/. {target_dir}/',
    f'sudo chown -R www-data:www-data {target_dir}',
    f'sudo rm -rf {remote_dir}',
    f'ls -la {target_dir}/ | head -3',
    f'echo "FILES: $(find {target_dir} -type f | wc -l)"',
]
for cmd in deploy_cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f'  > {cmd[:60]}\n    {out[:300]}')
    if err: print(f'  ERR: {err[:300]}')

ssh.close()
print('[3] Deploy done')
