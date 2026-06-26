#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V0.4.5 质保期 + Dashboard 部署脚本 (117 服务器)
- 上传 3 migration + 3 model + 3 service + 3 controller + 1 dashboard + 1 command + routes/api.php + routes/console.php
- 跑 migration
- restart php8.5-fpm
- 烟囱 6 列表 + 6 创建
"""
import os
import sys
import paramiko
import time

HOST = '192.168.3.117'
USER = 'nbcy'
PASSWORD = 'admin123'
LOCAL_API = r'D:\work\website\OA\pc-api'
REMOTE_API = '/var/www/oa-api'

PATCH_FILES = [
    # migrations (3)
    'database/migrations/2026_06_25_000011_create_warranties_table.php',
    'database/migrations/2026_06_25_000012_create_warranty_service_orders_table.php',
    'database/migrations/2026_06_25_000013_create_warranty_deposits_table.php',
    # models (3)
    'app/Models/Warranty.php',
    'app/Models/WarrantyServiceOrder.php',
    'app/Models/WarrantyDeposit.php',
    # services (3)
    'app/Services/WarrantyService.php',
    'app/Services/WarrantyServiceOrderService.php',
    'app/Services/WarrantyDepositService.php',
    # controllers (3)
    'app/Http/Controllers/Api/WarrantyController.php',
    'app/Http/Controllers/Api/WarrantyServiceOrderController.php',
    'app/Http/Controllers/Api/WarrantyDepositController.php',
    # dashboard (1)
    'app/Http/Controllers/Api/DashboardController.php',
    # command (1)
    'app/Console/Commands/ScanWarrantyExpiry.php',
    # routes (2)
    'routes/api.php',
    'routes/console.php',
]

def run_remote(ssh, cmd, timeout=60):
    print(f'  $ {cmd[:120]}')
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', errors='ignore')
    err = se.read().decode('utf-8', errors='ignore')
    if out: print(out[:2000])
    if err and 'WARN' not in err: print(f'  STDERR: {err[:500]}')
    return out, err

def main():
    print('=' * 60)
    print('V0.4.5 部署 - 质保期 + Dashboard')
    print('=' * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    print(f'\n[1/5] 上传 {len(PATCH_FILES)} 个文件到 /tmp ...')
    for rel in PATCH_FILES:
        local = os.path.join(LOCAL_API, rel).replace('\\', '/')
        name = os.path.basename(rel)
        remote_tmp = f'/tmp/{name}'
        if not os.path.exists(local):
            print(f'  ✗ {name} - 本地文件不存在: {local}')
            continue
        sftp.put(local, remote_tmp)
        size = os.path.getsize(local)
        print(f'  ✓ {name} ({size}B)')

    print('\n[2/5] sudo cp 到 /var/www/oa-api + chown ...')
    cmds = []
    for rel in PATCH_FILES:
        name = os.path.basename(rel)
        target = f'{REMOTE_API}/{rel}'
        cmds.append(f'sudo -n cp /tmp/{name} {target}')
    cmds.append(f'sudo -n chown -R nbcy:nbcy {REMOTE_API}/app/Http/Controllers/Api {REMOTE_API}/app/Services {REMOTE_API}/app/Models {REMOTE_API}/app/Console {REMOTE_API}/database/migrations {REMOTE_API}/routes')
    for c in cmds:
        out, _ = run_remote(ssh, c, timeout=30)
    print('\n[3/5] 跑 migration ...')
    out, _ = run_remote(ssh, f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan migrate --force 2>&1 | tail -20', timeout=120)
    print('\n[4/5] optimize:clear + restart fpm ...')
    run_remote(ssh, f'cd {REMOTE_API} && sudo -n php -d opcache.enable=0 artisan optimize:clear 2>&1 | tail -10', timeout=60)
    run_remote(ssh, 'sudo -n systemctl restart php8.5-fpm 2>&1', timeout=30)
    time.sleep(2)
    run_remote(ssh, 'sudo -n systemctl status php8.5-fpm 2>&1 | head -3', timeout=10)

    print('\n[5/5] 烟囱 6 列表 + 6 创建 ...')
    # 清缓存
    run_remote(ssh, "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c 'TRUNCATE cache' 2>&1 | tail -2", timeout=15)
    # 登录
    login = '''curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' '''
    out, _ = run_remote(ssh, login, timeout=15)
    import re
    m = re.search(r'"token":"([^"]+)"', out)
    if not m:
        print('  ✗ 登录失败，跳过烟囱')
        sftp.close(); ssh.close(); return 1
    token = m.group(1)
    print(f'  ✓ token = {token[:30]}...')

    # 6 列表
    list_apis = [
        '/api/warranties',
        '/api/warranties/expiring?within_days=30',
        '/api/warranty-service-orders',
        '/api/warranty-service-orders/technician-stats?technician_id=1',
        '/api/warranty-deposits',
        '/api/dashboard/overview',
    ]
    for path in list_apis:
        out, _ = run_remote(ssh, f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1{path} -H 'Authorization: Bearer {token}'", timeout=10)
        code = out.strip()
        status = '✓' if code == '200' else '✗'
        print(f'  {status} GET {path} -> {code}')

    # 6 创建 (拿真实 project_id/customer_id)
    out, _ = run_remote(ssh, "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -t -c 'SELECT id FROM projects ORDER BY id LIMIT 1'", timeout=10)
    pid = out.strip().split('\n')[0].strip() or '1'
    out, _ = run_remote(ssh, "PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -t -c 'SELECT id FROM customers ORDER BY id LIMIT 1'", timeout=10)
    cid = out.strip().split('\n')[0].strip() or '1'

    post_apis = [
        ('POST /api/warranties', f"curl -s -X POST http://127.0.0.1/api/warranties -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{\"project_id\":{pid},\"customer_id\":{cid},\"start_date\":\"2026-06-24\",\"period_months\":12,\"warranty_type\":\"basic\",\"coverage_scope\":\"V0.4.5测试\"}}'", 'msg'),
        ('POST /api/warranty-service-orders', f"curl -s -X POST http://127.0.0.1/api/warranty-service-orders -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{\"warranty_id\":2,\"service_type\":\"inspect\",\"title\":\"V0.4.5巡检测试\",\"description\":\"测试\",\"scheduled_date\":\"2026-06-30\"}}'", 'msg'),
        ('POST /api/warranty-deposits', f"curl -s -X POST http://127.0.0.1/api/warranty-deposits -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{{\"project_id\":{pid},\"customer_id\":{cid},\"contract_amount\":100000,\"deposit_rate\":5,\"hold_date\":\"2026-06-24\",\"reason\":\"V0.4.5测试\"}}'", 'msg'),
    ]
    for label, cmd, key in post_apis:
        out, _ = run_remote(ssh, cmd, timeout=10)
        import re
        m = re.search(rf'"{key}":"([^"]+)"', out)
        if m and '成功' in m.group(1):
            print(f'  ✓ {label} -> {m.group(1)}')
        else:
            print(f'  ? {label} -> {out[:200]}')

    sftp.close()
    ssh.close()
    print('\n✅ V0.4.5 部署完成')
    return 0

if __name__ == '__main__':
    sys.exit(main())
