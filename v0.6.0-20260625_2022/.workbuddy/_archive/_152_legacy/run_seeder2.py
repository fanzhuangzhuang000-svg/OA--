"""Run seeder with --force flag."""
import time
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
REMOTE_API = '/var/www/oa-api'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=20)
print(f"[OK] Connected")

# Run with --force to bypass production warning
print("\n[1/2] Running seeder with --force...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan db:seed --class=ComprehensiveTestDataSeeder --force 2>&1 | tail -150'
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"STDOUT:\n{out}")
if err:
    print(f"\nSTDERR:\n{err[:5000]}")

# Final stats
print("\n[2/2] Final table counts...")
cmd = f"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c \"SELECT 'projects' as t, count(*) FROM projects UNION ALL SELECT 'service_orders', count(*) FROM service_orders UNION ALL SELECT 'service_order_logs', count(*) FROM service_order_logs UNION ALL SELECT 'maintenance_contracts', count(*) FROM maintenance_orders UNION ALL SELECT 'attendance_records', count(*) FROM attendance_records UNION ALL SELECT 'expense_claims', count(*) FROM expense_claims UNION ALL SELECT 'receivables', count(*) FROM receivables UNION ALL SELECT 'vehicles', count(*) FROM vehicles UNION ALL SELECT 'inventory_items', count(*) FROM inventory_items UNION ALL SELECT 'customers', count(*) FROM customers;\""
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
print("\n[DONE]")
