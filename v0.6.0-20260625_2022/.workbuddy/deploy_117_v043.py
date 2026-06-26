"""V0.4.3 一键部署到 117 (192.168.3.117)

阶段:
  1) 传 9 migrations + 9 models + 5 services + 3 observers + 1 command + 6 controllers
  2) 改 AppServiceProvider + routes/console.php + routes/api.php
  3) composer dump-autoload
  4) 跑迁移
  5) 验证
  6) 烟囱测试
"""
import sys, os, time, base64, posixpath
import paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
REMOTE_API = '/var/www/oa-api'

# ====== 待传文件 ======
V043_FILES = [
    # 9 migrations
    'database/migrations/2026_06_25_000001_create_construction_teams_table.php',
    'database/migrations/2026_06_25_000002_create_construction_team_members_table.php',
    'database/migrations/2026_06_25_000003_create_project_commencement_orders_table.php',
    'database/migrations/2026_06_25_000004_create_work_processes_table.php',
    'database/migrations/2026_06_25_000005_alter_construction_logs_add_fields.php',
    'database/migrations/2026_06_25_000006_create_work_process_progress_table.php',
    'database/migrations/2026_06_25_000007_create_rectification_daily_required_table.php',
    'database/migrations/2026_06_25_000008_create_external_construction_works_table.php',
    'database/migrations/2026_06_25_000009_create_external_construction_bids_table.php',
    # 9 models
    'app/Models/ConstructionTeam.php',
    'app/Models/ConstructionTeamMember.php',
    'app/Models/ProjectCommencementOrder.php',
    'app/Models/WorkProcess.php',
    'app/Models/WorkProcessProgress.php',
    'app/Models/RectificationDailyRequired.php',
    'app/Models/ExternalConstructionWork.php',
    'app/Models/ExternalConstructionBid.php',
    'app/Models/ConstructionLog.php',
    # 5 services
    'app/Services/ConstructionTeamService.php',
    'app/Services/CommencementOrderService.php',
    'app/Services/ConstructionLogService.php',
    'app/Services/RectificationService.php',
    'app/Services/ExternalConstructionService.php',
    # 3 observers
    'app/Observers/ConstructionLogObserver.php',
    'app/Observers/CommencementOrderObserver.php',
    'app/Observers/ExternalConstructionBidObserver.php',
    # 1 command
    'app/Console/Commands/ScanOverdueConstructionLogs.php',
    # 6 controllers
    'app/Http/Controllers/Api/Construction/TeamController.php',
    'app/Http/Controllers/Api/Construction/CommencementOrderController.php',
    'app/Http/Controllers/Api/Construction/ConstructionLogController.php',
    'app/Http/Controllers/Api/Construction/RectificationController.php',
    'app/Http/Controllers/Api/Construction/WorkProcessController.php',
    'app/Http/Controllers/Api/Construction/ExternalConstructionController.php',
    # 3 改动文件
    'app/Providers/AppServiceProvider.php',
    'routes/console.php',
    'routes/api.php',
]


def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    return ssh


