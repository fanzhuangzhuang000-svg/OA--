#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Step 1: 清空数据"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

sql = """SET FOREIGN_KEY_CHECKS=0;
TRUNCATE employee_profiles; TRUNCATE employee_skills; TRUNCATE certificates;
TRUNCATE departments; TRUNCATE positions;
TRUNCATE customers; TRUNCATE customer_contacts; TRUNCATE customer_devices; TRUNCATE follow_up_records;
TRUNCATE projects; TRUNCATE project_contracts; TRUNCATE construction_logs;
TRUNCATE project_members; TRUNCATE suppliers; TRUNCATE purchase_orders; TRUNCATE purchase_items;
TRUNCATE service_orders; TRUNCATE service_order_logs; TRUNCATE service_order_parts;
TRUNCATE maintenance_contracts;
TRUNCATE expense_claims; TRUNCATE expense_items; TRUNCATE approval_records;
TRUNCATE vehicles; TRUNCATE vehicle_insurances; TRUNCATE vehicle_maintenance_records; TRUNCATE vehicle_usage_requests;
TRUNCATE warehouses; TRUNCATE inventory_items; TRUNCATE stock_records; TRUNCATE device_serial_numbers;
TRUNCATE receivables; TRUNCATE payables;
TRUNCATE disk_folders; TRUNCATE disk_files;
TRUNCATE knowledge_categories; TRUNCATE knowledge_articles;
TRUNCATE attendance_records; TRUNCATE leave_requests; TRUNCATE overtime_requests;
TRUNCATE system_logs; TRUNCATE notifications;
DELETE FROM users WHERE id > 5;
SET FOREIGN_KEY_CHECKS=1;
SELECT COUNT(*) as remaining FROM users;"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/clean.sql', 'w') as f:
    f.write(sql)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/clean.sql 2>&1', timeout=60)
print("Clean result:")
print(stdout.read().decode('utf-8', errors='replace').strip())
err = stderr.read().decode('utf-8', errors='replace').strip()
if err:
    print(f"STDERR: {err}")

ssh.close()
print("Done!")
