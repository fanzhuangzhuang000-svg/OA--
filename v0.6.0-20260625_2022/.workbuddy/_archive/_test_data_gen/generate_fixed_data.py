import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 查询实际的用户 ID
print('\n1. 查询实际的用户 ID...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id, name FROM users;" 2>&1'
)
output = stdout.read().decode()
print(f'  实际用户: {output}')

time.sleep(1)

# 2. 插入项目记录 (projects) - 只使用存在的用户 ID
print('\n2. 插入项目记录 (20 条)...')
sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
"""
project_types = ['安防工程', '监控安装', '门禁系统', '消防工程', '智能楼宇']
stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
statuses = ['in_progress', 'completed', 'planning']

values = []
for i in range(1, 21):
    project_no = f'P-2026-{i:04d}'
    name = f'{project_types[i % 5]}项目 {i}'
    customer_id = (i % 30) + 1
    type_val = project_types[i % 5]
    stage = stages[i % 7]
    status = statuses[i % 3]
    progress = (i % 10) * 10
    manager_id = (i % 4) + 1  # 只有 4 个用户，ID 1-4
    start_date = f'2026-{(i % 6) + 1:02d}-01'
    end_date = f'2026-{(i % 6) + 3:02d}-28'
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

# 3. 插入车辆使用记录 (vehicle_usage_requests)
print('\n3. 插入车辆使用记录 (30 条)...')
sql = """
INSERT INTO vehicle_usage_requests (vehicle_id, applicant_id, usage_date, start_time, end_time, destination, purpose, passengers, self_drive, status, created_at, updated_at)
VALUES 
"""
destinations = ['北京朝阳区', '上海浦东', '广州天河', '深圳南山', '杭州西湖']
purposes = ['客户拜访', '项目现场', '会议接送', '外地出差', '日常办公']

values = []
for i in range(1, 31):
    vehicle_id = (i % 5) + 1
    applicant_id = (i % 4) + 1  # 只有 4 个用户
    usage_date = f'2026-{(i % 6) + 1:02d}-{(i % 28) + 1:02d}'
    start_time = f'{8 + (i % 2)}:00:00'
    end_time = f'{17 + (i % 3)}:00:00'
    destination = destinations[i % 5]
    purpose = purposes[i % 5]
    passengers = 1 + (i % 4)
    self_drive = 'true' if i % 3 == 0 else 'false'
    status = ['pending', 'approved', 'completed', 'rejected'][i % 4]
    values.append(f"({vehicle_id}, {applicant_id}, '{usage_date}', '{start_time}', '{end_time}', '{destination}', '{purpose}', {passengers}, {self_drive}, '{status}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 车辆使用记录插入成功 (30 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 4. 插入通知记录 (notifications)
print('\n4. 插入通知记录 (50 条)...')
sql = """
INSERT INTO notifications (type, title, content, notifiable_id, notifiable_type, sender_id, level, created_at, updated_at)
VALUES 
"""
types = ['approval', 'message', 'reminder', 'system', 'alert']
levels = ['info', 'warning', 'error', 'success']

values = []
for i in range(1, 51):
    type_val = types[i % 5]
    title = f'{types[i % 5]}通知 {i}'
    content = f'这是第 {i} 条{type_val}通知的详细内容描述'
    notifiable_id = (i % 4) + 1  # 只有 4 个用户
    notifiable_type = 'App\\Models\\User'
    sender_id = (i % 4) + 1 if i % 2 == 0 else 'NULL'
    level = levels[i % 4]
    sender_part = str(sender_id) if i % 2 == 0 else 'NULL'
    values.append(f"('{type_val}', '{title}', '{content}', {notifiable_id}, '{notifiable_type}', {sender_part}, '{level}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 通知记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 5. 插入更多考勤记录 (attendance_records)
print('\n5. 插入更多考勤记录 (100 条)...')
sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
"""
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

values = []
for i in range(1, 101):
    user_id = (i % 4) + 1  # 只有 4 个用户
    month = (i % 6) + 1
    day = (i % 28) + 1
    date = f'2026-{month:02d}-{day:02d}'
    check_in_hour = 8 + (i % 2)
    check_out_hour = 17 + (i % 3)
    check_in = f'{check_in_hour:02d}:{(i % 60):02d}:00'
    check_out = f'{check_out_hour:02d}:{(i % 60):02d}:00'
    status = statuses[i % 6]
    values.append(f"({user_id}, '{date}', '{check_in}', '{check_out}', '{status}', NOW(), NOW())")

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

# 6. 验证所有数据
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
