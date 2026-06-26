"""部署新前端 dist/ 到 172.20.0.139"""
import paramiko, os, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')
sftp = c.open_sftp()

LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
STAGING = '/tmp/oa-web-staging'

# 1. 上传
print('[1/4] 上传 dist 到 staging...')
ssh_exec = c.exec_command('rm -rf ' + STAGING)
ssh_exec[1].read()
time.sleep(1)
try: sftp.mkdir(STAGING)
except: pass

count = 0
for root, dirs, files in os.walk(LOCAL_DIST):
    rel = os.path.relpath(root, LOCAL_DIST)
    remote_dir = STAGING if rel == '.' else STAGING + '/' + rel.replace('\\', '/')
    try: sftp.mkdir(remote_dir)
    except: pass
    for fn in files:
        local_path = os.path.join(root, fn).replace('\\', '/')
        remote_path = remote_dir + '/' + fn
        sftp.put(local_path, remote_path)
        count += 1
print(f'  上传 {count} 文件')

# 2. 备份 + 覆盖
print('[2/4] 备份 + 覆盖...')
ts = time.strftime('%Y%m%d_%H%M%S')
cmd = f'sudo -n bash -c "mv /var/www/oa-web /var/www/oa-web.bak.{ts} && cp -r {STAGING} /var/www/oa-web && chown -R www-data:www-data /var/www/oa-web && rm -rf {STAGING}"'
si, so, se = c.exec_command(cmd, timeout=60)
err = se.read().decode('utf-8', errors='ignore')
if err and 'unable to resolve host' not in err:
    print(f'  ERR: {err[:300]}')
else:
    print('  OK')

# 3. 验证
print('[3/4] 验证...')
for c_cmd in [
    'ls -la /var/www/oa-web/index.html',
    'stat /var/www/oa-web/index.html | grep Modify',
    'ls /var/www/oa-web/assets/ | head -10',
    'grep -c "purchase.getRequirements" /var/www/oa-web/assets/index-CPKvPOAw.js 2>/dev/null || echo 0',
    'grep -c "mockList" /var/www/oa-web/assets/index-CPKvPOAw.js 2>/dev/null || echo 0',
]:
    si, so, se = c.exec_command(c_cmd, timeout=15)
    out = so.read().decode('utf-8', errors='ignore').strip()
    print(f'  {out[:300]}')

# 4. curl 验证
print('[4/4] curl 验证...')
c_cmd = 'curl -sI http://127.0.0.1/'
si, so, se = c.exec_command(c_cmd, timeout=10)
print(so.read().decode('utf-8', errors='ignore'))

c_cmd = 'curl -s http://127.0.0.1/ | grep -E "title|index-"'
si, so, se = c.exec_command(c_cmd, timeout=10)
print(so.read().decode('utf-8', errors='ignore'))

# 5. 业务流 E2E（验证前端调 API 真的通）
print('[5/5] API 直连验证（前端会调的）...')
c_cmd = '''curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' | head -c 200'''
si, so, se = c.exec_command(c_cmd, timeout=10)
print(so.read().decode('utf-8', errors='ignore')[:300])

c.close()
print('\n=== DONE ===')
