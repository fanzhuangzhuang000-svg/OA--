import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1) 先看 service_orders 表结构
cmd1 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "\\d service_orders" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd1)
print("=== service_orders structure ===")
print(stdout.read().decode())

# 2) 看 contracts 字段（revenue-trend 用的）
cmd2 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "\\d contracts" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd2)
print("=== contracts structure ===")
print(stdout.read().decode())

# 3) 看 contracts 现有数据分布
cmd3 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "SELECT id, contract_no, signed_date, total_amount FROM contracts ORDER BY signed_date LIMIT 5;" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd3)
print("=== contracts sample ===")
print(stdout.read().decode())

ssh.close()
