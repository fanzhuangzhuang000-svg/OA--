"""V0.4.4 修复 patch 推 117 - 走 /tmp 中转 + sudo cp"""
import sys, time, os, paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
REMOTE_API = '/var/www/oa-api'

PATCH_FILES = [
    'app/Http/Controllers/Api/Construction/TeamController.php',
    'app/Http/Controllers/Api/Construction/CommencementOrderController.php',
    'app/Http/Controllers/Api/Construction/ConstructionLogController.php',
    'app/Http/Controllers/Api/Construction/ExternalConstructionController.php',
    'app/Http/Controllers/Api/Construction/RectificationController.php',
    'app/Services/ConstructionTeamService.php',
    'app/Services/CommencementOrderService.php',
    'app/Services/ConstructionLogService.php',
    'app/Services/ExternalConstructionService.php',
    'app/Services/RectificationService.php',
    'app/Models/Rectification.php',
    'app/Models/ProjectCommencementOrder.php',
    'app/Models/WorkProcessProgress.php',
    'app/Models/ConstructionTeamMember.php',
    'app/Observers/ConstructionLogObserver.php',
    'app/Observers/CommencementOrderObserver.php',
    'database/migrations/2026_06_24_000001_create_rectifications_v044_table.php',
    'database/migrations/2026_06_24_000002_add_commencement_order_id_to_rdr.php',
]


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    sftp = ssh.open_sftp()

    print(f'=== [1/4] 上传 {len(PATCH_FILES)} 个修复文件到 /tmp ===')
    for rel in PATCH_FILES:
        local = f'{LOCAL_API}/{rel}'.replace('\\', '/')
        name = os.path.basename(rel)
        remote = f'/tmp/{name}'
        sftp.put(local, remote)
        size = os.path.getsize(local)
        print(f'    ✓ {name} ({size}B)')

    sftp.close()

    print('\n=== [2/4] sudo cp + chown + optimize:clear + restart fpm ===')
    cmds = []
    for rel in PATCH_FILES:
        name = os.path.basename(rel)
        cmds.append(f'sudo -n cp /tmp/{name} {REMOTE_API}/{rel}')
    cmds.append(f'sudo -n chown -R nbcy:nbcy {REMOTE_API}/app/Http/Controllers/Api/Construction {REMOTE_API}/app/Services {REMOTE_API}/app/Models {REMOTE_API}/database/migrations')
    cmds.append(f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan migrate --force 2>&1 | tail -10')
    cmds.append(f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan optimize:clear 2>&1 | tail -3')
    cmds.append('sudo -n systemctl restart php8.5-fpm')
    cmds.append('sleep 2')
    cmds.append('sudo -n systemctl status php8.5-fpm | head -3')

    for cmd in cmds:
        print(f'  $ {cmd[:100]}')
        si, so, se = ssh.exec_command(cmd, timeout=60)
        out = so.read().decode('utf-8', 'replace').strip()
        err = se.read().decode('utf-8', 'replace').strip()
        rc = so.channel.recv_exit_status()
        if rc != 0:
            print(f'    ✗ rc={rc} err={err[:200]}')
        else:
            print(f'    ✓ rc={rc}')

    time.sleep(2)

    print('\n=== [3/4] 登录拿 token ===')
    si, so, se = ssh.exec_command(
        '''curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' ''',
        timeout=30
    )
    out = so.read().decode('utf-8', 'replace').strip()
    import json
    login = json.loads(out)
    token = (login.get('data') or {}).get('token') or login.get('token')
    if not token:
        print(f'  login fail: {out[:200]}')
        return
    print(f'    ✓ token={token[:30]}...')

    print('\n=== [4/4] 烟囱测试 ===')
    # GET 列表
    for label, path in [
        ('GET 团队', '/api/construction/teams'),
        ('GET 开工单', '/api/construction/commencement-orders'),
        ('GET 施工日志', '/api/construction/logs'),
        ('GET 工序字典', '/api/construction/work-processes'),
        ('GET 整改', '/api/construction/rectifications'),
        ('GET 发包', '/api/construction/external-works?project_id=1'),
    ]:
        cmd = f"""curl -s -o /tmp/out -w "%{{http_code}}" 'http://127.0.0.1{path}' -H 'Authorization: Bearer {token}' -H 'Accept: application/json'"""
        si, so, se = ssh.exec_command(cmd, timeout=30)
        http_code = so.read().decode('utf-8', 'replace').strip()
        si2, so2, se2 = ssh.exec_command('cat /tmp/out', timeout=10)
        body = so2.read().decode('utf-8', 'replace').strip()
        try:
            j = json.loads(body)
            code = j.get('code', '?')
            data = j.get('data', {})
            total = data.get('total', '?') if isinstance(data, dict) else (len(data) if isinstance(data, list) else '?')
            print(f'    [{label}] http={http_code} code={code} total={total}')
        except Exception:
            print(f'    [{label}] http={http_code} body={body[:120]}')

    # 项目 id 用于 POST
    si, so, se = ssh.exec_command(
        f"curl -s 'http://127.0.0.1/api/projects?per_page=1' -H 'Authorization: Bearer {token}' -H 'Accept: application/json'",
        timeout=30
    )
    body = so.read().decode('utf-8', 'replace').strip()
    try:
        j = json.loads(body)
        items = j.get('data', {}).get('data', []) if isinstance(j.get('data'), dict) else j.get('data', [])
        pid = items[0].get('id') if items else 1
    except Exception:
        pid = 1
    print(f'\n  project_id={pid}')

    # POST 关键 action
    actions = [
        ('POST 团队', 'POST', '/api/construction/teams', f'{{"project_id":{pid},"team_name":"验收测试-A","team_type":"internal","leader_name":"张班长","leader_phone":"13800138000"}}'),
        ('POST 开工单', 'POST', '/api/construction/commencement-orders', f'{{"project_id":{pid},"planned_start_date":"2026-06-25","planned_end_date":"2026-07-25","work_scope":"验收测试","safety_requirements":"注意安全"}}'),
        ('POST 工序', 'POST', '/api/construction/work-processes', '{"name":"验收工序-001","sequence":1,"status":"active"}'),
        ('POST 整改', 'POST', '/api/construction/rectifications', f'{{"project_id":{pid},"source_type":"audit","title":"验收整改","description":"整改内容","severity":"medium"}}'),
        ('POST 发包', 'POST', '/api/construction/external-works', f'{{"project_id":{pid},"title":"验收发包","type":"outsource","budget":50000,"deadline":"2026-07-15","description":"验收测试发包"}}'),
        ('POST 日志', 'POST', '/api/construction/logs', f'{{"commencement_order_id":1,"project_id":{pid},"work_date":"2026-06-24","content":"验收日志内容","progress_percentage":50}}'),
    ]
    for label, method, path, body in actions:
        cmd = f"""curl -s -X {method} 'http://127.0.0.1{path}' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{body}'"""
        si, so, se = ssh.exec_command(cmd, timeout=30)
        body_out = so.read().decode('utf-8', 'replace').strip()
        try:
            j = json.loads(body_out)
            code = j.get('code', '?')
            msg = j.get('message', '')[:50]
            data_id = (j.get('data') or {}).get('id') if isinstance(j.get('data'), dict) else None
            print(f'    [{label}] code={code} id={data_id} msg={msg}')
        except Exception:
            print(f'    [{label}] body={body_out[:150]}')

    ssh.close()
    print('\n=== 完成 ===')


if __name__ == '__main__':
    main()
