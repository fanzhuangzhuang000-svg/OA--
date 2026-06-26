"""部署 pc-web 到 172 服务器 (用 sudo cp)"""
import paramiko
import os

LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'
REMOTE_TMP = '/tmp/oa-web-deploy'
SSH_HOST = '172.20.0.139'
SSH_USER = 'nbcy'
SSH_PASS = 'admin123'


def main():
    print(f'==> 部署 {LOCAL_DIST} → {SSH_HOST}:{REMOTE_WEB}')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS)

    # 1. 准备远程 /tmp 目录
    ssh.exec_command(f'rm -rf {REMOTE_TMP} && mkdir -p {REMOTE_TMP}')

    # 2. sftp 上传到 /tmp
    sftp = ssh.open_sftp()
    n = 0
    for root, dirs, files in os.walk(LOCAL_DIST):
        rel_dir = os.path.relpath(root, LOCAL_DIST).replace('\\', '/')
        for f in files:
            local_path = os.path.join(root, f)
            remote_tmp = f'{REMOTE_TMP}/{rel_dir}/{f}' if rel_dir != '.' else f'{REMOTE_TMP}/{f}'
            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_tmp)
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                ssh.exec_command(f'mkdir -p {remote_dir}')
            sftp.put(local_path, remote_tmp)
            n += 1
    sftp.close()
    print(f'==> 上传到 /tmp 完成,{n} 个文件')

    # 3. sudo cp 到目标位置
    cmd = f'sudo cp -r {REMOTE_TMP}/* {REMOTE_WEB}/ && sudo chown -R www-data:www-data {REMOTE_WEB}/assets/* 2>/dev/null; echo COPY_DONE'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(f'==> cp 结果: {out.strip()}')
    if err:
        print(f'==> cp stderr: {err.strip()}')

    # 4. 清理 /tmp
    ssh.exec_command(f'rm -rf {REMOTE_TMP}')

    ssh.close()
    print('==> 部署完成')


if __name__ == '__main__':
    main()
