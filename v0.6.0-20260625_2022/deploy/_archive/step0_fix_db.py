#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Step 0: 修复数据库结构问题"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run_sql(sql):
    sftp = ssh.open_sftp()
    with sftp.open('/tmp/fix.sql', 'w') as f:
        f.write(sql)
    sftp.close()
    stdin, stdout, stderr = ssh.exec_command(
        'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/fix.sql 2>&1',
        timeout=60
    )
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# 1. 查看 vehicle_insurances.type ENUM 值
print("=== 检查 vehicle_insurances.type ENUM ===")
out, err = run_sql("SHOW COLUMNS FROM vehicle_insurances WHERE Field='type';")
print(f"Result: {out}")
if err: print(f"STDERR: {err}")

# 2. 查看 service_orders 外键
print("\n=== 检查 service_orders 外键 ===")
out, err = run_sql("""
SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='service_orders' AND REFERENCED_TABLE_NAME IS NOT NULL;
""")
print(f"Result: {out}")
if err: print(f"STDERR: {err}")

# 3. 查看 inventory_items.status ENUM
print("\n=== 检查 inventory_items.status ENUM ===")
out, err = run_sql("SHOW COLUMNS FROM inventory_items WHERE Field='status';")
print(f"Result: {out}")
if err: print(f"STDERR: {err}")

# 4. 修复 service_orders.customer_id 外键 (如果指向 users 则改为 customers)
print("\n=== 修复 service_orders.customer_id 外键 ===")
fix_sql = """
SET @fk_name = (
    SELECT CONSTRAINT_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='service_orders'
      AND COLUMN_NAME='customer_id' AND REFERENCED_TABLE_NAME IS NOT NULL
    LIMIT 1
);
SET @sql = IF(@fk_name IS NOT NULL AND (
    SELECT REFERENCED_TABLE_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA='oa_db' AND TABLE_NAME='service_orders'
      AND COLUMN_NAME='customer_id' AND REFERENCED_TABLE_NAME IS NOT NULL
    LIMIT 1
) = 'users',
    CONCAT('ALTER TABLE service_orders DROP FOREIGN KEY ', @fk_name,
           '; ALTER TABLE service_orders ADD CONSTRAINT service_orders_customer_id_foreign',
           ' FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL'),
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SELECT 'OK' AS result;
"""
out, err = run_sql(fix_sql)
print(f"Result: {out}")
if err: print(f"STDERR: {err}")

ssh.close()
print("\nDone!")
