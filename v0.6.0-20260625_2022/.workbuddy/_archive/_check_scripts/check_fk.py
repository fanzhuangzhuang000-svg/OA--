"""查 projects 表外键约束 + 列定义"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/fk.sql', 'w') as f:
    f.write("""
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE conrelid = 'projects'::regclass AND contype = 'f';

SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'projects' AND column_name LIKE '%cust%';
""")
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

out = run('sudo -u postgres psql -d security_oa -f /tmp/fk.sql 2>&1')
print(out)
