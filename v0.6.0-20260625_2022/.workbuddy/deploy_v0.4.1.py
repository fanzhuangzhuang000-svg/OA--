"""V0.4.1 一键部署 v2 — 修复版
- 直接 cp（nbcy:nbcy 归属）
- 数据库 security_oa
"""
import sys, os, time
import paramiko
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
REMOTE_API = '/var/www/oa-api'

V041_FILES = [
    'database/migrations/2026_06_24_100000_create_project_budgets_table.php',
    'database/migrations/2026_06_24_100001_create_project_budget_items_table.php',
    'database/migrations/2026_06_24_100002_create_project_actual_costs_table.php',
    'app/Models/ProjectBudget.php',
    'app/Models/ProjectBudgetItem.php',
    'app/Models/ProjectActualCost.php',
    'app/Services/ProjectBudgetService.php',
    'app/Observers/StockRecordObserver.php',
    'app/Observers/ExpenseClaimObserver.php',
    'app/Events/BudgetWarning.php',
    'app/Events/BudgetExceeded.php',
    'app/Rules/BudgetNotExceeded.php',
    'app/Http/Controllers/Api/Construction/BudgetController.php',
    'app/Console/Commands/SyncProjectActualCosts.php',
]

def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    return ssh

def run(ssh, cmd, t=60, label='', echo=True):
    if label and echo:
        print(f'  [{label}] $ {cmd[:80]}')
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    return rc, out, err

def sftp_mkdir_p(sftp, remote_path):
    if remote_path == '/':
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
    """nbcy 上传 nbcy 文件 - 直接 put"""
    fname = os.path.basename(local_path)
    tmp_remote = f'/tmp/v041_{fname}'
    sftp.put(local_path, tmp_remote)
    sftp_mkdir_p(sftp, posixpath.dirname(remote_path))
    # nbcy → nbcy 归属，无需 sudo
    cmd = f'cp {tmp_remote} {remote_path} && rm {tmp_remote}'
    si, so, se = ssh.exec_command(cmd, timeout=30)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    rc = so.channel.recv_exit_status()
    return rc, out, err

ssh = ssh_connect()
sftp = ssh.open_sftp()
print('=' * 60)
print('V0.4.1 部署 v2 → 172.20.0.139')
print('=' * 60)

# 1. 上传 14 个后端文件
print('\n[1/3] 上传后端 14 个文件')
ok, fail = 0, 0
for f in V041_FILES:
    local = os.path.join(LOCAL_API, f)
    remote = f'{REMOTE_API}/{f}'
    if not os.path.exists(local):
        print(f'  SKIP: {f}')
        fail += 1
        continue
    rc, out, err = upload_file(sftp, ssh, local, remote)
    if rc == 0:
        print(f'  ✓ {f}')
        ok += 1
    else:
        print(f'  ✗ {f}  ERR: {err[:120]}')
        fail += 1
print(f'  后端: {ok} 成功 / {fail} 失败')

# 2. 跑迁移（DB_DATABASE=security_oa）
print('\n[2/3] 跑迁移')
rc, out, err = run(ssh, f'php {REMOTE_API}/artisan migrate --force 2>&1', t=120, label='migrate')
print(out[:1000])
if err:
    print(f'  ERR: {err[:300]}')

# 3. 验证 3 张表
print('\n[3/3] 验证 3 张表就位')
for t in ['project_budgets', 'project_budget_items', 'project_actual_costs']:
    rc, out, err = run(ssh, f'PGPASSWORD=$(grep DB_PASSWORD /var/www/oa-api/.env | cut -d= -f2) psql -h 127.0.0.1 -U oa_user -d security_oa -tA -c "SELECT to_regclass(\'public.{t}\')"', label='check')
    print(f'  {t}: {out}')

# 4. 清缓存 + 重启 php-fpm
print('\n[Bonus] 清缓存 + 重启')
for c in ['config:clear', 'route:clear', 'cache:clear']:
    run(ssh, f'php {REMOTE_API}/artisan {c} 2>&1', label=c, echo=False)
rc, out, err = run(ssh, 'sudo systemctl restart php8.3-fpm 2>&1 || sudo systemctl restart php-fpm 2>&1', label='restart php-fpm')
if rc == 0:
    print('  ✓ php-fpm 重启完成')
else:
    print(f'  WARN: {err[:200]}')

sftp.close()
ssh.close()
print('\n' + '=' * 60)
print('V0.4.1 部署完成')
print('=' * 60)
