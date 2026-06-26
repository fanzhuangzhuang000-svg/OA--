import paramiko

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 检查 attendance_records 表结构
print('\n检查 attendance_records 表结构...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'attendance_records' 
ORDER BY ordinal_position;
" 2>&1"""
)
output = stdout.read().decode()
print(output)

ssh.close()
print('\n✅ 完成！')
