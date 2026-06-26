import paramiko, os, glob

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1. 打包 dist 目录
dist_dir = r'D:\work\website\OA\pc-web\dist'
files = []
for root, _, fnames in os.walk(dist_dir):
    for f in fnames:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, dist_dir).replace('\\', '/')
        files.append((full, rel))

print(f"Total files: {len(files)}")

# 2. 上传 + 部署
sftp = ssh.open_sftp()
uploaded = 0
for local, rel in files:
    remote_tmp = f'/tmp/oa-web-staging/{rel}'
    remote_final = f'/var/www/oa-web/{rel}'
    # 确保远程目录存在
    remote_dir = os.path.dirname(remote_tmp).replace('\\', '/')
    stdin, stdout, stderr = ssh.exec_command(f'mkdir -p "{remote_dir}"')
    stdout.read()
    sftp.put(local, remote_tmp)

    # 复制到目标
    stdin, stdout, stderr = ssh.exec_command(
        f'mkdir -p "{os.path.dirname(remote_final).replace(chr(92), "/")}" && '
        f'sudo cp "{remote_tmp}" "{remote_final}" && '
        f'sudo chown www-data:www-data "{remote_final}" && '
        f'rm "{remote_tmp}"'
    )
    stdout.read()
    err = stderr.read().decode()
    if err.strip():
        print(f"  ERR {rel}: {err[:100]}")
    uploaded += 1
    if uploaded % 20 == 0:
        print(f"  {uploaded}/{len(files)}")
sftp.close()

print(f"Deployed {uploaded} files")

# 3. 重启 nginx（清缓存）
stdin, stdout, stderr = ssh.exec_command('sudo nginx -s reload 2>&1')
out = stdout.read().decode()
err = stderr.read().decode()
print(f"Nginx reload: out={out.strip()}, err={err.strip()}")

ssh.close()
print("DONE")
