import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 查询已存在的考勤日期
print('\n1. 查询已存在的考勤日期 (前 20 条)...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT DISTINCT date FROM attendance_records ORDER BY date LIMIT 20;" 2>&1'
)
output = stdout.read().decode()
print(f'  已存在日期: {output[:300]}...')

time.sleep(1)

# 2. 插入考勤记录 (使用 2024 年日期，避免冲突)
print('\n2. 插入考勤记录 (300 条，使用 2024 年日期)...')
user_ids = [1, 71, 72, 73]

sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
"""
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

values = []
count = 0
for month in range(1, 13):  # 2024年 1-12月
    for day in range(1, 26):  # 每月 1-25日
        if count >= 300:
            break
        user_id = user_ids[count % 4]
        date = f'2024-{month:02d}-{day:02d}'
        check_in_hour = 8 + (count % 2)
        check_out_hour = 17 + (count % 3)
        check_in = f'{check_in_hour:02d}:{(count % 60):02d}:00'
        check_out = f'{check_out_hour:02d}:{(count % 60):02d}:00'
        status = statuses[count % 6]
        values.append(f"({user_id}, '{date}', '{check_in}', '{check_out}', '{status}', NOW(), NOW())")
        count += 1

sql += ',\n'.join(values[:300]) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 考勤记录插入成功 (300 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 3. 插入更多项目记录 (让 projects 达到 100+ 条)
print('\n3. 插入更多项目记录 (50 条)...')
customer_ids = list(range(1, 31))

sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
"""
project_types = ['安防工程', '监控安装', '门禁系统', '消防工程', '智能楼宇', '停车场系统', '楼宇对讲', '电子巡更']
stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
statuses = ['in_progress', 'completed', 'planning']

values = []
for i in range(1, 51):
    project_no = f'P-2024-{i:04d}'
    name = f'{project_types[i % 8]}项目 {i}'
    customer_id = customer_ids[i % 30]
    type_val = project_types[i % 8]
    stage = stages[i % 7]
    status = statuses[i % 3]
    progress = (i % 10) * 10
    manager_id = user_ids[i % 4]
    start_date = f'2024-{(i % 12) + 1:02d}-01'
    end_date = f'2024-{(i % 12) + 3:02d}-28'
    values.append(f"('{project_no}', '{name}', {customer_id}, '{type_val}', '{stage}', '{status}', {progress}, {manager_id}, '{start_date}', '{end_date}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 项目记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 4. 插入更多线索记录 (leads)
print('\n4. 插入更多线索记录 (50 条)...')
sql = """
INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at)
VALUES 
"""
sources = ['网站留言', '电话咨询', '朋友介绍', '展会', '网络推广', '客户推荐']
stages = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost']

values = []
for i in range(1, 51):
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
    print('  ✅ 线索记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 5. 验证所有数据
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
