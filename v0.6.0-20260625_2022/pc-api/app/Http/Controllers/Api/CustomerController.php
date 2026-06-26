<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Customer;
use App\Models\FollowUpRecord;
use App\Models\Project;
use App\Models\ProjectContract;
use App\Models\Receivable;
use App\Models\ServiceOrder;
use Carbon\Carbon;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class CustomerController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $perPage = (int) ($request->per_page ?? 15);
        $perPage = max(1, min($perPage, 200));

        $query = Customer::with(['primaryContact', 'contacts', 'assignedUser'])
            ->withCount(['projects', 'followUps']);

        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        if ($request->filled('category')) {
            $cat = $this->normalizeCategory($request->category);
            $query->where('category', $cat);
        }
        if ($request->filled('industry')) $query->where('industry', 'like', "%{$request->industry}%");
        if ($request->filled('tag')) {
            $tag = $request->tag;
            $query->where(function ($q) use ($tag) {
                $q->where('tags', 'like', '%"' . $tag . '"%')
                  ->orWhere('tags', 'like', '%' . $tag . '%');
            });
        }

        // V0.4.8 B2: 用子查询拿最近跟进 (替代 per-row followUps()->orderBy->first() N+1)
        $lastFollowSub = \DB::table('follow_up_records')
            ->selectRaw('customer_id, MAX(created_at) as last_at')
            ->groupBy('customer_id');

        $query->addSelect(['customers.*', 'lf.last_at as last_follow_at'])
            ->leftJoinSub($lastFollowSub, 'lf', 'lf.customer_id', '=', 'customers.id');

        $list = $query->orderBy('customers.created_at', 'desc')->paginate($perPage);

        // 计算健康度 (仍在 transform, 但无 query)
        $list->getCollection()->transform(function ($c) {
            $c->project_count = $c->projects_count;  // withCount
            $c->last_follow_at = $c->last_follow_at
                ? (\Carbon\Carbon::parse($c->last_follow_at)->format('Y-m-d H:i'))
                : null;
            $c->contact = $c->primaryContact?->name ?? ($c->contacts->first()?->name ?? '');
            $c->phone   = $c->primaryContact?->phone ?? ($c->contacts->first()?->phone ?? '');
            $c->health_score = $this->calcScore($c);
            $c->health_level = $this->toLevel($c->health_score);
            return $c;
        });
        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function stats(Request $request): JsonResponse
    {
        $data = Cache::remember('customers:stats', 300, function () {
            $total         = Customer::count();
            $vip           = Customer::where('category', 'vip')->count();
            $project_total = Customer::withCount('projects')->get()->sum('projects_count');
            $new_this_month = Customer::where('created_at', '>=', now()->startOfMonth())->count();
            return compact('total', 'vip', 'project_total', 'new_this_month');
        });
        return response()->json([
            'code' => 0,
            'data' => $data,
        ]);
    }

    /**
     * 客户健康度评分 — GET /api/customers/health
     * 5 维度加权(跟进 30 / 合同 25 / 回款 20 / 等级 15 / 项目 10)
     * PG 的 sum() 返回 string,所有金额用 (float) 强转
     */
    public function health(Request $request): JsonResponse
    {
        // V0.4.9 A2: 1 query 拿所有维度聚合 (替代 per-customer 5 query N+1)
        // step 1: 客户基础 + 等级分
        $customers = Customer::orderBy('id')->get(['id', 'name', 'category']);

        if ($customers->isEmpty()) {
            return response()->json(['code' => 0, 'data' => [
                'list'    => [],
                'summary' => ['total' => 0, 'healthy' => 0, 'good' => 0, 'average' => 0, 'warning' => 0, 'avg_score' => 0, 'needs_attention' => []],
            ]]);
        }

        $customerIds = $customers->pluck('id')->all();

        // step 2: 单 query 拿每个客户的最近跟进 (group by + max)
        $lastFollowMap = DB::table('follow_up_records')
            ->selectRaw('customer_id, MAX(created_at) as last_at')
            ->whereIn('customer_id', $customerIds)
            ->groupBy('customer_id')
            ->pluck('last_at', 'customer_id');

        // step 3: 单 query 拿每个客户的合同总额 (通过 projects 关联)
        $contractMap = DB::table('project_contracts as pc')
            ->join('projects as p', 'p.id', '=', 'pc.project_id')
            ->selectRaw('p.customer_id, COALESCE(SUM(pc.contract_amount), 0) as total')
            ->whereIn('p.customer_id', $customerIds)
            ->groupBy('p.customer_id')
            ->pluck('total', 'customer_id');

        // step 4: 单 query 拿每个客户的应收/已收
        $receivableMap = DB::table('receivables')
            ->selectRaw('customer_id, COALESCE(SUM(amount), 0) as total, COALESCE(SUM(received_amount), 0) as received')
            ->whereIn('customer_id', $customerIds)
            ->groupBy('customer_id')
            ->get()
            ->keyBy('customer_id');

        // step 5: 单 query 拿每个客户的活跃项目数
        $activeProjectMap = DB::table('projects')
            ->selectRaw('customer_id, COUNT(*) as cnt')
            ->whereIn('customer_id', $customerIds)
            ->whereNotIn('status', ['completed', 'cancelled', 'done'])
            ->groupBy('customer_id')
            ->pluck('cnt', 'customer_id');

        $list = [];
        $summary = [
            'total' => 0, 'healthy' => 0, 'good' => 0, 'average' => 0, 'warning' => 0,
            'avg_score' => 0, 'needs_attention' => [],
        ];
        $scoreTotal = 0;

        foreach ($customers as $c) {
            // ---- 1) 跟进活跃度(30) ----
            $lastAt = $lastFollowMap->get($c->id);
            $days = $lastAt ? (int) Carbon::parse($lastAt)->diffInDays(now()) : null;
            if ($days === null || $days > 90) {
                $follow = 0;
            } elseif ($days <= 7) {
                $follow = 30;
            } elseif ($days <= 30) {
                $follow = 20;
            } else { // 31-90
                $follow = 10;
            }

            // ---- 2) 合同价值(25) ----
            $contractAmount = (float) ($contractMap->get($c->id) ?? 0);
            if ($contractAmount >= 1_000_000) {
                $contract = 25;
            } elseif ($contractAmount >= 500_000) {
                $contract = 20;
            } elseif ($contractAmount >= 100_000) {
                $contract = 15;
            } elseif ($contractAmount >= 10_000) {
                $contract = 8;
            } else {
                $contract = 2;
            }

            // ---- 3) 回款健康(20) ----
            $recvRow = $receivableMap->get($c->id);
            $totalReceivable = $recvRow ? (float) $recvRow->total : 0.0;
            $totalReceived   = $recvRow ? (float) $recvRow->received : 0.0;
            if ($totalReceivable <= 0) {
                $payment = 15;
            } else {
                $ratio = $totalReceivable / max($totalReceived, 1.0);
                if ($ratio < 0.3)       $payment = 20;
                elseif ($ratio < 0.6)   $payment = 15;
                elseif ($ratio < 0.9)   $payment = 10;
                else                    $payment = 5;
            }

            // ---- 4) 客户等级(15) ----
            $cat = $c->category ?: 'normal';
            if ($cat === 'inactive') {
                $level = 0;
            } else {
                $level = match ($cat) {
                    'vip'       => 15,
                    'normal'    => 10,
                    'potential' => 5,
                    default     => 5,
                };
            }

            // ---- 5) 项目活跃(10) ----
            $activeProjects = (int) ($activeProjectMap->get($c->id) ?? 0);
            if ($activeProjects >= 3) {
                $project = 10;
            } elseif ($activeProjects >= 1) {
                $project = 7;
            } else {
                $project = 3;
            }

            $score = $follow + $contract + $payment + $level + $project;
            $levelName = $this->toLevel($score);

            $list[] = [
                'id'                      => $c->id,
                'name'                    => $c->name,
                'category'                => $c->category,
                'health_score'            => $score,
                'health_level'            => $levelName,
                'health_color'            => $this->toColor($levelName),
                'score_breakdown'         => [
                    'follow'   => $follow,
                    'contract' => $contract,
                    'payment'  => $payment,
                    'level'    => $level,
                    'project'  => $project,
                ],
                'last_follow_at'          => $lastAt ? Carbon::parse($lastAt)->format('Y-m-d H:i') : null,
                'active_projects'         => $activeProjects,
                'total_contract_amount'   => (int) $contractAmount,
                'outstanding_receivable'  => (int) max($totalReceivable - $totalReceived, 0),
            ];

            $summary['total']++;
            $scoreTotal += $score;
            match ($levelName) {
                '健康' => $summary['healthy']++,
                '良好' => $summary['good']++,
                '一般' => $summary['average']++,
                '预警' => $summary['warning']++,
                default => null,
            };
            if ($levelName === '预警') {
                $summary['needs_attention'][] = $c->id;
            }
        }

        if ($summary['total'] > 0) {
            $summary['avg_score'] = (int) round($scoreTotal / $summary['total']);
        }

        return response()->json(['code' => 0, 'data' => [
            'list'    => $list,
            'summary' => $summary,
        ]]);
    }

    /**
     * 5 维度加权评分,总分 100
     */
    private function calcScore(Customer $c): int
    {
        // 跟进
        $lastFollow = $c->followUps()->orderBy('created_at', 'desc')->first();
        if ($lastFollow) {
            $days = (int) $lastFollow->created_at->diffInDays(now());
        } else {
            $days = null;
        }
        if ($days === null || $days > 90)       $follow = 0;
        elseif ($days <= 7)                      $follow = 30;
        elseif ($days <= 30)                     $follow = 20;
        else                                    $follow = 10;

        // 合同
        $contractAmount = (float) \DB::table('project_contracts as pc')
            ->join('projects as p', 'p.id', '=', 'pc.project_id')
            ->where('p.customer_id', $c->id)
            ->sum('pc.contract_amount');
        if ($contractAmount >= 1_000_000)      $contract = 25;
        elseif ($contractAmount >= 500_000)    $contract = 20;
        elseif ($contractAmount >= 100_000)    $contract = 15;
        elseif ($contractAmount >= 10_000)     $contract = 8;
        else                                   $contract = 2;

        // 回款
        $totalReceivable = (float) $c->receivables()->sum('amount');
        $totalReceived   = (float) $c->receivables()->sum('received_amount');
        if ($totalReceivable <= 0) {
            $payment = 15;
        } else {
            $ratio = $totalReceivable / max($totalReceived, 1.0);
            if ($ratio < 0.3)       $payment = 20;
            elseif ($ratio < 0.6)   $payment = 15;
            elseif ($ratio < 0.9)   $payment = 10;
            else                    $payment = 5;
        }

        // 等级
        $cat = $c->category ?: 'normal';
        if ($cat === 'inactive') $level = 0;
        else $level = match ($cat) {
            'vip'       => 15,
            'normal'    => 10,
            'potential' => 5,
            default     => 5,
        };

        // 项目
        $activeProjects = (int) $c->projects()
            ->whereNotIn('status', ['completed', 'cancelled', 'done'])
            ->count();
        if ($activeProjects >= 3)      $project = 10;
        elseif ($activeProjects >= 1)  $project = 7;
        else                           $project = 3;

        return $follow + $contract + $payment + $level + $project;
    }

    private function toLevel(int $score): string
    {
        return match (true) {
            $score >= 80 => '健康',
            $score >= 60 => '良好',
            $score >= 40 => '一般',
            default      => '预警',
        };
    }

    private function toColor(string $level): string
    {
        return match ($level) {
            '健康' => 'green',
            '良好' => 'blue',
            '一般' => 'yellow',
            '预警' => 'red',
            default => 'gray',
        };
    }

    public function import(Request $request): JsonResponse
    {
        $request->validate(['file' => 'required|file|mimes:csv,xlsx,xls|max:10240']);
        $file = $request->file('file');
        $success = 0; $failed = 0; $errors = [];
        $rows = [];
        if (strtolower($file->getClientOriginalExtension()) === 'csv') {
            $rows = $this->parseCsv($file->getRealPath());
        } else {
            // Excel 暂用前两个列：客户名称, 行业 — 完整 xlsx 解析需要 maatwebsite/excel
            // 简化：返回错误提示用户用 CSV
            return response()->json(['code' => 1001, 'message' => '请使用 CSV 格式导入（Excel 请先另存为 .csv）'], 422);
        }
        foreach (array_slice($rows, 1) as $idx => $r) {  // 跳过表头
            if (empty($r[0])) { $failed++; continue; }
            try {
                $tags = !empty($r[5]) ? array_map('trim', explode(';', $r[5])) : [];
                $cat  = !empty($r[4]) ? $this->normalizeCategory($r[4]) : 'normal';
                $customer = Customer::create([
                    'name'     => trim($r[0]),
                    'industry' => $r[1] ?? null,
                    'category' => $cat,
                    'tags'     => $tags,
                    'status'   => 'active',
                    'province' => '',
                    'city'     => '',
                    'district' => '',
                    'address'  => '',
                ]);
                if (!empty($r[2]) || !empty($r[3])) {
                    $customer->contacts()->create([
                        'name'       => $r[2] ?? null,
                        'phone'      => $r[3] ?? null,
                        'is_primary' => true,
                    ]);
                }
                $success++;
            } catch (\Throwable $e) {
                $failed++;
                $errors[] = "第 " . ($idx + 2) . " 行: " . $e->getMessage();
            }
        }
        return response()->json(['code' => 0, 'data' => compact('success', 'failed', 'errors')]);
    }

    private function parseCsv(string $path): array
    {
        $rows = [];
        if (($h = fopen($path, 'r')) !== false) {
            // 检测 BOM
            $bom = fread($h, 3);
            if ($bom !== "\xEF\xBB\xBF") rewind($h);
            while (($row = fgetcsv($h)) !== false) {
                $rows[] = $row;
            }
            fclose($h);
        }
        return $rows;
    }

    public function show(Customer $customer): JsonResponse
    {
        // 一次性预加载所有关联 + 计数，避免 N+1
        $customer->load([
            'contacts',
            'devices',
            'projects:id,name,project_no,stage,status,customer_id',
            'serviceOrders',
            'followUps.user:id,name',
            'receivables',
        ]);
        // 加点常用字段给前端
        $customer->project_count = $customer->projects->count();
        $lastFollow = $customer->followUps->sortByDesc('created_at')->first();
        $customer->last_follow_at = $lastFollow ? $lastFollow->created_at->format('Y-m-d H:i') : null;
        $customer->contact = $customer->primaryContact?->name ?? ($customer->contacts->first()?->name ?? '');
        $customer->phone  = $customer->primaryContact?->phone ?? ($customer->contacts->first()?->phone ?? '');
        return response()->json(['code' => 0, 'data' => $customer]);
    }

    public function profile(Customer $customer): JsonResponse
    {
        $now = Carbon::now();

        // 1) 基础信息(沿用 show() 的聚合)
        $customer->load([
            'contacts',
            'devices:id,customer_id',
            'projects:id,name,project_no,stage,status,customer_id,manager_id,created_at',
            'serviceOrders:id,customer_id,status,created_at',
            'followUps.user:id,name',
            'receivables',
            'assignedUser:id,name',
        ]);
        $customer->project_count = $customer->projects->count();
        $lastFollow = $customer->followUps->sortByDesc('created_at')->first();
        $customer->last_follow_at = $lastFollow ? $lastFollow->created_at->format('Y-m-d H:i') : null;
        $customer->contact = $customer->primaryContact?->name ?? ($customer->contacts->first()?->name ?? '');
        $customer->phone  = $customer->primaryContact?->phone ?? ($customer->contacts->first()?->phone ?? '');
        $basic = $customer->toArray();

        // 2) 项目汇总 + 合同金额(避免 N+1)
        $projectIds = $customer->projects->pluck('id')->all();
        $contractSum = $projectIds
            ? (float) ProjectContract::whereIn('project_id', $projectIds)->sum('contract_amount')
            : 0.0;

        $projectsSummary = $customer->projects->map(function ($p) {
            return [
                'id'         => $p->id,
                'name'       => $p->name,
                'project_no' => $p->project_no,
                'stage'      => $p->stage?->value ?? (string) $p->stage,
                'status'     => $p->status?->value ?? $p->status,
                'amount'     => 0,  // 概览不展开,前端详情再查
            ];
        })->values();

        // 3) metrics
        $totalProjects      = $customer->projects->count();
        $activeProjects     = $customer->projects->whereIn('status', ['active', 'in_progress'])->count();
        $completedProjects  = $customer->projects->where('status', 'completed')->count();
        $receivedAmount     = (float) Receivable::where('customer_id', $customer->id)->sum('received_amount');
        $outstandingAmount  = (float) Receivable::where('customer_id', $customer->id)
            ->selectRaw('COALESCE(SUM(amount - received_amount),0) AS v')->value('v');
        $collectionRate     = $contractSum > 0 ? round($receivedAmount / $contractSum, 4) : 0.0;

        $totalServiceOrders    = $customer->serviceOrders->count();
        $pendingServiceOrders  = $customer->serviceOrders->whereIn('status', ['pending', 'assigned', 'in_progress'])->count();
        $deviceCount           = $customer->devices->count();
        $followUpCount         = $customer->followUps->count();

        // 首次合作时间: 最早的项目创建时间 或 最早的跟进时间
        $firstProjectAt = $projectIds
            ? Project::whereIn('id', $projectIds)->min('created_at')
            : null;
        $firstFollowAt  = $customer->followUps->min('created_at');
        $firstCoopAt    = collect([$firstProjectAt, $firstFollowAt])->filter()->min();
        $firstCoopDate  = $firstCoopAt ? Carbon::parse($firstCoopAt) : null;
        $cooperationYears = $firstCoopDate ? round($firstCoopDate->diffInDays($now) / 365, 1) : 0.0;

        // 平均跟进间隔: 跨度天数 / 次数
        $avgFollowIntervalDays = 0;
        if ($followUpCount > 1 && $firstFollowAt) {
            $span = Carbon::parse($firstFollowAt)->diffInDays($now);
            $avgFollowIntervalDays = $span > 0 ? (int) round($span / $followUpCount) : 0;
        } elseif ($followUpCount === 1) {
            $avgFollowIntervalDays = Carbon::parse($firstFollowAt)->diffInDays($now);
        }

        $metrics = [
            'total_projects'           => $totalProjects,
            'active_projects'          => $activeProjects,
            'completed_projects'       => $completedProjects,
            'total_contract_amount'    => $contractSum,
            'received_amount'          => $receivedAmount,
            'outstanding_amount'       => $outstandingAmount,
            'collection_rate'          => $collectionRate,
            'total_service_orders'     => $totalServiceOrders,
            'pending_service_orders'   => $pendingServiceOrders,
            'device_count'             => $deviceCount,
            'follow_up_count'          => $followUpCount,
            'avg_follow_interval_days' => $avgFollowIntervalDays,
            'cooperation_years'        => $cooperationYears,
            'first_cooperation_at'     => $firstCoopDate?->format('Y-m-d'),
        ];

        // 4) timeline: 4 类来源各取最近 N 条,内存合并倒序
        $perSource = 20;  // 单源 20 条,合并后取前 50,保证每类都覆盖
        $timeline = [];

        $followUps = $customer->followUps->sortByDesc('created_at')->take($perSource);
        foreach ($followUps as $f) {
            $timeline[] = [
                'type'        => 'follow_up',
                'date'        => $f->created_at->format('Y-m-d H:i'),
                'sort_at'     => $f->created_at->timestamp,
                'title'       => $this->followTypeLabel($f->type) . ' · ' . mb_substr((string) $f->content, 0, 20),
                'description' => (string) $f->content,
                'user_name'   => $f->user?->name ?? '未分配',
            ];
        }

        $projects = $customer->projects->sortByDesc('created_at')->take($perSource);
        foreach ($projects as $p) {
            $timeline[] = [
                'type'        => 'project_created',
                'date'        => $p->created_at->format('Y-m-d H:i'),
                'sort_at'     => $p->created_at->timestamp,
                'title'       => '创建项目『' . $p->name . '』',
                'description' => '项目编号 ' . $p->project_no,
                'user_name'   => $p->manager?->name ?? '未分配',
            ];
        }

        $serviceOrders = $customer->serviceOrders->sortByDesc('created_at')->take($perSource);
        foreach ($serviceOrders as $s) {
            $statusVal = $s->status?->value ?? $s->status;
            $timeline[] = [
                'type'        => 'service_order_created',
                'date'        => $s->created_at->format('Y-m-d H:i'),
                'sort_at'     => $s->created_at->timestamp,
                'title'       => '工单『' . ($s->order_no ?? ('#' . $s->id)) . '』',
                'description' => $this->serviceStatusLabel((string) $statusVal),
                'user_name'   => $s->assignedUser?->name ?? $s->creator?->name ?? '未分配',
            ];
        }

        // 收到回款: 用 received_date 或 updated_at(received_amount 变化时点)
        $receivedRows = Receivable::where('customer_id', $customer->id)
            ->where('received_amount', '>', 0)
            ->orderByRaw('COALESCE(received_date, updated_at) DESC')
            ->limit($perSource)
            ->get(['id', 'amount', 'received_amount', 'received_date', 'updated_at', 'notes']);
        foreach ($receivedRows as $r) {
            $ts = $r->received_date ?: $r->updated_at;
            $timeline[] = [
                'type'        => 'receivable_received',
                'date'        => $ts?->format('Y-m-d H:i') ?? '',
                'sort_at'     => $ts?->timestamp ?? 0,
                'title'       => '收到回款 ¥' . number_format((float) $r->received_amount, 0),
                'description' => $r->notes ?: '应收单 #' . $r->id,
                'user_name'   => '财务',
            ];
        }

        usort($timeline, fn($a, $b) => $b['sort_at'] <=> $a['sort_at']);
        $timeline = array_slice(array_values($timeline), 0, 50);
        // 输出时去掉 sort_at
        $timeline = array_map(function ($e) {
            unset($e['sort_at']);
            return $e;
        }, $timeline);

        // 5) top_employees: 来自项目 members + 工单 assigned_to + 跟进 user
        $employeeAgg = [];
        $bump = function ($userId, $userName) use (&$employeeAgg) {
            if (!$userId) return;
            $key = $userId;
            if (!isset($employeeAgg[$key])) {
                $employeeAgg[$key] = ['id' => $userId, 'name' => $userName, 'avatar' => null, 'role' => '客户经理', 'interaction_count' => 0];
            }
            $employeeAgg[$key]['interaction_count']++;
        };

        if ($projectIds) {
            $memberRows = DB::table('project_members')
                ->join('users', 'users.id', '=', 'project_members.user_id')
                ->whereIn('project_members.project_id', $projectIds)
                ->select('users.id', 'users.name', 'project_members.role')
                ->get();
            foreach ($memberRows as $m) {
                $bump($m->id, $m->name);
                $employeeAgg[$m->id]['role'] = $m->role ?: '项目成员';
            }
        }
        foreach ($customer->serviceOrders as $s) {
            if ($s->assigned_to) $bump($s->assigned_to, $s->assignedUser?->name);
        }
        foreach ($customer->followUps as $f) {
            if ($f->user_id) $bump($f->user_id, $f->user?->name);
        }
        $topEmployees = array_values($employeeAgg);
        usort($topEmployees, fn($a, $b) => $b['interaction_count'] <=> $a['interaction_count']);
        $topEmployees = array_slice($topEmployees, 0, 5);

        // 6) insights: 4-6 条规则
        $insights = [];
        $catLabel = match ($customer->category) {
            'vip'       => 'VIP',
            'potential' => '潜在',
            'normal'    => '普通',
            default     => (string) $customer->category,
        };
        if ($cooperationYears >= 1) {
            $insights[] = sprintf('客户合作 %.1f 年,处于%s', $cooperationYears, $cooperationYears >= 3 ? '稳定期' : '成长期');
        } else {
            $insights[] = '新合作客户,处于磨合期';
        }

        $recentFollows = $customer->followUps->filter(fn($f) => Carbon::parse($f->created_at)->gte($now->copy()->subDays(30)))->count();
        if ($recentFollows > 0) {
            $insights[] = sprintf('近 30 天有 %d 次主动跟进,服务响应积极', $recentFollows);
        } else {
            $insights[] = '近 30 天无主动跟进,建议尽快联系';
        }

        if ($activeProjects > 0) {
            $insights[] = sprintf('在执行项目 %d 个,涉及合同金额 %.0f 万元', $activeProjects, $contractSum / 10000);
        } else {
            $insights[] = '当前无在执行项目';
        }

        if ($outstandingAmount > 0) {
            $ratePct = (int) round($collectionRate * 100);
            $insights[] = sprintf('回款率 %d%%,需关注 %.0f 万未收款项', $ratePct, $outstandingAmount / 10000);
        } else {
            $insights[] = '款项已全部收回,回款健康';
        }

        if ($totalServiceOrders > 0) {
            $satis = $totalServiceOrders - $pendingServiceOrders;
            $insights[] = sprintf('工单 %d 次,仅 %d 次待处理,售后满意度%s', $totalServiceOrders, $pendingServiceOrders, $pendingServiceOrders === 0 ? '良好' : '一般');
        } else {
            $insights[] = '暂无售后工单记录';
        }

        if ($customer->category === 'vip') {
            $insights[] = '客户等级 VIP,建议维持季度回访';
        } elseif ($customer->category === 'potential') {
            $insights[] = '潜在客户,建议加快转化节奏';
        }

        // 7) next_action
        $lastFollowAt = $lastFollow?->created_at;
        $avgInterval  = max($avgFollowIntervalDays, 7);  // 兜底 7 天
        $suggestDate  = $lastFollowAt
            ? Carbon::parse($lastFollowAt)->addDays($avgInterval)
            : $now->copy();
        $reasonDays   = $lastFollowAt ? Carbon::parse($lastFollowAt)->diffInDays($now) : 0;
        $ownerName    = $customer->assignedUser?->name
            ?? $lastFollow?->user?->name
            ?? '未分配';

        $nextAction = [
            'title'        => '建议下次跟进',
            'suggest_date' => $suggestDate->format('Y-m-d'),
            'reason'       => $lastFollowAt
                ? sprintf('距上次 %d 天,平均间隔 %d 天', $reasonDays, $avgFollowIntervalDays ?: $avgInterval)
                : '该客户尚无跟进记录,建议尽快建联',
            'owner_name'   => $ownerName,
        ];

        return response()->json([
            'code' => 0,
            'data' => [
                'basic'            => $basic,
                'metrics'          => $metrics,
                'timeline'         => $timeline,
                'projects_summary' => $projectsSummary,
                'top_employees'    => $topEmployees,
                'insights'         => $insights,
                'next_action'      => $nextAction,
            ],
        ]);
    }

    private function followTypeLabel(string $t): string
    {
        return match ($t) {
            'visit'  => '上门拜访',
            'call'   => '电话沟通',
            'online' => '在线沟通',
            default  => '跟进',
        };
    }

    private function serviceStatusLabel(string $s): string
    {
        return match ($s) {
            'pending'    => '待派工',
            'assigned'   => '已派工',
            'in_progress'=> '处理中',
            'completed'  => '已完成',
            'confirmed'  => '客户已确认',
            'cancelled'  => '已取消',
            default      => $s,
        };
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'required|string|max:128',
            'industry'     => 'nullable|string|max:64',
            'category'     => 'nullable|in:vip,normal,potential,VIP,普通,潜在',
            'province'     => 'nullable|string|max:32',
            'city'         => 'nullable|string|max:32',
            'district'     => 'nullable|string|max:32',
            'address'      => 'nullable|string|max:255',
            'longitude'    => 'nullable|numeric|between:-180,180',
            'latitude'     => 'nullable|numeric|between:-90,90',
            'tags'         => 'nullable|array',
            'tags.*'       => 'string|max:32',
            'source'       => 'nullable|string|max:64',
            'status'       => 'nullable|in:active,inactive',
            'description'  => 'nullable|string',
            'contact'      => 'nullable|string|max:64',
            'phone'        => 'nullable|string|max:32',
        ]);
        if (empty($data['category'])) $data['category'] = 'normal';
        else $data['category'] = $this->normalizeCategory($data['category']);
        if (empty($data['status'])) $data['status'] = 'active';
        // NOT NULL 字段补空字符串
        $data['province'] = $data['province'] ?? '';
        $data['city']     = $data['city']     ?? '';
        $data['district'] = $data['district'] ?? '';
        $data['address']  = $data['address']  ?? '';

        $contactName  = $data['contact'] ?? null;
        $contactPhone = $data['phone'] ?? null;
        unset($data['contact'], $data['phone']);

        $customer = Customer::create($data);
        Cache::forget('customers:stats');
        if ($contactName) {
            $customer->contacts()->create([
                'name'      => $contactName,
                'phone'     => $contactPhone,
                'is_primary'=> true,
            ]);
        }
        return response()->json(['code' => 0, 'message' => '客户已创建', 'data' => $customer->load('contacts')]);
    }

    public function update(Request $request, Customer $customer): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'sometimes|required|string|max:128',
            'industry'     => 'sometimes|nullable|string|max:64',
            'category'     => 'sometimes|nullable|in:vip,normal,potential,VIP,普通,潜在',
            'province'     => 'sometimes|nullable|string|max:32',
            'city'         => 'sometimes|nullable|string|max:32',
            'district'     => 'sometimes|nullable|string|max:32',
            'address'      => 'sometimes|nullable|string|max:255',
            'longitude'    => 'sometimes|nullable|numeric',
            'latitude'     => 'sometimes|nullable|numeric',
            'tags'         => 'sometimes|nullable|array',
            'tags.*'       => 'string|max:32',
            'source'       => 'sometimes|nullable|string|max:64',
            'status'       => 'sometimes|nullable|in:active,inactive',
            'description'  => 'sometimes|nullable|string',
            'contact'      => 'sometimes|nullable|string|max:64',
            'phone'        => 'sometimes|nullable|string|max:32',
        ]);
        if (isset($data['category'])) $data['category'] = $this->normalizeCategory($data['category']);
        $contactName  = $data['contact'] ?? null;
        $contactPhone = $data['phone'] ?? null;
        unset($data['contact'], $data['phone']);
        // ⚠️ V0.5.8.9 兜底: ConvertEmptyStringsToNull 中间件会把空串变 null,
        // 但 customers.province/city/district/address 是 NOT NULL, 手动恢复空串
        foreach (['province', 'city', 'district', 'address'] as $nf) {
            if (array_key_exists($nf, $data) && $data[$nf] === null) {
                $data[$nf] = '';
            }
        }
        Cache::forget('customers:stats');
        $customer->fill($data)->save();
        if ($contactName !== null) {
            $primary = $customer->primaryContact;
            if ($primary) {
                $primary->update(['name' => $contactName, 'phone' => $contactPhone]);
            } else {
                $customer->contacts()->create([
                    'name' => $contactName, 'phone' => $contactPhone, 'is_primary' => true,
                ]);
            }
        }
        return response()->json(['code' => 0, 'message' => '客户已更新', 'data' => $customer->load('contacts')]);
    }

    // v0.5.8.9 联系人管理
    public function listContacts(Customer $customer): JsonResponse
    {
        $contacts = $customer->contacts()->orderBy('is_primary', 'desc')->orderBy('id')->get();
        return response()->json(['code' => 0, 'data' => $contacts]);
    }

    public function storeContact(Request $request, Customer $customer): JsonResponse
    {
        $data = $request->validate([
            'name'      => 'required|string|max:64',
            'position'  => 'nullable|string|max:100',
            'phone'     => 'required|string|max:32',
            'email'     => 'nullable|email|max:100',
            'wechat'    => 'nullable|string|max:50',
            'notes'     => 'nullable|string',
            'is_primary'=> 'sometimes|boolean',
        ]);
        // 如果要设为主联系人, 先把其他人降级
        if (!empty($data['is_primary'])) {
            $customer->contacts()->update(['is_primary' => false]);
        }
        $contact = $customer->contacts()->create($data);
        return response()->json(['code' => 0, 'message' => '联系人已添加', 'data' => $contact]);
    }

    public function updateContact(Request $request, Customer $customer, $contact): JsonResponse
    {
        $c = $customer->contacts()->findOrFail($contact);
        $data = $request->validate([
            'name'      => 'sometimes|required|string|max:64',
            'position'  => 'nullable|string|max:100',
            'phone'     => 'sometimes|required|string|max:32',
            'email'     => 'nullable|email|max:100',
            'wechat'    => 'nullable|string|max:50',
            'notes'     => 'nullable|string',
            'is_primary'=> 'sometimes|boolean',
        ]);
        if (!empty($data['is_primary'])) {
            $customer->contacts()->where('id', '!=', $c->id)->update(['is_primary' => false]);
        }
        $c->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '联系人已更新', 'data' => $c]);
    }

    public function destroyContact(Customer $customer, $contact): JsonResponse
    {
        $c = $customer->contacts()->findOrFail($contact);
        $c->delete();
        return response()->json(['code' => 0, 'message' => '联系人已删除']);
    }

    // v0.5.8.9 开票信息
    public function listInvoiceInfos(Customer $customer): JsonResponse
    {
        $infos = $customer->invoiceInfos()->orderBy('is_default', 'desc')->orderBy('id')->get();
        return response()->json(['code' => 0, 'data' => $infos]);
    }

    public function storeInvoiceInfo(Request $request, Customer $customer): JsonResponse
    {
        $data = $request->validate([
            'invoice_type'     => 'required|in:general,special,electronic',
            'company_name'     => 'required|string|max:200',
            'tax_no'           => 'required|string|max:50',
            'register_address' => 'nullable|string|max:200',
            'register_phone'   => 'nullable|string|max:32',
            'bank_name'        => 'nullable|string|max:100',
            'bank_account'     => 'nullable|string|max:50',
            'is_default'       => 'sometimes|boolean',
            'remark'           => 'nullable|string',
        ]);
        // 设默认时, 把其他降级
        if (!empty($data['is_default'])) {
            $customer->invoiceInfos()->update(['is_default' => false]);
        }
        $info = $customer->invoiceInfos()->create($data);
        return response()->json(['code' => 0, 'message' => '开票信息已添加', 'data' => $info]);
    }

    public function updateInvoiceInfo(Request $request, Customer $customer, $info): JsonResponse
    {
        $i = $customer->invoiceInfos()->findOrFail($info);
        $data = $request->validate([
            'invoice_type'     => 'sometimes|required|in:general,special,electronic',
            'company_name'     => 'sometimes|required|string|max:200',
            'tax_no'           => 'sometimes|required|string|max:50',
            'register_address' => 'nullable|string|max:200',
            'register_phone'   => 'nullable|string|max:32',
            'bank_name'        => 'nullable|string|max:100',
            'bank_account'     => 'nullable|string|max:50',
            'is_default'       => 'sometimes|boolean',
            'remark'           => 'nullable|string',
        ]);
        if (!empty($data['is_default'])) {
            $customer->invoiceInfos()->where('id', '!=', $i->id)->update(['is_default' => false]);
        }
        $i->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '开票信息已更新', 'data' => $i]);
    }

    public function destroyInvoiceInfo(Customer $customer, $info): JsonResponse
    {
        $i = $customer->invoiceInfos()->findOrFail($info);
        $i->delete();
        return response()->json(['code' => 0, 'message' => '开票信息已删除']);
    }

    private function normalizeCategory(string $c): string
    {
        return match ($c) {
            'VIP'   => 'vip',
            '普通'  => 'normal',
            '潜在'  => 'potential',
            default => $c,  // 已经是 vip/normal/potential
        };
    }

    public function destroy(Customer $customer): JsonResponse
    {
        // 不能删除有项目的客户
        $projCnt = $customer->projects()->count();
        if ($projCnt > 0) {
            return response()->json([
                'code' => 1001,
                'message' => "客户「{$customer->name}」下还有 {$projCnt} 个项目，请先处理",
            ], 422);
        }
        Cache::forget('customers:stats');
        $customer->contacts()->delete();
        $customer->followUps()->delete();
        $customer->delete();
        return response()->json(['code' => 0, 'message' => '客户已删除']);
    }

    public function followUps(Request $request, Customer $customer): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => $customer->followUps()->with('user')->orderBy('created_at', 'desc')->paginate()]);
    }

    public function storeFollowUp(Request $request, Customer $customer): JsonResponse
    {
        $data = $request->validate([
            // 跟进方式：后端 enum 为 visit/call/online/other
            // 前端可传 中文(上门/电话/微信/邮件/其他) 或 英文(visit/call/online/phone/wechat/email/other)
            'type'                  => 'nullable|string|max:32',
            'content'               => 'required|string',
            'next_follow_up_date'   => 'nullable|date',
            'next_follow_up_note'   => 'nullable|string',
        ]);
        if (!empty($data['type'])) {
            $data['type'] = $this->normalizeFollowType($data['type']);
        } else {
            $data['type'] = 'other';
        }
        $data['customer_id'] = $customer->id;
        $data['user_id']     = $request->user()->id;
        $f = FollowUpRecord::create($data);
        return response()->json(['code' => 0, 'message' => '跟进记录已添加', 'data' => $f->load('user')]);
    }

    /**
     * 跟进方式中英文 -> enum 归一
     * 目标 enum: visit / call / online / other
     */
    private function normalizeFollowType(string $t): string
    {
        $map = [
            '上门'   => 'visit',
            '拜访'   => 'visit',
            '电话'   => 'call',
            '通话'   => 'call',
            '微信'   => 'online',
            '邮件'   => 'online',
            '短信'   => 'online',
            '在线'   => 'online',
            '其他'   => 'other',
            'phone'  => 'call',
            'wechat' => 'online',
            'email'  => 'online',
            'sms'    => 'online',
        ];
        $key = trim($t);
        if (isset($map[$key])) return $map[$key];
        // 英文 enum 值原样接受
        if (in_array($key, ['visit', 'call', 'online', 'other'], true)) return $key;
        return 'other';
    }

    public function devices(Request $request, Customer $customer): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => $customer->devices()->paginate()]);
    }

    /**
     * 客户地图分布 — 兼容前端 /customers/map
     */
    public function mapData(Request $request): JsonResponse
    {
        // 安全 select（不依赖 level 列是否存在的猜测）
        try {
            $customers = Customer::select('id', 'name', 'province', 'city', 'district', 'address', 'industry', 'status')
                ->whereNotNull('province')
                ->get();
        } catch (\Throwable $e) {
            // 兜底：只 select 必定存在的字段
            $customers = Customer::whereNotNull('province')->get();
        }

        $list = $customers->map(function ($c) {
            return [
                'id' => $c->id,
                'name' => $c->name,
                'region' => trim(($c->province ?? '') . ' ' . ($c->city ?? '') . ' ' . ($c->district ?? '')),
                'province' => $c->province,
                'city' => $c->city,
                'address' => $c->address,
                'industry' => $c->industry ?? null,
                'level' => $c->level ?? null,
                'status' => $c->status ?? null,
            ];
        });

        $byProvince = $list->groupBy('province')->map(fn($g, $k) => [
            'province' => $k,
            'count' => $g->count(),
            'customers' => $g->values(),
        ])->values();

        return response()->json([
            'code' => 0,
            'data' => [
                'total' => $list->count(),
                'by_province' => $byProvince,
                'list' => $list,
            ],
        ]);
    }

    /**
     * v0.5.8: 客户行业字典 (前端客户列表筛选用)
     * GET /api/customers/industries
     */
    public function industries(): JsonResponse
    {
        $industries = \DB::table('customers')
            ->whereNotNull('industry')
            ->where('industry', '<>', '')
            ->distinct()
            ->orderBy('industry')
            ->pluck('industry');

        // 兜底: 库里没数据时返回常见行业
        if ($industries->isEmpty()) {
            $industries = collect(['教育', '医疗', '金融', '地产', '互联网', '制造业', '零售', '政府', '安防工程']);
        }

        return response()->json(['code' => 0, 'data' => $industries->values()]);
    }
}
