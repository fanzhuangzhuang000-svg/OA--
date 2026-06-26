"""扫描所有 customer_id 外键，错的都修"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_all_fk.sql', 'w') as f:
    f.write("""
-- 找所有 customer_id 外键
SELECT
    conname,
    conrelid::regclass AS table_name,
    confrelid::regclass AS ref_table,
    pg_get_constraintdef(oid) AS def
FROM pg_constraint
WHERE contype = 'f'
  AND pg_get_constraintdef(oid) LIKE '%customer_id%'
ORDER BY conrelid::regclass::text;
""")
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

out = run('sudo -u postgres psql -d security_oa -f /tmp/check_all_fk.sql 2>&1')
print('所有 customer_id 外键:')
print(out)
