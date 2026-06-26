"""部署库存表单抽屉到 172.20.0.139 - 先传 /tmp 再 sudo cp"""
import paramiko, os, posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'
REMOTE_TMP = '/tmp/oa-web-deploy'

def main():
    print(f'==> Deploy dist -> {HOST}:{REMOTE_WEB}')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

    # 1) 清空远程 tmp
    ssh.exec_command(f'rm -rf {REMOTE_TMP} && mkdir -p {REMOTE_TMP}')
    print(f'  [PREP] {REMOTE_TMP} ready')

    # 2) 上传到 tmp (nbcy 用户有写权限)
    sftp = ssh.open_sftp()
    n = 0
    for root, dirs, files in os.walk(LOCAL_DIST):
        rel = os.path.relpath(root, LOCAL_DIST).replace('\\', '/')
        tmp_dir = REMOTE_TMP if rel == '.' else posixpath.join(REMOTE_TMP, rel)
        try:
            sftp.stat(tmp_dir)
        except IOError:
            ssh.exec_command(f'mkdir -p {tmp_dir}')
        for f in files:
            local = posixpath.join(root.replace('\\', '/'), f)
            tmp_remote = posixpath.join(tmp_dir, f)
            sftp.put(local, tmp_remote)
            n += 1
    sftp.close()
    print(f'  [SFTP] {n} files -> {REMOTE_TMP}')

    # 3) sudo cp + chown 一次性
    cmd = f'sudo rm -rf {REMOTE_WEB} && sudo cp -r {REMOTE_TMP} {REMOTE_WEB} && sudo chown -R www-data:www-data {REMOTE_WEB} && sudo rm -rf {REMOTE_TMP}'
    si, so, se = ssh.exec_command(cmd, timeout=120)
    so.read()
    print('  [CP] dist -> /var/www/oa-web, www-data owner')

    # 4) 验证
    si, so, se = ssh.exec_command(f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1{REMOTE_WEB}/index.html')
    print(f'  [VERIFY] index.html HTTP {so.read().decode().strip()}')
    ssh.close()
    print('==> Done')

if __name__ == '__main__':
    main()