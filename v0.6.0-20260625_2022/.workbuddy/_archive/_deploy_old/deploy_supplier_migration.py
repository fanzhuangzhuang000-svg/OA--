import paramiko, os

host = '172.20.0.139'
user = 'nbcy'
pwd = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pwd, timeout=15)
print('SSH 连接成功')

# 1. 上传 migration
sftp = ssh.open_sftp()
local_mig = 'D:/work/website/OA/pc-api/database/migrations/2026_06_22_000000_add_nullable_supplier_id_to_payables_table.php'
remote_tmp = '/tmp/2026_06_22_000000_add_nullable_supplier_id_to_payables_table.php'
remote_target = '/var/www/oa-api/database/migrations/2026_06_22_000000_add_nullable_supplier_id_to_payables_table.php'

print('上传 migration...')
sftp.put(local_mig.replace('\\', '/'), remote_tmp)
ssh.exec_command(f'sudo cp {remote_tmp} {remote_target} && sudo chown www-data:www-data {remote_target}')
print('migration 上传完成')

# 2. 运行迁移
print('运行迁移...')
cmd = 'cd /var/www/oa-api && sudo -u www-data php artisan migrate --force 2>&1 | tail -20'
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=60)
out = stdout.read().decode('utf-8', errors='replace')
print('迁移输出:', out[:800])

# 3. 检查 supplier_id 是否已是 nullable
print()
print('检查 payables.supplier_id 是否已是 nullable...')
cmd2 = """sudo -u postgres psql -d security_oa -c "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='payables' AND column_name='supplier_id';" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(cmd2, get_pty=True, timeout=15)
out2 = stdout.read().decode('utf-8', errors='replace')
print(out2[:400])

sftp.close()
ssh.close()
print('完成')
