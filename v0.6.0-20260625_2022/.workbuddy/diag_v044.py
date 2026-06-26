"""抓 117 上的真实错误日志定位 POST 422 根因"""
import paramiko, json, time

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)

# 登录
si, so, se = ssh.exec_command(
    '''curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}' ''',
    timeout=30
)
login = json.loads(so.read().decode())
token = (login.get('data') or {}).get('token')

# 抓最近 50 行 laravel.log
print('=== laravel.log tail ===')
si, so, se = ssh.exec_command('sudo -n tail -60 /var/www/oa-api/storage/logs/laravel.log 2>&1', timeout=10)
print(so.read().decode('utf-8', 'replace'))

# 再 POST 一次团队看完整错
print('\n=== POST 团队 (抓完整错) ===')
body = '{"project_id":218,"team_name":"验收测试-A","team_type":"internal","leader_name":"张","leader_phone":"138"}'
si, so, se = ssh.exec_command(
    f"""curl -s -X POST 'http://127.0.0.1/api/construction/teams' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{body}'""",
    timeout=30
)
print(so.read().decode('utf-8', 'replace'))

# 查 construction_teams 真实 schema
print('\n=== construction_teams 真实列 ===')
si, so, se = ssh.exec_command('PGPASSWORD=nbcy123 psql -h 127.0.0.1 -U nbcy -d security_oa -c "\\d construction_teams" 2>&1 | head -30', timeout=10)
print(so.read().decode('utf-8', 'replace'))

print('\n=== project_commencement_orders 真实列 ===')
si, so, se = ssh.exec_command('PGPASSWORD=nbcy123 psql -h 127.0.0.1 -U nbcy -d security_oa -c "\\d project_commencement_orders" 2>&1 | head -30', timeout=10)
print(so.read().decode('utf-8', 'replace'))

print('\n=== external_construction_works 真实列 ===')
si, so, se = ssh.exec_command('PGPASSWORD=nbcy123 psql -h 127.0.0.1 -U nbcy -d security_oa -c "\\d external_construction_works" 2>&1 | head -30', timeout=10)
print(so.read().decode('utf-8', 'replace'))

print('\n=== rectifications 真实列 ===')
si, so, se = ssh.exec_command('PGPASSWORD=nbcy123 psql -h 127.0.0.1 -U nbcy -d security_oa -c "\\d rectifications" 2>&1 | head -30', timeout=10)
print(so.read().decode('utf-8', 'replace'))

print('\n=== construction_logs 真实列 ===')
si, so, se = ssh.exec_command('PGPASSWORD=nbcy123 psql -h 127.0.0.1 -U nbcy -d security_oa -c "\\d construction_logs" 2>&1 | head -30', timeout=10)
print(so.read().decode('utf-8', 'replace'))

# 检查 ConstructionLogService::createLog
print('\n=== ConstructionLogService methods ===')
si, so, se = ssh.exec_command('grep -n "function " /var/www/oa-api/app/Services/ConstructionLogService.php | head -20', timeout=10)
print(so.read().decode('utf-8', 'replace'))

ssh.close()
