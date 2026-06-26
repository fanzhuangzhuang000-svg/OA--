"""直接 SQL 插入 idle_* 三行,跳过整个 migration 链"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=10)

# 1. 插数据(idempotent)
sql = r"""
INSERT INTO system_settings (key, value, description, updated_at) VALUES
  ('idle_enabled',         'true'::jsonb, '是否启用闲置自动登出',          NOW()),
  ('idle_timeout_minutes', '30'::jsonb,   '无操作超时时间(分钟)',         NOW()),
  ('idle_warning_seconds', '60'::jsonb,   '登出前提前弹窗提示秒数',        NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
"""
cmd = f"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c \"{sql}\""
si, so, se = ssh.exec_command(cmd)
print('INSERT:', so.read().decode())
err = se.read().decode()
if err: print('ERR:', err)

# 2. 验证
cmd2 = r"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c \"SELECT key, value::text, description FROM system_settings WHERE key LIKE 'idle%' ORDER BY key;\""
si, so, se = ssh.exec_command(cmd2)
print('VERIFY:', so.read().decode())

# 3. 测试新路由
cmd3 = r"""curl -s -H 'Authorization: Bearer test' http://127.0.0.1:3001/api/settings/idle-config"""
si, so, se = ssh.exec_command(cmd3)
print('ROUTE TEST:', so.read().decode()[:500])

# 4. reload fpm
si, so, se = ssh.exec_command('ps -ef | grep php-fpm | grep master | grep -v grep | awk "{print \\$2}" | head -1')
pid = so.read().decode().strip()
if pid:
    si, so, se = ssh.exec_command(f'sudo -n kill -USR2 {pid} && echo FPM-RELOADED')
    print('FPM:', so.read().decode().strip())

ssh.close()
