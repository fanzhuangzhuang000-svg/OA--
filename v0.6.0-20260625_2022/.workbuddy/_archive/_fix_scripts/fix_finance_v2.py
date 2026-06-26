"""用 sftp 写入正确的 FinanceController::overview（去掉 ExpenseClaim + 加 use）"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 删除 ExpenseClaim 4 行
old = """        // 本月已批报销支出
        $totalExpense = (float) ExpenseClaim::where('status', 'approved')
            ->where('approved_at', '>= ', now()->startOfMonth())
            ->sum('total_amount');
"""
if old in content:
    content = content.replace(old, '')
    print('✓ 删除 ExpenseClaim 行')
else:
    print('⚠️ 未找到 old ExpenseClaim 块（可能已被替换）')

# 添加缺失的 use
old_use = "use App\\Models\\Payable;"
new_use = """use App\\Models\\Payable;
use App\\Models\\ServiceOrder;
use App\\Models\\Project;
use App\\Models\\Customer;"""
if 'use App\\Models\\ServiceOrder;' not in content:
    content = content.replace(old_use, new_use)
    print('✓ 添加 use: ServiceOrder, Project, Customer')

with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'w') as f:
    f.write(content)
sftp.close()

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

# 重启 FPM
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)
print('FPM restarted')

# 测试
import urllib.request, json
import urllib.error

data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

tests = [
    '/api/finance/overview',
    '/api/finance/receivables?page=1&per_page=5',
    '/api/finance/payables?page=1&per_page=5',
    '/api/dashboard/stats',
]
for url in tests:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f'  [{r.status}] {url}: {r.read().decode()[:300]}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:300]}')
    except Exception as e:
        print(f'  [ERR] {url}: {e}')

ssh.close()
