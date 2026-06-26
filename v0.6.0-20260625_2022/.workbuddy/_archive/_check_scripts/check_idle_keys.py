"""检查 idle_* 配置行是否存在"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)

# 用 heredoc 避免引号地狱
cmd = r"""PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c "SELECT key, value::text, description FROM system_settings WHERE key LIKE 'idle%';" 2>&1"""
si, so, se = ssh.exec_command(cmd)
out = so.read().decode()
err = se.read().decode()
print('OUT:', out)
if err: print('ERR:', err)

# 同时把 status 跑全看一眼前面的 fail
print('\n--- migration status (last 5) ---')
cmd2 = r"cd /var/www/oa-api && sudo -n -u www-data php artisan migrate:status 2>&1 | tail -20"
si, so, se = ssh.exec_command(cmd2)
print(so.read().decode())

ssh.close()
