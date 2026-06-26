"""手动部署采购模块到 172.20.0.139
- 8 Controller + 9 migration 上传
- GRANT 9 张表 + 10 sequence
- composer dump-autoload + route:clear + restart php-fpm
- 验证 route:list + 3 个 curl
"""
import paramiko
import time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('172.20.0.139', username='nbcy', password='admin123')
sftp = c.open_sftp()

# 1. 上传 8 Controller
controllers = [
    'PurchaseRequirementController.php',
    'PurchasePlanController.php',
    'PurchasePaymentRequestController.php',
    'PurchasePaymentController.php',
    'PurchaseContractController.php',
    'PurchaseShipmentController.php',
    'PurchaseLogisticsController.php',
    'PurchaseApprovalController.php',
]
LOCAL_BASE = r'D:\work\website\OA\pc-api\app\Http\Controllers\Api'
REMOTE_TMP = '/tmp'

print('[1/6] 上传 8 个 Controller...')
for fn in controllers:
    local = f'{LOCAL_BASE}\\{fn}'
    remote = f'{REMOTE_TMP}/{fn}'
    sftp.put(local, remote)
    print(f'  + {fn}')

# 2. 上传 9 个 migration
migrations = [
    '2026_06_19_110001_create_purchase_requirements_table.php',
    '2026_06_19_110002_create_purchase_plans_table.php',
    '2026_06_19_110003_create_purchase_contracts_table.php',
    '2026_06_19_110005_create_purchase_payment_requests_table.php',
    '2026_06_19_110006_create_purchase_payments_table.php',
    '2026_06_19_110007_create_purchase_shipments_table.php',
    '2026_06_19_110008_create_purchase_logistics_table.php',
    '2026_06_19_110009_create_purchase_approvals_table.php',
]
LOCAL_MIG = r'D:\work\website\OA\pc-api\database\migrations'
print('[2/6] 上传 8 个 migration...')
for fn in migrations:
    local = f'{LOCAL_MIG}\\{fn}'
    remote = f'{REMOTE_TMP}/{fn}'
    sftp.put(local, remote)
    print(f'  + {fn}')

sftp.close()

# 3. 复制 + 改 owner
print('[3/6] sudo cp + chown...')
for fn in controllers:
    cmd = f'sudo -n bash -c "cp /tmp/{fn} /var/www/oa-api/app/Http/Controllers/Api/{fn} && chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/{fn}"'
    si, so, se = c.exec_command(cmd)
    err = se.read().decode('utf-8', errors='ignore')
    if err and 'unable to resolve host' not in err:
        print(f'  WARN {fn}: {err.strip()}')

for fn in migrations:
    cmd = f'sudo -n bash -c "cp /tmp/{fn} /var/www/oa-api/database/migrations/{fn} && chown www-data:www-data /var/www/oa-api/database/migrations/{fn}"'
    si, so, se = c.exec_command(cmd)
    err = se.read().decode('utf-8', errors='ignore')
    if err and 'unable to resolve host' not in err:
        print(f'  WARN {fn}: {err.strip()}')

# 4. 跑 migration + GRANT
print('[4/6] migrate --force + GRANT...')
cmd = '''sudo -n bash -c "cd /var/www/oa-api && sudo -u www-data php artisan migrate --force 2>&1"'''
si, so, se = c.exec_command(cmd, timeout=60)
out = so.read().decode('utf-8', errors='ignore')
err = se.read().decode('utf-8', errors='ignore')
print('  MIGRATE:', out[:500])
if err:
    print('  STDERR:', err[:200])

# 5. GRANT
grant_sql = """
GRANT ALL PRIVILEGES ON TABLE purchase_requirements, purchase_plans, purchase_payment_requests, purchase_payments, purchase_contracts, purchase_shipments, purchase_shipment_items, purchase_logistics, purchase_approvals TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE purchase_requirements_id_seq, purchase_plans_id_seq, purchase_payment_requests_id_seq, purchase_payments_id_seq, purchase_contracts_id_seq, purchase_shipments_id_seq, purchase_shipment_items_id_seq, purchase_logistics_id_seq, purchase_approvals_id_seq TO oa_user;
"""
with open('/tmp/grant.sql', 'w') as f:
    f.write(grant_sql)
