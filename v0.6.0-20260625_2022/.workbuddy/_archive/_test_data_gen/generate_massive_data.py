import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 插入车辆使用记录 (vehicle_usage_requests)
print('\n1. 插入车辆使用记录 (50 条)...')
sql = """
INSERT INTO vehicle_usage_requests (vehicle_id, user_id, start_date, end_date, start_mileage, end_mileage, purpose, destination, status, created_at, updated_at)
VALUES 
"""
values = []
for i in range(1, 51):
    vehicle_id = (i % 5) + 1
    user_id = (i % 4) + 1
    start_date = f'2026-06-{(i % 30) + 1:02d}'
    end_date = f'2026-06-{(i % 30) + 2:02d}'
    start_mileage = 10000 + (i * 100)
    end_mileage = start_mileage + (i * 20)
    purpose = ['客户拜访', '项目现场', '会议接送', '外地出差', '日常办公'][i % 5]
    destination = ['北京朝阳区', '上海浦东', '广州天河', '深圳南山', '杭州西湖'][i % 5]
    status = ['completed', 'approved', 'pending', 'rejected'][i % 4]
    values.append(f"({vehicle_id}, {user_id}, '{start_date}', '{end_date}', {start_mileage}, {end_mileage}, '{purpose}', '{destination}', '{status}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 车辆使用记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:200]}')
    if err: print(f'  错误: {err[:200]}')

time.sleep(2)

# 2. 插入通知记录 (notifications)
print('\n2. 插入通知记录 (100 条)...')
sql = """
INSERT INTO notifications (user_id, type, title, content, is_read, created_at, updated_at)
VALUES 
"""
values = []
types = ['审批', '消息', '提醒', '系统']
for i in range(1, 101):
    user_id = (i % 4) + 1
    type_val = types[i % 4]
    title = f'{type_val}通知 {i}'
    content = f'这是第 {i} 条{type_val}通知内容'
    is_read = 'true' if i % 3 == 0 else 'false'
    values.append(f"({user_id}, '{type_val}', '{title}', '{content}', {is_read}, NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 通知记录插入成功 (100 条)')
else:
    print(f'  输出: {output[:200]}')
    if err: print(f'  错误: {err[:200]}')

time.sleep(2)

# 3. 插入更多考勤记录 (attendance_records) - 达到 300+ 条
print('\n3. 插入更多考勤记录 (200 条)...')
sql = """
INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
VALUES 
"""
values = []
for i in range(1, 201):
    user_id = (i % 4) + 1
    date = f'2026-{(i % 6) + 1:02d}-{(i % 28) + 1:02d}'
    check_in_hour = 8 + (i % 2)
    check_out_hour = 17 + (i % 3)
    check_in = f'{check_in_hour:02d}:{(i % 60):02d}:00'
    check_out = f'{check_out_hour:02d}:{(i % 60):02d}:00'
    status = ['normal', 'late', 'early_leave', 'absent'][i % 4]
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
    print(f'  输出: {output[:200]}')
    if err: print(f'  错误: {err[:200]}')

time.sleep(2)

# 4. 插入更多项目记录 (projects) - 达到 50+ 条
print('\n4. 插入更多项目记录 (30 条)...')
sql = """
INSERT INTO projects (name, customer_id, manager_id, status, progress, start_date, expected_end, created_at, updated_at)
VALUES 
"""
project_names = ['安防系统安装', '监控设备维护', '门禁系统升级', '停车场管理', '消防系统检测',
                 '智能楼宇', '视频会议', '网络布线', '机房建设', 'LED显示屏']
values = []
for i in range(1, 31):
    name = f'{project_names[i % 10]} {i}'
    customer_id = (i % 30) + 1
    manager_id = (i % 4) + 1
    status = ['in_progress', 'completed', 'planning'][i % 3]
    progress = (i % 10) * 10
    start_date = f'2026-{(i % 6) + 1:02d}-01'
    expected_end = f'2026-{(i % 6) + 2:02d}-28'
    values.append(f"('{name}', {customer_id}, {manager_id}, '{status}', {progress}, '{start_date}', '{expected_end}', NOW(), NOW())")

sql += ',\n'.join(values) + ';'

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 项目记录插入成功 (30 条)')
else:
    print(f'  输出: {output[:200]}')
    if err: print(f'  错误: {err[:200]}')

time.sleep(2)

# 5. 插入更多客户记录 (customers) - 达到 80+ 条
print('\n5. 插入更多客户记录 (50 条)...')
sql = """
INSERT INTO customers (name, contact, phone, email, source, status, health_score, created_at, updated_at)
VALUES 
"""
company_types = ['科技', '贸易', '制造', '金融', '教育', '医疗', '房地产', '物流', '餐饮', '零售']
values = []
for i in range(1, 51):
    name = f'{company_types[i % 10]}公司 {i}'
    contact = f'联系人 {i}'
    phone = f'138{(i % 100):08d}'
    email = f'contact{i}@example.com'
    source = ['网站留言', '电话咨询', '朋友介绍', '展会', '网络推广'][i % 5]
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
    print(f'  输出: {output[:200]}')
    if err: print(f'  错误: {err[:200]}')

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
        print(f'  {table}: 查询失败')

ssh.close()
print('\n✅ 172 服务器测试数据生成完成！')
