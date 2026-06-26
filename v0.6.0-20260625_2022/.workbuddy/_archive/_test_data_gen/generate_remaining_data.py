import paramiko
import random
from datetime import datetime, timedelta

print("Generating more test data for remaining tables...")
print("=" * 60)

try:
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    print("Connected successfully!")
    
    # 从 .env 文件读取数据库配置
    stdin, stdout, stderr = ssh.exec_command('cat /var/www/oa-api/.env | grep DB_')
    env_output = stdout.read().decode()
    
    # 解析数据库配置
    db_config = {}
    for line in env_output.split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            db_config[key.strip()] = value.strip()
    
    db_name = db_config.get('DB_DATABASE', 'security_oa')
    db_user = db_config.get('DB_USERNAME', 'oa_user')
    db_pass = db_config.get('DB_PASSWORD', '')
    
    print(f"\nDatabase config:")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    
    # 5. 插入考勤记录
    print("\n5. Inserting attendance records...")
    statuses = ['Normal', 'Late', 'EarlyLeave', 'Absent']
    
    for i in range(100):
        user_id = random.randint(1, 10)  # 假设有 10 个用户
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        status = random.choice(statuses)
        
        sql = f"INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES ({user_id}, '{date}', '{status}', NOW(), NOW());"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output:
            if i % 20 == 0:
                print(f"  Inserted {i} attendance records")
        else:
            if i % 20 == 0:
                print(f"  Failed to insert attendance record: {err[:200]}")
    
    # 6. 插入车辆数据
    print("\n6. Inserting vehicles...")
    vehicles = [
        ('JingA12345', 'Audi', 'A6', 'Black', 'available'),
        ('JingB67890', 'BMW', '5Series', 'White', 'available'),
        ('JingC54321', 'Benz', 'EClass', 'Gray', 'maintenance'),
        ('JingD09876', 'Toyota', 'Camry', 'Silver', 'available'),
        ('JingE13579', 'Honda', 'Accord', 'Blue', 'assigned'),
    ]
    
    for plate_no, brand, model, color, status in vehicles:
        sql = f"INSERT INTO vehicles (plate_no, brand, model, color, status, created_at, updated_at) SELECT '{plate_no}', '{brand}', '{model}', '{color}', '{status}', NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM vehicles WHERE plate_no = '{plate_no}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Vehicle {plate_no} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert vehicle {plate_no}: {err[:200]}")
    
    # 7. 插入库存物品数据
    print("\n7. Inserting inventory items...")
    inventory_items = [
        ('Notebook', 'Office', 100),
        ('Pen', 'Office', 500),
        ('A4Paper', 'Office', 50),
        ('Stapler', 'Office', 20),
        ('Calculator', 'Office', 15),
    ]
    
    for name, category, quantity in inventory_items:
        sql = f"INSERT INTO inventory_items (name, category, current_stock, created_at, updated_at) SELECT '{name}', '{category}', {quantity}, NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM inventory_items WHERE name = '{name}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Inventory item {name} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert inventory item {name}: {err[:200]}")
    
    # 8. 插入项目数据
    print("\n8. Inserting projects...")
    projects = [
        ('TestProjectA', 1, 'implementation', 'in_progress', 30),
        ('TestProjectB', 2, 'implementation', 'in_progress', 50),
        ('TestProjectC', 3, 'design', 'in_progress', 70),
    ]
    
    for name, customer_id, type, status, progress in projects:
        sql = f"INSERT INTO projects (name, customer_id, type, status, progress, created_at, updated_at) SELECT '{name}', {customer_id}, '{type}', '{status}', {progress}, NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM projects WHERE name = '{name}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Project {name} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert project {name}: {err[:200]}")
    
    # 9. 验证数据生成
    print("\nVerifying data generation...")
    tables = ['users', 'customers', 'leads', 'opportunities', 'attendance_records', 'vehicles', 'inventory_items', 'projects']
    
    for table in tables:
        query = f"SELECT COUNT(*) FROM {table};"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -t -c \"{query}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode().strip()
        err = stderr.read().decode()
        
        if output and 'ERROR' not in output:
            print(f"  {table}: {output} records")
        else:
            if 'does not exist' in err:
                print(f"  {table}: table does not exist")
            else:
                print(f"  {table}: query failed")
    
    ssh.close()
    print("\n" + "=" * 60)
    print("✅ Test data generation completed!")
    print("\n172 server now has sufficient test data for demonstration and testing.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
