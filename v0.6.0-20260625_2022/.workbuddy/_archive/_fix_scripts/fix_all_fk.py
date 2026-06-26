"""修 maintenance_contracts 和 service_orders 的 customer_id 外键 + 重跑 seed"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/fix_all_fk.sql', 'w') as f:
    f.write("""
-- 删错的外键
ALTER TABLE maintenance_contracts DROP CONSTRAINT IF EXISTS maintenance_contracts_customer_id_foreign;
ALTER TABLE service_orders DROP CONSTRAINT IF EXISTS service_orders_customer_id_foreign;
-- 重建正确的
ALTER TABLE maintenance_contracts ADD CONSTRAINT maintenance_contracts_customer_id_foreign
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT;
ALTER TABLE service_orders ADD CONSTRAINT service_orders_customer_id_foreign
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT;
""")
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

out = run('sudo -u postgres psql -d security_oa -f /tmp/fix_all_fk.sql 2>&1')
print('修复:')
print(out)

# 重跑 seed
print('\n=== 重跑 seed ===')
out = run('cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=BusinessLogicTestDataSeeder --force 2>&1 | tail -15', t=300)
print(out)
