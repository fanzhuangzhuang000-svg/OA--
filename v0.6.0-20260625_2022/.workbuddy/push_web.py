"""推送前端 dist 到 172 — 通过 /tmp 中转 + sudo cp"""
import paramiko
import posixpath
import os
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)
sftp = ssh.open_sftp()

LOCAL = r'D:\work\website\OA\pc-web\dist'
REMOTE = '/var/www/oa-web'
TMP = '/tmp/oaweb'

# 1. 清空 /tmp/oaweb，建目录
ssh.exec_command(f'rm -rf {TMP} && mkdir -p {TMP}')
import time
time.sleep(1)

count = 0
errs = 0
for root, dirs, files in os.walk(LOCAL):
    rel = os.path.relpath(root, LOCAL)
    rel_norm = rel.replace('\\', '/')
    tmp_dir = posixpath.join(TMP, rel_norm)
    remote_dir = posixpath.join(REMOTE, rel_norm)
    # tmp 建目录
    try:
        sftp.mkdir(tmp_dir)
    except IOError:
        pass
    # remote 建目录
    ssh.exec_command(f'sudo -u www-data mkdir -p {remote_dir}')
    for f in files:
        local_path = os.path.join(root, f)
        tmp_path = posixpath.join(tmp_dir, f)
        remote_path = posixpath.join(remote_dir, f)
        try:
            # nbcy → /tmp（无权限问题）
            sftp.put(local_path, tmp_path)
            # sudo cp + chown（一次性）
            cmd = f'sudo -u www-data cp {tmp_path} {remote_path} && sudo -u www-data chown www-data:www-data {remote_path} && rm {tmp_path}'
            si, so, se = ssh.exec_command(cmd, timeout=30)
            so.read()
            count += 1
        except Exception as e:
            errs += 1
            if errs <= 3:
                print(f'  ERR {remote_path}: {e}')

print(f'上传完成: {count} 成功 / {errs} 失败')

# 2. 清理
ssh.exec_command(f'rm -rf {TMP}')

sftp.close()
ssh.close()
