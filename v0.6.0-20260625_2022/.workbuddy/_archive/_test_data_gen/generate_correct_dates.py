import paramiko
import time
from datetime import datetime, timedelta

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 插入考勤记录 (使用正确的日期)
print('\n1. 插入考勤记录 (300 条，使用 2024-01-01 到 2024-12-31 的日期)...')
user_ids = [1, 71, 72, 73]
statuses = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime']

# 生成 2024 年的日期列表
dates = []
for month in range(1, 13):  # 1-12月
    for day in range(1, 32):  # 1-31日
        try:
            date = datetime(2024, month, day).strftime('%Y-%m-%d')
            dates.append(date)
        except:
            pass  # 跳过无效日期（如 2月30日）

print(f'  2024 年有效日期数: {len(dates)}')

# 插入考勤记录
count = 0
batch_size = 50
total = min(300, len(dates) * len(user_ids))

for i in range(0, total, batch_size):
    sql = """
    INSERT INTO attendance_records (user_id, date, check_in, check_out, status, created_at, updated_at)
    VALUES 
    """
    values = []
    for j in range(batch_size):
        if count >= total:
            break
        user_id = user_ids[count % len(user_ids)]
        date = dates[count % len(dates)]
        check_in_hour = 8 + (count % 2)
        check_out_hour = 17 + (count % 3)
        check_in = f'{check_in_hour:02d}:{(count % 60):02d}:00'
        check_out = f'{check_out_hour:02d}:{(count % 60):02d}:00'
        status = statuses[count % 6]
        values.append(f"({user_id}, '{date}', '{check_in}', '{check_out}', '{status}', NOW(), NOW())")
        count += 1
    
    sql += ',\n'.join(values) + ';'
    
    stdin, stdout, stderr = ssh.exec_command(
        f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
    )
    output = stdout.read().decode()
    err = stderr.read().decode()
    
    if 'ERROR' in err or 'ERROR' in output:
        print(f'  批次 {i//batch_size + 1} 失败: {err[:200]}')
        break
    else:
        print(f'  批次 {i//batch_size + 1} 插入成功 ({len(values)} 条)')
    
    time.sleep(1)

time.sleep(2)

# 2. 插入项目记录 (使用正确的日期)
print('\n2. 插入项目记录 (50 条)...')
customer_ids = list(range(1, 31))
project_types = ['安防工程', '监控安装', '门禁系统', '消防工程', '智能楼宇', '停车场系统', '楼宇对讲', '电子巡更']
stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty']
statuses = ['in_progress', 'completed', 'planning']

sql = """
INSERT INTO projects (project_no, name, customer_id, type, stage, status, progress, manager_id, start_date, end_date, created_at, updated_at)
VALUES 
"""

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
    
    # 使用正确的日期（确保在范围内）
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
    print('  ✅ 项目记录插入成功 (50 条)')
else:
    print(f'  输出: {output[:300]}')
    if err: print(f'  错误: {err[:300]}')

time.sleep(2)

# 3. 插入线索记录 (leads)
print('\n3. 插入线索记录 (50 条)...')
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
