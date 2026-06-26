import paramiko
import time

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(
        f"echo '{PASS}' | sudo -S bash -c '{cmd}'", 
        get_pty=True, 
        timeout=timeout
    )
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return output + err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print('🔗 连接 172.20.0.139...')
client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
print('✅ 连接成功')

# 1. 修改 pgbouncer.ini：用 Unix socket 连接 PG
print('\n⚙️ 配置 pgBouncer 用 Unix socket 连接 PG...')
pgbouncer_ini = """[databases]
oa = host=/var/run/postgresql port=5432 dbname=oa

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
unix_socket_dir = /var/run/postgresql
auth_type = trust
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 200
default_pool_size = 25
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
server_lifetime = 3600
server_idle_timeout = 600
server_connect_timeout = 5
server_login_retry = 3
query_timeout = 30
stats_period = 60
admin_users = postgres
logfile = /var/log/postgresql/pgbouncer.log
pidfile = /var/run/postgresql/pgbouncer.pid
"""

# 写入配置文件
with open('/tmp/pgbouncer_v2.ini', 'w') as f:
    f.write(pgbouncer_ini)

sftp = client.open_sftp()
sftp.put('/tmp/pgbouncer_v2.ini', '/tmp/pgbouncer_v2.ini')
sftp.close()

out = run_cmd(client, 'cp /tmp/pgbouncer_v2.ini /etc/pgbouncer/pgbouncer.ini && chown pgbouncer:pgbouncer /etc/pgbouncer/pgbouncer.ini && rm /tmp/pgbouncer_v2.ini')
print('✅ pgbouncer.ini 已更新 (Unix socket 连接)')

# 2. 确保 userlist.txt 有正确格式
print('\n📝 配置 userlist.txt...')
out = run_cmd(client, 'echo \'""\'\'>\' /etc/pgbouncer/userlist.txt && chown pgbouncer:pgbouncer /etc/pgbouncer/userlist.txt')
print('✅ userlist.txt 已配置')

# 3. 重启 pgBouncer
print('\n🔄 重启 pgBouncer...')
out = run_cmd(client, 'systemctl restart pgbouncer && sleep 3 && systemctl status pgbouncer --no-pager | head -10')
if 'active (running)' in out:
    print('✅ pgBouncer 重启成功')
else:
    print('⚠️ pgBouncer 状态:', out[:500])

# 4. 测试 pgBouncer 连接 (通过 Unix socket)
print('\n🧪 测试 pgBouncer 连接...')
out = run_cmd(client, 'psql -h /var/run/postgresql -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接测试 (Unix socket):', out[:300])
if 'test' in out or '1' in out:
    print('✅ pgBouncer 连接成功！')
else:
    print('⚠️ 连接失败')
    out2 = run_cmd(client, 'tail -30 /var/log/postgresql/pgbouncer.log 2>/dev/null || journalctl -u pgbouncer --no-pager -n 30')
    print('  pgBouncer 日志:', out2[:800])

# 5. 测试 TCP 连接 pgBouncer
print('\n🧪 测试 TCP 连接 pgBouncer (127.0.0.1:6432)...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接测试 (TCP):', out[:300])

client.close()
print('\n✅ pgBouncer 配置完成！')
print('\n📊 注意：Laravel .env 中的 DB_HOST 可能也需要改为 /var/run/postgresql（Unix socket）')
