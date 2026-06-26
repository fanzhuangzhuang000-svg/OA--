import paramiko

print("Uploading and running simple test data generation script...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("Connected successfully!")
    
    # 创建简单的 Python 脚本（无 Unicode 字符）
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

print("Database connected successfully")

# 1. 插入用户数据
print("Inserting users...")
users = [
    ('ZhangSan', 'zhangsan', 'zhangsan@example.com', '13800000001', 'active'),
    ('LiSi', 'lisi', 'lisi@example.com', '13800000002', 'active'),
    ('WangWu', 'wangwu', 'wangwu@example.com', '13800000003', 'active'),
]

for name, username, email, phone, status in users:
    try:
        cursor.execute(
            "INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())",
            (name, username, email, phone, '123456', status)
        )
        print(f"  User {name} created successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"  User {name} already exists")

# 2. 插入客户数据
print("Inserting customers...")
customers = [
    ('TestCustomerA', 'Enterprise', 'Beijing', 'Beijing', 'Chaoyang', 'TestAddressA'),
    ('TestCustomerB', 'Enterprise', 'Shanghai', 'Shanghai', 'Pudong', 'TestAddressB'),
    ('TestCustomerC', 'Individual', 'Guangdong', 'Shenzhen', 'Nanshan', 'TestAddressC'),
]

for name, category, province, city, district, address in customers:
    try:
        cursor.execute(
            "INSERT INTO customers (name, category, province, city, district, address, source, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
            (name, category, province, city, district, address, 'Website', 'active')
        )
        print(f"  Customer {name} created successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"  Customer {name} already exists")

# 3. 插入线索数据
print("Inserting leads...")
sources = ['Website', 'Phone', 'Referral', 'Ad', 'Exhibition']

for i in range(1, 21):
    name = f"LeadCustomer{i}"
    contact_name = f"Contact{i}"
    contact_phone = f"138{str(i).zfill(8)}"
    source = random.choice(sources)
    
    try:
        cursor.execute(
            "INSERT INTO leads (customer_name, contact_name, contact_phone, source, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (name, contact_name, contact_phone, source, 'new')
        )
        if i % 5 == 0:
            print(f"  Inserted {i} leads")
    except Exception as e:
        print(f"  Failed to create lead {name}: {e}")

# 4. 插入商机数据
print("Inserting opportunities...")
stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted']

for i in range(1, 11):
    name = f"Opportunity{i}"
    customer_id = random.randint(1, 30)  # 假设有 30 个客户
    stage = random.choice(stages)
    estimated_amount = random.randint(10000, 500000)
    
    try:
        cursor.execute(
            "INSERT INTO opportunities (name, customer_id, stage, estimated_amount, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
            (name, customer_id, stage, estimated_amount)
        )
        if i % 5 == 0:
            print(f"  Inserted {i} opportunities")
    except Exception as e:
        print(f"  Failed to create opportunity {name}: {e}")

# 5. 插入考勤记录
print("Inserting attendance records...")
statuses = ['Normal', 'Late', 'EarlyLeave', 'Absent']

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
            print(f"  Inserted {i} attendance records")
    except Exception as e:
        print(f"  Failed to create attendance record: {e}")

# 6. 插入车辆数据
print("Inserting vehicles...")
vehicles = [
    ('JingA12345', 'Audi', 'A6', 'Black', 'available'),
    ('JingB67890', 'BMW', '5Series', 'White', 'available'),
    ('JingC54321', 'Benz', 'EClass', 'Gray', 'maintenance'),
    ('JingD09876', 'Toyota', 'Camry', 'Silver', 'available'),
    ('JingE13579', 'Honda', 'Accord', 'Blue', 'assigned'),
]

for plate_no, brand, model, color, status in vehicles:
    try:
        cursor.execute(
            "INSERT INTO vehicles (plate_no, brand, model, color, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (plate_no, brand, model, color, status)
        )
        print(f"  Vehicle {plate_no} created successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"  Vehicle {plate_no} already exists")

# 7. 插入库存物品数据
print("Inserting inventory items...")
inventory_items = [
    ('Notebook', 'Office', 100),
    ('Pen', 'Office', 500),
    ('A4Paper', 'Office', 50),
    ('Stapler', 'Office', 20),
    ('Calculator', 'Office', 15),
]

for name, category, quantity in inventory_items:
    try:
        cursor.execute(
            "INSERT INTO inventory_items (name, category, current_stock, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
            (name, category, quantity)
        )
        print(f"  Inventory item {name} created successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"  Inventory item {name} already exists")

# 8. 插入项目数据
print("Inserting projects...")
projects = [
    ('TestProjectA', 1, 'implementation', 'in_progress', 30),
    ('TestProjectB', 2, 'implementation', 'in_progress', 50),
    ('TestProjectC', 3, 'design', 'in_progress', 70),
]

for name, customer_id, type, status, progress in projects:
    try:
        cursor.execute(
            "INSERT INTO projects (name, customer_id, type, status, progress, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
            (name, customer_id, type, status, progress)
        )
        print(f"  Project {name} created successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"  Project {name} already exists")

# 关闭连接
cursor.close()
conn.close()

print("=" * 60)
print("Test data generation completed!")
'''

    # 上传 Python 脚本到服务器
    print("\nUploading Python script...")
    sftp = ssh.open_sftp()
    remote_script = '/tmp/generate_test_data_simple.py'
    
    # 将 Python 脚本内容写入本地文件，然后上传
    with open('/tmp/generate_test_data_simple.py', 'w', encoding='utf-8') as f:
        f.write(python_script)
    
    sftp.put('/tmp/generate_test_data_simple.py', remote_script)
    sftp.close()
    print("  Upload completed!")
    
    # 运行 Python 脚本
    print("\nRunning Python script (may take a few minutes)...")
    stdin, stdout, stderr = ssh.exec_command(f'python3 {remote_script} 2>&1', get_pty=True)
    
    # 实时输出
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.strip())
    
    err = stderr.read().decode() if stderr else ''
    if err:
        print(f"\nWarning: {err[:500]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_script}')
    print("\nTemporary file cleaned up")
    
    # 验证数据生成
    print("\nVerifying data generation...")
    tables = ['users', 'customers', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items', 'projects']
    
    for table in tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
            cursor.close()
        except Exception as e:
            print(f"  {table}: query failed - {e}")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("Test data generation completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
