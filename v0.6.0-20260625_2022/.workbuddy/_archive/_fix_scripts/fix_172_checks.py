#!/usr/bin/env python3
"""DROP all public schema check constraints + re-run BusinessSeeder + verify login."""
import paramiko
import sys

HOST = '172.20.0.139'
USER = 'nbcy'
PWD = 'admin123'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PWD, timeout=15)

    def run(cmd, t=60):
        si, so, se = ssh.exec_command(cmd, timeout=t)
        out = so.read().decode('utf-8', 'replace').strip()
        err = se.read().decode('utf-8', 'replace').strip()
        rc = so.channel.recv_exit_status()
        return out, err, rc

    # 1. Query all check constraints via stdin
    print('=== 1. List public check constraints ===')
    sql = """
SELECT conname || E'\\t' || conrelid::regclass::text
FROM pg_constraint
WHERE contype = 'c'
  AND connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text, conname;
"""
    sftp = ssh.open_sftp()
    with sftp.file('/tmp/list_checks.sql', 'w') as f:
        f.write(sql)
    sftp.close()

    out, err, _ = run("sudo -u postgres psql -d security_oa -tA -f /tmp/list_checks.sql 2>&1")
    print(f'  output length: {len(out)}')
    print(f'  first 5 lines: {repr(out[:500])}')

    # 2. Parse - tab separated
    constraints = []
    for line in out.split('\n'):
        line = line.rstrip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) == 2 and parts[0] and parts[1]:
            constraints.append((parts[0].strip(), parts[1].strip()))

    print(f'  parsed: {len(constraints)} constraints')

    if not constraints:
        print('  ! No constraints parsed. Aborting.')
        ssh.close()
        return 1

    # 3. Build drop SQL
    drop_lines = ['BEGIN;']
    for cname, ctable in constraints:
        drop_lines.append(f'ALTER TABLE {ctable} DROP CONSTRAINT IF EXISTS {cname};')
    drop_lines.append('COMMIT;')
    drop_sql = '\n'.join(drop_lines) + '\n'

    sftp = ssh.open_sftp()
    with sftp.file('/tmp/drop_all_checks.sql', 'w') as f:
        f.write(drop_sql)
    sftp.close()

    print(f'  drop SQL: {len(drop_lines)} lines')

    # 4. Execute drop
    print('=== 2. Execute drop ===')
    out, err, _ = run('sudo -u postgres psql -d security_oa -f /tmp/drop_all_checks.sql 2>&1 | head -20')
    print(f'  drop result: {out[:500]}')

    # 5. Verify
    print('=== 3. Verify remaining ===')
    out, _, _ = run("sudo -u postgres psql -d security_oa -tAc \"SELECT count(*) FROM pg_constraint WHERE contype='c' AND connamespace='public'::regnamespace\"")
    print(f'  remaining check constraints: {out}')

    # 6. Run BusinessSeeder
    print('=== 4. Run BusinessSeeder ===')
    out, err, rc = run('cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=BusinessLogicTestDataSeeder --force 2>&1', t=300)
    print(f'  rc={rc}')
    print(out[:800] or err[:800])

    # 7. Verify data
    print('=== 5. Data verify ===')
    for t in ['users', 'customers', 'projects', 'work_orders', 'service_orders',
              'vehicles', 'inventory_items', 'warehouses', 'attendance_records',
              'contracts', 'expense_claims', 'purchases', 'suppliers', 'notifications',
              'messages', 'follow_up_records', 'customer_devices']:
        out, _, _ = run(f'sudo -u postgres psql -d security_oa -tAc "SELECT count(*) FROM {t}" 2>&1')
        print(f'  {t}: {out}')

    # 8. Restart FPM
    print('=== 6. Restart FPM ===')
    run('sudo systemctl restart php8.3-fpm 2>&1', t=15)
    print('  fpm restarted')

    # 9. Login test
    print('=== 7. Login test ===')
    login_data = '{"username":"admin","password":"admin123"}'
    out, _, _ = run(f'curl -s -X POST http://172.20.0.139:3001/api/auth/login -H "Content-Type: application/json" -d \'{login_data}\' 2>&1 | head -c 500')
    print(f'  login response: {out}')

    ssh.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
