import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 插入考勤记录 (attendance_records) - 使用正确的字段名
print('\n1. 插入考勤记录 (100 条，使用 2024 年日期)...')
user_ids = [1, 71, 72, 73]
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

sql = """
INSERT INTO attendance_records (user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, created_at, updated_at)
VALUES 
"""

values = []
count = 0
for month in range(1, 13):  # 2024年 1-12月
    for day in range(1, 32):  # 1-31日
        if count >= 100:
            break
        try:
            from datetime import datetime
            date = datetime(2024, month, day).strftime('%Y-%m-%d')
            
            user_id = user_ids[count % 4]
            clock_in_hour = 8 + (count % 2)
            clock_out_hour = 17 + (count % 3)
            clock_in = f'{clock_in_hour:02d}:{(count % 60):02d}:00'
            clock_out = f'{clock_out_hour:02d}:{(count % 60):02d}:00'
            status = statuses[count % 6]
            work_hours = clock_out_hour - clock_in_hour
            overtime_hours = 0 if work_hours <= 8 else work_hours - 8
            
            values.append(f"({user_id}, '{date}', '{clock_in}', '{clock_out}', '{status}', {work_hours}, {overtime_hours}, NOW(), NOW())")
            count += 1
        except:
            pass  # 跳过无效日期

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 考勤记录插入成功 (100 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 2. 插入更多线索记录 (leads)
print('\n2. 插入更多线索记录 (80 条)...')
sql = """
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at)
VALUES 
"""
sources = ['网站留言', '电话咨询', '朋友介绍', '展会', '网络推广', '客户推荐']
stages = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost']

values = []
for i in range(1, 81):
    name = f'线索联系人 {i}'
    phone = f'139{(i % 100):08d}'
    email = f'lead{i}@example.com'
    source = sources[i % 6]
    stage = stages[i % 6]
    values.append(f"('{name}', '{phone}', '{email}', '{source}', '{stage}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 线索记录插入成功 (80 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 3. 插入更多商机记录 (opportunities)
print('\n3. 插入更多商机记录 (50 条)...')
sql = """
INSERT INTO opportunities (name, customer_id, stage, amount, probability, expected_close, created_at, updated_at)
VALUES 
"""
stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost']

values = []
for i in range(1, 51):
    name = f'商机 {i}'
    customer_id = (i % 30) + 1
    stage = stages[i % 7]
    amount = 10000 + (i * 1000)
    probability = (i % 10) * 10
    expected_close = f'2026-{(i % 6) + 1:02d}-28'
    values.append(f"('{name}', {customer_id}, '{stage}', {amount}, {probability}, '{expected_close}', NOW(), NOW())")

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
