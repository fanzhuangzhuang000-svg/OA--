import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 先手动插入 1 条考勤记录，看看具体错误
print('\n1. 测试插入 1 条考勤记录...')
sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
(1, '2024-01-15', '08:00:00', '17:00:00', 'normal', NOW(), NOW());
"""

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(f'  输出: {output}')
if err:
    print(f'  错误: {err[:500]}')

time.sleep(2)

# 2. 如果上面成功，继续插入更多
print('\n2. 插入考勤记录 (50 条)...')
user_ids = [1, 71, 72, 73]
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
"""
values = []
count = 0
for month in range(1, 13):  # 2024年 1-12月
    for day in range(1, 32):  # 1-31日
        if count >= 50:
            break
        try:
            date = f'2024-{month:02d}-{day:02d}'
            # 验证日期是否有效
            import datetime
            datetime.datetime.strptime(date, '%Y-%m-%d')
            
            user_id = user_ids[count % 4]
            check_in = f'{8 + (count % 2)}:00:00'
            check_out = f'{17 + (count % 3)}:00:00'
            status = statuses[count % 6]
            values.append(f"({user_id}, '{date}', '{check_in}', '{check_out}', '{status}', NOW(), NOW())")
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
    print('  ✅ 考勤记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 3. 插入项目记录 (使用正确的 customer_id)
print('\n3. 查询实际的客户 ID...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id FROM customers ORDER BY id LIMIT 10;" 2>&1'
)
output = stdout.read().decode()
customer_ids = [int(line.strip()) for line in output.strip().split('\n') if line.strip().isdigit()]
print(f'  实际客户 ID (前 10 个): {customer_ids}')

time.sleep(1)

print('\n4. 插入项目记录 (20 条)...')
project_types = ['安防工程', '监控安装', '门禁系统', '消防工程', '智能楼宇']
stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
statuses = ['in_progress', 'completed', 'planning']

sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
"""
values = []
for i in range(1, 21):
    project_no = f'P-2024-{i:04d}'
    name = f'{project_types[i % 5]}项目 {i}'
    customer_id = customer_ids[i % len(customer_ids)]  # 使用实际的客户 ID
    type_val = project_types[i % 5]
    stage = stages[i % 7]
    status = statuses[i % 3]
    progress = (i % 10) * 10
    manager_id = user_ids[i % 4]
    
    # 使用正确的日期
    start_month = (i % 12) + 1
    start_day = (i % 28) + 1
    end_month = ((i + 3) % 12) + 1
    end_day = (i % 28) + 1
    
    start_date = f'2024-{start_month:02d}-{start_day:02d}'
    end_date = f'2024-{end_month:02d}-{end_day:02d}'
    
    values.append(f"('{project_no}', '{name}', {customer_id}, '{type_val}', '{stage}', '{status}', {progress}, {manager_id}, '{start_date}', '{end_date}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 项目记录插入成功 (20 条)')
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
