import paramiko

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 查询实际的客户 ID
print('\n1. 查询实际的客户 ID (前 10 条)...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id, name FROM customers LIMIT 10;" 2>&1'
)
output = stdout.read().decode()
print(f'  实际客户 ID: {output}')

# 2. 查询客户总数
print('\n2. 查询客户总数...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT COUNT(*) FROM customers;" 2>&1'
)
output = stdout.read().decode().strip()
print(f'  客户总数: {output}')

# 3. 查询考勤记录总数
print('\n3. 查询考勤记录总数...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT COUNT(*) FROM attendance_records;" 2>&1'
)
output = stdout.read().decode().strip()
print(f'  考勤记录总数: {output}')

# 4. 插入项目记录 (使用正确的客户 ID)
print('\n4. 插入项目记录 (20 条)...')
# 假设客户 ID 是 1-30，但可能实际 ID 不同
# 先插入一条测试记录看看
sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
('P-2026-0099', '测试项目', 1, '安防工程', 'initiation', 'in_progress', 0, 1, '2026-06-01', '2026-12-31', NOW(), NOW())
ON CONFLICT (project_no) DO NOTHING;
"""

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'  测试插入: {output}')
if err: print(f'  错误: {err[:200]}')

ssh.close()
print('\n✅ 完成！')
