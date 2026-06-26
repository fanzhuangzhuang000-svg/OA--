import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 测试数据库备份（用 sudo -u postgres bash -c 包裹）
print('=== 测试数据库备份 ===')
cmd = 'sudo -u postgres bash -c "pg_dump security_oa | gzip > /var/backups/oa-db/test-backup.sql.gz"'
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
print('备份结果:', out[:200])

# 验证备份文件
print('\n=== 验证备份文件 ===')
stdin, stdout, stderr = ssh.exec_command('ls -lh /var/backups/oa-db/ 2>&1', get_pty=True, timeout=10)
print(stdout.read().decode()[:300])

# 修复 crontab 中的备份命令（同样需要 bash -c 包裹）
print('\n=== 修复 crontab 备份命令 ===')
cron = """# OA 数据库自动备份
0 2 * * * sudo -u postgres bash -c "pg_dump security_oa | gzip > /var/backups/oa-db/oa-db-$(date +\\%Y-\\%m-\\%d).sql.gz"
0 3 * * * find /var/backups/oa-db/ -name "*.sql.gz" -mtime +7 -delete
"""
# 写入 crontab
stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/oa-cron.txt << "EOF"\n{cron}\nEOF\nsudo crontab -u postgres /tmp/oa-cron.txt', get_pty=True, timeout=10)
result = stdout.read().decode('utf-8', errors='replace')
print('crontab 更新:', result[:200])

# 验证 crontab
print('\n=== 验证 crontab ===')
stdin, stdout, stderr = ssh.exec_command('sudo crontab -u postgres -l 2>&1', get_pty=True, timeout=10)
print(stdout.read().decode()[:400])

ssh.close()
print('\n✅ 数据库备份配置完成')
