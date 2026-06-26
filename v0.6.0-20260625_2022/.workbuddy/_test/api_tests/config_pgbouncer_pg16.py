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
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=HOST, username=USER, password=PASS, timeout=15)
print('✅ 已连接 172')

# 1. 修改 PG 16 的 pg_hba.conf (允许 127.0.0.1 trust)
print('\n📝 修改 /etc/postgresql/16/main/pg_hba.conf...')
# 先查看当前内容
out = run_cmd(client, 'head -20 /etc/postgresql/16/main/pg_hba.conf')
print('  当前前 20 行:', out[:300])

# 在文件顶部添加 trust 规则
cmd = """echo 'host    all    all    127.0.0.1/32    trust' | cat - /etc/postgresql/16/main/pg_hba.conf > /tmp/pg_hba_new.conf && mv /tmp/pg_hba_new.conf /etc/postgresql/16/main/pg_hba.conf && chown postgres:postgres /etc/postgresql/16/main/pg_hba.conf"""
out = run_cmd(client, cmd)
print('  ✅ pg_hba.conf 已更新')

# 2. 重启 PostgreSQL 16
print('\n🔄 重启 PostgreSQL 16...')
out = run_cmd(client, 'systemctl restart postgresql && sleep 3')
# 验证 PG 是否运行
out2 = run_cmd(client, 'ss -tlnp | grep 5432')
if '5432' in out2:
    print('  ✅ PostgreSQL 16 重启成功，监听 5432')
else:
    print('  ⚠️ PostgreSQL 可能未启动:', out2)

# 3. 配置 pgBouncer (auth_type = trust，连接 PG 用 Unix socket)
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

with open('/tmp/pgbouncer_ok.ini', 'w') as f:
    f.write(pgbouncer_ini)
sftp = client.open_sftp()
sftp.put('/tmp/pgbouncer_ok.ini', '/tmp/pgbouncer_ok.ini')
sftp.close()

out = run_cmd(client, 'cp /tmp/pgbouncer_ok.ini /etc/pgbouncer/pgbouncer.ini && chown pgbouncer:pgbouncer /etc/pgbouncer/pgbouncer.ini && rm /tmp/pgbouncer_ok.ini')
print('  ✅ pgbouncer.ini 已更新')

# 4. 重启 pgBouncer
print('\n🔄 重启 pgBouncer...')
out = run_cmd(client, 'systemctl restart pgbouncer && sleep 3')
out2 = run_cmd(client, 'systemctl status pgbouncer --no-pager | head -3')
if 'active (running)' in out2:
    print('  ✅ pgBouncer 重启成功')
else:
    print('  ⚠️ pgBouncer 状态:', out2)

# 5. 测试 pgBouncer 连接
print('\n🧪 测试 pgBouncer 连接...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接结果:', out[:400])
if 'test' in out or '1 row' in out:
    print('  ✅ pgBouncer 连接 PG 成功！')
else:
    print('  ⚠️ 连接失败')
    # 尝试用 postgres 用户
    out2 = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U postgres -d oa -c "SELECT 1;" 2>&1')
    print('  用 postgres 用户:', out2[:300])

# 6. 检查 Laravel .env
print('\n🔍 检查 Laravel .env DB 配置...')
out = run_cmd(client, 'cat /var/www/oa-api/.env | grep DB_')
print('  DB 配置:')
print('  ' + out.replace('\n', '\n  '))

client.close()
print('\n✅ 配置完成！')
