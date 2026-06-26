import paramiko
import random
from datetime import datetime, timedelta

print("🚀 生成测试数据 SQL 文件...")
print("=" * 60)

# 生成 SQL 文件
sql_content = """-- 172 服务器测试数据生成脚本
-- 运行方法: psql -U oa_user -d security_oa -f /tmp/test_data_172.sql

BEGIN;

-- 1. 插入用户数据（如果少于 10 个）
INSERT INTO users (name, email, password, role, department, created_at, updated_at)
SELECT * FROM (
    VALUES 
    ('张三', 'zhangsan@example.com', '123456', '员工', '技术部', NOW(), NOW()),
    ('李四', 'lisi@example.com', '123456', '员工', '销售部', NOW(), NOW()),
    ('王五', 'wangwu@example.com', '123456', '经理', '技术部', NOW(), NOW()),
    ('赵六', 'zhaoliu@example.com', '123456', '员工', '财务部', NOW(), NOW()),
    ('钱七', 'qianqi@example.com', '123456', '员工', '行政部', NOW(), NOW())
) AS new_users(name, email, password, role, department, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = new_users.email);

-- 2. 插入线索数据
"""

# 生成 50 个线索
sources = ['网站留言', '电话咨询', '朋友介绍', '线上广告', '展会收集']
stages = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost']

for i in range(1, 51):
    name = f"线索客户 {i}"
    phone = f"138{str(i).zfill(8)}"
    email = f"lead{i}@example.com"
    source = random.choice(sources)
    stage = random.choice(stages)
    
    sql_content += f"INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ('{name}', '{phone}', '{email}', '{source}', '{stage}', NOW(), NOW());\n"

sql_content += "\n-- 3. 插入商机数据\n"

# 生成 30 个商机
opp_stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost']

for i in range(1, 31):
    title = f"商机项目 {i}"
    amount = random.randint(10000, 500000)
    stage = random.choice(opp_stages)
    customer_id = random.randint(1, 27)  # 假设有 27 个客户
    
    sql_content += f"INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ('{title}', {amount}, '{stage}', {customer_id}, NOW(), NOW());\n"

sql_content += "\n-- 4. 插入考勤记录\n"

# 生成 100 条考勤记录
statuses = ['正常', '迟到', '早退', '缺勤']

for i in range(100):
    user_id = random.randint(1, 10)  # 假设有 10 个用户
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    status = random.choice(statuses)
    
    sql_content += f"INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES ({user_id}, '{date}', '{status}', NOW(), NOW());\n"

sql_content += "\n-- 5. 插入车辆数据\n"

# 生成 5 辆车
vehicles = [
    ('京A12345', '奥迪A6', '可用'),
    ('京B67890', '宝马5系', '可用'),
    ('京C54321', '奔驰E级', '维修中'),
    ('京D09876', '丰田凯美瑞', '可用'),
    ('京E13579', '本田雅阁', '已分配'),
]

for plate, model, status in vehicles:
    sql_content += f"INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ('{plate}', '{model}', '{status}', NOW(), NOW());\n"

sql_content += "\n-- 6. 插入库存物品数据\n"

# 生成 10 个库存物品
inventory_items = [
    ('笔记本', '办公用品', 100),
    ('签字笔', '办公用品', 500),
    ('A4纸', '办公用品', 50),
    ('订书机', '办公用品', 20),
    ('计算器', '办公用品', 15),
    ('打印纸', '办公用品', 200),
    ('文件夹', '办公用品', 80),
    ('胶带', '办公用品', 100),
    ('剪刀', '办公用品', 30),
    ('胶水', '办公用品', 50),
]

for name, category, quantity in inventory_items:
    sql_content += f"INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ('{name}', '{category}', {quantity}, NOW(), NOW());\n"

sql_content += "\nCOMMIT;\n"

# 保存 SQL 文件
sql_file = r'D:\work\website\OA\.workbuddy\test_data_172.sql'
with open(sql_file, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"✅ SQL 文件已生成: {sql_file}")
print(f"   文件大小: {len(sql_content)} 字节")
print(f"   包含数据:")
print(f"   - 用户: 5 个")
print(f"   - 线索: 50 个")
print(f"   - 商机: 30 个")
print(f"   - 考勤记录: 100 条")
print(f"   - 车辆: 5 辆")
print(f"   - 库存物品: 10 个")

print("\n" + "=" * 60)
print("✅ 测试数据 SQL 文件生成完成！")
print("\n下一步: 上传到 172 服务器并运行")
