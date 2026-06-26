import paramiko
import time
import random

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 获取所有实际的客户 ID
print('\n1. 获取所有客户 ID...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id FROM customers ORDER BY id;" 2>&1'
)
output = stdout.read().decode()
customer_ids = [int(line.strip()) for line in output.strip().split('\n') if line.strip().isdigit()]
print(f'  客户 ID: {customer_ids[:10]}... (共 {len(customer_ids)} 个)')

time.sleep(1)

# 2. 获取所有实际的用户 ID
print('\n2. 获取所有用户 ID...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -t -c "SELECT id FROM users ORDER BY id;" 2>&1'
)
output = stdout.read().decode()
user_ids = [int(line.strip()) for line in output.strip().split('\n') if line.strip().isdigit()]
print(f'  用户 ID: {user_ids}')

time.sleep(1)

# 3. 插入项目记录 (projects) - 使用实际的客户 ID
print('\n3. 插入项目记录 (30 条)...')
sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
"""
project_types = ['安防工程', '监控安装', '门禁系统', '消防工程', '智能楼宇']
stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
statuses = ['in_progress', 'completed', 'planning']

values = []
for i in range(1, 31):
    project_no = f'P-2026-{i:04d}'
    name = f'{project_types[i % 5]}项目 {i}'
    customer_id = customer_ids[i % len(customer_ids)]  # 使用实际的客户 ID
    type_val = project_types[i % 5]
    stage = stages[i % 7]
    status = statuses[i % 3]
    progress = (i % 10) * 10
    manager_id = user_ids[i % len(user_ids)]  # 使用实际的用户 ID
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
    print('  ✅ 项目记录插入成功 (30 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 4. 插入考勤记录 (attendance_records) - 使用不同的日期避免重复
print('\n4. 插入考勤记录 (200 条，使用 2025 年日期)...')
sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
"""
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

values = []
for i in range(1, 201):
    user_id = user_ids[i % len(user_ids)]
    month = (i % 12) + 1
    day = (i % 28) + 1
    date = f'2025-{month:02d}-{day:02d}'  # 使用 2025 年，避免和现有数据冲突
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
    print('  ✅ 考勤记录插入成功 (200 条)')
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
