#!/usr/bin/env python3
"""B 数据权限: 扫 8 张表的关键字段 + users + roles + service_orders"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', port=22, username='nbcy', password='admin123', timeout=20)

tables = [
    'projects', 'customer_receivables', 'purchase_orders', 'construction_logs',
    'rectifications', 'warranties', 'warranty_service_orders', 'warranty_deposits',
    'project_members', 'service_order_technicians', 'users', 'service_orders',
    'roles', 'model_has_roles',
]

for table in tables:
    sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}' AND table_schema='public' ORDER BY ordinal_position"
    cmd = f'sudo -n -u postgres psql -d security_oa -c "{sql}"'
    si, so, se = ssh.exec_command(cmd)
    out = so.read().decode()
    err = se.read().decode()
    print(f'=== {table} ===')
    print(out)
    if err: print('ERR:', err)

# 查 role 实际名字
print('=== 角色名清单 ===')
sql = "SELECT id, name FROM roles"
cmd = f'sudo -n -u postgres psql -d security_oa -c "{sql}"'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

# admin 用户 id (写烟囱用)
print('=== admin 用户 ===')
sql = "SELECT id, name, email FROM users WHERE email='admin@oa.local' OR name='admin' LIMIT 5"
cmd = f'sudo -n -u postgres psql -d security_oa -c "{sql}"'
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())

ssh.close()
