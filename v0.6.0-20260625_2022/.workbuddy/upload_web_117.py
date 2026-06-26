"""117 前端 dist 上传"""
import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', username='nbcy', password='admin123', timeout=15)


def run(cmd, t=15):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    return so.read().decode('utf-8', 'replace').strip()


LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_DIST = '/var/www/oa-web'

# 1. 清空 oa-web
out = run(f'sudo rm -rf {REMOTE_DIST}/* 2>/dev/null; echo CLEARED')
print('clear:', out)

# 2. chown 让 nbcy 能写
run(f'sudo chown -R nbcy:nbcy {REMOTE_DIST}')

# 3. 递归上传
sftp = ssh.open_sftp()
n = 0
for dirpath, dirnames, filenames in os.walk(LOCAL_DIST):
    rel = os.path.relpath(dirpath, LOCAL_DIST).replace('\\', '/')
    remote_dir = REMOTE_DIST if rel == '.' else REMOTE_DIST + '/' + rel

    try:
        sftp.stat(remote_dir)
    except IOError:
        # 创建目录
        parts = remote_dir.split('/')
        cur = ''
        for p in parts:
            if not p:
                continue
            cur += '/' + p
            try:
                sftp.stat(cur)
            except IOError:
                try:
                    sftp.mkdir(cur)
                except IOError:
                    pass

    for f in filenames:
        local = os.path.join(dirpath, f)
        remote = remote_dir + '/' + f
        sftp.put(local, remote)
        n += 1
sftp.close()
print(f'  uploaded: {n} files')

# 4. chown www-data
run(f'sudo chown -R www-data:www-data {REMOTE_DIST}')

# 5. 验证
out = run(f'ls -la {REMOTE_DIST} | head -10')
print(f'\n=== oa-web ===\n{out}')

# 6. 测试前端
out = run(f'curl -s -w "HTTP=%{{http_code}}\\n" http://192.168.3.117/ 2>&1 | head -3', 15)
print(f'\n=== / test ===\n{out[:500]}')

# 7. 测试 assets
import glob
js_assets = glob.glob(LOCAL_DIST + r'\assets\*.js')[:1]
if js_assets:
    js_name = os.path.basename(js_assets[0])
    out = run(f'curl -s -w "HTTP=%{{http_code}}\\n" http://192.168.3.117/assets/{js_name} 2>&1 | head -3', 15)
    print(f'\n=== assets/{js_name} ===\n{out[:300]}')

ssh.close()
