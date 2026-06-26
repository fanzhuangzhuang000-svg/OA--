import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)
print('SSH 连接成功')

# 1. 标记 approval_records_v2 migration 为已执行
print('\n1. 标记 approval_records_v2 migration 为已执行...')
sql1 = """
sudo -u postgres psql -d security_oa -c "
INSERT INTO migrations (migration, batch) 
SELECT '2024_01_05_000004_create_approval_records_v2_table', MAX(batch)+1 
FROM migrations 
ON CONFLICT DO NOTHING;
" 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(sql1, get_pty=True, timeout=15)
out1 = stdout.read().decode('utf-8', errors='replace')
print('结果:', out1[:400])

# 2. 标记 supplier_id nullable migration 为已执行
print('\n2. 标记 supplier_id nullable migration 为已执行...')
sql2 = """
sudo -u postgres psql -d security_oa -c "
INSERT INTO migrations (migration, batch) 
SELECT '2026_06_22_000000_add_nullable_supplier_id_to_payables_table', MAX(batch)+1 
FROM migrations 
ON CONFLICT DO NOTHING;
" 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(sql2, get_pty=True, timeout=15)
out2 = stdout.read().decode('utf-8', errors='replace')
print('结果:', out2[:400])

# 3. 验证 migration 状态
print('\n3. 验证 migration 状态...')
cmd3 = 'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | tail -20'
stdin, stdout, stderr = ssh.exec_command(cmd3, get_pty=True, timeout=30)
out3 = stdout.read().decode('utf-8', errors='replace')
print(out3[:800])

# 4. 测试不传 supplier_id 创建应付款
print('\n4. 测试不传 supplier_id 创建应付款（验证修复）...')
test_cmd = """
token=$(curl -s -X POST http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

curl -s -X POST http://127.0.0.1/api/finance/payables \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"amount":12345,"due_date":"2026-08-01","notes":"测试不传supplier_id"}' 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(test_cmd, get_pty=True, timeout=20)
out4 = stdout.read().decode('utf-8', errors='replace')
print('测试结果:', out4[:600])

ssh.close()
print('\n完成')
