import paramiko

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 1. 检查 projects 表结构
print('\n1. 检查 projects 表结构...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'projects' 
ORDER BY ordinal_position;
" 2>&1"""
)
output = stdout.read().decode()
print(output)

# 2. 检查 vehicle_usage_requests 表结构
print('\n2. 检查 vehicle_usage_requests 表结构...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'vehicle_usage_requests' 
ORDER BY ordinal_position;
" 2>&1"""
)
output = stdout.read().decode()
print(output)

# 3. 检查 notifications 表结构
print('\n3. 检查 notifications 表结构...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'notifications' 
ORDER BY ordinal_position;
" 2>&1"""
)
output = stdout.read().decode()
print(output)

ssh.close()
print('\n✅ 完成！')
