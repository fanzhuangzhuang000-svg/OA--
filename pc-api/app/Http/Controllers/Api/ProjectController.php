<?php

namespace App\Http\Controllers\Api;

use App\Enums\ProjectStage;
use App\Http\Controllers\Controller;
use App\Models\{Project, ProjectContract, ConstructionLog, ProjectMaterial, ProjectSettlement, PurchaseOrder, Supplier, ContractPaymentNode, WorkOrder, RepairOrder};
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class ProjectController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        // V0.4.8 B2: withCount + 限定 members 状态 (project_members.status 避免与 users.status 歧义)
        $query = Project::with([
            'customer:id,name',
            'manager:id,name',
            'members' => fn ($q) => $q->where('project_members.status', 'active'),
        ])
            ->withCount('constructionLogs');
        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        if ($request->filled('stage')) $query->where('stage', $request->stage);
        if ($request->filled('status')) $query->where('status', $request->status);
        if ($request->filled('customer_id')) $query->where('customer_id', $request->customer_id);
        if ($request->filled('type')) $query->where('type', $request->type);

        $perPage = (int) ($request->per_page ?? 15);
        $perPage = max(1, min($perPage, 200));

        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate($perPage)]);
    }

    public function show(Project $project): JsonResponse
    {
        // V0.4.9 B3: 拆 9 个关系为 2 批 (基础 + 业务)
        // 基础批 (前端路由守卫用) 一次拉
        $project->load([
            'customer:id,name,category',
            'manager:id,name,email',
            'members' => fn ($q) => $q->where('project_members.status', 'active')->select('users.id', 'users.name'),
            'devices:id,project_id,device_name,serial_number,status',
        ]);
        // 业务批: 全用 DB 直查 (Project Model 上关系不全, 表名按真实 schema)
        $project->loadCount([
            'constructionLogs', 'materials', 'purchaseOrders',
        ]);
        $project->setAttribute('process_instances_count', (int) DB::table('process_instances')->where('project_id', $project->id)->count());
        $project->setAttribute('rectifications_count',    (int) DB::table('rectifications')->where('project_id', $project->id)->count());
        $project->setAttribute('warranties_count',        (int) DB::table('warranties')->where('project_id', $project->id)->count());
        $project->setAttribute('settlements_count',       (int) DB::table('project_settlements')->where('project_id', $project->id)->count());

        return response()->json(['code' => 0, 'data' => $project]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name' => 'required|string|max:200', 'customer_id' => 'nullable|integer',
            'type' => 'nullable|string', 'description' => 'nullable|string',
            'budget_device' => 'nullable|numeric', 'budget_material' => 'nullable|numeric',
            'budget_labor' => 'nullable|numeric', 'budget_outsource' => 'nullable|numeric',
            'budget_other' => 'nullable|numeric', 'manager_id' => 'nullable|integer',
            'start_date' => 'nullable|date', 'end_date' => 'nullable|date', 'priority' => 'nullable|string',
            'member_ids' => 'nullable|array', 'member_ids.*' => 'integer',
        ]);

        $memberIds = $data['member_ids'] ?? [];
        unset($data['member_ids']);

        Cache::forget('projects:dashboard_summary');
        $project = Project::create($data + ['stage' => 'initiation', 'status' => 'pending', 'progress' => 0]);

        // 添加团队成员
        foreach ($memberIds as $userId) {
            DB::table('project_members')->insert([
                'project_id' => $project->id, 'user_id' => $userId,
                'role' => 'worker', 'status' => 'active',
                'created_at' => now(), 'updated_at' => now(),
            ]);
        }
        $managerId = $data['manager_id'] ?? null;
        if ($managerId && !in_array($managerId, $memberIds)) {
            DB::table('project_members')->insert([
                'project_id' => $project->id, 'user_id' => $data['manager_id'],
                'role' => 'manager', 'status' => 'active',
                'created_at' => now(), 'updated_at' => now(),
            ]);
        }

        return response()->json(['code' => 0, 'message' => '创建成功', 'data' => $project->load('customer', 'manager')]);
    }

    public function update(Request $request, Project $project): JsonResponse
    {
        $validStages = implode(',', array_map(fn($c) => $c->value, ProjectStage::cases()));
        $data = $request->validate([
            'name' => 'sometimes|string|max:200',
            'stage' => "sometimes|string|in:{$validStages}",
            'status' => 'sometimes|string',
            'progress' => 'sometimes|integer|min:0|max:100',
            'description' => 'nullable|string', 'end_date' => 'nullable|date', 'priority' => 'nullable|string',
        ]);

        $project->update($data);
        Cache::forget('projects:dashboard_summary');
        return response()->json(['code' => 0, 'message' => '更新成功', 'data' => $project]);
    }

    public function updateStage(Request $request, Project $project): JsonResponse
    {
        $validStages = implode(',', array_map(fn($c) => $c->value, ProjectStage::cases()));
        $data = $request->validate([
            'stage' => "required|string|in:{$validStages}"
        ]);
        Cache::forget('projects:dashboard_summary');
        $project->update(['stage' => $data['stage']]);
        return response()->json(['code' => 0, 'message' => '阶段更新成功']);
    }

    public function constructionLogs(Request $request, Project $project): JsonResponse
    {
        $perPage = (int) ($request->per_page ?? 15);
        $perPage = max(1, min($perPage, 200));
        $logs = $project->constructionLogs()->with('operator:id,name')->orderBy('work_date', 'desc')->paginate($perPage);
        return response()->json(['code' => 0, 'data' => $logs]);
    }

    public function storeConstructionLog(Request $request, Project $project): JsonResponse
    {
        $data = $request->validate([
            'work_date' => 'required|date', 'content' => 'required|string',
            'weather' => 'nullable|string', 'problems' => 'nullable|string',
            'solutions' => 'nullable|string', 'photos' => 'nullable|array',
            'work_hours' => 'nullable|numeric', 'location' => 'nullable|string',
        ]);
        $data['project_id'] = $project->id;
        $data['user_id'] = $request->user()->id;
        $log = ConstructionLog::create($data);
        return response()->json(['code' => 0, 'data' => $log]);
    }

    // 供应商
    public function suppliers(Request $request): JsonResponse
    {
        $query = Supplier::query();
        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        if ($request->filled('category')) $query->where('category', $request->category);
        $perPage = (int) ($request->per_page ?? 15);
        $perPage = max(1, min($perPage, 200));
        return response()->json(['code' => 0, 'data' => $query->paginate($perPage)]);
    }

    public function storeSupplier(Request $request): JsonResponse
    {
        $data = $request->validate(['name' => 'required|string', 'contact_person' => 'required|string', 'phone' => 'required|string', 'email' => 'nullable|email', 'address' => 'nullable|string', 'category' => 'nullable|string']);
        return response()->json(['code' => 0, 'data' => Supplier::create($data)]);
    }

    public function projectSuppliers(Project $project): JsonResponse
    {
        $supplierIds = PurchaseOrder::where('project_id', $project->id)->pluck('supplier_id')->unique();
        return response()->json(['code' => 0, 'data' => Supplier::whereIn('id', $supplierIds)->get()]);
    }

    public function projectContracts(Project $project): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => $project->contract()->with('paymentNodes')->get()]);
    }

    public function destroy(Request $request, Project $project): JsonResponse
    {
        // 业务规则：已开工/已完成的项目不能删
        $stageValue = $project->stage instanceof \BackedEnum ? $project->stage->value : $project->stage;
        if (in_array($stageValue, ['construction', 'settlement', 'warranty'], true)) {
            return response()->json(['code' => 1001, 'message' => '项目已进入施工/结算/质保阶段，不允许删除'], 422);
        }
        // 业务规则：有合同的项目不能删
        if (\App\Models\ProjectContract::where('project_id', $project->id)->exists()) {
            return response()->json(['code' => 1002, 'message' => '项目已关联合同，不允许删除'], 422);
        }
        Cache::forget('projects:dashboard_summary');
        DB::table('project_members')->where('project_id', $project->id)->delete();
        $project->delete();
        return response()->json(['code' => 0, 'message' => '项目已删除']);
    }

    /**
     * 跨项目付款日历 — 聚合所有合同付款节点，按月份分组
     * - 跨项目汇总
     * - 支持按月份过滤
     * - 标注逾期/即将到期 (7 天内)
     */
    public function paymentCalendar(Request $request): JsonResponse
    {
        $query = ContractPaymentNode::with(['contract.project.customer']);

        if ($request->filled('month')) {
            // YYYY-MM 格式
            $month = $request->month;
            $start = $month . '-01';
            $end = date('Y-m-t', strtotime($start));
            $query->whereBetween('planned_date', [$start, $end]);
        }
        if ($request->filled('status')) $query->where('status', $request->status);

        $nodes = $query->orderBy('planned_date')->get();

        $now = now();
        $items = $nodes->map(function ($n) use ($now) {
            $isOverdue = $n->status === 'pending' && $n->planned_date && strtotime($n->planned_date) < $now->timestamp;
            $daysLeft = $n->planned_date ? (int) floor((strtotime($n->planned_date) - $now->timestamp) / 86400) : null;
            $status = $n->status;
            if ($isOverdue) $status = 'overdue';
            return [
                'id' => $n->id,
                'contract_id' => $n->contract_id,
                'contract_no' => $n->contract?->contract_no,
                'project_id' => $n->contract?->project_id,
                'project_name' => $n->contract?->project?->name,
                'customer_name' => $n->contract?->project?->customer?->name,
                'name' => $n->name,
                'amount' => (float) $n->amount,
                'paid_amount' => (float) ($n->paid_amount ?? 0),
                'percentage' => (float) $n->percentage,
                'planned_date' => $n->planned_date,
                'actual_date' => $n->actual_date,
                'status' => $status,
                'is_overdue' => $isOverdue,
                'days_left' => $daysLeft,
                'is_soon' => $daysLeft !== null && $daysLeft >= 0 && $daysLeft <= 7 && $status === 'pending',
            ];
        });

        // 按月分组
        $byMonth = [];
        foreach ($items as $it) {
            if (!$it['planned_date']) continue;
            $m = substr($it['planned_date'], 0, 7);
            if (!isset($byMonth[$m])) $byMonth[$m] = ['month' => $m, 'count' => 0, 'total_amount' => 0, 'paid_amount' => 0, 'items' => []];
            $byMonth[$m]['count']++;
            $byMonth[$m]['total_amount'] += $it['amount'];
            $byMonth[$m]['paid_amount'] += $it['paid_amount'];
            $byMonth[$m]['items'][] = $it;
        }
        ksort($byMonth);

        // 汇总统计
        $totalAmount = $items->sum('amount');
        $paidAmount = $items->sum('paid_amount');
        $pendingAmount = $totalAmount - $paidAmount;
        $overdueCount = $items->where('is_overdue', true)->count();
        $overdueAmount = $items->where('is_overdue', true)->sum('amount') - $items->where('is_overdue', true)->sum('paid_amount');
        $soonCount = $items->where('is_soon', true)->count();

        return response()->json([
            'code' => 0,
            'data' => [
                'summary' => [
                    'total_count' => $items->count(),
                    'total_amount' => $totalAmount,
                    'paid_amount' => $paidAmount,
                    'pending_amount' => $pendingAmount,
                    'overdue_count' => $overdueCount,
                    'overdue_amount' => $overdueAmount,
                    'soon_count' => $soonCount,
                ],
                'by_month' => array_values($byMonth),
                'items' => $items->values(),
            ],
        ]);
    }

    /**
     * 项目跟踪 — 单项目 4 维度聚合数据
     * - stageProgress: 7 阶段进度（含已到达/未到达标记）
     * - paymentStatus: 合同付款节点（已付/待付/逾期）
     * - materialProgress: 物资/采购进度
     * - risks: 风险预警（超期/付款逾期/物料缺口/进度落后）
     * - timeline: 阶段流转 + 关键节点 拼装的 timeline
     */
    public function tracking(Project $project): JsonResponse
    {
        $project->load(['manager:id,name', 'contract.paymentNodes', 'purchaseOrders.items', 'materials']);        // 1) 阶段进度
        $stageOrder = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty'];
        $stageLabels = ['initiation' => '立项', 'inquiry' => '询价', 'contract' => '合同', 'purchase' => '采购', 'construction' => '施工', 'settlement' => '结算', 'warranty' => '质保'];
        // 兼容 BackedEnum：把 stage 归一化成字符串
        $stageValue = $project->stage instanceof \BackedEnum ? $project->stage->value : (string) $project->stage;
        $currentIdx = array_search($stageValue, $stageOrder);
        $currentIdx = $currentIdx === false ? 0 : (int) $currentIdx;

        // 自动进度计算：基于当前阶段索引 (每个阶段 100/7 ≈ 14.3%)
        $computedProgress = min(100, max(0, ($currentIdx + 1) * 100 / 7));
        $displayProgress = $project->progress > 0 ? $project->progress : (int) round($computedProgress);

        $stageProgress = array_map(function ($s, $idx) use ($currentIdx, $stageLabels) {
            return [
                'value' => $s,
                'label' => $stageLabels[$s] ?? $s,
                'index' => $idx,
                'reached' => $idx <= $currentIdx,
                'is_current' => $idx === $currentIdx,
                'is_completed' => $idx < $currentIdx,
            ];
        }, $stageOrder, array_keys($stageOrder));

        // 2) 合同付款状态
        $contract = $project->contract->first();
        $paymentNodes = [];
        $totalContractAmount = 0;
        $paidAmount = 0;
        $overdueAmount = 0;
        $overdueCount = 0;
        $pendingCount = 0;
        if ($contract) {
            $totalContractAmount = (float) $contract->contract_amount;
            $now = now();
            foreach ($contract->paymentNodes as $node) {
                $isOverdue = $node->status === 'pending' && $node->planned_date && strtotime($node->planned_date) < $now->timestamp;
                $status = $node->status;
                if ($isOverdue) {
                    $status = 'overdue';
                    $overdueCount++;
                    $overdueAmount += (float) $node->amount;
                }
                if ($node->status === 'pending' && !$isOverdue) $pendingCount++;
                if ($node->status === 'paid') $paidAmount += (float) $node->amount;

                $paymentNodes[] = [
                    'id' => $node->id,
                    'name' => $node->name,
                    'amount' => (float) $node->amount,
                    'paid_amount' => (float) $node->paid_amount,
                    'percentage' => (float) $node->percentage,
                    'planned_date' => $node->planned_date,
                    'actual_date' => $node->actual_date,
                    'status' => $status,
                ];
            }
        }
        $paymentRate = $totalContractAmount > 0 ? round($paidAmount / $totalContractAmount * 100, 1) : 0;

        // 3) 物资/采购进度（基于实际表字段：purchase_items 有 received_quantity vs quantity）
        $purchaseOrders = $project->purchaseOrders;
        $totalItemsQty = 0;
        $totalReceivedQty = 0;
        foreach ($purchaseOrders as $po) {
            foreach ($po->items as $it) {
                $totalItemsQty += (float) $it->quantity;
                $totalReceivedQty += (float) $it->received_quantity;
            }
        }
        $purchaseStats = [
            'total_orders' => $purchaseOrders->count(),
            'completed_orders' => $purchaseOrders->whereIn('status', ['completed', 'approved'])->count(),
            'pending_orders' => $purchaseOrders->whereIn('status', ['draft', 'submitted', 'purchasing'])->count(),
            'total_amount' => (float) $purchaseOrders->sum('total_amount'),
            'total_items_qty' => $totalItemsQty,
            'total_received_qty' => $totalReceivedQty,
        ];
        $purchaseStats['fulfill_rate'] = $totalItemsQty > 0 ? round($totalReceivedQty / $totalItemsQty * 100, 1) : 0;

        $materialCount = $project->materials->count();
        $materialCost = (float) $project->materials->sum('total_cost');
        $materialStats = [
            'issued_records' => $materialCount,
            'issued_cost' => $materialCost,
        ];

        // 4) 风险预警
        $risks = [];
        $now = now();

        // 风险 R1: 工期超期
        if ($project->end_date && strtotime($project->end_date) < $now->timestamp && $project->status !== 'completed') {
            $days = (int) floor(($now->timestamp - strtotime($project->end_date)) / 86400);
            $risks[] = [
                'level' => 'danger',
                'type' => 'overdue',
                'title' => "工期超期 {$days} 天",
                'desc' => "计划完成日期 {$project->end_date} 已过，项目仍在进行中",
                'icon' => 'Clock',
            ];
        }
        // 风险 R2: 付款节点逾期
        if ($overdueCount > 0) {
            $risks[] = [
                'level' => 'danger',
                'type' => 'payment_overdue',
                'title' => "{$overdueCount} 个付款节点逾期",
                'desc' => "逾期金额合计 ¥" . number_format($overdueAmount, 2),
                'icon' => 'Money',
            ];
        }
        // 风险 R3: 进度严重落后（实际进度 < 阶段应有进度 30% 以上）
        $expectedProgress = min(100, max(0, ($currentIdx + 1) * 100 / 7));
        if ($currentIdx >= 2 && $displayProgress + 30 < $expectedProgress) {
            $risks[] = [
                'level' => 'warning',
                'type' => 'progress_lag',
                'title' => '进度严重落后',
                'desc' => "当前进度 {$displayProgress}% 低于阶段预期 " . round($expectedProgress) . "%",
                'icon' => 'Warning',
            ];
        }
        // 风险 R4: 物料到位率低（仅在采购/施工阶段才有意义）
        if ($purchaseStats['fulfill_rate'] > 0 && $purchaseStats['fulfill_rate'] < 60 && $currentIdx >= 3) {
            $risks[] = [
                'level' => 'warning',
                'type' => 'material_shortage',
                'title' => '物料到位率偏低',
                'desc' => "到位率 {$purchaseStats['fulfill_rate']}%，已到采购/施工阶段，需跟进供应商",
                'icon' => 'Box',
            ];
        }
        // 风险 R5: 临近截止日期（30 天内 + 进度 < 80%）
        if ($project->end_date && $project->status !== 'completed') {
            $diff = (int) floor((strtotime($project->end_date) - $now->timestamp) / 86400);
            if ($diff >= 0 && $diff <= 30 && $displayProgress < 80) {
                $risks[] = [
                    'level' => 'warning',
                    'type' => 'deadline_soon',
                    'title' => "距截止还有 {$diff} 天",
                    'desc' => "当前进度 {$displayProgress}%，建议加速推进",
                    'icon' => 'Bell',
                ];
            }
        }

        // 5) Timeline（阶段 + 付款 + 采购 关键节点拼装）
        $timeline = [];
        $timeline[] = [
            'time' => $project->created_at?->toDateTimeString(),
            'stage' => '立项',
            'action' => '项目立项',
            'operator' => '系统',
            'content' => "项目「{$project->name}」创建",
            'type' => 'primary',
        ];
        if ($contract && $contract->signed_at) {
            $timeline[] = [
                'time' => $contract->signed_at,
                'stage' => '合同',
                'action' => '合同签订',
                'operator' => '-',
                'content' => "签订合同 {$contract->contract_no}，金额 ¥" . number_format($contract->contract_amount, 2),
                'type' => 'success',
            ];
        }
        foreach ($paymentNodes as $pn) {
            if ($pn['status'] === 'paid' && $pn['actual_date']) {
                $timeline[] = [
                    'time' => $pn['actual_date'] . ' 00:00:00',
                    'stage' => '合同',
                    'action' => '回款',
                    'operator' => '-',
                    'content' => "「{$pn['name']}」已付款 ¥" . number_format($pn['paid_amount'] ?: $pn['amount'], 2),
                    'type' => 'success',
                ];
            }
        }
        foreach ($purchaseOrders as $po) {
            if ($po->status === 'completed' && $po->updated_at) {
                $timeline[] = [
                    'time' => $po->updated_at->toDateTimeString(),
                    'stage' => '采购',
                    'action' => '采购完成',
                    'operator' => '-',
                    'content' => "采购单 {$po->po_no} 完成，金额 ¥" . number_format($po->total_amount, 2),
                    'type' => 'success',
                ];
            }
        }
        // 按时间倒序
        usort($timeline, fn ($a, $b) => strtotime($b['time'] ?? 0) - strtotime($a['time'] ?? 0));

        return response()->json([
            'code' => 0,
            'data' => [
                'project_id' => $project->id,
                'project_name' => $project->name,
                'current_stage' => $stageValue,
                'current_stage_index' => $currentIdx,
                'current_stage_label' => $stageLabels[$stageValue] ?? $stageValue,
                'display_progress' => $displayProgress,
                'stage_progress' => $stageProgress,
                'payment' => [
                    'contract_amount' => $totalContractAmount,
                    'paid_amount' => $paidAmount,
                    'pending_count' => $pendingCount,
                    'overdue_count' => $overdueCount,
                    'overdue_amount' => $overdueAmount,
                    'payment_rate' => $paymentRate,
                    'nodes' => $paymentNodes,
                ],
                'purchase_stats' => $purchaseStats,
                'material_stats' => $materialStats,
                'risks' => $risks,
                'risk_count' => count($risks),
                'timeline' => $timeline,
            ],
        ]);
    }

    /**
     * 项目概览 — 给列表头部统计卡用
     * - 各阶段项目数
     * - 在建项目数 / 逾期项目数 / 本月到期数
     */
    public function dashboardSummary(): JsonResponse
    {
        $data = Cache::remember('projects:dashboard_summary', 300, function () {
            $now = now();
            $stageOrder = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty'];
            $stageLabels = ['initiation' => '立项', 'inquiry' => '询价', 'contract' => '合同', 'purchase' => '采购', 'construction' => '施工', 'settlement' => '结算', 'warranty' => '质保'];

            $byStage = [];
            foreach ($stageOrder as $s) {
                $byStage[$s] = [
                    'value' => $s,
                    'label' => $stageLabels[$s] ?? $s,
                    'count' => Project::where('stage', $s)->count(),
                ];
            }

            $inProgress = Project::where('status', 'in_progress')->count();
            $completed = Project::where('status', 'completed')->count();
            $overdue = Project::where('status', 'in_progress')
                ->whereNotNull('end_date')
                ->where('end_date', '<', $now->toDateString())
                ->count();
            $deadline30 = Project::where('status', 'in_progress')
                ->whereNotNull('end_date')
                ->whereBetween('end_date', [$now->toDateString(), $now->copy()->addDays(30)->toDateString()])
                ->count();

            $atRisk = $overdue;

            return [
                'by_stage' => array_values($byStage),
                'in_progress' => $inProgress,
                'completed' => $completed,
                'overdue' => $overdue,
                'deadline_30_days' => $deadline30,
                'at_risk' => $atRisk,
                'total' => Project::count(),
            ];
        });
        return response()->json([
            'code' => 0,
            'data' => $data,
        ]);
    }

    public function stages(): JsonResponse
    {
        $stages = [
            ['value' => 'initiation', 'label' => '立项'],
            ['value' => 'inquiry', 'label' => '询价'],
            ['value' => 'contract', 'label' => '合同'],
            ['value' => 'purchase', 'label' => '采购'],
            ['value' => 'construction', 'label' => '施工'],
            ['value' => 'settlement', 'label' => '结算'],
            ['value' => 'warranty', 'label' => '质保'],
        ];
        return response()->json(['code' => 0, 'data' => $stages]);
    }

    /**
     * 看板: 按 7 阶段分组聚合,给 Board.vue 拖拽用
     * GET /api/projects/board
     */
    public function board(Request $request): JsonResponse
    {
        $projects = Project::with(['customer:id,name', 'manager:id,name'])
            ->select('id', 'project_no', 'name', 'customer_id', 'manager_id', 'stage',
                'budget_device', 'budget_material', 'budget_labor', 'budget_outsource', 'budget_other',
                'start_date', 'end_date', 'status', 'progress', 'created_at')
            ->orderBy('created_at', 'desc')
            ->limit(500)
            ->get()
            ->map(function ($p) {
                $p->amount = (float)($p->budget_device ?? 0) + (float)($p->budget_material ?? 0) + (float)($p->budget_labor ?? 0);
                return $p;
            });

        $board = [
            'initiation' => [], 'inquiry' => [], 'contract' => [],
            'purchase' => [], 'construction' => [], 'settlement' => [], 'warranty' => [],
        ];
        foreach ($projects as $p) {
            $stage = $p->stage;
            $key = is_object($stage) ? ($stage->value ?? (string)$stage) : ($stage ?: 'initiation');
            if (isset($board[$key])) {
                $board[$key][] = $p;
            }
        }
        return response()->json(['code' => 0, 'data' => $board, 'total' => $projects->count()]);
    }

    /**
     * GET /api/projects/{project}/maintenance
     * V0.5.7 块1 — 拿一个项目下的所有售后记录: 维修工单 + 返修单
     *
     * 关联: work_orders.project_id = project.id  +  repair_orders.project_id = project.id
     */
    public function maintenance(Request $request, Project $project): JsonResponse
    {
        $workOrders = WorkOrder::where('project_id', $project->id)
            ->orderByDesc('created_at')
            ->get(['id', 'code', 'status', 'priority', 'fault_description', 'assigned_to',
                   'started_at', 'completed_at', 'created_at', 'is_locked', 'total_cost'])
            ->map(fn ($w) => [
                'id'                 => $w->id,
                'code'               => $w->code,
                'type'               => 'work_order',
                'status'             => is_object($w->status) ? $w->status->value : $w->status,
                'priority'           => $w->priority,
                'fault_description'  => $w->fault_description,
                'started_at'         => $w->started_at?->toDateTimeString(),
                'completed_at'       => $w->completed_at?->toDateTimeString(),
                'created_at'         => $w->created_at?->toDateTimeString(),
                'is_locked'          => (bool) $w->is_locked,
                'total_cost'         => (float) $w->total_cost,
            ]);

        $repairOrders = RepairOrder::where('project_id', $project->id)
            ->orderByDesc('created_at')
            ->get(['id', 'code', 'status', 'source_type', 'source_code',
                   'fault_description', 'method_type', 'total_cost', 'received_at', 'updated_at'])
            ->map(fn ($r) => [
                'id'                => $r->id,
                'code'              => $r->code,
                'type'              => 'repair_order',
                'status'            => is_object($r->status) ? $r->status->value : $r->status,
                'source_type'       => $r->source_type,
                'source_code'       => $r->source_code,
                'method_type'       => $r->method_type,
                'fault_description' => $r->fault_description,
                'total_cost'        => (float) $r->total_cost,
                'received_at'       => $r->received_at?->toDateTimeString(),
                'updated_at'        => $r->updated_at?->toDateTimeString(),
            ]);

        $merged = $workOrders->merge($repairOrders)
            ->sortByDesc(fn ($x) => $x['created_at'] ?? $x['updated_at'] ?? $x['received_at'] ?? '')
            ->values();

        $stats = [
            'work_order_count'    => $workOrders->count(),
            'repair_order_count'  => $repairOrders->count(),
            'in_repair_count'     => $repairOrders->whereIn('status', ['in_repair', 'sent_for_repair'])->count(),
            'total_cost'          => $workOrders->sum('total_cost') + $repairOrders->sum('total_cost'),
        ];

        return response()->json([
            'code' => 0,
            'data' => [
                'project_id' => $project->id,
                'project_code' => $project->code ?? null,
                'project_stage' => is_object($project->stage) ? $project->stage->value : $project->stage,
                'can_create_maintenance' => $this->canCreateMaintenance($project),
                'items' => $merged,
                'stats' => $stats,
            ],
        ]);
    }

    /**
     * V0.5.7 块1 — 项目阶段校验:
     * 只有 settlement / warranty 阶段 (以及之后的"已交付"状态) 才能开售后工单
     * 施工/采购/合同阶段不能开 (否则数据错乱)
     */
    private function canCreateMaintenance(Project $project): array
    {
        $stage = is_object($project->stage) ? $project->stage->value : $project->stage;
        $allowed = ['settlement', 'warranty'];

        if (in_array($stage, $allowed, true)) {
            return ['allowed' => true, 'reason' => null];
        }

        $stageLabels = [
            'initiation'   => '立项',
            'inquiry'      => '询价',
            'contract'     => '合同',
            'purchase'     => '采购',
            'construction' => '施工',
        ];
        $currentLabel = $stageLabels[$stage] ?? $stage;

        return [
            'allowed'  => false,
            'reason'   => "项目当前阶段为「{$currentLabel}」, 需进入「结算」或「质保」阶段后才能创建售后工单",
            'required_stages' => $allowed,
        ];
    }
}
