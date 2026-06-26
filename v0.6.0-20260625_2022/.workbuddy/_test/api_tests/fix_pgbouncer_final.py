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

# 1. 修改 pg_hba.conf：允许本地 Unix socket trust
print('\n⚙️ 修改 pg_hba.conf (local trust)...')
out = run_cmd(client, "sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' /etc/postgresql/15/main/pg_hba.conf")
out2 = run_cmd(client, "grep 'local.*all.*all' /etc/postgresql/15/main/pg_hba.conf")
print('✅ pg_hba.conf 已更新:', out2[:100])

# 2. 重启 PostgreSQL
print('\n🔄 重启 PostgreSQL...')
out = run_cmd(client, 'systemctl restart postgresql && sleep 3')
print('✅ PostgreSQL 重启完成')

# 3. 配置 pgBouncer (用 Unix socket 连 PG)
print('\n⚙️ 配置 pgBouncer...')
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

with open('/tmp/pgbouncer_final.ini', 'w') as f:
    f.write(pgbouncer_ini)

sftp = client.open_sftp()
sftp.put('/tmp/pgbouncer_final.ini', '/tmp/pgbouncer_final.ini')
sftp.close()

out = run_cmd(client, 'cp /tmp/pgbouncer_final.ini /etc/pgbouncer/pgbouncer.ini && chown pgbouncer:pgbouncer /etc/pgbouncer/pgbouncer.ini && rm /tmp/pgbouncer_final.ini')
print('✅ pgbouncer.ini 已更新')

# 4. 重启 pgBouncer
print('\n🔄 重启 pgBouncer...')
out = run_cmd(client, 'systemctl restart pgbouncer && sleep 3 && systemctl status pgbouncer --no-pager | head -10')
if 'active (running)' in out:
    print('✅ pgBouncer 重启成功')
else:
    print('⚠️ pgBouncer 状态:', out[:500])

# 5. 测试 pgBouncer 连接
print('\n🧪 测试 pgBouncer 连接 (TCP 127.0.0.1:6432)...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接测试:', out[:400])
if 'test' in out or '1 row' in out:
    print('✅ pgBouncer 连接成功！')
    
    # 6. 测试 Laravel 连接
    print('\n🧪 测试 Laravel DB 连接...')
    out2 = run_cmd(client, 'cd /var/www/oa-api && php artisan db:monitor 2>&1 || php -r "echo \\"DB_HOST: \\" . env(\\"DB_HOST\\") . \\"\\n\\";"')
    print('  Laravel:', out2[:200])
else:
    print('⚠️ 连接失败，查看日志...')
    out3 = run_cmd(client, 'tail -30 /var/log/postgresql/pgbouncer.log 2>/dev/null || journalctl -u pgbouncer -n 30 --no-pager')
    print('  日志:', out3[:800])

client.close()
print('\n✅ 配置完成！')
