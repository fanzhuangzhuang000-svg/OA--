import paramiko

print("🚀 在 172 服务器上直接运行 Python 脚本生成测试数据...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 创建 Python 脚本（在服务器上运行）
    python_script = '''#!/usr/bin/env python3
import psycopg2
from datetime import datetime, timedelta
import random

# 读取 .env 文件获取数据库配置
with open('/var/www/oa-api/.env', 'r') as f:
    env = f.read()

config = {}
for line in env.split('\\n'):
    if '=' in line:
        key, value = line.split('=', 1)
        config[key.strip()] = value.strip()

# 连接数据库
conn = psycopg2.connect(
    host=config.get('DB_HOST', '127.0.0.1'),
    port=config.get('DB_PORT', '5432'),
    database=config.get('DB_DATABASE', 'security_oa'),
    user=config.get('DB_USERNAME', 'oa_user'),
    password=config.get('DB_PASSWORD', '')
)
conn.autocommit = True
cursor = conn.cursor()

print("✅ 数据库连接成功")

# 1. 插入用户数据
print("\\n1️⃣ 插入用户数据...")
users = [
    ('张三', 'zhangsan', 'zhangsan@example.com', '13800000001', 'active'),
    ('李四', 'lisi', 'lisi@example.com', '13800000002', 'active'),
    ('王五', 'wangwu', 'wangwu@example.com', '13800000003', 'active'),
]

for name, username, email, phone, status in users:
    try:
        cursor.execute(
            "INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())",
            (name, username, email, phone, '123456', status)
        )
        print(f"  ✅ 用户 {name} 创建成功")
    except psycopg2.errors.UniqueViolation:
        print(f"  ⚠️ 用户 {name} 已存在")

# 2. 插入客户数据
print("\\n2️⃣ 插入客户数据...")
customers = [
    ('测试客户A', '企业', '北京市', '北京市', '朝阳区', '测试地址A'),
    ('测试客户B', '企业', '上海市', '上海市', '浦东新区', '测试地址B'),
    ('测试客户C', '个人', '广东省', '深圳市', '南山区', '测试地址C'),
]

for name, category, province, city, district, address in customers:
    try:
        cursor.execute(
            "INSERT INTO customers (name, category, province, city, district, address, source, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
            (name, category, province, city, district, address, '网站留言', 'active')
        )
        print(f"  ✅ 客户 {name} 创建成功")
    except psycopg2.errors.UniqueViolation:
        print(f"  ⚠️ 客户 {name} 已存在")

# 3. 插入线索数据
print("\\n3️⃣ 插入线索数据...")
sources = ['网站留言', '电话咨询', '朋友介绍', '线上广告', '展会收集']

for i in range(1, 21):
    name = f"线索客户{i}"
    contact_name = f"联系人{i}"
    contact_phone = f"138{str(i).zfill(8)}"
    source = random.choice(sources)
    
    try:
        cursor.execute(
            "INSERT INTO leads (customer_name, contact_name, contact_phone, source, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (name, contact_name, contact_phone, source, 'new')
        )
        if i % 5 == 0:
            print(f"  ✅ 已插入 {i} 个线索")
    except Exception as e:
        print(f"  ❌ 线索 {name} 创建失败: {e}")

# 4. 插入商机数据
print("\\n4️⃣ 插入商机数据...")
stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted']

for i in range(1, 11):
    name = f"商机项目{i}"
    customer_id = random.randint(1, 30)  # 假设有 30 个客户
    stage = random.choice(stages)
    estimated_amount = random.randint(10000, 500000)
    
    try:
        cursor.execute(
            "INSERT INTO opportunities (name, customer_id, stage, estimated_amount, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
            (name, customer_id, stage, estimated_amount)
        )
        if i % 5 == 0:
            print(f"  ✅ 已插入 {i} 个商机")
    except Exception as e:
        print(f"  ❌ 商机 {name} 创建失败: {e}")

# 5. 插入考勤记录
print("\\n5️⃣ 插入考勤记录...")
statuses = ['正常', '迟到', '早退', '缺勤']

for i in range(100):
    user_id = random.randint(1, 10)  # 假设有 10 个用户
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    status = random.choice(statuses)
    
    try:
        cursor.execute(
            "INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
            (user_id, date, status)
        )
        if i % 20 == 0:
            print(f"  ✅ 已插入 {i} 条考勤记录")
    except Exception as e:
        print(f"  ❌ 考勤记录创建失败: {e}")

# 6. 插入车辆数据
print("\\n6️⃣ 插入车辆数据...")
vehicles = [
    ('京A12345', '奥迪', 'A6', '黑色', 'available'),
    ('京B67890', '宝马', '5系', '白色', 'available'),
    ('京C54321', '奔驰', 'E级', '灰色', 'maintenance'),
    ('京D09876', '丰田', '凯美瑞', '银色', 'available'),
    ('京E13579', '本田', '雅阁', '蓝色', 'assigned'),
]

for plate_no, brand, model, color, status in vehicles:
    try:
        cursor.execute(
            "INSERT INTO vehicles (plate_no, brand, model, color, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (plate_no, brand, model, color, status)
        )
        print(f"  ✅ 车辆 {plate_no} 创建成功")
    except psycopg2.errors.UniqueViolation:
        print(f"  ⚠️ 车辆 {plate_no} 已存在")

# 7. 插入库存物品数据
print("\\n7️⃣ 插入库存物品数据...")
inventory_items = [
    ('笔记本', '办公用品', 100),
    ('签字笔', '办公用品', 500),
    ('A4纸', '办公用品', 50),
    ('订书机', '办公用品', 20),
    ('计算器', '办公用品', 15),
]

for name, category, quantity in inventory_items:
    try:
        cursor.execute(
            "INSERT INTO inventory_items (name, category, current_stock, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
            (name, category, quantity)
        )
        print(f"  ✅ 库存物品 {name} 创建成功")
    except psycopg2.errors.UniqueViolation:
        print(f"  ⚠️ 库存物品 {name} 已存在")

# 8. 插入项目数据
print("\\n8️⃣ 插入项目数据...")
projects = [
    ('测试项目A', 1, 'implementation', 'in_progress', 30),
    ('测试项目B', 2, 'implementation', 'in_progress', 50),
    ('测试项目C', 3, 'design', 'in_progress', 70),
]

for name, customer_id, type, status, progress in projects:
    try:
        cursor.execute(
            "INSERT INTO projects (name, customer_id, type, status, progress, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (name, customer_id, type, status, progress)
        )
        print(f"  ✅ 项目 {name} 创建成功")
    except psycopg2.errors.UniqueViolation:
        print(f"  ⚠️ 项目 {name} 已存在")

# 关闭连接
cursor.close()
conn.close()

print("\\n" + "=" * 60)
print("✅ 测试数据生成完成！")
'''

    # 上传 Python 脚本到服务器
    print("\n上传 Python 脚本...")
    sftp = ssh.open_sftp()
    remote_script = '/tmp/generate_test_data_final.py'
    
    # 将 Python 脚本内容写入本地文件，然后上传
    with open('/tmp/generate_test_data_final.py', 'w') as f:
        f.write(python_script)
    
    sftp.put('/tmp/generate_test_data_final.py', remote_script)
    sftp.close()
    print("  ✅ 上传完成！")
    
    # 运行 Python 脚本
    print("\n运行 Python 脚本（可能需要几分钟）...")
    stdin, stdout, stderr = ssh.exec_command(f'python3 {remote_script} 2>&1', get_pty=True)
    
    # 实时输出
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.strip())
    
    err = stderr.read().decode() if stderr else ''
    if err:
        print(f"\n⚠️ 错误输出: {err[:500]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_script}')
    print("\n✅ 临时文件已清理")
    
    # 验证数据生成
    print("\n验证数据生成...")
    tables = ['users', 'customers', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items', 'projects']
    
    for table in tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条")
            cursor.close()
        except Exception as e:
            print(f"  {table}: 查询失败 - {e}")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 测试数据生成完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
