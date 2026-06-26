"""Fix FinanceController::overview and check for related issues"""
import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace').strip()
    return out

sftp = ssh.open_sftp()

# ===== 1. 修 FinanceController::overview =====
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 用单行查找
import_start = content.find('public function overview(Request $request): JsonResponse')
if import_start > -1:
    # 找下一个 'public function'
    next_func = content.find('\n    public function', import_start + 10)
    if next_func > -1:
        old_method = content[import_start:next_func].rstrip()
        print('OLD overview:')
        print(old_method)
        print('---')

        new_method = '''    public function overview(Request $request): JsonResponse
    {
        // 本月已收金额
        $totalRevenue = (float) Receivable::where('received_date', '>=', now()->startOfMonth())->sum('received_amount');
        // 未收齐的应收款（status != paid 即 pending/partial/overdue）
        $totalReceivable = (float) Receivable::where('status', '!=', 'paid')->sum('remaining_amount');
        // 未付清的应付款
        $totalPayable = (float) Payable::where('status', '!=', 'paid')->sum('remaining_amount');
        // 本月已批报销支出
        $totalExpense = (float) ExpenseClaim::where('status', 'approved')
            ->where('approved_at', '>=', now()->startOfMonth())
            ->sum('total_amount');
        // 应收合同合计
        $totalReceivableAmount = (float) Receivable::sum('amount');
        // 应付合同合计
        $totalPayableAmount = (float) Payable::sum('amount');
        // 工单数量
        $totalServiceOrders = ServiceOrder::count();
        $pendingServiceOrders = ServiceOrder::where('status', 'pending')->count();
        // 项目数量
        $totalProjects = Project::count();
        $activeProjects = Project::whereNotIn('stage', ['completed', 'closed'])->count();
        // 客户数量
        $totalCustomers = Customer::count();

        return response()->json([
            'code' => 0,
            'data' => compact(
                'totalRevenue',
                'totalReceivable',
                'totalPayable',
                'totalExpense',
                'totalReceivableAmount',
                'totalPayableAmount',
                'totalServiceOrders',
                'pendingServiceOrders',
                'totalProjects',
                'activeProjects',
                'totalCustomers'
            ),
        ]);
    }'''

        new_content = content[:import_start] + new_method + '\n\n' + content[next_func+1:]
        with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/FinanceController.php', 'w') as f:
            f.write(new_content)
        print('✓ FinanceController::overview 已重写')
    else:
        print('找不到下一个 function 边界')
else:
    print('找不到 overview 方法')

# ===== 2. 查 attendance 路由补 calendar / makeup-cards =====
print()
print('=== attendance 路由 ===')
routes = run("cd /var/www/oa-api && sudo -u www-data php artisan route:list 2>&1 | grep -i 'attendance\\|calendar\\|makeup' | head -20")
print(routes)

# ===== 3. 重启 FPM =====
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)
print('FPM restarted')

# ===== 4. 测接口 =====
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
tests = [
    ('GET', '/api/finance/overview'),
    ('GET', '/api/attendance/overview'),
    ('GET', '/api/attendance/records?page=1&per_page=5'),
    ('GET', '/api/service/orders/1'),
]
for method, url in tests:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f'  [{r.status}] {method} {url}: {r.read().decode()[:200]}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {method} {url}: {e.read().decode()[:200]}')
    except Exception as e:
        print(f'  [ERR] {url}: {e}')

ssh.close()
