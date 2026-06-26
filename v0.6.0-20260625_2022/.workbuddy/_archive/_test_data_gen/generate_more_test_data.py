import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 插入客户跟进记录
print('\n1. 插入客户跟进记录...')
sql = """
INSERT INTO customer_followups (customer_id, user_id, followup_date, type, content, next_followup_date, created_at, updated_at)
VALUES 
(1, 1, '2026-06-01', '电话', '首次电话沟通，了解客户需求', '2026-06-08', NOW(), NOW()),
(1, 1, '2026-06-08', '拜访', '上门拜访，演示产品功能', '2026-06-15', NOW(), NOW()),
(2, 2, '2026-06-05', '邮件', '发送产品资料和报价', '2026-06-12', NOW(), NOW()),
(3, 1, '2026-06-10', '电话', '跟进项目进展', '2026-06-17', NOW(), NOW()),
(4, 2, '2026-06-12', '微信', '沟通合同细节', '2026-06-19', NOW(), NOW()),
(5, 1, '2026-06-15', '拜访', '现场考察项目环境', '2026-06-22', NOW(), NOW())
ON CONFLICT DO NOTHING;
"""
stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "{sql}" 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 客户跟进记录插入成功')
else:
    print(f'  输出: {output}')
    if err: print(f'  错误: {err}')

time.sleep(1)

# 2. 插入项目阶段数据
print('\n2. 插入项目阶段数据...')
sql = """
INSERT INTO project_stages (project_id, stage, started_at, ended_at, created_at, updated_at)
VALUES 
(1, 'inquiry', '2026-01-15', '2026-02-01', NOW(), NOW()),
(1, 'qualification', '2026-02-02', '2026-02-20', NOW(), NOW()),
(1, 'proposal', '2026-02-21', '2026-03-10', NOW(), NOW()),
(1, 'negotiating', '2026-03-11', '2026-03-25', NOW(), NOW()),
(1, 'quoted', '2026-03-26', '2026-04-05', NOW(), NOW()),
(2, 'inquiry', '2026-02-01', '2026-02-15', NOW(), NOW()),
(2, 'qualification', '2026-02-16', '2026-03-01', NOW(), NOW()),
(3, 'inquiry', '2026-03-01', '2026-03-15', NOW(), NOW())
ON CONFLICT DO NOTHING;
"""
stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "{sql}" 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 项目阶段数据插入成功')
else:
    print(f'  输出: {output}')
    if err: print(f'  错误: {err}')

time.sleep(1)

# 3. 插入售后工单
print('\n3. 插入售后工单...')
sql = """
INSERT INTO service_tickets (ticket_no, customer_id, project_id, type, priority, status, title, description, reported_by, reported_at, created_at, updated_at)
VALUES 
('SR-20260601-001', 1, 1, 'installation', 'medium', 'in_progress', '监控设备安装', '需要安装50个监控摄像头', '张三', '2026-06-01', NOW(), NOW()),
('SR-20260605-001', 2, 2, 'maintenance', 'high', 'pending', '门禁系统故障', '主入口门禁无法识别指纹', '李四', '2026-06-05', NOW(), NOW()),
('SR-20260610-001', 3, 3, 'repair', 'low', 'resolved', '显示屏亮度调节', '会议室显示屏太亮，需要调节', '王五', '2026-06-10', NOW(), NOW()),
('SR-20260615-001', 4, 4, 'consultation', 'medium', 'in_progress', '系统升级咨询', '咨询安防系统是否支持手机APP控制', '赵六', '2026-06-15', NOW(), NOW()),
('SR-20260620-001', 5, 5, 'installation', 'high', 'pending', '停车场系统安装', '需要安装车牌识别系统', '钱七', '2026-06-20', NOW(), NOW())
ON CONFLICT (ticket_no) DO NOTHING;
"""
stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "{sql}" 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 售后工单插入成功')
else:
    print(f'  输出: {output}')
    if err: print(f'  错误: {err}')

time.sleep(1)

# 4. 插入报销记录
print('\n4. 插入报销记录...')
sql = """
INSERT INTO reimbursements (reimb_no, user_id, type, amount, purpose, expense_date, status, created_at, updated_at)
VALUES 
('BX-20260601-001', 1, '差旅', 1250.00, '客户拜访差旅费', '2026-06-01', 'approved', NOW(), NOW()),
('BX-20260605-001', 2, '招待', 580.00, '客户招待费', '2026-06-05', 'pending', NOW(), NOW()),
('BX-20260610-001', 1, '交通', 320.00, '出租车费', '2026-06-10', 'approved', NOW(), NOW()),
('BX-20260615-001', 3, '办公', 450.00, '购买办公用品', '2026-06-15', 'submitted', NOW(), NOW()),
('BX-20260620-001', 2, '差旅', 2180.00, '外地项目差旅费', '2026-06-20', 'pending', NOW(), NOW())
ON CONFLICT (reimb_no) DO NOTHING;
"""
stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "{sql}" 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 报销记录插入成功')
else:
    print(f'  输出: {output}')
    if err: print(f'  错误: {err}')

time.sleep(1)

# 5. 插入车辆使用记录
print('\n5. 插入车辆使用记录...')
sql = """
INSERT INTO vehicle_usages (vehicle_id, user_id, start_date, end_date, start_mileage, end_mileage, purpose, destination, status, created_at, updated_at)
VALUES 
(1, 1, '2026-06-01', '2026-06-01', 15000, 15120, '客户拜访', '北京朝阳区', 'completed', NOW(), NOW()),
(2, 2, '2026-06-05', '2026-06-05', 28500, 28680, '项目现场', '上海浦东', 'completed', NOW(), NOW()),
(3, 1, '2026-06-10', '2026-06-11', 5200, 5420, '外地出差', '广州天河', 'completed', NOW(), NOW()),
(1, 3, '2026-06-15', '2026-06-15', 15120, 15180, '会议接送', '北京大兴机场', 'completed', NOW(), NOW()),
(2, 2, '2026-06-20', '2026-06-20', 28680, 28750, '客户演示', '北京海淀', 'pending', NOW(), NOW())
ON CONFLICT DO NOTHING;
"""
stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "{sql}" 2>&1')
output = stdout.read().decode()
err = stderr.read().decode()
if 'INSERT' in output or 'INSERT' in err:
    print('  ✅ 车辆使用记录插入成功')
else:
    print(f'  输出: {output}')
    if err: print(f'  错误: {err}')

time.sleep(1)

# 6. 验证所有数据
print('\n\n✅ 数据插入完成！正在验证...')
tables = ['customer_followups', 'project_stages', 'service_tickets', 'reimbursements', 'vehicle_usages']
for table in tables:
    stdin, stdout, stderr = ssh.exec_command(f'psql -U oa_user -d security_oa -c "SELECT COUNT(*) FROM {table};" 2>&1')
    output = stdout.read().decode()
    lines = output.strip().split('\n')
    if len(lines) >= 3:
        count = lines[2].strip()
        print(f'  {table}: {count} 条记录')

ssh.close()
print('\n✅ 172 服务器测试数据生成完成！')
