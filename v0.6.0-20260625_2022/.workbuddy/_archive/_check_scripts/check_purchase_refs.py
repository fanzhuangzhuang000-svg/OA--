import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 查 purchase_contracts / suppliers / purchase_items / project_purchase_contracts 的数量
for t in ['purchase_contracts','suppliers','purchase_items','project_purchase_contracts','projects','users']:
    stdin, stdout, stderr = ssh.exec_command(
        f"export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c \"SELECT COUNT(*) FROM {t};\""
    )
    print(f"{t}: {stdout.read().decode().strip()}")

# 拿一个 contract id 列表 和 supplier id 列表（用于建 shipment / payment_request）
stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c \"SELECT id, code FROM purchase_contracts ORDER BY id LIMIT 5;\""
)
print("\nfirst 5 contracts:")
print(stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command(
    "export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c \"SELECT id, name FROM suppliers ORDER BY id LIMIT 5;\""
)
print("first 5 suppliers:")
print(stdout.read().decode())

ssh.close()
