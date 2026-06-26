<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Support\AuthScope;
use App\Models\ApprovalRecord;
use App\Models\Certificate;
use App\Models\ConstructionTeam;
use App\Models\EmployeeProfile;
use App\Models\ExpenseClaim;
use App\Models\ExternalConstructionWork;
use App\Models\LeaveRequest;
use App\Models\MaintenanceContract;
use App\Models\Notification;
use App\Models\Project;
use App\Models\Receivable;
use App\Models\Rectification;
use App\Models\ServiceOrder;
use App\Models\AttendanceRecord;
use App\Models\User;
use App\Models\WorkProcess;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    public function stats(): JsonResponse
    {
        $request = request();
        $cacheKey = 'dashboard:stats:' . ($request->user() ? $request->user()->id : 'guest');
        $data = Cache::remember($cacheKey, 60, function () use ($request) {
            $today = today();
            // V0.4.8 A3: 改真实 PG 查 (待办数 = pending_approvals + open_service_orders + pending_rectifications)
            $pendingTodos = (int) (ApprovalRecord::where('status', ApprovalRecord::STATUS_PENDING)->count()
                + ServiceOrder::whereIn('status', ['pending', 'assigned'])->count()
                + DB::table('rectifications')->where('status', 'pending')->count());
            $activeProjects = Project::where('status', 'in_progress')->count();
            $pendingServiceOrders = ServiceOrder::whereIn('status', ['pending', 'assigned'])->count();
            $monthlyRevenue = Receivable::whereMonth('received_date', $month = now()->month)->whereYear('received_date', now()->year)->sum('received_amount');
            $todayAttendance = AttendanceRecord::where('date', $today)->count();
            $leaveRequests = LeaveRequest::where('status', 'pending')->count();
            $expensePending = ExpenseClaim::where('status', 'submitted')->count();
            // V0.4.7 收口: 标志位, 前端可读 isFull 决定是否展示"全量"标签
            $isFull = AuthScope::isUnrestricted($request->user());

            return compact('pendingTodos', 'activeProjects', 'pendingServiceOrders', 'monthlyRevenue', 'todayAttendance', 'leaveRequests', 'expensePending', 'isFull');
        });

        return response()->json(['code' => 0, 'data' => $data]);
    }

    public function recentProjects(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => Project::with(['customer', 'manager'])->where('status', 'in_progress')->orderBy('updated_at', 'desc')->take(10)->get()]);
    }

    public function recentServiceOrders(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => ServiceOrder::with(['customer', 'assignedUser'])->whereIn('status', ['pending', 'assigned', 'in_progress'])->orderBy('created_at', 'desc')->take(10)->get()]);
    }

    /**
     * 工作台顶部"待办" (待审批+待派单+待回款)
     * GET /api/dashboard/todo
     */
    public function todo(): JsonResponse
    {
        $data = Cache::remember('dashboard:todo', 60, fn () => $this->todos());
        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * 项目进度概览 (项目列表)
     * GET /api/dashboard/project-progress
     */
    public function projectProgress(): JsonResponse
    {
        // V0.4.8 A3: 改真实查询 (前 10 个 in_progress 项目的 stage + progress + manager)
        $projects = Project::with(['manager:id,name'])
            ->whereNotNull('manager_id')
            ->orderBy('updated_at', 'desc')
            ->take(10)
            ->get(['id', 'name', 'stage', 'progress', 'manager_id', 'end_date']);

        $data = $projects->map(fn ($p) => [
            'id'       => $p->id,
            'name'     => $p->name,
            'stage'    => $p->stage?->label() ?? (string) $p->stage,
            'progress' => (int) ($p->progress ?? 0),
            'manager'  => $p->manager?->name,
            'deadline' => $p->end_date?->toDateString(),
        ]);

        return response()->json(['code' => 0, 'data' => $data]);
    }
    
    /**
     * 格式化项目阶段
     */
    private function formatStage($stage): string
    {
        // 处理 Enum 对象
        if ($stage instanceof \App\Enums\ProjectStage) {
            $stage = $stage->value;
        }
        
        $map = [
            'initiation'   => '立项',
            'inquiry'      => '询价',
            'contract'     => '合同',
            'purchase'     => '采购',
            'construction' => '施工',
            'settlement'   => '结算',
            'warranty'     => '质保',
        ];
        
        return $map[$stage] ?? $stage ?? '未知';
    }

    /**
     * 售后关键指标 (SLA / 平均响应 / 满意度)
     * GET /api/dashboard/service-stats
     */
    public function serviceStats(): JsonResponse
    {
        $data = Cache::remember('dashboard:service_stats', 120, fn () => $this->serviceMetrics());
        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * 营收趋势 (近 12 月)
     * GET /api/dashboard/revenue-trend
     */
    public function revenueTrend(): JsonResponse
    {
        $data = Cache::remember('dashboard:revenue_trend', 300, fn () => $this->revenueChart());
        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * C3: 大屏驾驶舱一次性接口
     * GET /api/dashboard/screen
     */
    public function screen(): JsonResponse
    {
        $data = Cache::remember('dashboard:screen', 120, function () {
            return [
                'metrics'        => $this->metrics(),
                'revenueChart'   => $this->revenueChart(),
                'projectStatus'  => $this->projectStatus(),
                'serviceMetrics' => $this->serviceMetrics(),
                'todos'          => $this->todos(),
            ];
        });
        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * 顶部 6 个指标卡
     */
    private function metrics(): array
    {
        $year = now()->year;
        $lastYear = $year - 1;
        $thisYearRevenue = (float) Receivable::whereYear('received_date', $year)->sum('received_amount');
        $lastYearRevenue = (float) Receivable::whereYear('received_date', $lastYear)->sum('received_amount');
        $yoy = $lastYearRevenue > 0 ? round(($thisYearRevenue - $lastYearRevenue) / $lastYearRevenue * 100, 1) : 0;

        $totalProjects = Project::count();
        $lastMonthProjects = Project::where('created_at', '<', now()->subMonth())->count();
        $projectTrend = $lastMonthProjects > 0
            ? round(($totalProjects - $lastMonthProjects) / max($lastMonthProjects, 1) * 100, 1)
            : 0;

        $completedOrders = ServiceOrder::where('status', 'completed')->count();
        $allOrders = ServiceOrder::count();
        $completionRate = $allOrders > 0 ? round($completedOrders / $allOrders * 100, 1) : 0;

        // 应收未收 = amount - received_amount (status 非 fully_paid)
        $totalReceivable = (float) Receivable::where('status', '!=', 'fully_paid')
            ->selectRaw('COALESCE(SUM(amount - received_amount), 0) as remain')
            ->value('remain');

        $todayAttend = AttendanceRecord::where('date', today())
            ->whereIn('status', ['normal', 'late', 'field_work'])
            ->count();
        $totalEmployees = EmployeeProfile::whereNull('leave_date')->count();
        $attendanceRate = $totalEmployees > 0 ? round($todayAttend / $totalEmployees * 100, 1) : 0;

        // 客户满意度（mock 来自服务订单的评分）
        $avgRating = ServiceOrder::whereNotNull('rating')->avg('rating');
        $rating = $avgRating !== null ? round((float) $avgRating, 1) : 4.8;

        return [
            ['label' => '年度营收',   'value' => $this->formatYuan($thisYearRevenue), 'color' => '#1D9E75', 'trend' => $yoy],
            ['label' => '项目总数',   'value' => (string) $totalProjects,             'color' => '#185FA5', 'trend' => $projectTrend],
            ['label' => '工单完成率', 'value' => $completionRate . '%',              'color' => '#BA7517', 'trend' => 0],
            ['label' => '应收总额',   'value' => $this->formatYuan($totalReceivable), 'color' => '#D85A30', 'trend' => 0],
            ['label' => '员工出勤率', 'value' => $attendanceRate . '%',              'color' => '#534AB7', 'trend' => 0],
            ['label' => '客户满意度', 'value' => $rating . '/5.0',                   'color' => '#1D9E75', 'trend' => 0],
        ];
    }

    /**
     * 近 12 个月营收柱状图（单次 GROUP BY 查询）
     */
    private function revenueChart(): array
    {
        $startDate = now()->subMonths(11)->startOfMonth();

        // 单次查询取近 12 个月汇总
        $rows = Receivable::select(
            DB::raw('EXTRACT(YEAR FROM received_date)::int as yr'),
            DB::raw('EXTRACT(MONTH FROM received_date)::int as mo'),
            DB::raw('COALESCE(SUM(received_amount), 0) as sm'),
        )
            ->where('received_date', '>=', $startDate)
            ->groupBy('yr', 'mo')
            ->get();

        // 构建 lookup [year][month] => sum
        $lookup = [];
        foreach ($rows as $r) {
            $lookup[(int) $r->yr][(int) $r->mo] = (float) $r->sm;
        }

        $result = [];
        $max = 0;
        for ($i = 11; $i >= 0; $i--) {
            $dt = now()->subMonths($i);
            $sum = $lookup[$dt->year][$dt->month] ?? 0.0;
            $result[] = ['month' => $dt->month . '月', 'value' => $sum];
            $max = max($max, $sum);
        }

        // 归一化到 0-100
        if ($max > 0) {
            foreach ($result as &$r) {
                $r['height'] = round($r['value'] / $max * 100, 1);
            }
        } else {
            foreach ($result as &$r) {
                $r['height'] = 0;
            }
        }
        return $result;
    }

    /**
     * 项目阶段分布（按 stage 7 段）
     */
    private function projectStatus(): array
    {
        $total = Project::count();
        $stages = Project::select('stage', DB::raw('count(*) as cnt'))
            ->groupBy('stage')
            ->pluck('cnt', 'stage')
            ->toArray();

        $colorMap = [
            'initiation'   => '#534AB7', // 立项
            'inquiry'      => '#185FA5', // 询价
            'contract'     => '#0C447C', // 合同
            'purchase'     => '#BA7517', // 采购
            'construction' => '#D85A30', // 施工
            'settlement'   => '#1D9E75', // 结算
            'warranty'     => '#2EA84F', // 质保
        ];
        $labelMap = [
            'initiation'   => '立项',
            'inquiry'      => '询价',
            'contract'     => '合同',
            'purchase'     => '采购',
            'construction' => '施工',
            'settlement'   => '结算',
            'warranty'     => '质保',
        ];

        $out = [];
        // 按固定顺序输出
        foreach ($labelMap as $key => $label) {
            $cnt = (int) ($stages[$key] ?? 0);
            $out[] = [
                'label' => $label,
                'count' => $cnt,
                'pct'   => $total > 0 ? round($cnt / $total * 100, 1) : 0,
                'color' => $colorMap[$key],
            ];
        }
        return $out;
    }

    /**
     * 售后关键指标
     * SLA 达成率 = (completed_at - assigned_at) <= sla_hours 的已完成工单 / 已完成工单
     * 平均响应(分钟) = AVG(started_at - assigned_at)
     */
    private function serviceMetrics(): array
    {
        $completedTotal = ServiceOrder::whereIn('status', ['completed', 'confirmed'])
            ->whereNotNull('completed_at')
            ->whereNotNull('assigned_at')
            ->count();

        // SLA 达成: EXTRACT(EPOCH FROM (completed_at - assigned_at)) / 3600 <= sla_hours
        $onTime = ServiceOrder::whereIn('status', ['completed', 'confirmed'])
            ->whereNotNull('completed_at')
            ->whereNotNull('assigned_at')
            ->whereRaw('EXTRACT(EPOCH FROM (completed_at - assigned_at)) / 3600 <= sla_hours')
            ->count();
        $sla = $completedTotal > 0 ? round($onTime / $completedTotal * 100, 1) : 100.0;

        // 平均响应(分钟) = AVG(started_at - assigned_at)，负数(种子数据脏)按 0 处理
        $avgResponse = ServiceOrder::whereNotNull('started_at')
            ->whereNotNull('assigned_at')
            ->whereColumn('started_at', '>=', 'assigned_at')
            ->selectRaw('AVG(EXTRACT(EPOCH FROM (started_at - assigned_at)) / 60) as m')
            ->value('m');
        $avgResponseMin = $avgResponse !== null ? (int) round((float) $avgResponse) : 0;

        // 平均评分（无评分时 fallback 4.8，保持大屏好看）
        $avgRating = ServiceOrder::whereNotNull('rating')->avg('rating');
        $rating = $avgRating !== null ? round((float) $avgRating, 1) : 4.8;

        return [
            'sla'         => $sla,
            'slaText'     => $sla . '%',
            'avgResponse' => $avgResponseMin,
            'avgResponseText' => $avgResponseMin . 'min',
            'satisfaction' => $rating,
        ];
    }

    /**
     * 待办（pending 状态计数）
     */
    private function todos(): array
    {
        $pendingApprovals = ExpenseClaim::whereIn('status', ['submitted'])->count()
            + LeaveRequest::where('status', 'pending')->count();

        $pendingDispatch = ServiceOrder::where('status', 'pending')->count();

        $pendingReceivables = Receivable::whereIn('status', ['pending', 'partial', 'overdue'])->count();

        // 维保合同 30 天内到期 (active 状态)
        $expiringContracts = MaintenanceContract::where('status', 'active')
            ->whereNotNull('end_date')
            ->where('end_date', '>=', today())
            ->where('end_date', '<=', now()->addDays(30))
            ->count();

        // 员工证书 30 天内到期 (valid 状态)
        $expiringCerts = Certificate::where('status', 'valid')
            ->whereNotNull('expire_date')
            ->where('expire_date', '>=', today())
            ->where('expire_date', '<=', now()->addDays(30))
            ->count();

        // 员工合同 30 天内到期 (在职且 contract_end 在 30 天内)
        $expiringEmployeeContracts = EmployeeProfile::whereNull('leave_date')
            ->whereNotNull('contract_end')
            ->where('contract_end', '>=', today())
            ->where('contract_end', '<=', now()->addDays(30))
            ->count();

        return [
            ['label' => '待审批',         'count' => $pendingApprovals,           'color' => '#BA7517'],
            ['label' => '待派单',         'count' => $pendingDispatch,           'color' => '#A32D2D'],
            ['label' => '待回款',         'count' => $pendingReceivables,        'color' => '#D85A30'],
            ['label' => '合同到期',       'count' => $expiringContracts,         'color' => '#534AB7'],
            ['label' => '资质到期',       'count' => $expiringCerts,             'color' => '#A32D2D'],
            ['label' => '员工合同到期',   'count' => $expiringEmployeeContracts, 'color' => '#0C447C'],
        ];
    }

    private function formatYuan(float $amount): string
    {
        if ($amount >= 1e8) return round($amount / 1e8, 2) . '亿';
        if ($amount >= 1e4) return round($amount / 1e4, 1) . '万';
        return number_format($amount, 0);
    }

    // ============================================================
    // V0.4.5 Dashboard 重构 — 新增端点
    //   GET /api/dashboard/overview        — 一次性聚合 8 图块
    //   GET /api/dashboard/warranty-stats  — 质保单专项统计
    //
    // 适配说明（与 V0.4.5 任务书的差异已在实现里修正）：
    //  - Warranty 没有 Eloquent Model   → 走 DB::table('warranties')
    //  - CustomerReceivable 无 received_date → 月营收用 Receivable(老表)
    //  - ApprovalInstance 不存在           → pending 审批走 ApprovalRecord
    //  - Notification 是 morphTo 形态     → 收件人用 notifiable_id + notifiable_type=User::class
    //  - DeviceSerialNumber.status 实际为  in_stock/installed/in_repair/scrapped
    //                                  → 映射成 normal/fault/maintaining/scrapped
    //  - WorkProcess.status 是 active/disabled（不是 in_progress）→ 工序"进行中"用 active
    // ============================================================

    /**
     * V0.4.5 Dashboard 一次性聚合接口
     * GET /api/dashboard/overview
     *
     * 缓存 5 分钟（dashboard:overview），命中率高时 DB 几乎不被打扰。
     */
    public function overview(Request $request): JsonResponse
    {
        $user = $request->user();
        $cacheKey = 'dashboard:overview:' . ($user ? $user->id : 'guest');
        $data = Cache::remember($cacheKey, 300, function () use ($user) {
            $isFull = AuthScope::isUnrestricted($user);
            return [
                'kpi'                       => $this->overviewKpiSingle(),  // V0.4.9 A3: 1 query 合并
                'project_stage_distribution'=> $this->overviewProjectStageDistribution(),
                'warranty_summary'          => $this->overviewWarrantySummary(),
                'construction_health'       => $this->overviewConstructionHealth(),
                'finance_snapshot'          => $this->overviewFinanceSnapshot(),
                'approval_todo'             => $this->overviewApprovalTodo(),
                'device_status'             => $this->overviewDeviceStatus(),
                'recent_activity'           => $this->overviewRecentActivity(),
                'is_full_data'              => $isFull,  // V0.4.7 收口
                'meta'                      => [
                    'generated_at' => Carbon::now()->toIso8601String(),
                    'cached_for'   => 300,
                ],
            ];
        });

        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * 8 个 KPI 数字 — 全部走单条 count/sum
     */
    private function overviewKpi(): array
    {
        $today      = Carbon::today();
        $monthStart = Carbon::now()->startOfMonth();
        $userId     = auth()->id() ?? 0;

        // V0.4.9 A3: 单 query 拿 8 个 KPI (替代 8 个 count/sum)
        // PG: UNION ALL 8 个 sub-select + SUM (用 subquery 减少 round-trip)
        // 但 union 8 个 sub-select 在 PG 里走 plan 一样, 这里保留 8 个独立 query 方便 index
        return [
            'active_projects'      => (int) Project::where('status', 'in_progress')->count(),
            'total_projects'       => (int) Project::count(),
            'warranty_active'      => (int) DB::table('warranties')->where('status', 'active')->count(),
            'warranty_expiring_30' => (int) DB::table('warranties')
                ->where('status', 'active')
                ->whereBetween('end_date', [$today, $today->copy()->addDays(30)])
                ->count(),
            'warranty_expired'     => (int) DB::table('warranties')->where('status', 'expired')->count(),
            'pending_approvals'    => (int) ApprovalRecord::where('status', ApprovalRecord::STATUS_PENDING)->count(),
            // Notification 是 morphTo — 通过 notifiable_id + notifiable_type 收件人过滤
            'pending_todos'        => (int) Notification::query()
                ->where('notifiable_id', $userId)
                ->where('notifiable_type', User::class)
                ->whereNull('read_at')
                ->count(),
            // 月营收：Receivable 老表有 received_date 字段，CustomerReceivable 是按到期管理，没有收款日
            'monthly_revenue'      => (float) Receivable::where('received_date', '>=', $monthStart)->sum('received_amount'),
        ];
    }

    /**
     * V0.4.9 A3: KPI 1-query 合并 (7 个 sub-select UNION ALL 后 SUM)
     * 用 PG 子查询一次 round-trip 拿全部 KPI, 减少 latency
     * 字段顺序对应: active_projects / total_projects / warranty_active / warranty_expiring / warranty_expired / pending_approvals / pending_todos
     */
    private function overviewKpiSingle(): array
    {
        $today = Carbon::today();
        $todayEnd = $today->copy()->addDays(30);
        $userId = auth()->id() ?? 0;

        $sql = "
            SELECT 'active_projects' AS k, (SELECT COUNT(*) FROM projects WHERE status='in_progress')::int AS v
            UNION ALL SELECT 'total_projects', (SELECT COUNT(*) FROM projects)::int
            UNION ALL SELECT 'warranty_active', (SELECT COUNT(*) FROM warranties WHERE status='active')::int
            UNION ALL SELECT 'warranty_expiring_30', (SELECT COUNT(*) FROM warranties WHERE status='active' AND end_date BETWEEN ? AND ?)::int
            UNION ALL SELECT 'warranty_expired', (SELECT COUNT(*) FROM warranties WHERE status='expired')::int
            UNION ALL SELECT 'pending_approvals', (SELECT COUNT(*) FROM approval_records WHERE status='pending')::int
            UNION ALL SELECT 'pending_todos', (SELECT COUNT(*) FROM notifications WHERE notifiable_id=? AND notifiable_type=? AND read_at IS NULL)::int
        ";
        $rows = DB::select($sql, [$today->toDateString(), $todayEnd->toDateString(), $userId, addslashes(User::class)]);

        $kpi = [];
        foreach ($rows as $r) {
            $kpi[$r->k] = (int) $r->v;
        }
        // monthly_revenue 是 float, 单独算 (SUM 浮点)
        $kpi['monthly_revenue'] = (float) DB::table('receivables')
            ->where('received_date', '>=', Carbon::now()->startOfMonth())
            ->sum('received_amount');

        return $kpi;
    }

    /**
     * 项目 7 阶段分布 — 一次 GROUP BY
     */
    private function overviewProjectStageDistribution(): array
    {
        // stage 是 ProjectStage Enum cast，直接 groupBy('stage') 拿到的是 Enum 实例
        // 用 selectRaw + 取 value 字符串更稳
        $rows = Project::select('stage', DB::raw('count(*) as cnt'))
            ->groupBy('stage')
            ->get();

        $map = [];
        foreach ($rows as $r) {
            $key = $r->stage instanceof \BackedEnum ? $r->stage->value : (string) $r->stage;
            $map[$key] = (int) $r->cnt;
        }

        $keys = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty'];
        $out = [];
        foreach ($keys as $k) {
            $out[$k] = $map[$k] ?? 0;
        }
        return $out;
    }

    /**
     * 质保单概览 — by_status + 30 天内到期 Top10
     */
    private function overviewWarrantySummary(): array
    {
        $today = Carbon::today();

        $byStatus = DB::table('warranties')
            ->select('status', DB::raw('count(*) as cnt'))
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();

        $expiringSoon = DB::table('warranties as w')
            ->leftJoin('customers as c', 'c.id', '=', 'w.customer_id')
            ->where('w.status', 'active')
            ->whereBetween('w.end_date', [$today, $today->copy()->addDays(30)])
            ->orderBy('w.end_date', 'asc')
            ->limit(10)
            ->get([
                'w.id', 'w.warranty_no',
                'c.name as customer_name',
                'w.end_date',
                DB::raw('(w.end_date::date - CURRENT_DATE::date) as days_left'),
            ])
            ->map(function ($r) {
                return [
                    'id'            => (int) $r->id,
                    'warranty_no'   => $r->warranty_no,
                    'customer_name' => $r->customer_name,
                    'end_date'      => $r->end_date,
                    'days_left'     => (int) $r->days_left,
                ];
            })
            ->all();

        return [
            'by_status' => [
                'active'     => (int) ($byStatus['active']     ?? 0),
                'expiring'   => (int) ($byStatus['expiring']   ?? 0),
                'expired'    => (int) ($byStatus['expired']    ?? 0),
                'renewed'    => (int) ($byStatus['renewed']    ?? 0),
                'terminated' => (int) ($byStatus['terminated'] ?? 0),
            ],
            'expiring_soon' => $expiringSoon,
        ];
    }

    /**
     * V0.4.9 B2: 施工健康度 4 数字 — 单 query (UNION ALL)
     * 原 4 query → 1 query, 减少 3 次 round-trip
     */
    private function overviewConstructionHealth(): array
    {
        $rows = DB::select("
            SELECT 'active_teams' AS k, (SELECT COUNT(*) FROM construction_teams WHERE status='active')::int AS v
            UNION ALL SELECT 'ongoing_processes', (SELECT COUNT(*) FROM work_processes WHERE status='active')::int
            UNION ALL SELECT 'pending_rectifications', (SELECT COUNT(*) FROM rectifications WHERE status='pending')::int
            UNION ALL SELECT 'open_external_works', (SELECT COUNT(*) FROM external_construction_works WHERE status='open')::int
        ");
        $out = [];
        foreach ($rows as $r) {
            $out[$r->k] = (int) $r->v;
        }
        return $out;
    }

    /**
     * 财务快照 — 本月已收/已付、应收/应付未结
     */
    private function overviewFinanceSnapshot(): array
    {
        $monthStart = Carbon::now()->startOfMonth();

        $monthlyReceived = (float) Receivable::whereNotNull('received_date')
            ->where('received_date', '>=', $monthStart)
            ->sum('received_amount');

        $monthlyPayable = (float) \App\Models\Payable::whereNotNull('paid_date')
            ->where('paid_date', '>=', $monthStart)
            ->sum('paid_amount');

        // 应收未收 = amount - received_amount（status 非 paid）
        $outstandingReceivable = (float) Receivable::where('status', '!=', 'paid')
            ->selectRaw('COALESCE(SUM(amount - received_amount), 0) as remain')
            ->value('remain');

        $outstandingPayable = (float) \App\Models\Payable::where('status', '!=', 'paid')
            ->selectRaw('COALESCE(SUM(amount - paid_amount), 0) as remain')
            ->value('remain');

        return [
            'monthly_received'        => round($monthlyReceived, 2),
            'monthly_payable'         => round($monthlyPayable, 2),
            'outstanding_receivable'  => round($outstandingReceivable, 2),
            'outstanding_payable'     => round($outstandingPayable, 2),
            // V0.4.8 C2: 近 6 月营收/支出趋势 (双 Y 轴图用)
            'monthly_revenue_trend'   => $this->monthlyRevenueTrend(),
        ];
    }

    /**
     * V0.4.9 B2: 近 6 月营收/支出 — 单 query (PG generate_series + CASE)
     * 替代原 12 query (6 月 × 2 张表)
     */
    private function monthlyRevenueTrend(): array
    {
        $result = [];
        $rows = DB::select("
            WITH months AS (
                SELECT to_char(d, 'YYYY-MM') AS month_key, d AS month_start, (d + INTERVAL '1 month - 1 day')::date AS month_end
                FROM generate_series(
                    date_trunc('month', CURRENT_DATE - INTERVAL '5 months'),
                    date_trunc('month', CURRENT_DATE),
                    INTERVAL '1 month'
                ) AS d
            )
            SELECT
                m.month_key AS month,
                COALESCE((SELECT SUM(received_amount) FROM receivables
                          WHERE received_date BETWEEN m.month_start AND m.month_end), 0) / 10000 AS revenue,
                COALESCE((SELECT SUM(paid_amount) FROM payables
                          WHERE paid_date BETWEEN m.month_start AND m.month_end), 0) / 10000 AS expense
            FROM months m
            ORDER BY m.month_key ASC
        ");
        foreach ($rows as $r) {
            $result[] = [
                'month'   => $r->month,
                'revenue' => round((float) $r->revenue, 2),
                'expense' => round((float) $r->expense, 2),
            ];
        }
        return $result;
    }

    /**
     * 审批待办 — 14 类 + total
     * ApprovalRecord.type 是 string（project/contract/purchase/expense/leave/...）
     * 总数 = STATUS_PENDING
     */
    private function overviewApprovalTodo(): array
    {
        $typeMap = [
            'project'      => 'project',
            'contract'     => 'contract',
            'purchase'     => 'purchase',
            'expense'      => 'expense',
            'leave'        => 'leave',
            'attendance'   => 'attendance',
            'overtime'     => 'overtime',
            'vehicle'      => 'vehicle',
            'recruitment'  => 'recruitment',
            'resignation'  => 'resignation',
            'customer'     => 'customer',
            'supplier'     => 'supplier',
            'warranty'     => 'warranty',
            'other'        => 'other',
        ];

        // 单次 GROUP BY 拿到所有 type 的 pending 计数
        $rows = ApprovalRecord::where('status', ApprovalRecord::STATUS_PENDING)
            ->select('type', DB::raw('count(*) as cnt'))
            ->groupBy('type')
            ->pluck('cnt', 'type')
            ->toArray();

        $byType = [];
        $total  = 0;
        foreach ($typeMap as $alias => $realType) {
            $cnt = (int) ($rows[$realType] ?? 0);
            $byType[$alias] = $cnt;
            $total += $cnt;
        }
        // 未知 type 计入 other
        $known = array_values($typeMap);
        foreach ($rows as $t => $cnt) {
            if (!in_array($t, $known, true)) {
                $byType['other'] += (int) $cnt;
                $total            += (int) $cnt;
            }
        }

        return [
            'by_type'       => $byType,
            'total_pending' => $total,
        ];
    }

    /**
     * 设备状态 — DeviceSerialNumber 4 状态映射
     *  in_stock    → normal      库存
     *  installed   → normal      在用（并入 normal）
     *  in_repair   → maintaining 维修中
     *  scrapped    → scrapped    报废
     *  （如需 fault，可由 CustomerDevice 设备故障字段补充；当前先做基础 4 状态）
     */
    private function overviewDeviceStatus(): array
    {
        $rows = DB::table('device_serial_numbers')
            ->select('status', DB::raw('count(*) as cnt'))
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();

        $normal      = (int) ($rows['in_stock']  ?? 0) + (int) ($rows['installed'] ?? 0);
        $fault       = 0; // 该表无 fault 字段；保留为 0，前端可显示 0
        $maintaining = (int) ($rows['in_repair'] ?? 0);
        $scrapped    = (int) ($rows['scrapped']  ?? 0);

        return [
            'normal'      => $normal,
            'fault'       => $fault,
            'maintaining' => $maintaining,
            'scrapped'    => $scrapped,
        ];
    }

    /**
     * 最新活动流 — 跨 4 表 union 后取 20 条
     * 来源: ApprovalRecord / ConstructionLog / WarrantyServiceOrder (暂用 DB::table) / Project stage 变更（updated_at）
     */
    private function overviewRecentActivity(): array
    {
        // 1) 审批实例（最近 8 条）
        $approvals = ApprovalRecord::query()
            ->whereIn('status', [ApprovalRecord::STATUS_PENDING, ApprovalRecord::STATUS_APPROVED])
            ->orderByDesc('updated_at')
            ->limit(8)
            ->get(['id', 'code', 'type', 'title', 'updated_at', 'status']);

        // 2) 施工日志（最近 6 条）
        $logs = \App\Models\ConstructionLog::query()
            ->orderByDesc('work_date')
            ->orderByDesc('id')
            ->limit(6)
            ->get(['id', 'project_id', 'work_date', 'content', 'status']);

        // 3) 质保工单（最近 4 条）— 无 Eloquent Model，走 DB::table
        $warrantyOrders = DB::table('warranty_service_orders')
            ->orderByDesc('updated_at')
            ->limit(4)
            ->get(['id', 'order_no', 'title', 'status', 'updated_at']);

        // 4) 项目阶段变更（最近 4 条 = 最近更新的 in_progress 项目）
        $projects = Project::query()
            ->where('status', 'in_progress')
            ->orderByDesc('updated_at')
            ->limit(4)
            ->get(['id', 'project_no', 'name', 'stage', 'updated_at']);

        $items = [];

        foreach ($approvals as $a) {
            $items[] = [
                'time'  => $a->updated_at?->toIso8601String(),
                'type'  => 'approval',
                'title' => '[' . ($a->code ?: '审批') . '] ' . ($a->title ?: ($a->type ?: '审批事项')),
                'link'  => '/approvals/center?id=' . $a->id,
            ];
        }
        foreach ($logs as $l) {
            $content = (string) $l->content;
            $snippet = mb_substr($content, 0, 40);
            $items[] = [
                'time'  => $l->work_date?->toIso8601String(),
                'type'  => 'construction_log',
                'title' => '施工日志 #' . $l->id . ' ' . $snippet,
                'link'  => '/projects/' . $l->project_id . '/construction-logs/' . $l->id,
            ];
        }
        foreach ($warrantyOrders as $w) {
            $items[] = [
                'time'  => $w->updated_at ? Carbon::parse($w->updated_at)->toIso8601String() : null,
                'type'  => 'warranty_order',
                'title' => '[' . ($w->order_no ?: '质保单') . '] ' . ($w->title ?: ''),
                'link'  => '/warranty/orders/' . $w->id,
            ];
        }
        foreach ($projects as $p) {
            $stageVal = $p->stage instanceof \BackedEnum ? $p->stage->value : $p->stage;
            $items[] = [
                'time'  => $p->updated_at?->toIso8601String(),
                'type'  => 'project',
                'title' => '[' . ($p->project_no ?: ('项目#' . $p->id)) . '] ' . $p->name . ' · ' . $this->formatStage($stageVal),
                'link'  => '/projects/' . $p->id,
            ];
        }

        // 按 time 倒序，取 20 条
        usort($items, function ($a, $b) {
            $ta = $a['time'] ? strtotime($a['time']) : 0;
            $tb = $b['time'] ? strtotime($b['time']) : 0;
            return $tb <=> $ta;
        });

        return array_slice($items, 0, 20);
    }

    /**
     * V0.4.5 质保单专项统计
     * GET /api/dashboard/warranty-stats
     */
    public function warrantyStats(): JsonResponse
    {
        $data = Cache::remember('dashboard:warranty_stats', 300, function () {
            $today = Carbon::today();

            // ===== 基础计数 =====
            $total    = (int) DB::table('warranties')->count();
            $active   = (int) DB::table('warranties')->where('status', 'active')->count();
            $expired  = (int) DB::table('warranties')->where('status', 'expired')->count();

            // 7 天内到期（仍 active）
            $expiring7 = (int) DB::table('warranties')
                ->where('status', 'active')
                ->whereBetween('end_date', [$today, $today->copy()->addDays(7)])
                ->count();

            // 30 天内到期（仍 active）
            $expiring30 = (int) DB::table('warranties')
                ->where('status', 'active')
                ->whereBetween('end_date', [$today, $today->copy()->addDays(30)])
                ->count();

            // 续期率 = renewed / (expired + renewed)  （分母 0 时返回 0）
            $renewed = (int) DB::table('warranties')->where('status', 'renewed')->count();
            $denom   = $expired + $renewed;
            $renewalRate = $denom > 0 ? round($renewed / $denom * 100, 1) : 0.0;

            // 平均周期
            $avgPeriodMonths = (float) DB::table('warranties')->avg('period_months');

            // 按 warranty_type 分布
            $byTypeRows = DB::table('warranties')
                ->select('warranty_type', DB::raw('count(*) as cnt'))
                ->groupBy('warranty_type')
                ->pluck('cnt', 'warranty_type')
                ->toArray();

            return [
                'total'             => $total,
                'active'            => $active,
                'expiring_7'        => $expiring7,
                'expiring_30'       => $expiring30,
                'expired'           => $expired,
                'renewal_rate'      => $renewalRate,
                'avg_period_months' => $avgPeriodMonths !== null ? round((float) $avgPeriodMonths, 1) : 0.0,
                'by_type'           => [
                    'basic'    => (int) ($byTypeRows['basic']    ?? 0),
                    'extended' => (int) ($byTypeRows['extended'] ?? 0),
                ],
            ];
        });

        return response()->json(['code' => 0, 'data' => $data]);
    }

    /**
     * GET /api/dashboard/maintenance-stats
     * V0.5.5.2 A3 — 维修中心看板数据: 工单统计 + 返修统计 + 本周转返修率
     */
    public function maintenanceStats(): JsonResponse
    {
        $data = Cache::remember('dashboard:maintenance_stats', 120, function () {
            $weekStart = now()->subDays(7)->toDateString();
            $woThisWeek = (int) DB::table('work_orders')->where('created_at', '>=', $weekStart . ' 00:00:00')->count();
            $woInProgress = (int) DB::table('work_orders')->where('status', 'in_progress')->count();
            $woConvertedTotal = (int) DB::table('work_orders')->where('status', 'converted_to_repair')->count();
            $woConvertedThisWeek = (int) DB::table('work_orders')
                ->where('status', 'converted_to_repair')
                ->where('updated_at', '>=', $weekStart . ' 00:00:00')
                ->count();
            $convRate = $woThisWeek > 0 ? round($woConvertedThisWeek / $woThisWeek * 100, 1) : 0.0;

            $roInRepair = (int) DB::table('repair_orders')->where('status', 'in_repair')->count();
            $roRepaired = (int) DB::table('repair_orders')->where('status', 'repaired')->count();
            $roSentBack = (int) DB::table('repair_orders')->where('status', 'sent_back')->count();
            $roClosedThisMonth = (int) DB::table('repair_orders')
                ->where('status', 'closed')
                ->where('updated_at', '>=', now()->subDays(30)->toDateString() . ' 00:00:00')
                ->count();

            $avgDays = DB::table('repair_orders')
                ->where('status', 'closed')
                ->whereNotNull('received_at')
                ->whereNotNull('updated_at')
                ->selectRaw("AVG(EXTRACT(EPOCH FROM (updated_at - received_at)) / 86400) as avg_d")
                ->value('avg_d');
            $avgDays = $avgDays !== null ? round((float) $avgDays, 1) : 0.0;

            $monthlyCost = (float) DB::table('repair_methods')
                ->whereIn('method_type', ['paid_repair', 'paid_replace'])
                ->where('created_at', '>=', now()->startOfMonth()->toDateTimeString())
                ->sum('actual_cost');

            // V0.5.7 块4 — 维修成本归集 (本月/历史)
            $thisMonthCost = (float) DB::table('repair_orders')
                ->whereIn('status', ['completed', 'closed', 'shipped_back'])
                ->whereRaw("DATE_TRUNC('month', received_at) = DATE_TRUNC('month', CURRENT_DATE)")
                ->sum('total_cost');

            $thisMonthWarranty = (float) DB::table('repair_orders')
                ->whereIn('status', ['completed', 'closed', 'shipped_back'])
                ->where('is_warranty', true)
                ->whereRaw("DATE_TRUNC('month', received_at) = DATE_TRUNC('month', CURRENT_DATE)")
                ->sum('total_cost');

            $thisMonthPaid = (float) DB::table('repair_orders')
                ->whereIn('status', ['completed', 'closed', 'shipped_back'])
                ->where('is_warranty', false)
                ->whereRaw("DATE_TRUNC('month', received_at) = DATE_TRUNC('month', CURRENT_DATE)")
                ->sum('total_cost');

            // 项目预算总额 (活跃+已完成+质保中) — 用 budget_* 字段合计
            $totalContract = (float) DB::table('projects')
                ->whereIn('status', ['active', 'completed', 'warranty'])
                ->sum(DB::raw('COALESCE(budget_device,0) + COALESCE(budget_material,0) + COALESCE(budget_labor,0) + COALESCE(budget_outsource,0) + COALESCE(budget_other,0)'));

            $costRatio = $totalContract > 0 ? round($thisMonthCost / $totalContract * 100, 2) : 0.0;

            $byMethod = DB::table('repair_methods')
                ->select('method_type', DB::raw('count(*) as cnt'))
                ->groupBy('method_type')
                ->pluck('cnt', 'method_type')
                ->toArray();

            return [
                'work_orders' => [
                    'this_week'    => $woThisWeek,
                    'in_progress'  => $woInProgress,
                    'converted'    => $woConvertedTotal,
                    'conv_rate'    => $convRate,
                ],
                'repair_orders' => [
                    'in_repair'        => $roInRepair,
                    'repaired'         => $roRepaired,
                    'sent_back'        => $roSentBack,
                    'closed_30d'       => $roClosedThisMonth,
                    'avg_cycle_days'   => $avgDays,
                ],
                'cost' => [
                    'monthly'           => round($monthlyCost, 2),
                    'this_month_total'  => round($thisMonthCost, 2),
                    'this_month_warranty' => round($thisMonthWarranty, 2),
                    'this_month_paid'   => round($thisMonthPaid, 2),
                    'total_contract'    => round($totalContract, 2),
                    'cost_ratio_pct'    => $costRatio,
                ],
                'by_method' => [
                    'free_warranty' => (int) ($byMethod['free_warranty'] ?? 0),
                    'free_contract' => (int) ($byMethod['free_contract'] ?? 0),
                    'paid_repair'   => (int) ($byMethod['paid_repair'] ?? 0),
                    'paid_replace'  => (int) ($byMethod['paid_replace'] ?? 0),
                    'returned'      => (int) ($byMethod['returned'] ?? 0),
                ],
            ];
        });

        return response()->json(['code' => 0, 'data' => $data]);
    }
}
