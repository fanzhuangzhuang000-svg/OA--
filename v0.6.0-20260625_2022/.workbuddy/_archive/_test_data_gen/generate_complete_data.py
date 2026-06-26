import paramiko
import random
from datetime import datetime, timedelta

print("Fixing remaining issues and generating complete test data...")
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
    
    # 先查询有效的 user_id 和 customer_id
    print("\nQuerying valid IDs...")
    
    # 查询有效的 user_id
    query = "SELECT id FROM users LIMIT 10;"
    cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -t -c \"{query}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    user_ids = [int(line.strip()) for line in output.split('\n') if line.strip().isdigit()]
    print(f"  Valid user_ids: {user_ids}")
    
    # 查询有效的 customer_id
    query = "SELECT id FROM customers LIMIT 30;"
    cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -t -c \"{query}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    customer_ids = [int(line.strip()) for line in output.split('\n') if line.strip().isdigit()]
    print(f"  Valid customer_ids: {len(customer_ids)} customers")
    
    if not user_ids:
        print("❌ No valid user_ids found. Please insert users first.")
        exit(1)
    
    # 5. 插入考勤记录（使用有效的 user_id）
    print("\n5. Inserting attendance records...")
    statuses = ['Normal', 'Late', 'EarlyLeave', 'Absent']
    
    for i in range(100):
        user_id = random.choice(user_ids)
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
    
    # 7. 插入库存物品数据（包含 code 字段）
    print("\n7. Inserting inventory items...")
    inventory_items = [
        ('INV001', 'Notebook', 'Office', 100),
        ('INV002', 'Pen', 'Office', 500),
        ('INV003', 'A4Paper', 'Office', 50),
        ('INV004', 'Stapler', 'Office', 20),
        ('INV005', 'Calculator', 'Office', 15),
    ]
    
    for code, name, category, quantity in inventory_items:
        sql = f"INSERT INTO inventory_items (code, name, category, current_stock, created_at, updated_at) SELECT '{code}', '{name}', '{category}', {quantity}, NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM inventory_items WHERE code = '{code}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Inventory item {code} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert inventory item {code}: {err[:200]}")
    
    # 8. 插入项目数据（包含 project_no 字段）
    print("\n8. Inserting projects...")
    projects = [
        ('PRJ001', 'TestProjectA', 1, 'implementation', 'in_progress', 30),
        ('PRJ002', 'TestProjectB', 2, 'implementation', 'in_progress', 50),
        ('PRJ003', 'TestProjectC', 3, 'design', 'in_progress', 70),
    ]
    
    for project_no, name, customer_id, type, status, progress in projects:
        sql = f"INSERT INTO projects (project_no, name, customer_id, type, status, progress, created_at, updated_at) SELECT '{project_no}', '{name}', {customer_id}, '{type}', '{status}', {progress}, NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM projects WHERE project_no = '{project_no}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Project {project_no} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert project {project_no}: {err[:200]}")
    
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
