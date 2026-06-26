import paramiko
import time

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
API_REMOTE = '/var/www/oa-api'

def run_cmd(client, cmd, timeout=30):
    """执行命令并返回输出"""
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

# 1. 安装 pgBouncer
print('\n📦 安装 pgBouncer...')
out = run_cmd(client, 'apt-get update && apt-get install -y pgbouncer', timeout=120)
if 'Setting up pgbouncer' in out or 'already installed' in out or 'pgbouncer is already' in out:
    print('✅ pgBouncer 安装成功')
else:
    print('⚠️ 安装输出:', out[:500])

# 2. 配置 pgBouncer
print('\n⚙️ 配置 pgBouncer...')

pgbouncer_ini = """
[databases]
oa = host=127.0.0.1 port=5432 dbname=oa

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
"""

# 写入配置文件
print('  - 写入 pgbouncer.ini...')
with open('/tmp/pgbouncer.ini', 'w') as f:
    f.write(pgbouncer_ini)

sftp = client.open_sftp()
sftp.put('/tmp/pgbouncer.ini', '/tmp/pgbouncer.ini')
sftp.close()

out = run_cmd(client, 'cp /tmp/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini && chown pgbouncer:pgbouncer /etc/pgbouncer/pgbouncer.ini && rm /tmp/pgbouncer.ini')
print('  ✅ pgbouncer.ini 已写入')

# 3. 配置 userlist.txt (trust 模式，空文件即可)
print('  - 配置 userlist.txt...')
out = run_cmd(client, 'echo \'""\'\'>\' /etc/pgbouncer/userlist.txt && chown pgbouncer:pgbouncer /etc/pgbouncer/userlist.txt')
print('  ✅ userlist.txt 已配置')

# 4. 修改 Laravel .env (DB_PORT=6432)
print('\n🔧 修改 Laravel .env (DB_PORT=6432)...')
out = run_cmd(client, f'sed -i "s/DB_PORT=5432/DB_PORT=6432/" {API_REMOTE}/.env')
out2 = run_cmd(client, f'grep DB_PORT {API_REMOTE}/.env')
print('  ✅ .env 已更新:', out2[:100])

# 5. 启动 pgBouncer
print('\n🚀 启动 pgBouncer...')
out = run_cmd(client, 'systemctl enable pgbouncer && systemctl restart pgbouncer && sleep 2 && systemctl status pgbouncer --no-pager', timeout=15)
if 'active (running)' in out:
    print('✅ pgBouncer 启动成功')
else:
    print('⚠️ pgBouncer 状态:', out[:500])

# 6. 验证 pgBouncer 端口
print('\n🔍 验证 pgBouncer 端口 6432...')
out = run_cmd(client, 'ss -tlnp | grep 6432')
if '6432' in out:
    print('✅ pgBouncer 监听 6432 端口')
else:
    print('⚠️ 端口未监听:', out)

# 7. 测试 pgBouncer 连接
print('\n🧪 测试 pgBouncer 连接...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1;" 2>&1 || echo "CONN_FAILED"')
print('  连接测试:', out[:300])

# 8. 重启 FPM (让 Laravel 重新读取 .env)
print('\n🔄 重启 PHP-FPM...')
out = run_cmd(client, 'systemctl restart php8.3-fpm && sleep 2 && systemctl status php8.3-fpm --no-pager | head -5')
if 'active (running)' in out:
    print('✅ FPM 重启成功')
else:
    print('⚠️ FPM 状态:', out[:300])

# 9. 验证 Laravel 能连 PG (通过 pgBouncer)
print('\n🧪 验证 Laravel DB 连接...')
out = run_cmd(client, f'cd {API_REMOTE} && php artisan tinker --execute="try {{ DB::connection()->getPdo(); echo \\"DB_OK\\"; }} catch (\\Exception $e) {{ echo \\"DB_FAIL: \\" . $e->getMessage(); }}"\' 2>&1')
print('  Laravel DB 连接:', out[:300])

client.close()
print('\n✅ pgBouncer 配置完成！')
print('\n📊 下一步: 跑性能测试验证 50 并发优化效果')
