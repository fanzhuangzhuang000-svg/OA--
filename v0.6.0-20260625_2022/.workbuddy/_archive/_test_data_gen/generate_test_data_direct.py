import paramiko
import random
from datetime import datetime, timedelta

print("🚀 在 172 服务器上直接生成测试数据（使用 Python + psycopg2）...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("✅ 连接成功！")
    
    # 创建 Python 脚本（在服务器上运行）
    print("\n创建 Python 脚本...")
    python_script = '''
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
    ('张三', 'zhangsan@example.com', '123456', '员工', '技术部'),
    ('李四', 'lisi@example.com', '123456', '员工', '销售部'),
    ('王五', 'wangwu@example.com', '123456', '经理', '技术部'),
    ('赵六', 'zhaoliu@example.com', '123456', '员工', '财务部'),
    ('钱七', 'qianqi@example.com', '123456', '员工', '行政部'),
]

for name, email, password, role, department in users:
    cursor.execute(
        "INSERT INTO users (name, email, password, role, department, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW()) ON CONFLICT (email) DO NOTHING",
        (name, email, password, role, department)
    )
    if cursor.rowcount > 0:
        print(f"  ✅ 用户 {name} 创建成功")
    else:
        print(f"  ⚠️ 用户 {name} 已存在")

# 2. 插入线索数据
print("\\n2️⃣ 插入线索数据...")
sources = ['网站留言', '电话咨询', '朋友介绍', '线上广告', '展会收集']
stages = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost']

for i in range(1, 51):
    name = f"线索客户 {i}"
    phone = f"138{str(i).zfill(8)}"
    email = f"lead{i}@example.com"
    source = random.choice(sources)
    stage = random.choice(stages)
    
    cursor.execute(
        "INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
        (name, phone, email, source, stage)
    )
    if i % 10 == 0:
        print(f"  ✅ 已插入 {i} 个线索")

# 3. 插入商机数据
print("\\n3️⃣ 插入商机数据...")
opp_stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost']

for i in range(1, 31):
    title = f"商机项目 {i}"
    amount = random.randint(10000, 500000)
    stage = random.choice(opp_stages)
    customer_id = random.randint(1, 27)  # 假设有 27 个客户
    
    cursor.execute(
        "INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
        (title, amount, stage, customer_id)
    )
    if i % 10 == 0:
        print(f"  ✅ 已插入 {i} 个商机")

# 4. 插入考勤记录
print("\\n4️⃣ 插入考勤记录...")
statuses = ['正常', '迟到', '早退', '缺勤']

for i in range(100):
    user_id = random.randint(1, 10)  # 假设有 10 个用户
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    status = random.choice(statuses)
    
    cursor.execute(
        "INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
        (user_id, date, status)
    )
    if i % 20 == 0:
        print(f"  ✅ 已插入 {i} 条考勤记录")

# 5. 插入车辆数据
print("\\n5️⃣ 插入车辆数据...")
vehicles = [
    ('京A12345', '奥迪A6', '可用'),
    ('京B67890', '宝马5系', '可用'),
    ('京C54321', '奔驰E级', '维修中'),
    ('京D09876', '丰田凯美瑞', '可用'),
    ('京E13579', '本田雅阁', '已分配'),
]

for plate, model, status in vehicles:
    cursor.execute(
        "INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
        (plate, model, status)
    )
    print(f"  ✅ 车辆 {plate} 创建成功")

# 6. 插入库存物品数据
print("\\n6️⃣ 插入库存物品数据...")
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
    cursor.execute(
        "INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
        (name, category, quantity)
    )
    print(f"  ✅ 库存物品 {name} 创建成功")

# 关闭连接
cursor.close()
conn.close()

print("\\n" + "=" * 60)
print("✅ 测试数据生成完成！")
'''
    
    # 上传 Python 脚本到服务器
    print("\n上传 Python 脚本...")
    sftp = ssh.open_sftp()
    remote_script = '/tmp/generate_test_data_172.py'
    
    # 将 Python 脚本内容写入本地文件，然后上传
    with open('/tmp/generate_test_data_172.py', 'w') as f:
        f.write(python_script)
    
    sftp.put('/tmp/generate_test_data_172.py', remote_script)
    sftp.close()
    print("  ✅ 上传完成！")
    
    # 运行 Python 脚本
    print("\n运行 Python 脚本（可能需要几分钟）...")
    stdin, stdout, stderr = ssh.exec_command(f'python3 {remote_script} 2>&1', get_pty=True)
    
    # 实时输出
    output = ""
    while True:
        line = stdout.readline()
        if not line:
            break
        output += line
        print(line.strip())
    
    err = stderr.read().decode() if stderr else ''
    if err:
        print(f"\n⚠️ 错误输出: {err[:500]}")
    
    # 清理临时文件
    ssh.exec_command(f'rm {remote_script}')
    print("\n✅ 临时文件已清理")
    
    # 验证数据生成
    print("\n验证数据生成...")
    tables = ['users', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items']
    
    for table in tables:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条")
        cursor.close()
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ 测试数据生成完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
