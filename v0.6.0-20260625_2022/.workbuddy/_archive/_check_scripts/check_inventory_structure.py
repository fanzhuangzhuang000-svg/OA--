import paramiko
import time

# 连接服务器
print('正在连接 172.20.0.139 服务器...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print('✅ 连接成功！')

# 先检查 inventory_items 表结构
print('\n检查 inventory_items 表结构...')
stdin, stdout, stderr = ssh.exec_command(
    "psql -U oa_user -d security_oa -c '\d inventory_items' 2>&1"
)
output = stdout.read().decode()
err = stderr.read().decode()
print(output)
if err and 'WARNING' not in err:
    print(f'错误: {err}')

# 等待一下，确保上面的输出完成
time.sleep(2)

# 如果上面没有显示完整结构，再用 SQL 查询
print('\n用 SQL 查询表结构...')
stdin, stdout, stderr = ssh.exec_command(
    """psql -U oa_user -d security_oa -c "
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'inventory_items'
ORDER BY ordinal_position;
" 2>&1"""
)
output = stdout.read().decode()
err = stderr.read().decode()
print(output)
if err and 'WARNING' not in err:
    print(f'错误: {err}')

ssh.close()
print('\n完成！')
