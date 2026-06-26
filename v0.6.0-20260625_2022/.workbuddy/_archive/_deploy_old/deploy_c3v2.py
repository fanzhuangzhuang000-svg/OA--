"""
C3 后端修复 + 部署 + 单元测试 (走内网 172.20.0.139 nbcy 用户)
"""
import paramiko, sys, time, urllib.request, urllib.parse, json, re

HOST = '172.20.0.139'
USER = 'nbcy'
PWD  = 'admin123'
API  = 'http://172.20.0.139:3001'
LOCAL = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php'
REMOTE = '/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php'

def sftp_put(sftp, local, remote):
    sftp.put(local, remote)

def ssh_cmd(ssh, cmd, timeout=30):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    return so.read().decode('utf-8', errors='ignore'), se.read().decode('utf-8', errors='ignore')

def main():
    print('=== C3 deploy (intranet) ===')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD)
    sftp = ssh.open_sftp()

    # 1) 上传文件
    print(f'[1] upload {LOCAL} -> {REMOTE}')
    sftp.put(LOCAL, REMOTE)
    sftp.chmod(REMOTE, 0o664)

    # 2) 校验 syntax
    print('[2] php -l syntax check')
    out, err = ssh_cmd(ssh, f'php -l {REMOTE}')
    print(out or err)
    if 'No syntax errors' not in (out + err):
        print('SYNTAX FAIL'); sys.exit(1)

    # 3) 清缓存
    print('[3] clear caches')
    for c in ['php artisan optimize:clear', 'php artisan config:clear', 'php artisan route:clear']:
        out, err = ssh_cmd(ssh, f'cd /var/www/oa-api && {c} 2>&1')
        print(f'  {c}: {(out+err).strip()[:120]}')

    # 4) 重启 fpm (route cache 改完需要)
    print('[4] restart php-fpm')
    out, err = ssh_cmd(ssh, 'sudo systemctl restart php8.3-fpm 2>&1')
    print(out or err)

    # 5) 拿 token 测接口
    print('[5] login to get token')
    body = json.dumps({'username': 'admin', 'password': 'admin123'}).encode()
    req = urllib.request.Request(f'{API}/api/auth/login', data=body, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        token = data.get('data', {}).get('token') or data.get('token')
        print(f'  token={token[:30] if token else None}...')
    except Exception as e:
        print(f'  login err: {e}')
        token = None

    # 6) GET /api/dashboard/screen
    print('[6] GET /api/dashboard/screen')
    req = urllib.request.Request(f'{API}/api/dashboard/screen', headers={'Accept': 'application/json', 'Authorization': f'Bearer {token}'} if token else {'Accept': 'application/json'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        body = resp.read().decode()
        data = json.loads(body)
        if data.get('code') == 0:
            d = data['data']
            print('  ✅ 200 OK')
            print(f'  metrics:        {len(d["metrics"])} items')
            for m in d['metrics']: print(f'    - {m["label"]:10s} = {m["value"]}')
            print(f'  revenueChart:   {len(d["revenueChart"])} months')
            for r in d['revenueChart'][:3]: print(f'    - {r["month"]:4s} value={r["value"]:.0f} h={r["height"]:.0f}')
            print(f'  projectStatus:  {len(d["projectStatus"])} stages')
            for s in d['projectStatus']: print(f'    - {s["label"]:6s} count={s["count"]} pct={s["pct"]}%')
            print(f'  serviceMetrics: SLA={d["serviceMetrics"]["sla"]}% avgResp={d["serviceMetrics"]["avgResponseText"]} sat={d["serviceMetrics"]["satisfaction"]}/5.0')
            print(f'  todos:          {len(d["todos"])} items')
            for t in d['todos']: print(f'    - {t["label"]:12s} count={t["count"]}')
        else:
            print(f'  ✗ business err: {data}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        print(f'  ✗ HTTP {e.code}: {body[:600]}')
    except Exception as e:
        print(f'  ✗ {e}')

    ssh.close()

if __name__ == '__main__':
    main()
