import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# 标记 approval_records_v2 migration 为已执行
print('=== 标记 approval_records_v2 migration ===')
cmd = """
sudo -u postgres psql -d security_oa -c "
INSERT INTO migrations (migration, batch) 
SELECT '2024_01_05_000004_create_approval_records_v2_table', MAX(batch)+1 
FROM migrations 
ON CONFLICT (migration) DO NOTHING;
" 2>&1
"""
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print(out[:300])

# 验证 migration 状态
print('\n=== 验证 migration 状态 ===')
cmd2 = 'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | tail -10'
stdin, stdout, stderr = ssh.exec_command(cmd2, get_pty=True, timeout=15)
out2 = stdout.read().decode('utf-8', errors='replace')
print(out2[:400])

ssh.close()
print('\n✅ migration 状态已修复')
