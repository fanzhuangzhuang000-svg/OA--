import paramiko
import random
from datetime import datetime, timedelta

print("Uploading and running test data via psql commands...")
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
    
    # 1. 插入用户数据
    print("\n1. Inserting users...")
    users = [
        ('ZhangSan', 'zhangsan', 'zhangsan@example.com', '13800000001', 'active'),
        ('LiSi', 'lisi', 'lisi@example.com', '13800000002', 'active'),
        ('WangWu', 'wangwu', 'wangwu@example.com', '13800000003', 'active'),
    ]
    
    for name, username, email, phone, status in users:
        sql = f"INSERT INTO users (name, username, email, phone, password, status, created_at, updated_at) SELECT '{name}', '{username}', '{email}', '{phone}', '123456', '{status}', NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = '{email}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  User {name} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert user {name}: {err[:200]}")
    
    # 2. 插入客户数据
    print("\n2. Inserting customers...")
    customers = [
        ('TestCustomerA', 'Enterprise', 'Beijing', 'Beijing', 'Chaoyang', 'TestAddressA'),
        ('TestCustomerB', 'Enterprise', 'Shanghai', 'Shanghai', 'Pudong', 'TestAddressB'),
        ('TestCustomerC', 'Individual', 'Guangdong', 'Shenzhen', 'Nanshan', 'TestAddressC'),
    ]
    
    for name, category, province, city, district, address in customers:
        sql = f"INSERT INTO customers (name, category, province, city, district, address, source, status, created_at, updated_at) SELECT '{name}', '{category}', '{province}', '{city}', '{district}', '{address}', 'Website', 'active', NOW(), NOW() WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = '{name}');"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if 'INSERT' in output or 'SELECT' in output:
            print(f"  Customer {name} inserted successfully (or already exists)")
        else:
            print(f"  Failed to insert customer {name}: {err[:200]}")
    
    # 3. 插入线索数据
    print("\n3. Inserting leads...")
    sources = ['Website', 'Phone', 'Referral', 'Ad', 'Exhibition']
    
    for i in range(1, 21):
        name = f"LeadCustomer{i}"
        contact_name = f"Contact{i}"
        contact_phone = f"138{str(i).zfill(8)}"
        source = sources[i % 5]
        
        sql = f"INSERT INTO leads (customer_name, contact_name, contact_phone, source, status, created_at, updated_at) VALUES ('{name}', '{contact_name}', '{contact_phone}', '{source}', 'new', NOW(), NOW());"
        cmd = f"PGPASSWORD='{db_pass}' psql -h 127.0.0.1 -U {db_user} -d {db_name} -c \"{sql}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        err = stderr.read().decode()
        
        if i % 5 == 0:
            if 'INSERT' in output:
                print(f"  Inserted {i} leads")
            else:
                print(f"  Failed to insert leads: {err[:200]}")
    
    # 4. 验证数据生成
    print("\nVerifying data generation...")
    tables = ['users', 'customers', 'leads']
    
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
    print("Test data generation completed!")
    print("\nNext steps: Generate more data for other tables (opportunities, attendance_records, etc.)")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
