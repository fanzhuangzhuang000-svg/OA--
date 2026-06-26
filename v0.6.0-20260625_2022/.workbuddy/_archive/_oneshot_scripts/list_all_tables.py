import paramiko

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 查询所有表名
print('\n查询所有表名...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
" 2>&1"""
)
output = stdout.read().decode()
print(output)

ssh.close()
print('\n✅ 完成！')
