import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=20)

def run(cmd):
    si, so, se = ssh.exec_command(cmd, timeout=30, get_pty=True)
    out = so.read().decode('utf-8', 'replace').strip()
    err = se.read().decode('utf-8', 'replace').strip()
    return out or err

export = 'PGPASSWORD=oa_pg_pwd_782997781'

# 1) migrations 表最新 10 条
print('--- migrations 表里最近 10 条 ---')
print(run(f'{export} psql -h 127.0.0.1 -U oa_user -d security_oa -c "SELECT migration FROM migrations ORDER BY id DESC LIMIT 15;"'))

# 2) 现有 process_* 表是否存在
print('\n--- process_* 表 ---')
print(run(f"{export} psql -h 127.0.0.1 -U oa_user -d security_oa -c \"SELECT tablename FROM pg_tables WHERE schemaname=\\'public\\' AND tablename LIKE \\'process%\\';\""))

# 3) 全部 migration 文件
print('\n--- migrations/ 目录文件 ---')
print(run('ls /var/www/oa-api/database/migrations/ | sort | tail -20'))

# 4) approval_records_v2 是否真存在
print('\n--- approval_records_v2 存在? ---')
print(run(f"{export} psql -h 127.0.0.1 -U oa_user -d security_oa -c \"SELECT to_regclass(\\'public.approval_records_v2\\');\""))

ssh.close()
