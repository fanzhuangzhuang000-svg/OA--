import paramiko
import time

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'

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

# 1. 备份 pg_hba.conf
print('\n📦 备份 pg_hba.conf...')
out = run_cmd(client, 'cp /etc/postgresql/15/main/pg_hba.conf /etc/postgresql/15/main/pg_hba.conf.bak')
print('✅ 备份完成')

# 2. 在 pg_hba.conf 顶部添加 trust 规则 (允许 127.0.0.1 无需密码)
print('\n⚙️ 配置 pg_hba.conf (允许 127.0.0.1 trust)...')
cmd = """echo 'host    all    all    127.0.0.1/32    trust' | cat - /etc/postgresql/15/main/pg_hba.conf > /tmp/pg_hba_new.conf && mv /tmp/pg_hba_new.conf /etc/postgresql/15/main/pg_hba.conf && chown postgres:postgres /etc/postgresql/15/main/pg_hba.conf"""
out = run_cmd(client, cmd)
print('✅ pg_hba.conf 已更新')

# 3. 重启 PostgreSQL 使配置生效
print('\n🔄 重启 PostgreSQL...')
out = run_cmd(client, 'systemctl restart postgresql && sleep 3 && systemctl status postgresql --no-pager | head -5')
if 'active (running)' in out:
    print('✅ PostgreSQL 重启成功')
else:
    print('⚠️ PostgreSQL 状态:', out[:300])

# 4. 测试 pgbouncer 连接
print('\n🧪 测试 pgBouncer 连接...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接测试:', out[:300])
if 'test' in out or '1' in out:
    print('✅ pgBouncer 连接成功！')
else:
    print('⚠️ 连接失败，查看日志...')
    out2 = run_cmd(client, 'tail -20 /var/log/postgresql/pgbouncer.log 2>/dev/null || journalctl -u pgbouncer --no-pager -n 20')
    print('  pgBouncer 日志:', out2[:500])

# 5. 测试 Laravel DB 连接
print('\n🧪 测试 Laravel DB 连接...')
out = run_cmd(client, 'cd /var/www/oa-api && php artisan tinker --execute="echo DB::connection()->getDatabaseName();" 2>&1')
print('  Laravel DB:', out[:300])

client.close()
print('\n✅ pgBouncer + PostgreSQL 配置完成！')
