import paramiko

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

# 修改 pgbouncer.ini：auth_type = any
print('\n⚙️ 修改 pgbouncer.ini: auth_type = any...')
out = run_cmd(client, "sed -i 's/auth_type = trust/auth_type = any/' /etc/pgbouncer/pgbouncer.ini")
out2 = run_cmd(client, "grep 'auth_type' /etc/pgbouncer/pgbouncer.ini")
print('✅ 已更新:', out2[:100])

# 重启 pgBouncer
print('\n🔄 重启 pgBouncer...')
out = run_cmd(client, 'systemctl restart pgbouncer && sleep 3')
print('✅ pgBouncer 重启完成')

# 测试连接
print('\n🧪 测试 pgBouncer 连接...')
out = run_cmd(client, 'psql -h 127.0.0.1 -p 6432 -U oa_user -d oa -c "SELECT 1 as test;" 2>&1')
print('  连接测试:', out[:400])
if 'test' in out or '1 row' in out:
    print('✅ pgBouncer 连接成功！')
    
    # 测试 Laravel
    print('\n🧪 测试 Laravel API...')
    out2 = run_cmd(client, 'curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/projects/stats -H "Authorization: Bearer $(cat /tmp/token 2>/dev/null || echo test)" 2>&1 || echo "CURL_FAILED"')
    print('  Laravel API:', out2[:100])
else:
    print('⚠️ 仍失败，查看日志...')
    out3 = run_cmd(client, 'tail -20 /var/log/postgresql/pgbouncer.log 2>/dev/null || journalctl -u pgbouncer -n 20 --no-pager')
    print('  日志:', out3[:800])

client.close()
print('\n完成')
