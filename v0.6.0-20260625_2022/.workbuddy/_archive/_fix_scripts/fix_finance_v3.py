"""用 Python 在 server 端重写 FinanceController::overview"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 找 ExpenseClaim 4 行
import re
m = re.search(r'        // 本月已批报销支出\n        \$totalExpense = \(float\) ExpenseClaim::where\(.status., .approved.\)\n            ->where\(.approved_at., .>= ., now\(\)->startOfMonth\(\)\)\n            ->sum\(.total_amount.\);\n', content)
if m:
    print('找到 ExpenseClaim 段，长度:', len(m.group(0)))
    content = content.replace(m.group(0), '')
    print('✓ 删除 ExpenseClaim 段')
else:
    # 尝试简化匹配
    m = re.search(r'.*ExpenseClaim.*\n.*->sum\(.total_amount.\);\n', content)
    if m:
        print('找到相似段:', repr(m.group(0))[:200])
        content = content.replace(m.group(0), '')

# 验证
if 'ExpenseClaim' in content:
    print('⚠️ 还有 ExpenseClaim 引用')
    # 找出剩余位置
    for i, line in enumerate(content.split('\n')):
        if 'ExpenseClaim' in line:
            print(f'  L{i}: {line}')
else:
    print('✓ 全部 ExpenseClaim 已删除')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'w') as f:
    f.write(content)
sftp.close()

# 重启 FPM
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=15)
so.read()
print('FPM restarted')

# 测试
import urllib.request, json
import urllib.error

data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

try:
    req = urllib.request.Request('http://172.20.0.139:3000/api/finance/overview', headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=10) as r:
        print('overview:', r.read().decode())
except urllib.error.HTTPError as e:
    print('overview HTTP', e.code, e.read().decode())
