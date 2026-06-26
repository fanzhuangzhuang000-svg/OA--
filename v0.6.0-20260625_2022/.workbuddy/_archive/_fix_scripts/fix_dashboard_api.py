"""给 DashboardController 加 4 个方法：todo/project-progress/service-stats/revenue-trend"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

sftp = ssh.open_sftp()
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'r') as f:
    content = f.read().decode('utf-8')

# 4 个新方法
new_methods = '''
    public function todo(): JsonResponse
    {
        $expensePending = \\ExpenseClaim::where('status', 'submitted')->count();
        $leavePending = \\LeaveRequest::where('status', 'pending')->count();
        $dispatchPending = \\ServiceOrder::where('status', 'pending')->count();
        $receivablePending = \\Receivable::whereIn('status', ['pending', 'partial', 'overdue'])->count();

        $list = [];
        $id = 1;
        if ($expensePending > 0) {
            $list[] = ['id' => $id++, 'type' => '审批', 'content' => $expensePending . ' 笔报销待审批', 'time' => '刚刚', 'tagType' => 'warning', 'link' => '/expense/approval'];
        }
        if ($leavePending > 0) {
            $list[] = ['id' => $id++, 'type' => '审批', 'content' => $leavePending . ' 个请假待审批', 'time' => '刚刚', 'tagType' => 'warning', 'link' => '/attendance/leave'];
        }
        if ($dispatchPending > 0) {
            $list[] = ['id' => $id++, 'type' => '工单', 'content' => $dispatchPending . ' 个工单待派单', 'time' => '刚刚', 'tagType' => 'danger', 'link' => '/service/orders'];
        }
        if ($receivablePending > 0) {
            $list[] = ['id' => $id++, 'type' => '回款', 'content' => $receivablePending . ' 笔应收待回款', 'time' => '刚刚', 'tagType' => 'info', 'link' => '/finance/receivables'];
        }
        if (empty($list)) {
            $list[] = ['id' => 1, 'type' => '提示', 'content' => '暂无待办事项', 'time' => '刚刚', 'tagType' => 'info', 'link' => ''];
        }
        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function projectProgress(): JsonResponse
    {
        $projects = \\Project::orderBy('updated_at', 'desc')->take(5)->get(['id', 'name', 'stage', 'progress', 'end_date']);
        $managerIds = $projects->pluck('manager_id')->filter()->unique()->all();
        $managers = empty($managerIds) ? [] : \\DB::table('users')->whereIn('id', $managerIds)->pluck('name', 'id')->toArray();
        $data = $projects->map(function ($p) use ($managers) {
            return [
                'id' => $p->id,
                'name' => $p->name,
                'stage' => $p->stage ?? 'initiation',
                'progress' => (int) ($p->progress ?? 0),
                'manager' => $managers[$p->manager_id] ?? '—',
                'deadline' => $p->end_date ? substr((string) $p->end_date, 0, 10) : '—',
            ];
        });
        return response()->json(['code' => 0, 'data' => $data]);
    }

    public function serviceStats(): JsonResponse
    {
        $today = today();
        $stats = [
            'today_new' => \\ServiceOrder::whereDate('created_at', $today)->count(),
            'processing' => \\ServiceOrder::whereIn('status', ['assigned', 'in_progress'])->count(),
            'today_done' => \\ServiceOrder::whereDate('completed_at', $today)->count(),
            'month_done' => \\ServiceOrder::whereMonth('completed_at', now()->month)->whereYear('completed_at', now()->year)->count(),
            'sla_rate' => 100.0,
        ];
        return response()->json(['code' => 0, 'data' => $stats]);
    }

    public function revenueTrend(\\Illuminate\\Http\\Request $request): JsonResponse
    {
        $type = $request->query('type', 'contract');
        $data = [];
        for ($i = 5; $i >= 0; $i--) {
            $dt = now()->subMonths($i);
            $contract = (float) \\Receivable::whereYear('created_at', $dt->year)
                ->whereMonth('created_at', $dt->month)->sum('amount');
            $payment = (float) \\Receivable::whereYear('received_date', $dt->year)
                ->whereMonth('received_date', $dt->month)->sum('received_amount');
            $data[] = [
                'month' => $dt->month . '月',
                'contract' => round($contract / 10000, 1),
                'payment' => round($payment / 10000, 1),
            ];
        }
        return response()->json(['code' => 0, 'data' => $data]);
    }
'''

# 在最后一个 } 前插入新方法
# 找 class 末尾的 }
marker = "    private function formatYuan(float $amount): string\n    {\n"
if marker in content:
    # 在 formatYuan 之前插入新方法
    content = content.replace(marker, new_methods + "\n" + marker)
    with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/DashboardController.php', 'w') as f:
        f.write(content)
    print('✓ 4 个新方法已添加')
else:
    print('❌ 找不到插入点')

sftp.close()

import paramiko
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd, t=10):
    si, so, se = ssh2.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8','replace').strip()
    return out

# 清缓存 + 重启
run('cd /var/www/oa-api && sudo -u www-data php artisan route:clear 2>&1', t=15)
run('cd /var/www/oa-api && sudo -u www-data php artisan config:clear 2>&1', t=15)
run('sudo systemctl restart php8.3-fpm 2>&1', t=15)

# 验证路由
out = run("sudo -u www-data php /var/www/oa-api/artisan route:list 2>&1 | grep -i dashboard | head -10")
print('=== 新路由 ===')
print(out)

# 测 4 个接口
import urllib.request, json
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

import urllib.error
for url in ['/api/dashboard/todo', '/api/dashboard/project-progress', '/api/dashboard/service-stats', '/api/dashboard/revenue-trend']:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8')[:300]
            print(f'  [200] {url}: {body}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {url}: {e.read().decode()[:200]}')

ssh2.close()
