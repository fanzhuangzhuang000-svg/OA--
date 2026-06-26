#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Step 0d: 修复 maintenance_contracts.customer_id 外键"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

sftp = ssh.open_sftp()

# Drop old FK
with sftp.open('/tmp/fix_mc.sql', 'w') as f:
    f.write("ALTER TABLE maintenance_contracts DROP FOREIGN KEY maintenance_contracts_customer_id_foreign;")
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix_mc.sql 2>&1',
    timeout=60
)
print("Drop FK:", stdout.read().decode('utf-8', errors='replace').strip())

# Add correct FK (CASCADE since customer_id is NOT NULL)
sftp = ssh.open_sftp()
with sftp.open('/tmp/fix_mc2.sql', 'w') as f:
    f.write("ALTER TABLE maintenance_contracts ADD CONSTRAINT maintenance_contracts_customer_id_foreign FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE;")
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix_mc2.sql 2>&1',
    timeout=60
)
print("Add FK:", stdout.read().decode('utf-8', errors='replace').strip())

# Verify
sftp = ssh.open_sftp()
with sftp.open('/tmp/fix_mc3.sql', 'w') as f:
    f.write("""
SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='maintenance_contracts' AND COLUMN_NAME='customer_id' AND REFERENCED_TABLE_NAME IS NOT NULL;
""")
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix_mc3.sql 2>&1',
    timeout=60
)
print("Verify:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("Done!")
