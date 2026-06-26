"""查项目相关表 + 字段"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_project_tables.sql', 'w') as f:
    f.write("""
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
  AND (tablename LIKE '%project%' OR tablename LIKE '%contract%' OR tablename LIKE '%construction%' OR tablename LIKE '%milestone%' OR tablename LIKE '%purchase%' OR tablename LIKE '%settlement%' OR tablename LIKE '%material%')
ORDER BY tablename;
""")
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

out = run('sudo -u postgres psql -d security_oa -f /tmp/check_project_tables.sql 2>&1')
print(out)
