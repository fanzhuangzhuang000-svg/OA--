import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 先检查是否有仓库和分类数据
print('\n检查 warehouses 表...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -c "SELECT * FROM warehouses LIMIT 5;" 2>&1'
)
output = stdout.read().decode()
print(output)

time.sleep(1)

print('\n检查 inventory_categories 表...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -c "SELECT * FROM inventory_categories LIMIT 5;" 2>&1'
)
output = stdout.read().decode()
print(output)

time.sleep(1)

# 插入库存物品测试数据
print('\n插入 inventory_items 测试数据...')
sql = """
INSERT INTO inventory_items (name, code, category, unit, safety_stock, current_stock, cost_price, sell_price, has_serial, status, min_stock, created_at, updated_at)
VALUES 
('笔记本电脑', 'IT-001', '电子设备', '台', 5, 20, 5000.00, 6500.00, false, 'active', 3, NOW(), NOW()),
('无线鼠标', 'IT-002', '电子设备', '个', 10, 50, 50.00, 80.00, false, 'active', 5, NOW(), NOW()),
('办公椅', 'OF-001', '办公家具', '把', 3, 15, 300.00, 450.00, false, 'active', 2, NOW(), NOW()),
('A4打印纸', 'OF-002', '办公用品', '箱', 20, 100, 25.00, 35.00, false, 'active', 10, NOW(), NOW()),
('签字笔', 'OF-003', '办公用品', '支', 50, 200, 2.00, 3.50, false, 'active', 30, NOW(), NOW()),
('网络交换机', 'IT-003', '网络设备', '台', 2, 8, 800.00, 1200.00, false, 'active', 1, NOW(), NOW()),
('投影仪', 'IT-004', '电子设备', '台', 2, 5, 3000.00, 4200.00, false, 'active', 1, NOW(), NOW()),
('文件柜', 'OF-004', '办公家具', '个', 2, 10, 400.00, 600.00, false, 'active', 1, NOW(), NOW()),
('复印纸', 'OF-005', '办公用品', '包', 30, 150, 20.00, 28.00, false, 'active', 20, NOW(), NOW()),
('订书机', 'OF-006', '办公用品', '个', 10, 30, 15.00, 22.00, false, 'active', 5, NOW(), NOW())
ON CONFLICT (code) DO NOTHING;
"""

stdin, stdout, stderr = ssh.exec_command(
    f'psql -U oa_user -d security_oa -c "{sql}" 2>&1'
)
output = stdout.read().decode()
err = stderr.read().decode()
print(output)
if err and 'WARNING' not in err and 'NOTICE' not in err:
    print(f'错误: {err}')

# 验证插入结果
print('\n验证 inventory_items 数据...')
stdin, stdout, stderr = ssh.exec_command(
    'psql -U oa_user -d security_oa -c "SELECT * FROM inventory_items;" 2>&1'
)
output = stdout.read().decode()
print(output)

ssh.close()
print('\n✅ 完成！')
