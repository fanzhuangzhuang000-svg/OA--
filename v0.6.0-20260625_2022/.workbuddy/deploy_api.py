"""
v0.3.7.3 部署脚本 — 上传后端文件 + 清理缓存 + reload PHP-FPM
使用方式: python deploy_api.py <file1> [file2] ...
"""
import sys
import os
import paramiko
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
REMOTE_ROOT = '/var/www/oa-api'
LOCAL_ROOT = r'D:\work\website\OA\pc-api'

def ssh_exec(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    return out, err

def sftp_upload(sftp, local_path, remote_path):
    """递归创建远程目录并上传文件"""
    parent = posixpath.dirname(remote_path)
    parts = parent.replace(REMOTE_ROOT, '').strip('/').split('/')
    cur = REMOTE_ROOT
    for p in parts:
        if not p:
            continue
        cur = f'{cur}/{p}'
        try:
            sftp.stat(cur)
        except IOError:
            try:
                sftp.mkdir(cur)
            except IOError:
                pass
    sftp.put(local_path, remote_path)

def main():
    files = sys.argv[1:]
    if not files:
        print("用法: python deploy_api.py <file1> [file2] ...\n例如: python deploy_api.py app/Http/Controllers/Api/EmployeeController.php routes/api.php")
        return 1

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)

    # 先把目标路径 chown 给 nbcy，方便上传
    print("[pre] chown 目标路径给 nbcy")
    for f in files:
        remote = f"{REMOTE_ROOT}/{f.replace('\\\\', '/').replace('\\', '/')}"
        out, err = ssh_exec(ssh, f"sudo -n chown -R nbcy:nbcy {remote} 2>&1; echo OK")
        print(f"  {f}: {out.strip() or err.strip()}")

    sftp = ssh.open_sftp()
    print(f"\n[upload] 准备上传 {len(files)} 个文件")
    for f in files:
        local = os.path.join(LOCAL_ROOT, f.replace('/', os.sep))
        remote = f"{REMOTE_ROOT}/{f.replace('\\', '/')}"
        if not os.path.exists(local):
            print(f"  [SKIP] {f} (本地不存在)")
            continue
        sftp_upload(sftp, local, remote)
        print(f"  [OK]   {f}")

    sftp.close()

    # 修正 owner 为 www-data
    print("\n[fix] 修正 owner 为 www-data")
    for f in files:
        remote = f"{REMOTE_ROOT}/{f.replace('\\', '/')}"
        out, err = ssh_exec(ssh, f"sudo -n chown -R www-data:www-data {remote} 2>&1; echo OK")
        print(f"  {f}: {out.strip() or err.strip()}")

    print("\n[cache] 清理路由/配置/视图缓存")
    for cmd in [
        f"cd {REMOTE_ROOT} && php artisan route:clear",
        f"cd {REMOTE_ROOT} && php artisan config:clear",
        f"cd {REMOTE_ROOT} && php artisan cache:clear",
        f"cd {REMOTE_ROOT} && php artisan view:clear",
    ]:
        out, err = ssh_exec(ssh, cmd)
        print(f"  {cmd.split('&& ')[-1]}: {out.strip() or err.strip() or 'OK'}")

    # 找 PHP-FPM master
    print("\n[fpm] reload PHP-FPM")
    out, err = ssh_exec(ssh, "ps -ef | grep -E 'php-fpm.*master' | grep -v grep | awk '{print $2}' | head -1")
    pid = out.strip()
    if pid:
        out, err = ssh_exec(ssh, f"sudo -n kill -USR2 {pid} 2>&1; echo RELOADED")
        print(f"  USR2 -> pid {pid}: {out.strip() or err.strip()}")
    else:
        print("  [WARN] 没找到 php-fpm master")

    ssh.close()
    print("\n[done] 后端部署完成")
    return 0

if __name__ == '__main__':
    sys.exit(main())
