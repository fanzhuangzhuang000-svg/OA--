import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 查询实际的客户 ID
print('\n1. 查询实际的客户 ID...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id FROM customers ORDER BY id;" 2>&1'
)
output = stdout.read().decode()
customer_ids = [int(line.strip()) for line in output.strip().split('\n') if line.strip().isdigit()]
print(f'  实际客户 ID (前 10 个): {customer_ids[:10]}... (共 {len(customer_ids)} 个)')

time.sleep(1)

# 2. 插入商机记录 (opportunities) - 使用正确的 customer_id
print('\n2. 插入商机记录 (50 条)...')
sql = """
INSERT INTO opportunities (opp_no, name, customer_id, estimated_amount, stage, probability, expected_sign_date, created_at, updated_at)
VALUES 
"""
stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost']

values = []
for i in range(1, 51):
    opp_no = f'OPP-2024-{i:04d}'
    name = f'商机 {i}'
    customer_id = customer_ids[i % len(customer_ids)]  # 使用实际的客户 ID
    estimated_amount = 50000 + (i * 2000)
    stage = stages[i % 7]
    probability = (i % 10) * 10
    expected_sign_date = f'2026-{(i % 6) + 1:02d}-28'
    values.append(f"('{opp_no}', '{name}', {customer_id}, {estimated_amount}, '{stage}', {probability}, '{expected_sign_date}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 商机记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 3. 验证所有数据
print('\n\n✅ 数据插入完成！正在验证...')
tables = ['users', 'customers', 'leads', 'opportunities', 'attendance_records', 
          'vehicles', 'projects', 'inventory_items', 'notifications', 'vehicle_usage_requests']

for table in tables:
    stdin, stdout, stderr = ssh.exec_command(
        f'psql -U oa_user -d security_oa -t -c "SELECT COUNT(*) FROM {table};" 2>&1'
    )
    output = stdout.read().decode().strip()
    
    if output and output.isdigit():
        print(f'  {table}: {output} 条记录')
    else:
        print(f'  {table}: 查询失败 ({output})')

ssh.close()
print('\n✅ 172 服务器测试数据生成完成！')
