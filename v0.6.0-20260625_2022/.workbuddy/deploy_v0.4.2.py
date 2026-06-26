"""V0.4.2 一键部署 v1 — 38 个文件"""
import sys, os, time
import paramiko
import posixpath

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
REMOTE_API = '/var/www/oa-api'

V042_FILES = [
    # 12 migrations
    'database/migrations/2026_06_24_110000_create_suppliers_table.php',
    'database/migrations/2026_06_24_110001_create_supplier_contacts_table.php',
    'database/migrations/2026_06_24_110002_create_supplier_evaluations_table.php',
    'database/migrations/2026_06_24_110003_create_supplier_attachments_table.php',
    'database/migrations/2026_06_24_110004_create_external_quote_requests_table.php',
    'database/migrations/2026_06_24_110005_create_external_quotes_table.php',
    'database/migrations/2026_06_24_110006_create_supplier_payables_table.php',
    'database/migrations/2026_06_24_110007_create_supplier_payments_table.php',
    'database/migrations/2026_06_24_110008_create_customer_receivables_table.php',
    'database/migrations/2026_06_24_110009_create_customer_receipts_table.php',
    'database/migrations/2026_06_24_110010_alter_users_add_supplier_fields.php',
    'database/migrations/2026_06_24_110011_alter_stock_records_add_batch_fields.php',
    # 10 models
    'app/Models/Supplier.php',
    'app/Models/SupplierContact.php',
    'app/Models/SupplierEvaluation.php',
    'app/Models/SupplierAttachment.php',
    'app/Models/ExternalQuoteRequest.php',
    'app/Models/ExternalQuote.php',
    'app/Models/SupplierPayable.php',
    'app/Models/SupplierPayment.php',
    'app/Models/CustomerReceivable.php',
    'app/Models/CustomerReceipt.php',
    # 3 services
    'app/Services/SupplierService.php',
    'app/Services/ExternalQuoteService.php',
    'app/Services/LedgerService.php',
    # 4 controllers
    'app/Http/Controllers/Api/SupplierController.php',
    'app/Http/Controllers/Api/ExternalQuoteController.php',
    'app/Http/Controllers/Api/LedgerController.php',
    'app/Http/Controllers/Api/SupplierPortalController.php',
    # 2 middleware
    'app/Http/Middleware/SupplierOnly.php',
    'app/Http/Middleware/SupplierScope.php',
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
    if remote_path == '/': return
    try:
        sftp.stat(remote_path)
        return
    except IOError:
        parent = posixpath.dirname(remote_path)
        if parent and parent != '/': sftp_mkdir_p(sftp, parent)
        try: sftp.mkdir(remote_path)
        except IOError: pass

def upload_file(sftp, ssh, local_path, remote_path):
    fname = os.path.basename(local_path)
    tmp_remote = f'/tmp/v042_{fname}'
    sftp.put(local_path, tmp_remote)
    sftp_mkdir_p(sftp, posixpath.dirname(remote_path))
    cmd = f'cp {tmp_remote} {remote_path} && rm {tmp_remote}'
    si, so, se = ssh.exec_command(cmd, timeout=30)
    so.read()
    return so.channel.recv_exit_status()

ssh = ssh_connect()
sftp = ssh.open_sftp()
print('=' * 60)
print('V0.4.2 部署 → 172.20.0.139')
print('=' * 60)

# 1. 上传
print('\n[1/3] 上传 31 个文件')
ok, fail = 0, 0
for f in V042_FILES:
    local = os.path.join(LOCAL_API, f)
    remote = f'{REMOTE_API}/{f}'
    if not os.path.exists(local):
        print(f'  SKIP: {f}'); fail += 1; continue
    rc = upload_file(sftp, ssh, local, remote)
    if rc == 0: ok += 1
    else: print(f'  ✗ {f}'); fail += 1
print(f'  后端: {ok} 成功 / {fail} 失败')

# 2. 跑迁移
print('\n[2/3] 跑迁移')
rc, out, err = run(ssh, f'php {REMOTE_API}/artisan migrate --force 2>&1', t=120, label='migrate')
for l in out.split('\n'):
    if 'Migrated' in l or 'Migrating' in l: print(f'  {l}')
if err: print(f'  ERR: {err[:300]}')

# 3. 验证
print('\n[3/3] 验证 10 张新表')
tables = ['suppliers', 'supplier_contacts', 'supplier_evaluations', 'supplier_attachments',
          'external_quote_requests', 'external_quotes', 'supplier_payables', 'supplier_payments',
          'customer_receivables', 'customer_receipts']
for t in tables:
    rc, out, err = run(ssh, f'PGPASSWORD=$(grep DB_PASSWORD /var/www/oa-api/.env | cut -d= -f2) psql -h 127.0.0.1 -U oa_user -d security_oa -tA -c "SELECT to_regclass(\'public.{t}\')"', label='check')
    print(f'  {t}: {out}')

# 清缓存 + 重启
for c in ['config:clear', 'route:clear', 'cache:clear']:
    run(ssh, f'php {REMOTE_API}/artisan {c} 2>&1', label=c, echo=False)
run(ssh, 'sudo systemctl restart php8.3-fpm 2>&1', label='restart php-fpm')
print('  ✓ php-fpm 重启完成')

sftp.close()
ssh.close()
print('\n' + '=' * 60)
print('V0.4.2 部署完成')
print('=' * 60)