sftp = c.open_sftp()
sftp.put('/tmp/grant.sql', '/tmp/grant.sql')
sftp.close()

cmd = '''sudo -n bash -c "psql -U oa_user -d oa -f /tmp/grant.sql 2>&1 || PGPASSWORD=oa_pass psql -U oa_user -d oa -f /tmp/grant.sql 2>&1"'''
si, so, se = c.exec_command(cmd, timeout=30)
out = so.read().decode('utf-8', errors='ignore')
print('  GRANT:', out[:300])

# 6. composer dump-autoload + clear + restart
print('[5/6] composer dump-autoload + clear + restart...')
cmd = '''sudo -n bash -c "cd /var/www/oa-api && sudo -u www-data composer dump-autoload --no-dev 2>&1"'''
si, so, se = c.exec_command(cmd, timeout=60)
out = so.read().decode('utf-8', errors='ignore')
print('  COMPOSER:', out[:200])

cmd = '''sudo -n bash -c "cd /var/www/oa-api && sudo -u www-data php artisan route:clear && sudo -u www-data php artisan config:clear && sudo -u www-data php artisan cache:clear && sudo -u www-data php artisan view:clear 2>&1"'''
si, so, se = c.exec_command(cmd, timeout=30)
out = so.read().decode('utf-8', errors='ignore')
print('  CLEAR:', out[:200])

cmd = '''sudo systemctl restart php8.3-fpm 2>&1'''
si, so, se = c.exec_command(cmd, timeout=30)
out = so.read().decode('utf-8', errors='ignore')
print('  RESTART:', out[:200])

time.sleep(2)

# 7. 验证
print('[6/6] 验证...')
cmd = '''sudo -n bash -c "cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | grep -E '/api/purchase' | wc -l"'''
si, so, se = c.exec_command(cmd, timeout=30)
out = so.read().decode('utf-8', errors='ignore')
print(f'  /api/purchase 路由数: {out.strip()}')

cmd = '''sudo -n bash -c "cd /var/www/oa-api && sudo -u www-data php -r \\\"require 'vendor/autoload.php'; echo class_exists('App\\\\Http\\\\Controllers\\\\Api\\\\PurchaseRequirementController') ? 'PurchaseReq:OK' : 'PurchaseReq:NO'; echo PHP_EOL; echo class_exists('App\\\\Http\\\\Controllers\\\\Api\\\\PurchaseApprovalController') ? 'PurchaseApp:OK' : 'PurchaseApp:NO'; echo PHP_EOL;\\\" 2>&1"'''
si, so, se = c.exec_command(cmd, timeout=30)
out = so.read().decode('utf-8', errors='ignore')
print(f'  class_exists: {out.strip()}')

# 8. 业务流验证（用 admin token）
print('[验证] 业务流 curl...')
cmd = '''curl -s -X POST http://127.0.0.1:3001/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}' '''
si, so, se = c.exec_command(cmd, timeout=10)
import json
out = so.read().decode('utf-8', errors='ignore')
try:
    j = json.loads(out)
    token = j.get('data', {}).get('token', '')
except:
    token = ''
print(f'  Token: {token[:30] if token else "NO"}...')

if token:
    # 验证 4 个核心端点
    for ep, method, body in [
        ('/api/purchase/requirements', 'GET', None),
        ('/api/purchase/requirements', 'POST', '{"title":"测试需求","priority":"normal","status":"draft"}'),
        ('/api/purchase/plans', 'GET', None),
        ('/api/purchase/contracts', 'GET', None),
    ]:
        if method == 'GET':
            cmd = f'''curl -s -o /dev/null -w "%{{http_code}}" -H "Authorization: Bearer {token}" http://127.0.0.1:3001{ep}'''
        else:
            cmd = f'''curl -s -o /dev/null -w "%{{http_code}}" -X {method} -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d '{body}' http://127.0.0.1:3001{ep}'''
        si, so, se = c.exec_command(cmd, timeout=10)
        out = so.read().decode('utf-8', errors='ignore')
        print(f'  {method} {ep} → {out.strip()}')

c.close()
print('\n=== DONE ===')
