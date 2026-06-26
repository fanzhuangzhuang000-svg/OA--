import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 插入线索记录 (leads) - 使用正确的字段名
print('\n1. 插入线索记录 (100 条)...')
sql = """
INSERT INTO leads (lead_no, customer_name, contact_name, contact_phone, source, status, estimated_amount, created_at, updated_at)
VALUES 
"""
sources = ['网站留言', '电话咨询', '朋友介绍', '展会', '网络推广', '客户推荐']
statuses = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost']

values = []
for i in range(1, 101):
    lead_no = f'LD-2024-{i:04d}'
    customer_name = f'潜在客户 {i}'
    contact_name = f'联系人 {i}'
    contact_phone = f'139{(i % 100):08d}'
    source = sources[i % 6]
    status = statuses[i % 6]
    estimated_amount = 10000 + (i * 500)
    values.append(f"('{lead_no}', '{customer_name}', '{contact_name}', '{contact_phone}', '{source}', '{status}', {estimated_amount}, NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 线索记录插入成功 (100 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 2. 插入商机记录 (opportunities) - 使用正确的字段名
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
    customer_id = (i % 30) + 1
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

# 3. 插入更多客户记录 (customers)
print('\n3. 插入更多客户记录 (50 条)...')
sql = """
INSERT INTO customers (name, contact, phone, email, source, status, health_score, created_at, updated_at)
VALUES 
"""
company_types = ['科技', '贸易', '制造', '金融', '教育', '医疗', '房地产', '物流', '餐饮', '零售']
sources = ['网站留言', '电话咨询', '朋友介绍', '展会', '网络推广']

values = []
for i in range(1, 51):
    name = f'{company_types[i % 10]}公司 {i}'
    contact = f'联系人 {i}'
    phone = f'138{(i % 100):08d}'
    email = f'contact{i}@example.com'
    source = sources[i % 5]
    status = ['active', 'inactive', 'potential'][i % 3]
    health_score = 50 + (i % 51)
    values.append(f"('{name}', '{contact}', '{phone}', '{email}', '{source}', '{status}', {health_score}, NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 客户记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 4. 验证所有数据
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
