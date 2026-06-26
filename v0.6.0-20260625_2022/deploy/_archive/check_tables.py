import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run_sql(sql):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db -e "{sql}"', timeout=15)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    return out

# 1. List all tables
print("=== ALL TABLES ===")
tables = run_sql("SHOW TABLES")
print(tables)

# 2. Check specific columns
for check in [
    "SHOW COLUMNS FROM project_contracts WHERE Field='payment_method'",
    "SHOW COLUMNS FROM maintenance_contracts WHERE Field='inspection_frequency'",
]:
    tbl = check.split('FROM ')[1].split(' WHERE')[0]
    print(f"\n=== {tbl} ===")
    print(run_sql(check))

ssh.close()
