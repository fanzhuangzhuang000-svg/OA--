"""修 EmployeeController::departments：User 关系带外键 department_id"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/EmployeeController.php', 'rb') as f:
    content = f.read().decode('utf-8')

# 修 departments 方法里的 'users:id,department_id' → 显式外键
old = "'users:id,department_id'"
new = "'users:id,name,department_id'"
if old in content:
    content = content.replace(old, new)
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/EmployeeController.php', 'w') as f:
        f.write(content)
    print('✓ Department.users 关联已加 name 字段')
else:
    print('⚠️ 找不到原字符串')

sftp.close()

# 重启
import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=10):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

run('cd /var/www/oa-api && sudo -u www-data composer dump-autoload 2>&1 | tail -2', t=30)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

# 测接口
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

out = run(f'curl -s http://172.20.0.139:3000/api/employees/departments -H "Authorization: Bearer {token}" 2>&1 | head -c 2000')
print('=== 接口响应 ===')
print(out)

ssh2.close()