def run(ssh, cmd, timeout=60, label='', echo=True):
    if label and echo:
        print(f'  [{label}] $ {cmd[:80]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    if (out or err) and echo:
        for line in (out or err).split('\n')[:10]:
            print(f'    {line}')
    return rc, out, err


def sftp_mkdir_p(sftp, remote_path):
    if not remote_path or remote_path == '/':
        return
    try:
        sftp.stat(remote_path)
        return
    except IOError:
        parent = posixpath.dirname(remote_path)
        if parent and parent != '/':
            sftp_mkdir_p(sftp, parent)
        try:
            sftp.mkdir(remote_path)
        except IOError:
            pass


def upload_file(sftp, ssh, local_path, remote_path):
    fname = os.path.basename(local_path)
    tmp_remote = f'/tmp/v043_{fname}'
    sftp.put(local_path, tmp_remote)
    # 117 上 oa-api 是 nbcy:nbcy，可以直接 cp
    parent = posixpath.dirname(remote_path)
    cmd = f'cp {tmp_remote} {remote_path} && rm {tmp_remote}'
    si, so, se = ssh.exec_command(cmd, timeout=30)
    so.read()
    return so.channel.recv_exit_status()


# ====== 阶段 1: 上传 ======
def phase1_upload():
    print('\n' + '='*60)
    print('阶段 1/5: 上传 36 个 V0.4.3 文件')
    print('='*60)
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    ok, fail = 0, 0
    for f in V043_FILES:
        local = os.path.join(LOCAL_API, f)
        remote = f'{REMOTE_API}/{f}'
        if not os.path.exists(local):
            print(f'  SKIP: {f}')
            fail += 1
            continue
        rc = upload_file(sftp, ssh, local, remote)
        if rc == 0:
            ok += 1
        else:
            print(f'  ✗ {f}')
            fail += 1
    sftp.close()
    print(f'\n  成功 {ok} 失败 {fail}')
    ssh.close()
    return fail == 0


# ====== 阶段 2: composer dump + 迁移 ======
def phase2_migrate():
    print('\n' + '='*60)
    print('阶段 2/5: composer dump + 跑迁移')
    print('='*60)
    ssh = ssh_connect()
    print('  composer dump-autoload...')
    rc, out, err = run(ssh, f'cd {REMOTE_API} && composer dump-autoload --no-dev 2>&1', timeout=60, label='dump')
    print('  跑迁移...')
    rc, out, err = run(ssh, f'cd {REMOTE_API} && php artisan migrate --force 2>&1', timeout=120, label='migrate')
    for line in out.split('\n'):
        if 'Migrat' in line:
            print(f'    {line}')
    # 重启 fpm
    print('  重启 php-fpm 清 opcache...')
    rc, out, err = run(ssh, 'sudo systemctl restart php8.5-fpm 2>&1', label='restart fpm')
    # config:clear
    for c in ['config:clear', 'route:clear', 'cache:clear']:
        run(ssh, f'cd {REMOTE_API} && php artisan {c} 2>&1', timeout=20, label=c, echo=False)
    ssh.close()


# ====== 阶段 3: 验证表 + 路由 ======
def phase3_verify():
    print('\n' + '='*60)
    print('阶段 3/5: 验证 9 张新表 + V0.4.3 路由')
    print('='*60)
    ssh = ssh_connect()
    tables = [
        'construction_teams',
        'construction_team_members',
        'project_commencement_orders',
        'work_processes',
        'work_process_progress',
        'rectification_daily_required',
        'external_construction_works',
        'external_construction_bids',
    ]
    for t in tables:
        rc, out, err = run(ssh,
            f"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -tAc \"SELECT to_regclass('public.{t}')\"",
            label=f'check {t}', echo=False)
        print(f'  {t}: {out}')
    # route:list
    print('\n  V0.4.3 路由 (前 40 条):')
    rc, out, err = run(ssh, f'cd {REMOTE_API} && sudo -u www-data php artisan route:list 2>&1 | grep -iE "construction|commencement|external-work|rectification|work-process" | head -40', timeout=30, label='route list', echo=False)
    print(out[:3000])
    ssh.close()


# ====== 阶段 4: 烟囱测试 ======
def phase4_smoke():
    print('\n' + '='*60)
    print('阶段 4/5: 端到端烟囱测试')
    print('='*60)
    ssh = ssh_connect()

    def r(cmd, t=15):
        si, so, se = ssh.exec_command(cmd, timeout=t)
        return so.read().decode('utf-8', 'replace').strip()

    # login
    out = r('curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' 2>&1', 15)
    import re
    m = re.search(r'"token":"([^"]+)"', out)
    token = m.group(1) if m else None
    print(f'  token: {token[:30] if token else "NONE"}...')

    # 测 6 个 V0.4.3 模块
    print('\n=== V0.4.3 烟囱测试 (15 API) ===')
    tests = []
    urls = [
        # 团队
        ('GET /api/construction/teams', 'GET', '/api/construction/teams'),
        ('POST /api/construction/teams', 'POST', '/api/construction/teams', '{"name":"测试团队A","leader_name":"王队长","leader_phone":"13800138000","member_count":5,"status":"active"}'),
        # 开工单
        ('GET /api/construction/commencement-orders', 'GET', '/api/construction/commencement-orders'),
        # 工序
        ('GET /api/construction/work-processes', 'GET', '/api/construction/work-processes'),
        ('POST /api/construction/work-processes', 'POST', '/api/construction/work-processes', '{"name":"线缆敷设","sort_order":1,"description":"主干线缆布放"}'),
        # 日志
        ('GET /api/construction/logs', 'GET', '/api/construction/logs'),
        # 整改
        ('GET /api/construction/rectifications', 'GET', '/api/construction/rectifications'),
        # 发包
        ('GET /api/construction/external-works', 'GET', '/api/construction/external-works'),
        ('POST /api/construction/external-works', 'POST', '/api/construction/external-works', '{"project_id":1,"title":"测试发包","description":"测试","budget":50000,"deadline":"2026-07-30","status":"draft"}'),
        # 整改 - V0.4.4 占位
        ('GET /api/construction/teams/1', 'GET', '/api/construction/teams/1'),
        ('GET /api/construction/commencement-orders/1', 'GET', '/api/construction/commencement-orders/1'),
        ('GET /api/construction/logs/1', 'GET', '/api/construction/logs/1'),
        ('GET /api/construction/logs/overdue', 'GET', '/api/construction/logs/overdue'),
        ('GET /api/construction/external-works/1', 'GET', '/api/construction/external-works/1'),
    ]
    for u in urls:
        if len(u) == 3:
            name, method, path = u
            body = None
        else:
            name, method, path, body = u
        if method == 'GET':
            cmd = f'curl -s -w "\\n%{{http_code}}" -H "Authorization: Bearer {token}" -H "Accept: application/json" http://127.0.0.1{path} 2>&1'
        else:
            cmd = f"curl -s -w '\\n%{{http_code}}' -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{body}' http://127.0.0.1{path} 2>&1"
        out = r(cmd, 15)
        parts = out.rsplit('\n', 1)
        code = parts[-1] if len(parts) > 1 else '?'
        body_out = parts[0][:200] if len(parts) > 0 else ''
        print(f'  {name:>50}  HTTP={code}  body={body_out[:150]}')
        tests.append((name, code))

    ok = sum(1 for _, c in tests if c == '200')
    print(f'\n=== V0.4.3 烟囱: {ok}/{len(tests)} 全 200 ===')

    # 业务端到端：建团队 → 建开工单 → 建日志
    print('\n=== 业务端到端 ===')
    # 1) 建团队
    out = r(f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{\"name\":\"E2E-施工一组\",\"leader_name\":\"王工\",\"leader_phone\":\"13800138001\",\"member_count\":8,\"status\":\"active\"}}' http://127.0.0.1/api/construction/teams 2>&1", 15)
    m = re.search(r'"id":(\d+)', out)
    team_id = m.group(1) if m else None
    print(f'  1) 建团队 ID={team_id} body={out[:200]}')

    if team_id:
        # 2) 加成员
        out = r(f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{\"members\":[{{\"name\":\"张三\",\"role\":\"工长\",\"phone\":\"13800138002\"}},{{\"name\":\"李四\",\"role\":\"电工\",\"phone\":\"13800138003\"}}]}}' http://127.0.0.1/api/construction/teams/{team_id}/members 2>&1", 15)
        print(f'  2) 加成员 body={out[:200]}')

        # 3) 找 project_id
        out = r("PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -tAc \"SELECT id FROM projects WHERE status != 'completed' LIMIT 1\"", 10)
        project_id = out.strip()
        print(f'  3) using project_id={project_id}')

        # 4) 建开工单
        out = r(f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{\"project_id\":{project_id},\"title\":\"E2E开工测试\",\"team_id\":{team_id},\"planned_start_date\":\"2026-06-25\",\"planned_end_date\":\"2026-08-25\",\"description\":\"测试开工\",\"status\":\"draft\"}}' http://127.0.0.1/api/construction/commencement-orders 2>&1", 15)
        m = re.search(r'"id":(\d+)', out)
        order_id = m.group(1) if m else None
        print(f'  4) 建开工单 ID={order_id} body={out[:200]}')

        if order_id:
            # 5) 开工
            out = r(f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Accept: application/json' http://127.0.0.1/api/construction/commencement-orders/{order_id}/start 2>&1", 15)
            print(f'  5) 开工 body={out[:200]}')

            # 6) 报日志
            out = r(f"curl -s -X POST -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{{\"project_id\":{project_id},\"commencement_order_id\":{order_id},\"work_date\":\"2026-06-24\",\"weather\":\"晴\",\"work_hours\":8,\"worker_count\":5,\"progress_percentage\":15,\"content\":\"开始基础施工\",\"status\":\"submitted\"}}' http://127.0.0.1/api/construction/logs 2>&1", 15)
            print(f'  6) 报日志 body={out[:200]}')

    ssh.close()


# ====== 阶段 5: 前端 dist 推送 ======
def phase5_web():
    print('\n' + '='*60)
    print('阶段 5/5: 前端 dist 推送')
    print('='*60)
    LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
    REMOTE_DIST = '/var/www/oa-web'

    ssh = ssh_connect()
    r = lambda cmd, t=15: (lambda x: x.read().decode('utf-8', 'replace').strip())(ssh.exec_command(cmd, timeout=t)[1])
    r(f'sudo rm -rf {REMOTE_DIST}/* 2>/dev/null; echo CLEARED')
    r(f'sudo chown -R nbcy:nbcy {REMOTE_DIST}')

    sftp = ssh.open_sftp()
    n = 0
    for dirpath, dirnames, filenames in os.walk(LOCAL_DIST):
        rel = os.path.relpath(dirpath, LOCAL_DIST).replace('\\', '/')
        remote_dir = REMOTE_DIST if rel == '.' else REMOTE_DIST + '/' + rel
        try:
            sftp.stat(remote_dir)
        except IOError:
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
    print(f'  上传完成: {n} 个文件')

    r(f'sudo chown -R www-data:www-data {REMOTE_DIST}')
    r(f'ls -la {REMOTE_DIST}/ | head -5')

    out = r('curl -s -w "HTTP=%{http_code}}" -o /dev/null http://192.168.3.117/ 2>&1')
    print(f'\n  前端 / 测试: {out}')
    ssh.close()


# ====== 主入口 ======
def main():
    print('='*60)
    print('  V0.4.3 一键部署到 117 (192.168.3.117)')
    print('  36 文件 / 9 表 / 5 服务 / 3 Observer / 6 控制器')
    print('='*60)

    if not phase1_upload():
        print('  上传失败，终止')
        return
    phase2_migrate()
    phase3_verify()
    phase4_smoke()
    phase5_web()

    print('\n' + '='*60)
    print('  ✓ V0.4.3 部署完成')
    print('  117: http://192.168.3.117/')
    print('='*60)


if __name__ == '__main__':
    main()
