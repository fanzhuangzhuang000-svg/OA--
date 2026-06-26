#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Step 0b: 修复 service_orders.customer_id 外键"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

sftp = ssh.open_sftp()

# Step 1: Drop existing FK
sql1 = "ALTER TABLE service_orders DROP FOREIGN KEY service_orders_customer_id_foreign;"
with sftp.open('/tmp/fix1.sql', 'w') as f:
    f.write(sql1)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix1.sql 2>&1',
    timeout=60
)
print("Drop FK:", stdout.read().decode('utf-8', errors='replace').strip())

# Step 2: Add correct FK
sftp = ssh.open_sftp()
sql2 = "ALTER TABLE service_orders ADD CONSTRAINT service_orders_customer_id_foreign FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL;"
with sftp.open('/tmp/fix2.sql', 'w') as f:
    f.write(sql2)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix2.sql 2>&1',
    timeout=60
)
print("Add FK:", stdout.read().decode('utf-8', errors='replace').strip())

# Verify
sftp = ssh.open_sftp()
sql3 = """
SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='service_orders' AND REFERENCED_TABLE_NAME IS NOT NULL;
"""
with sftp.open('/tmp/fix3.sql', 'w') as f:
    f.write(sql3)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(
    'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix3.sql 2>&1',
    timeout=60
)
print("Verify:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("Done!")
