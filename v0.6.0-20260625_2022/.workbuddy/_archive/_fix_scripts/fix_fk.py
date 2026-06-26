"""修 projects.customer_id 外键 + 重跑 seed"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.file('/tmp/fix_fk.sql', 'w') as f:
    f.write("""
-- 删错的外键
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_customer_id_foreign;
-- 重建正确的外键
ALTER TABLE projects ADD CONSTRAINT projects_customer_id_foreign
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL;
""")
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

out = run('sudo -u postgres psql -d security_oa -f /tmp/fix_fk.sql 2>&1')
print('外键修正:')
print(out)

# 验证
out = run('sudo -u postgres psql -d security_oa -c "SELECT conname, confrelid::regclass FROM pg_constraint WHERE conrelid=' + chr(39) + 'projects' + chr(39) + '::regclass AND contype = ' + chr(39) + 'f' + chr(39) + '"')
print('修正后:')
print(out)

# 重跑 seed
print()
print('=== 重跑 seed ===')
out = run('cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=BusinessLogicTestDataSeeder --force 2>&1 | tail -10', t=300)
print(out)
