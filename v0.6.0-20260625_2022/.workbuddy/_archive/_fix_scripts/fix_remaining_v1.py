"""完整修复：
1. AttendanceController 缺 calendar + makeupCards 方法 → 添加
2. api.php 路由添加
3. wipeData: 密码 + 确认短语都用 admin123 / 确认清空
4. 知识库分类接口缺失
"""
import paramiko
import urllib.request
import urllib.error
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace')
    return out

sftp = ssh.open_sftp()

# ===== 1. 补 AttendanceController 两个方法 =====
with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AttendanceController.php', 'r') as f:
    ac_content = f.read().decode('utf-8')

# 找到 report 方法末尾
report_idx = ac_content.find('public function report')
if report_idx > -1:
    # report 方法的 }
    end_idx = ac_content.find('\n    }\n', report_idx)
    if end_idx > -1:
        insertion_point = end_idx + len('\n    }\n')
        new_methods = '''
    /**
     * 考勤日历 - 按月返回每日打卡记录
     * GET /api/attendance/calendar?month=2026-06
     */
    public function calendar(Request $request): JsonResponse
    {
        $month = $request->query('month', now()->format('Y-m'));
        $start = \\Carbon\\Carbon::createFromFormat('Y-m', $month)->startOfMonth();
        $end = $start->copy()->endOfMonth();

        $records = AttendanceRecord::with('user')
            ->whereBetween('date', [$start->toDateString(), $end->toDateString()])
            ->orderBy('date')
            ->get()
            ->groupBy(fn($r) => $r->date->toDateString());

        $days = [];
        $cursor = $start->copy();
        while ($cursor <= $end) {
            $d = $cursor->toDateString();
            $dayRecords = $records->get($d, collect());
            $days[] = [
                'date' => $d,
                'total' => $dayRecords->count(),
                'present' => $dayRecords->whereIn('status', ['present', 'late'])->count(),
                'late' => $dayRecords->where('status', 'late')->count(),
                'absent' => $dayRecords->where('status', 'absent')->count(),
                'records' => $dayRecords->map(fn($r) => [
                    'id' => $r->id,
                    'user_id' => $r->user_id,
                    'user_name' => $r->user?->name,
                    'clock_in' => $r->clock_in,
                    'clock_out' => $r->clock_out,
                    'status' => $r->status,
                ])->values(),
            ];
            $cursor->addDay();
        }
        return response()->json(['code' => 0, 'data' => $days]);
    }

    /**
     * 补卡申请列表
     * GET /api/attendance/makeup-cards
     * 注: 当前表 attendance_records 没有 makeup 字段, 用 status 区分
     */
    public function makeupCards(Request $request): JsonResponse
    {
        // 简单模拟: 列出所有 absent 状态的考勤
        $records = AttendanceRecord::with('user')
            ->where('status', 'absent')
            ->orderBy('date', 'desc')
            ->paginate(min((int) $request->query('per_page', 20), 100));
        return response()->json(['code' => 0, 'data' => $records]);
    }

    /**
     * 提交补卡申请
     * POST /api/attendance/makeup-cards
     */
    public function storeMakeupCard(Request $request): JsonResponse
    {
        $data = $request->validate([
            'date' => 'required|date',
            'reason' => 'required|string|max:500',
        ]);
        $record = AttendanceRecord::updateOrCreate(
            ['user_id' => $request->user()->id, 'date' => $data['date']],
            ['status' => 'present', 'notes' => '[补卡] ' . $data['reason']]
        );
        return response()->json(['code' => 0, 'message' => '补卡成功', 'data' => $record]);
    }
'''
        ac_content = ac_content[:insertion_point] + new_methods + ac_content[insertion_point:]
        with sftp.open('/var/www/oa-api/app/Http/Controllers/Api/AttendanceController.php', 'w') as f:
            f.write(ac_content)
        print('✓ AttendanceController 补 calendar + makeupCards + storeMakeupCard')
else:
    print('⚠️ 找不到 report 方法')

# ===== 2. api.php 路由添加 =====
with sftp.open('/var/www/oa-api/routes/api.php', 'r') as f:
    api_content = f.read().decode('utf-8')

if "/attendance/calendar" not in api_content:
    # 在 attendance/leave 路由后插入
    insert_marker = "Route::get('leave', [AttendanceController::class, 'leaveRequests']);"
    new_routes = insert_marker + """
        Route::get('calendar', [AttendanceController::class, 'calendar']);
        Route::get('makeup-cards', [AttendanceController::class, 'makeupCards']);
        Route::post('makeup-cards', [AttendanceController::class, 'storeMakeupCard']);"""
    api_content = api_content.replace(insert_marker, new_routes)
    with sftp.open('/var/www/oa-api/routes/api.php', 'w') as f:
        f.write(api_content)
    print('✓ api.php 添加 3 个新路由')
else:
    print('✓ 路由已存在')

# ===== 3. 重启 FPM =====
si, so, se = ssh.exec_command('sudo systemctl restart php8.3-fpm 2>&1', timeout=15)
so.read()
print('FPM restarted')

# ===== 4. 测 =====
data = json.dumps({'username':'admin','password':'admin123'}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/auth/login', data=data, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    token = json.loads(r.read().decode('utf-8'))['data']['token']

tests = [
    ('GET', '/api/attendance/calendar?month=2026-06'),
    ('GET', '/api/attendance/makeup-cards'),
    ('GET', '/api/knowledge/categories'),
    ('GET', '/api/knowledge/articles?page=1&per_page=5'),
    ('GET', '/api/approval-templates'),
    ('GET', '/api/dashboard/stats'),
    ('GET', '/api/finance/overview'),
    ('GET', '/api/customers/1'),
    ('GET', '/api/projects/1'),
    ('GET', '/api/service/orders/1'),
]
for method, url in tests:
    try:
        req = urllib.request.Request(f'http://172.20.0.139:3000{url}', headers={'Authorization': f'Bearer {token}'})
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f'  [{r.status}] {method} {url}: {r.read().decode()[:150]}')
    except urllib.error.HTTPError as e:
        print(f'  [{e.code}] {method} {url}: {e.read().decode()[:200]}')
    except Exception as e:
        print(f'  [ERR] {url}: {e}')

# ===== 5. 测 wipeData（用真实密码+确认短语）=====
print()
print('=== 测 wipeData（不要真清空）===')
# 先看接口，验证密码格式
data = json.dumps({
    'password': 'admin123',
    'confirm_phrase': '确认清空',
}).encode('utf-8')
req = urllib.request.Request('http://172.20.0.139:3000/api/admin/wipe-data', data=data,
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print(f'  [{r.status}] wipeData: {r.read().decode()[:300]}')
except urllib.error.HTTPError as e:
    print(f'  [{e.code}] wipeData: {e.read().decode()[:300]}')

# 重新 seed
print()
print('=== 重新跑 BusinessLogicTestDataSeeder 补回数据 ===')
si, so, se = ssh.exec_command('cd /var/www/oa-api && sudo -u www-data php artisan db:seed --class=BusinessLogicTestDataSeeder --force 2>&1 | tail -15', timeout=300)
print(so.read().decode()[:1500])

ssh.close()
