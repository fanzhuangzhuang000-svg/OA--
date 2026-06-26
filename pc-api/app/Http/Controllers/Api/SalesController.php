<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Lead;
use App\Models\Opportunity;
use App\Models\Quotation;
use App\Models\QuotationItem;
use App\Models\Referrer;
use App\Models\ProjectPool;
use App\Models\Project;
use App\Models\ReferralSettlement;
use App\Models\SalesFollowUp;
use App\Models\SalesFollowUpAttachment;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/**
 * 销售前链路 P1 — 真实 CRUD + 转化闭环 + 报价单 + 跟进附件
 */
class SalesController extends Controller
{
    // ============================================================
    // === 线索池 (5 个 CRUD 端点) ===
    // ============================================================

    public function leadsIndex(Request $request): JsonResponse
    {
        $query = Lead::with(['customer', 'owner']);
        $user = $request->user();
        // v0.3.11 P1 块一: 销售员 owner 隔离 (非管理员/经理只能看自己 + 部门共享)
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->where(function ($q) use ($user) {
                $q->where('owner_id', $user->id);
                // 部门共享: 同部门的可见 (v0.4 再决定是否放开)
                if ($user->department_id) {
                    $q->orWhereIn('owner_id', function ($sub) use ($user) {
                        $sub->select('id')->from('users')->where('department_id', $user->department_id);
                    });
                }
            });
        }
        if ($request->filled('keyword')) $query->where('customer_name', 'like', "%{$request->keyword}%");
        if ($request->filled('status')) $query->where('status', $request->status);
        if ($request->filled('source')) $query->where('source', $request->source);
        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function leadsShow(Lead $lead): JsonResponse
    {
        $lead->load(['customer', 'owner', 'referrer']);
        return response()->json(['code' => 0, 'data' => $lead]);
    }

    public function leadsSourceOptions(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => [
            ['value' => 'online', 'label' => '网络推广'],
            ['value' => 'phone', 'label' => '电话陌拜'],
            ['value' => 'exhibition', 'label' => '展会活动'],
            ['value' => 'referral', 'label' => '老客户转介'],
            ['value' => 'other', 'label' => '其他'],
        ]]);
    }

    public function leadsStore(Request $request): JsonResponse
    {
        $data = $request->validate([
            'customer_id'    => 'nullable|integer|exists:customers,id',
            'customer_name'  => 'required_without:customer_id|string|max:200',
            'contact_name'   => 'required|string|max:50',
            'contact_phone'  => 'required|string|max:20',
            'contact_title'  => 'nullable|string|max:50',
            'source'         => 'required|string|in:online,phone,exhibition,referral,other',
            'referrer_id'    => 'nullable|integer|exists:referrers,id',
            'requirement'    => 'nullable|string',
            'estimated_amount' => 'nullable|numeric|min:0',
            'rating'         => 'nullable|string|in:A,B,C,D',
            'follow_up_at'   => 'nullable|date',
        ]);

        $data['owner_id'] = $request->user()->id;
        $data['status'] = 'new';
        $data['rating'] = $data['rating'] ?? 'C';
        $data['estimated_amount'] = $data['estimated_amount'] ?? 0;

        $lead = Lead::create($data);
        return response()->json(['code' => 0, 'data' => $lead->load(['customer', 'owner'])]);
    }

    public function leadsUpdate(Request $request, Lead $lead): JsonResponse
    {
        if ($lead->status === 'converted') {
            return response()->json(['code' => 1, 'message' => '已转商机的线索不可编辑'], 409);
        }

        $data = $request->validate([
            'customer_name'    => 'sometimes|string|max:200',
            'contact_name'     => 'sometimes|string|max:50',
            'contact_phone'    => 'sometimes|string|max:20',
            'contact_title'    => 'nullable|string|max:50',
            'source'           => 'sometimes|string|in:online,phone,exhibition,referral,other',
            'referrer_id'      => 'nullable|integer|exists:referrers,id',
            'requirement'      => 'nullable|string',
            'estimated_amount' => 'nullable|numeric|min:0',
            'rating'           => 'nullable|string|in:A,B,C,D',
            'follow_up_at'     => 'nullable|date',
        ]);

        $lead->update($data);
        return response()->json(['code' => 0, 'data' => $lead->fresh()->load(['customer', 'owner'])]);
    }

    public function leadsDestroy(Lead $lead): JsonResponse
    {
        if (!in_array($lead->status, ['new', 'discarded'])) {
            return response()->json(['code' => 1, 'message' => '只有「新建」或「已丢弃」状态的线索可删除'], 409);
        }
        $lead->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    public function leadsUpdateStatus(Request $request, Lead $lead): JsonResponse
    {
        // v0.5.8 修复：7 段独立成真实状态，不再归一压缩成 5 段
        // 看板 7 段 (new/contacted/qualified/proposal/negotiating/won/lost) 全部独立存进 DB
        // won/lost 仍转成 converted/discarded（业务语义相同），proposal/negotiating 保留为真值
        $request->validate([
            'status' => 'required|string|in:new,contacted,contacting,qualified,proposal,negotiating,won,lost,converted,discarded',
        ]);

        $boardMap = [
            'new'         => 'new',
            'contacted'   => 'contacted',
            'contacting'  => 'contacted',
            'proposal'    => 'proposal',
            'qualified'   => 'qualified',
            'negotiating' => 'negotiating',
            'won'         => 'converted',
            'converted'   => 'converted',
            'lost'        => 'discarded',
            'discarded'   => 'discarded',
        ];

        $new = $boardMap[$request->status];
        // 防御历史脏数据: DB 里 lead.status 可能是任意历史 5 段值
        $current = $boardMap[$lead->status] ?? $lead->status;
        if (!in_array($current, ['new', 'contacted', 'contacting', 'qualified', 'proposal', 'negotiating', 'converted', 'discarded'], true)) {
            return response()->json(['code' => 1, 'message' => "线索状态异常：{$lead->status}，请联系管理员修复"], 409);
        }

        $transitions = [
            'new'         => ['contacted', 'qualified', 'proposal', 'negotiating', 'converted', 'discarded'],
            'contacted'   => ['qualified', 'proposal', 'negotiating', 'converted', 'discarded', 'new'],
            'contacting'  => ['contacted', 'qualified', 'proposal', 'negotiating', 'converted', 'discarded', 'new'],
            'qualified'   => ['proposal', 'negotiating', 'converted', 'discarded', 'new', 'contacted'],
            'proposal'    => ['negotiating', 'qualified', 'converted', 'discarded', 'contacted'],
            'negotiating' => ['qualified', 'proposal', 'converted', 'discarded', 'contacted'],
            'converted'   => [],
            'discarded'   => [],
        ];

        if ($new === $current) {
            return response()->json(['code' => 0, 'data' => $lead->fresh()]);
        }

        if (!in_array($new, $transitions[$current] ?? [], true)) {
            return response()->json(['code' => 1, 'message' => "状态机非法流转：{$current} → {$new}"], 409);
        }

        $lead->update(['status' => $new, 'last_contact_at' => now()]);
        return response()->json(['code' => 0, 'data' => $lead->fresh()]);
    }

    public function leadsConvertToOpp(Request $request, Lead $lead): JsonResponse
    {
        if ($lead->status === 'converted') {
            return response()->json(['code' => 1, 'message' => '该线索已转商机'], 409);
        }
        if ($lead->status === 'discarded') {
            return response()->json(['code' => 1, 'message' => '已丢弃的线索不可转商机'], 409);
        }

        $data = $request->validate([
            'name'             => 'required|string|max:200',
            'estimated_amount' => 'required|numeric|min:0',
            'expected_sign_date' => 'nullable|date',
            'sales_id'         => 'required|integer|exists:users,id',
            'presale_id'       => 'required|integer|exists:users,id',
        ]);

        $opp = DB::transaction(function () use ($lead, $data) {
            $opp = Opportunity::create([
                'name'             => $data['name'],
                'customer_id'      => $lead->customer_id,
                'lead_id'          => $lead->id,
                'type'             => 'comprehensive',
                'estimated_amount' => $data['estimated_amount'],
                'expected_sign_date' => $data['expected_sign_date'] ?? null,
                'stage'            => 'requirement',
                'probability'      => 20,
                'sales_id'         => $data['sales_id'],
                'presale_id'       => $data['presale_id'],
            ]);

            $lead->update(['status' => 'converted']);

            return $opp;
        });

        return response()->json(['code' => 0, 'data' => $opp->load(['customer', 'sales', 'presale'])]);
    }

    // ============================================================
    // === 商机池 (6 个 CRUD 端点) ===
    // ============================================================

    public function oppsIndex(Request $request): JsonResponse
    {
        $query = Opportunity::with(['customer', 'sales', 'presale']);
        $user = $request->user();
        // v0.3.11 P1 块一: 销售员 owner 隔离
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->where(function ($q) use ($user) {
                $q->where('sales_id', $user->id);
                if ($user->department_id) {
                    $q->orWhereIn('sales_id', function ($sub) use ($user) {
                        $sub->select('id')->from('users')->where('department_id', $user->department_id);
                    });
                }
            });
        }
        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        if ($request->filled('stage')) $query->where('stage', $request->stage);
        if ($request->filled('sales_id')) $query->where('sales_id', $request->sales_id);
        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function oppsShow(Opportunity $opp): JsonResponse
    {
        $opp->load(['customer', 'sales', 'presale', 'quotations.items', 'followUps']);
        return response()->json(['code' => 0, 'data' => $opp]);
    }

    public function oppsStageOptions(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => [
            ['value' => 'requirement', 'label' => '需求确认', 'color' => '#0C447C'],
            ['value' => 'solution', 'label' => '方案制定', 'color' => '#534AB7'],
            ['value' => 'negotiation', 'label' => '报价谈判', 'color' => '#BA7517'],
            ['value' => 'contracting', 'label' => '合同拟定', 'color' => '#1D9E75'],
            ['value' => 'won', 'label' => '成交', 'color' => '#1D9E75'],
            ['value' => 'lost', 'label' => '战败', 'color' => '#A32D2D'],
        ]]);
    }

    public function oppsFunnel(Request $request): JsonResponse
    {
        $rows = Opportunity::query()
            ->selectRaw('stage, COUNT(*) as count, COALESCE(SUM(estimated_amount), 0) as total_amount')
            ->groupBy('stage')
            ->get();
        return response()->json(['code' => 0, 'data' => $rows]);
    }

    public function oppsLostReasons(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => [
            ['value' => 'price_high', 'label' => '价格过高'],
            ['value' => 'competitor', 'label' => '客户选了其他家'],
            ['value' => 'budget', 'label' => '客户预算不足'],
            ['value' => 'tech', 'label' => '技术方案不满足'],
            ['value' => 'relation', 'label' => '客户关系不到位'],
            ['value' => 'other', 'label' => '其他原因'],
        ]]);
    }

    public function oppsStore(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'             => 'required|string|max:200',
            'customer_id'      => 'nullable|integer|exists:customers,id',
            'lead_id'          => 'nullable|integer|exists:leads,id',
            'type'             => 'nullable|string|max:50',
            'estimated_amount' => 'required|numeric|min:0',
            'expected_sign_date' => 'nullable|date',
            'sales_id'         => 'required|integer|exists:users,id',
            'presale_id'       => 'required|integer|exists:users,id',
            'competitor'       => 'nullable|string|max:200',
            'notes'            => 'nullable|string',
        ]);

        $opp = Opportunity::create([
            'name'             => $data['name'],
            'customer_id'      => $data['customer_id'] ?? null,
            'lead_id'          => $data['lead_id'] ?? null,
            'type'             => $data['type'] ?? 'comprehensive',
            'estimated_amount' => $data['estimated_amount'],
            'expected_sign_date' => $data['expected_sign_date'] ?? null,
            'stage'            => 'requirement',
            'probability'      => 20,
            'sales_id'         => $data['sales_id'],
            'presale_id'       => $data['presale_id'],
            'competitor'       => $data['competitor'] ?? null,
            'notes'            => $data['notes'] ?? null,
        ]);

        return response()->json(['code' => 0, 'data' => $opp->load(['customer', 'sales', 'presale'])]);
    }

    public function oppsUpdate(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可编辑'], 409);
        }

        $data = $request->validate([
            'name'             => 'sometimes|string|max:200',
            'customer_id'      => 'nullable|integer|exists:customers,id',
            'type'             => 'nullable|string|max:50',
            'estimated_amount' => 'sometimes|numeric|min:0',
            'expected_sign_date' => 'nullable|date',
            'sales_id'         => 'sometimes|integer|exists:users,id',
            'presale_id'       => 'sometimes|integer|exists:users,id',
            'competitor'       => 'nullable|string|max:200',
            'probability'      => 'nullable|integer|min:0|max:100',
            'next_action'      => 'nullable|string',
            'next_action_at'   => 'nullable|date',
            'notes'            => 'nullable|string',
        ]);

        $opp->update($data);
        return response()->json(['code' => 0, 'data' => $opp->fresh()->load(['customer', 'sales', 'presale'])]);
    }

    public function oppsDestroy(Opportunity $opp): JsonResponse
    {
        if (!in_array($opp->stage, ['requirement', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '只有「需求确认」或「战败」状态的商机可删除'], 409);
        }
        $opp->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    public function oppsUpdateStage(Request $request, Opportunity $opp): JsonResponse
    {
        // v0.5.8 修复: 7 段独立成真实 stage, 不再归一压缩成 6 段
        // 看板 7 段 (inquiry/qualification/proposal/negotiating/quoted/won/lost) 全部独立
        // 兼容历史脏数据: DB 可能是老 6 段值
        $oppStageMap = [
            'inquiry'         => 'inquiry',
            'qualification'   => 'qualification',
            'proposal'        => 'proposal',
            'negotiating'     => 'negotiating',
            'quoted'          => 'quoted',
            'won'             => 'won',
            'lost'            => 'lost',
            // 兼容老 6 段值
            'requirement'     => 'inquiry',
            'solution'        => 'qualification',
            'negotiation'     => 'negotiation',  // 老 negotiation 兼容映射
            'contracting'     => 'quoted',
        ];
        $data = $request->validate([
            'stage'        => 'required|string|in:' . implode(',', array_keys($oppStageMap)),
            'probability'  => 'nullable|integer|min:0|max:100',
        ]);

        $new = $oppStageMap[$data['stage']];
        $current = $oppStageMap[$opp->stage] ?? $opp->stage;

        if (in_array($current, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可拖动，请用「成交/战败」按钮'], 409);
        }
        if (in_array($new, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '成交/战败请用专用按钮'], 409);
        }

        // 各阶段默认成交概率 (前端可显式传入 probability 覆盖)
        $stageProb = [
            'inquiry'        => 10,
            'qualification'  => 30,
            'proposal'       => 50,
            'negotiating'    => 70,
            'quoted'         => 85,
        ];

        $update = ['stage' => $new];
        if (!isset($data['probability'])) {
            $update['probability'] = $stageProb[$new] ?? 50;
        } else {
            $update['probability'] = $data['probability'];
        }

        $opp->update($update);
        return response()->json(['code' => 0, 'data' => $opp->fresh()]);
    }

    public function oppsMarkWon(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '商机已终结'], 409);
        }

        $data = $request->validate([
            'contract_amount' => 'required|numeric|min:0',
            'signed_at'       => 'required|date',
            'notes'           => 'nullable|string',
        ]);

        $user = $request->user();
        $result = DB::transaction(function () use ($opp, $data, $user) {
            $pool = ProjectPool::create([
                'pool_no'         => 'POOL-' . date('Ymd') . '-' . str_pad(ProjectPool::whereDate('created_at', today())->count() + 1, 3, '0', STR_PAD_LEFT),
                'opportunity_id'  => $opp->id,
                'name'            => $opp->name,
                'customer_id'     => $opp->customer_id,
                'contract_amount' => $data['contract_amount'],
                'signed_at'       => $data['signed_at'],
                'status'          => 'pending',
            ]);

            $opp->update([
                'stage'        => 'won',
                'probability'  => 100,
                'pool_id'      => $pool->id,
                'notes'        => $data['notes'] ?? $opp->notes,
            ]);

            // v0.3.11 P0 块六：自动建居间费结算单（若 lead.referrer_id 非空）
            // 先查 lead（商机 lead_id），再看 referrer
            $lead = $opp->lead_id ? Lead::find($opp->lead_id) : null;
            if ($lead && $lead->referrer_id) {
                $referrer = Referrer::find($lead->referrer_id);
                if ($referrer) {
                    // 唯一约束保护：同商机同推荐人不重复
                    ReferralSettlement::firstOrCreate(
                        [
                            'opportunity_id' => $opp->id,
                            'referrer_id'    => $referrer->id,
                        ],
                        [
                            'lead_id'         => $lead->id,
                            'amount'          => round($data['contract_amount'] * $referrer->commission_rate / 100, 2),
                            'commission_rate' => $referrer->commission_rate,
                            'contract_amount' => $data['contract_amount'],
                            'status'          => 'pending',
                            'created_by'      => $user?->id,
                            'notes'           => "自动建单 (商机成交, 推荐人: {$referrer->name}, 佣金比例 {$referrer->commission_rate}%)",
                        ]
                    );
                }
            }

            return $pool;
        });

        return response()->json(['code' => 0, 'data' => $result->load('opportunity')]);
    }

    // ============================================================
    // === 推荐人居间费结算 (v0.3.11 P0 块六) ===
    // ============================================================

    /**
     * GET /api/sales/referral-settlements - 结算单列表（分页 + 过滤 + 权限隔离）
     */
    public function referralSettlementsIndex(Request $request): JsonResponse
    {
        $query = ReferralSettlement::with(['opportunity', 'referrer', 'creator', 'approver', 'payer']);

        // 销售只能看自己创建的；财务/管理员可看全部
        $user = $request->user();
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('finance') || $user->hasRole('manager'))) {
            $query->where('created_by', $user->id);
        }

        // 过滤
        if ($request->filled('status')) $query->where('status', $request->status);
        if ($request->filled('referrer_id')) $query->where('referrer_id', $request->referrer_id);
        if ($request->filled('opportunity_id')) $query->where('opportunity_id', $request->opportunity_id);
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('notes', 'like', "%{$kw}%")
                  ->orWhere('payment_no', 'like', "%{$kw}%")
                  ->orWhereHas('referrer', fn($q2) => $q2->where('name', 'like', "%{$kw}%"));
            });
        }

        $perPage = min((int) $request->input('per_page', 20), 100);
        $page = $query->orderByDesc('id')->paginate($perPage);

        return response()->json(['code' => 0, 'data' => $page]);
    }

    /**
     * GET /api/sales/referral-settlements/{settlement} - 详情
     */
    public function referralSettlementsShow(ReferralSettlement $settlement): JsonResponse
    {
        $settlement->load(['opportunity.customer', 'referrer', 'lead', 'creator', 'approver', 'payer']);
        return response()->json(['code' => 0, 'data' => $settlement]);
    }

    /**
     * POST /api/sales/referral-settlements/{settlement}/approve - 财务审核 (pending → approved)
     */
    public function referralSettlementsApprove(Request $request, ReferralSettlement $settlement): JsonResponse
    {
        $user = $request->user();
        // v0.3.14 D1: 审核权限细分 — sales_manager + finance + admin
        $userRoles = method_exists($user, 'getRoleNames') ? $user->getRoleNames()->toArray() : [];
        $allowed = array_intersect($userRoles, ['admin', 'sales_manager', 'finance', 'manager']);
        if (empty($allowed)) {
            return response()->json(['code' => 403, 'message' => '仅销售经理/财务可审核'], 403);
        }

        if ($settlement->status !== 'pending') {
            return response()->json(['code' => 1, 'message' => "仅 pending 状态可审核，当前 status={$settlement->status}"], 409);
        }

        $settlement->update([
            'status'      => 'approved',
            'approved_by' => $user->id,
            'approved_at' => now(),
        ]);

        return response()->json(['code' => 0, 'data' => $settlement->fresh()]);
    }

    /**
     * POST /api/sales/referral-settlements/{settlement}/pay - 财务发放 (approved → paid)
     * v0.3.14 D1: 发放权限细分 — 仅 finance + admin（不含 sales_manager）
     */
    public function referralSettlementsPay(Request $request, ReferralSettlement $settlement): JsonResponse
    {
        $user = $request->user();
        $userRoles = method_exists($user, 'getRoleNames') ? $user->getRoleNames()->toArray() : [];
        $allowed = array_intersect($userRoles, ['admin', 'finance']);
        if (empty($allowed)) {
            return response()->json(['code' => 403, 'message' => '仅财务可发放结算款（销售经理无发放权）'], 403);
        }

        if ($settlement->status !== 'approved') {
            return response()->json(['code' => 1, 'message' => "仅 approved 状态可发放，当前 status={$settlement->status}"], 409);
        }

        $data = $request->validate([
            'payment_no'      => 'required|string|max:100',
            'payment_voucher' => 'nullable|string|max:500',
        ]);

        DB::transaction(function () use ($settlement, $data, $user) {
            $settlement->update([
                'status'          => 'paid',
                'paid_by'         => $user->id,
                'paid_at'         => now(),
                'payment_no'      => $data['payment_no'],
                'payment_voucher' => $data['payment_voucher'] ?? null,
            ]);

            // 累加到推荐人 total_commission
            if ($settlement->referrer) {
                $settlement->referrer->increment('total_commission', (float) $settlement->amount);
            }
        });

        return response()->json(['code' => 0, 'data' => $settlement->fresh('payer')]);
    }

    /**
     * GET /api/sales/referral-settlements/stats - 统计（待审核/待发放/已发放 计数）
     */
    public function referralSettlementsStats(Request $request): JsonResponse
    {
        $user = $request->user();
        $query = ReferralSettlement::query();
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('finance') || $user->hasRole('manager'))) {
            $query->where('created_by', $user->id);
        }
        $stats = [
            'pending'  => (clone $query)->where('status', 'pending')->count(),
            'approved' => (clone $query)->where('status', 'approved')->count(),
            'paid'     => (clone $query)->where('status', 'paid')->count(),
            'total_amount_pending'  => (clone $query)->where('status', 'pending')->sum('amount'),
            'total_amount_approved' => (clone $query)->where('status', 'approved')->sum('amount'),
            'total_amount_paid'     => (clone $query)->where('status', 'paid')->sum('amount'),
        ];
        return response()->json(['code' => 0, 'data' => $stats]);
    }

    public function oppsMarkLost(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '商机已终结'], 409);
        }

        $data = $request->validate([
            'lost_reason' => 'required|string|in:price_high,competitor,budget,tech,relation,other',
            'notes'       => 'nullable|string',
        ]);

        $opp->update([
            'stage'       => 'lost',
            'probability' => 0,
            'lost_reason' => $data['lost_reason'],
            'notes'       => $data['notes'] ?? $opp->notes,
        ]);

        return response()->json(['code' => 0, 'data' => $opp->fresh()]);
    }

    /**
     * POST /api/sales/opps/{id}/revive - 战败复活（仅 sales_manager 可操作）
     * PRD 4.2.2 验收: 战败的商机由销售经理可复活到「需求确认」阶段
     * 状态: lost → requirement (回到商机池最前阶段)
     */
    public function oppsRevive(Request $request, Opportunity $opp): JsonResponse
    {
        $user = $request->user();
        // 仅销售经理 / 总经理 / 管理员可复活
        if (method_exists($user, 'hasRole') &&
            !($user->hasRole('sales_manager') || $user->hasRole('manager') || $user->hasRole('admin'))) {
            return response()->json([
                'code'    => 403,
                'message' => '仅销售经理/总经理可复活战败商机',
            ], 403);
        }

        if ($opp->stage !== 'lost') {
            return response()->json([
                'code'    => 1,
                'message' => "仅战败(lost)的商机可复活，当前 stage={$opp->stage}",
            ], 409);
        }

        $opp->update([
            'stage'       => 'requirement',
            'probability' => 20,
            'lost_reason' => null,
            'notes'       => ($opp->notes ? $opp->notes . "\n" : '') . '[复活 ' . now()->toDateTimeString() . ' by ' . ($user->name ?? $user->username ?? 'mgr') . ']',
        ]);

        return response()->json(['code' => 0, 'data' => $opp->fresh()]);
    }

    // ============================================================
    // === 报价单 (7 个 CRUD 端点) ===
    // ============================================================

    public function quotesIndex(Request $request): JsonResponse
    {
        $query = Quotation::with(['opportunity.customer', 'items']);
        $user = $request->user();
        // v0.3.11 P1 块一: 报价单 owner 隔离 (通过 created_by 字段)
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->where(function ($q) use ($user) {
                $q->where('created_by', $user->id);
                if ($user->department_id) {
                    $q->orWhereIn('created_by', function ($sub) use ($user) {
                        $sub->select('id')->from('users')->where('department_id', $user->department_id);
                    });
                }
            });
        }
        if ($request->filled('opportunity_id')) $query->where('opportunity_id', $request->opportunity_id);
        if ($request->filled('status')) $query->where('status', $request->status);
        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function quotesShow(Quotation $quote): JsonResponse
    {
        $quote->load(['opportunity.customer', 'items.inventoryItem']);
        return response()->json(['code' => 0, 'data' => $quote]);
    }

    public function quotesStatusOptions(): JsonResponse
    {
        return response()->json(['code' => 0, 'data' => [
            ['value' => 'draft', 'label' => '草稿', 'color' => '#909399'],
            ['value' => 'submitted', 'label' => '已提交', 'color' => '#534AB7'],
            ['value' => 'negotiating', 'label' => '谈判中', 'color' => '#BA7517'],
            ['value' => 'accepted', 'label' => '客户接受', 'color' => '#1D9E75'],
            ['value' => 'rejected', 'label' => '客户拒绝', 'color' => '#A32D2D'],
            ['value' => 'expired', 'label' => '已过期', 'color' => '#909399'],
        ]]);
    }

    public function quotesStore(Request $request): JsonResponse
    {
        $user = $request->user();
        $isManager = method_exists($user, 'hasRole') ? $user->hasRole('manager') : false;
        $maxDiscount = $isManager ? 50 : 30;

        $data = $request->validate([
            'opportunity_id'  => 'required|integer|exists:opportunities,id',
            'discount_rate'   => "nullable|numeric|min:0|max:{$maxDiscount}",
            'tax_rate'        => 'nullable|numeric|in:0,3,6,9,13',
            'valid_until'     => 'nullable|date',
            'notes'           => 'nullable|string|max:500',
        ]);

        $data['created_by'] = $request->user()->id;
        $data['version'] = 1;
        $data['status'] = 'draft';
        $data['discount_rate'] = $data['discount_rate'] ?? 0;
        $data['tax_rate'] = $data['tax_rate'] ?? 13;
        $data['subtotal'] = 0;
        $data['discount_amount'] = 0;
        $data['tax_amount'] = 0;
        $data['total_amount'] = 0;
        $data['valid_until'] = $data['valid_until'] ?? now()->addDays(30)->toDateString();

        $quote = Quotation::create($data);

        return response()->json(['code' => 0, 'data' => $quote->load('opportunity.customer')]);
    }

    public function quotesUpdate(Request $request, Quotation $quote): JsonResponse
    {
        if ($quote->status !== 'draft') {
            return response()->json(['code' => 1, 'message' => '只有草稿状态可编辑基础信息'], 409);
        }

        $user = $request->user();
        $isManager = method_exists($user, 'hasRole') ? $user->hasRole('manager') : false;
        $maxDiscount = $isManager ? 50 : 30;

        $data = $request->validate([
            'discount_rate'   => "nullable|numeric|min:0|max:{$maxDiscount}",
            'tax_rate'        => 'nullable|numeric|in:0,3,6,9,13',
            'valid_until'     => 'nullable|date',
            'notes'           => 'nullable|string|max:500',
        ]);

        $quote->update($data);
        $this->recalcQuotation($quote);
        return response()->json(['code' => 0, 'data' => $quote->fresh()->load(['opportunity.customer', 'items.inventoryItem'])]);
    }

    public function quotesDestroy(Quotation $quote): JsonResponse
    {
        if ($quote->status !== 'draft') {
            return response()->json(['code' => 1, 'message' => '只有草稿状态可删除'], 409);
        }
        $quote->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    public function quotesStoreItems(Request $request, Quotation $quote): JsonResponse
    {
        if (!in_array($quote->status, ['draft', 'rejected'])) {
            return response()->json(['code' => 1, 'message' => '当前状态不可编辑产品清单'], 409);
        }

        $data = $request->validate([
            'items'                          => 'required|array|min:1',
            'items.*.inventory_item_id'      => 'nullable|integer|exists:inventory_items,id',
            'items.*.product_id'             => 'nullable|integer|exists:sales_products,id', // v0.3.11 块四: 销售产品库关联
            'items.*.code'                   => 'nullable|string|max:64',
            'items.*.name'                   => 'required|string|max:200',
            'items.*.specification'          => 'nullable|string|max:200',
            'items.*.unit'                   => 'nullable|string|max:20',
            'items.*.quantity'               => 'required|numeric|min:0',
            'items.*.unit_price'             => 'required|numeric|min:0',
            'items.*.remark'                 => 'nullable|string',
            // 顶部设置 (v0.3.11 块四: 前端可调折扣/税率/有效期)
            'discount_rate'                  => 'nullable|numeric|min:0|max:30',
            'tax_rate'                       => 'nullable|numeric|in:0,3,6,9,13',
            'valid_until'                    => 'nullable|date',
        ]);

        $items = $data['items'];
        $invIds = array_filter(array_column($items, 'inventory_item_id'));
        $productIds = array_filter(array_column($items, 'product_id'));
        // 唯一性检查
        if (count($invIds) !== count(array_unique($invIds))) {
            return response()->json(['code' => 1, 'message' => '同一库存物资不可重复添加'], 422);
        }
        if (count($productIds) !== count(array_unique($productIds))) {
            return response()->json(['code' => 1, 'message' => '同一销售产品不可重复添加'], 422);
        }

        DB::transaction(function () use ($quote, $items, $data) {
            QuotationItem::where('quotation_id', $quote->id)->delete();
            foreach ($items as $it) {
                $total = round(($it['quantity'] ?? 0) * ($it['unit_price'] ?? 0), 2);
                QuotationItem::create([
                    'quotation_id'      => $quote->id,
                    'inventory_item_id' => $it['inventory_item_id'] ?? null,
                    'product_id'        => $it['product_id'] ?? null,
                    'code'              => $it['code'] ?? null,
                    'name'              => $it['name'],
                    'specification'     => $it['specification'] ?? null,
                    'unit'              => $it['unit'] ?? '件',
                    'quantity'          => $it['quantity'],
                    'unit_price'        => $it['unit_price'],
                    'total_price'       => $total,
                    'remark'            => $it['remark'] ?? null,
                ]);
            }
            // 顶部设置 (v0.3.11 块四)
            $quoteUpdate = [];
            if (isset($data['discount_rate'])) $quoteUpdate['discount_rate'] = $data['discount_rate'];
            if (isset($data['tax_rate']))      $quoteUpdate['tax_rate'] = $data['tax_rate'];
            if (isset($data['valid_until']))   $quoteUpdate['valid_until'] = $data['valid_until'];
            if ($quoteUpdate) $quote->update($quoteUpdate);
            $this->recalcQuotation($quote);
        });

        return response()->json(['code' => 0, 'data' => $quote->fresh()->load(['opportunity.customer', 'items.inventoryItem'])]);
    }

    public function quotesUpdateStatus(Request $request, Quotation $quote): JsonResponse
    {
        $data = $request->validate([
            'status' => 'required|string|in:draft,submitted,negotiating,accepted,rejected,expired',
            'notes'  => 'nullable|string|max:500',
        ]);

        $new = $data['status'];
        $current = $quote->status;

        $transitions = [
            'draft'       => ['submitted'],
            'submitted'   => ['negotiating', 'accepted', 'rejected', 'expired'],
            'negotiating' => ['accepted', 'rejected', 'submitted', 'expired'],
            'accepted'    => [],
            'rejected'    => ['draft'],
            'expired'     => ['draft'],
        ];

        if (!in_array($new, $transitions[$current] ?? [])) {
            return response()->json(['code' => 1, 'message' => "状态机非法流转：{$current} → {$new}"], 409);
        }

        $update = ['status' => $new];
        if ($new === 'submitted') $update['sent_at'] = now();
        if (in_array($new, ['accepted', 'rejected'])) $update['responded_at'] = now();
        if (isset($data['notes'])) $update['notes'] = $data['notes'];

        DB::transaction(function () use ($quote, $update, $new) {
            $quote->update($update);

            if ($new === 'accepted') {
                Quotation::where('opportunity_id', $quote->opportunity_id)
                    ->where('id', '!=', $quote->id)
                    ->where('status', '!=', 'rejected')
                    ->update(['status' => 'rejected', 'responded_at' => now()]);

                Opportunity::where('id', $quote->opportunity_id)->update([
                    'stage'       => 'contracting',
                    'probability' => 80,
                ]);
            }
        });

        return response()->json(['code' => 0, 'data' => $quote->fresh()->load(['opportunity.customer', 'items.inventoryItem'])]);
    }

    public function quotesNewVersion(Quotation $quote): JsonResponse
    {
        $new = DB::transaction(function () use ($quote) {
            $maxVersion = (int) Quotation::where('opportunity_id', $quote->opportunity_id)->max('version');
            $newQuote = Quotation::create([
                'opportunity_id'   => $quote->opportunity_id,
                'version'          => $maxVersion + 1,
                'subtotal'         => $quote->subtotal,
                'discount_rate'    => $quote->discount_rate,
                'discount_amount'  => $quote->discount_amount,
                'tax_rate'         => $quote->tax_rate,
                'tax_amount'       => $quote->tax_amount,
                'total_amount'     => $quote->total_amount,
                'valid_until'      => now()->addDays(30)->toDateString(),
                'status'           => 'draft',
                'notes'            => $quote->notes,
                'created_by'       => $quote->created_by,
            ]);
            $newQuote->quote_no = 'QT-' . date('Ymd') . '-' . str_pad($newQuote->id, 4, '0', STR_PAD_LEFT);
            $newQuote->save();

            foreach ($quote->items as $it) {
                QuotationItem::create([
                    'quotation_id'      => $newQuote->id,
                    'inventory_item_id' => $it->inventory_item_id,
                    'name'              => $it->name,
                    'specification'     => $it->specification,
                    'unit'              => $it->unit,
                    'quantity'          => $it->quantity,
                    'unit_price'        => $it->unit_price,
                    'total_price'       => $it->total_price,
                    'remark'            => $it->remark,
                ]);
            }

            return $newQuote;
        });

        return response()->json(['code' => 0, 'data' => $new->load(['opportunity.customer', 'items.inventoryItem'])]);
    }

    /**
     * 重算报价单 subtotal/discount/tax/total
     */
    private function recalcQuotation(Quotation $quote): void
    {
        $subtotal = (float) QuotationItem::where('quotation_id', $quote->id)->sum('total_price');
        $subtotal = round($subtotal, 2);

        $discountRate = (float) ($quote->discount_rate ?? 0);
        $discountAmount = round($subtotal * $discountRate / 100, 2);
        $afterDiscount = $subtotal - $discountAmount;

        $taxRate = (float) ($quote->tax_rate ?? 0);
        $taxAmount = round($afterDiscount * $taxRate / 100, 2);
        $total = round($afterDiscount + $taxAmount, 2);

        $quote->update([
            'subtotal'        => $subtotal,
            'discount_amount' => $discountAmount,
            'tax_amount'      => $taxAmount,
            'total_amount'    => $total,
        ]);
    }

    // ============================================================
    // === 推荐人 (3 个 CRUD 端点 + 1 个 GET 详情) ===
    // ============================================================

    public function referrersIndex(Request $request): JsonResponse
    {
        $query = Referrer::with('customer');
        $user = $request->user();
        // v0.3.11 P1 块一: 推荐人 owner 隔离
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->where('owner_id', $user->id);
        }
        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function referrersShow(Referrer $referrer): JsonResponse
    {
        $referrer->load('customer');
        return response()->json(['code' => 0, 'data' => $referrer]);
    }

    public function referrersStore(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'            => 'required|string|max:50',
            'phone'           => 'nullable|string|max:20',
            'customer_id'     => 'nullable|integer|exists:customers,id',
            'bank_name'       => 'nullable|string|max:50',
            'bank_account'    => 'nullable|string|max:50',
            'commission_rate' => 'required|numeric|min:1|max:30',
            'notes'           => 'nullable|string',
        ]);

        $referrer = Referrer::create($data);
        return response()->json(['code' => 0, 'data' => $referrer->load('customer')]);
    }

    public function referrersUpdate(Request $request, Referrer $referrer): JsonResponse
    {
        $data = $request->validate([
            'name'            => 'sometimes|string|max:50',
            'phone'           => 'nullable|string|max:20',
            'customer_id'     => 'nullable|integer|exists:customers,id',
            'bank_name'       => 'nullable|string|max:50',
            'bank_account'    => 'nullable|string|max:50',
            'commission_rate' => 'sometimes|numeric|min:1|max:30',
            'notes'           => 'nullable|string',
        ]);

        $referrer->update($data);
        return response()->json(['code' => 0, 'data' => $referrer->fresh()->load('customer')]);
    }

    public function referrersDestroy(Referrer $referrer): JsonResponse
    {
        $exists = Lead::where('referrer_id', $referrer->id)->exists();
        if ($exists) {
            return response()->json(['code' => 1, 'message' => '该推荐人已被线索引用，不可删除'], 409);
        }
        $referrer->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    // ============================================================
    // === 项目池 (2 个端点 — 1 个 PUT 改 + 1 个 POST 转施工项目) ===
    // ============================================================

    public function poolIndex(Request $request): JsonResponse
    {
        $query = ProjectPool::with(['customer', 'opportunity', 'project']);
        $user = $request->user();
        // v0.3.11 P1 块一: 项目池通过关联的 opportunity 隔离
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->whereHas('opportunity', function ($q) use ($user) {
                $q->where('sales_id', $user->id);
                if ($user->department_id) {
                    $q->orWhereIn('sales_id', function ($sub) use ($user) {
                        $sub->select('id')->from('users')->where('department_id', $user->department_id);
                    });
                }
            });
        }
        if ($request->filled('keyword')) $query->where('name', 'like', "%{$request->keyword}%");
        if ($request->filled('status')) $query->where('status', $request->status);
        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function poolShow(ProjectPool $pool): JsonResponse
    {
        $pool->load(['customer', 'opportunity.sales', 'opportunity.presale', 'project']);
        return response()->json(['code' => 0, 'data' => $pool]);
    }

    public function poolUpdate(Request $request, ProjectPool $pool): JsonResponse
    {
        if ($pool->status === 'active') {
            return response()->json(['code' => 1, 'message' => '已转为施工项目的项目池不可编辑'], 409);
        }

        $data = $request->validate([
            'name'            => 'sometimes|string|max:200',
            'contract_amount' => 'sometimes|numeric|min:0',
            'signed_at'       => 'nullable|date',
            'notes'           => 'nullable|string',
        ]);

        $pool->update($data);
        return response()->json(['code' => 0, 'data' => $pool->fresh()->load(['customer', 'opportunity', 'project'])]);
    }

    public function poolConvertToProject(Request $request, ProjectPool $pool): JsonResponse
    {
        if ($pool->status !== 'pending') {
            return response()->json(['code' => 1, 'message' => '只有 pending 状态的项目池可转施工项目'], 409);
        }

        $data = $request->validate([
            'name'        => 'required|string|max:200',
            'manager_id'  => 'required|integer|exists:users,id',
            'start_date'  => 'required|date',
            'end_date'    => 'nullable|date|after_or_equal:start_date',
            'budget'      => 'required|numeric|min:0',
        ]);

        $project = DB::transaction(function () use ($pool, $data) {
            // projects.customer_id 实际是 users.id（schema 历史遗留，FK 到 users 表）
            // 若 pool.customer_id 为空，回退到 manager_id
            $projectCustomerId = $pool->customer_id ?? $data['manager_id'];
            $project = Project::create([
                'name'             => $data['name'],
                'customer_id'      => $projectCustomerId,
                'type'             => 'comprehensive',
                'stage'            => 'contract',
                'status'           => 'in_progress',
                'manager_id'       => $data['manager_id'],
                'start_date'       => $data['start_date'],
                'end_date'         => $data['end_date'] ?? null,
                'priority'         => 'medium',
                'budget_device'    => 0,
                'budget_material'  => 0,
                'budget_labor'     => 0,
                'budget_outsource' => 0,
                'budget_other'     => $data['budget'],
                'progress'         => 0,
            ]);

            $pool->update([
                'related_project_id' => $project->id,
                'status'             => 'active',
            ]);

            if ($pool->opportunity) {
                $pool->opportunity->update([
                    'project_id' => $project->id,
                    'pool_id'    => $pool->id,
                ]);
            }

            return $project;
        });

        return response()->json(['code' => 0, 'data' => $project->load('customer')]);
    }

    // ============================================================
    // === 跟进记录 + 附件 (5+1 端点) ===
    // ============================================================

    public function followUpsIndex(Request $request): JsonResponse
    {
        $query = SalesFollowUp::with(['user', 'attachments']);
        $user = $request->user();
        // v0.3.11 P1 块一: 跟进 owner 隔离
        if ($user && method_exists($user, 'hasRole') &&
            !($user->hasRole('admin') || $user->hasRole('manager'))) {
            $query->where('user_id', $user->id);
        }
        if ($request->filled('target_type')) $query->where('target_type', $request->target_type);
        if ($request->filled('target_id')) $query->where('target_id', $request->target_id);
        $perPage = (int) ($request->per_page ?? 20);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function followUpsShow(SalesFollowUp $followUp): JsonResponse
    {
        $followUp->load(['user', 'attachments']);
        return response()->json(['code' => 0, 'data' => $followUp]);
    }

    public function followUpsStore(Request $request): JsonResponse
    {
        $data = $request->validate([
            'target_type'    => 'required|string|in:lead,opp,quote',
            'target_id'      => 'required|integer',
            'contact_method' => 'nullable|string|in:phone,wechat,visit,email,other',
            'content'        => 'required|string',
            'result'         => 'nullable|string',
            'next_action'    => 'nullable|string',
            'next_action_at' => 'nullable|date',
        ]);

        $data['user_id'] = $request->user()->id;

        $followUp = DB::transaction(function () use ($data) {
            $f = SalesFollowUp::create($data);

            if ($data['target_type'] === 'lead') {
                Lead::where('id', $data['target_id'])->update(['last_contact_at' => now()]);
            } elseif ($data['target_type'] === 'opp') {
                Opportunity::where('id', $data['target_id'])->update([
                    'last_contact_at' => now(),
                    'next_action'     => $data['next_action'] ?? null,
                    'next_action_at'  => $data['next_action_at'] ?? null,
                ]);
            }

            return $f;
        });

        return response()->json(['code' => 0, 'data' => $followUp->load(['user', 'attachments'])]);
    }

    public function followUpsUpdate(Request $request, SalesFollowUp $followUp): JsonResponse
    {
        $data = $request->validate([
            'contact_method' => 'nullable|string|in:phone,wechat,visit,email,other',
            'content'        => 'sometimes|string',
            'result'         => 'nullable|string',
            'next_action'    => 'nullable|string',
            'next_action_at' => 'nullable|date',
        ]);

        $followUp->update($data);
        return response()->json(['code' => 0, 'data' => $followUp->fresh()->load(['user', 'attachments'])]);
    }

    public function followUpsDestroy(SalesFollowUp $followUp): JsonResponse
    {
        $followUp->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    public function followUpsUploadAttachment(Request $request, SalesFollowUp $followUp): JsonResponse
    {
        $request->validate([
            'file' => 'required|file|max:20480',  // 20MB
        ]);

        $file = $request->file('file');
        $ext = strtolower($file->getClientOriginalExtension());
        $allowedExt = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md'];
        if (!in_array($ext, $allowedExt, true)) {
            throw ValidationException::withMessages(['file' => "文件类型 .{$ext} 不支持"]);
        }

        $realMime = $file->getMimeType();
        $allowedMime = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain', 'text/markdown', 'application/zip'];
        if (!in_array($realMime, $allowedMime, true)) {
            throw ValidationException::withMessages(['file' => "文件 MIME 类型不被允许: {$realMime}"]);
        }

        $count = $followUp->attachments()->count();
        if ($count >= 20) {
            return response()->json(['code' => 1, 'message' => '单条跟进最多 20 个附件'], 422);
        }
        $totalSize = (int) $followUp->attachments()->sum('size') + $file->getSize();
        if ($totalSize > 50 * 1024 * 1024) {
            return response()->json(['code' => 1, 'message' => '单条跟进附件总大小不能超过 50MB'], 422);
        }

        $path = $file->storeAs('sales/follow-up/' . $followUp->id . '/' . date('Y/m'), Str::uuid() . '.' . $ext, 'public');

        $att = SalesFollowUpAttachment::create([
            'follow_up_id' => $followUp->id,
            'name'         => $file->getClientOriginalName(),
            'path'         => $path,
            'mime'         => $realMime,
            'size'         => $file->getSize(),
        ]);

        return response()->json(['code' => 0, 'data' => $att]);
    }

    public function followUpsDownloadAttachment(SalesFollowUpAttachment $att)
    {
        if (!Storage::disk('public')->exists($att->path)) {
            return response()->json(['code' => 1, 'message' => '文件不存在'], 404);
        }
        return Storage::disk('public')->download($att->path, $att->name);
    }

    public function followUpsDeleteAttachment(SalesFollowUpAttachment $att): JsonResponse
    {
        DB::transaction(function () use ($att) {
            $path = $att->path;
            $att->delete();
            if ($path && Storage::disk('public')->exists($path)) {
                Storage::disk('public')->delete($path);
            }
        });
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    // ============================================================
    // === 商机下报价单 (子操作,opps/{id}/quotations) ===
    // ============================================================

    /**
     * GET /api/sales/opps/{id}/quotations
     * 某商机下的所有报价单(包含 items)
     */
    public function oppsQuotationsIndex(Opportunity $opp): JsonResponse
    {
        $quotes = Quotation::with(['items.inventoryItem'])
            ->where('opportunity_id', $opp->id)
            ->orderBy('version', 'desc')
            ->orderBy('created_at', 'desc')
            ->get();

        return response()->json(['code' => 0, 'data' => $quotes]);
    }

    /**
     * POST /api/sales/opps/{id}/quotations
     * 为商机创建报价单(可同时提交 items)
     * items 不传则只建空壳,后续走 sales/quotes/{id}/items
     */
    public function oppsQuotationsStore(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可报价'], 409);
        }

        $user = $request->user();
        $isManager = method_exists($user, 'hasRole') ? $user->hasRole('manager') : false;
        $maxDiscount = $isManager ? 50 : 30;

        $data = $request->validate([
            'discount_rate'              => "nullable|numeric|min:0|max:{$maxDiscount}",
            'tax_rate'                   => 'nullable|numeric|in:0,3,6,9,13',
            'valid_until'                => 'nullable|date',
            'notes'                      => 'nullable|string|max:500',
            'items'                      => 'nullable|array',
            'items.*.inventory_item_id'  => 'nullable|integer|exists:inventory_items,id',
            'items.*.name'               => 'required_with:items|string|max:200',
            'items.*.specification'      => 'nullable|string|max:200',
            'items.*.unit'               => 'nullable|string|max:20',
            'items.*.quantity'           => 'required_with:items|numeric|min:0',
            'items.*.unit_price'         => 'required_with:items|numeric|min:0',
            'items.*.remark'             => 'nullable|string',
        ]);

        $quote = DB::transaction(function () use ($opp, $data, $request) {
            $quote = Quotation::create([
                'opportunity_id'  => $opp->id,
                'version'         => 1,
                'subtotal'        => 0,
                'discount_rate'   => $data['discount_rate'] ?? 0,
                'discount_amount' => 0,
                'tax_rate'        => $data['tax_rate'] ?? 13,
                'tax_amount'      => 0,
                'total_amount'    => 0,
                'valid_until'     => $data['valid_until'] ?? now()->addDays(30)->toDateString(),
                'status'          => 'draft',
                'notes'           => $data['notes'] ?? null,
                'created_by'      => $request->user()->id,
            ]);

            if (!empty($data['items'])) {
                $invIds = array_filter(array_column($data['items'], 'inventory_item_id'));
                if (count($invIds) !== count(array_unique($invIds))) {
                    throw ValidationException::withMessages(['items' => '同一产品不可重复添加']);
                }
                foreach ($data['items'] as $it) {
                    $total = round(($it['quantity'] ?? 0) * ($it['unit_price'] ?? 0), 2);
                    QuotationItem::create([
                        'quotation_id'      => $quote->id,
                        'inventory_item_id' => $it['inventory_item_id'] ?? null,
                        'name'              => $it['name'],
                        'specification'     => $it['specification'] ?? null,
                        'unit'              => $it['unit'] ?? '件',
                        'quantity'          => $it['quantity'],
                        'unit_price'        => $it['unit_price'],
                        'total_price'       => $total,
                        'remark'            => $it['remark'] ?? null,
                    ]);
                }
                $this->recalcQuotation($quote);
            }

            return $quote;
        });

        return response()->json([
            'code' => 0,
            'data' => $quote->fresh()->load(['items.inventoryItem']),
        ]);
    }

    /**
     * GET /api/sales/quotations/{id} - 报价单详情
     */
    public function quotationsShow(Quotation $quotation): JsonResponse
    {
        $quotation->load(['opportunity.customer', 'items.inventoryItem']);
        return response()->json(['code' => 0, 'data' => $quotation]);
    }

    /**
     * PUT /api/sales/quotations/{id} - 修改报价单(基础信息 + items)
     */
    public function quotationsUpdate(Request $request, Quotation $quotation): JsonResponse
    {
        if ($quotation->status !== 'draft') {
            return response()->json(['code' => 1, 'message' => '只有草稿状态可编辑基础信息'], 409);
        }

        $user = $request->user();
        $isManager = method_exists($user, 'hasRole') ? $user->hasRole('manager') : false;
        $maxDiscount = $isManager ? 50 : 30;

        $data = $request->validate([
            'discount_rate'              => "nullable|numeric|min:0|max:{$maxDiscount}",
            'tax_rate'                   => 'nullable|numeric|in:0,3,6,9,13',
            'valid_until'                => 'nullable|date',
            'notes'                      => 'nullable|string|max:500',
            'items'                      => 'sometimes|array',
            'items.*.inventory_item_id'  => 'nullable|integer|exists:inventory_items,id',
            'items.*.name'               => 'required_with:items|string|max:200',
            'items.*.specification'      => 'nullable|string|max:200',
            'items.*.unit'               => 'nullable|string|max:20',
            'items.*.quantity'           => 'required_with:items|numeric|min:0',
            'items.*.unit_price'         => 'required_with:items|numeric|min:0',
            'items.*.remark'             => 'nullable|string',
        ]);

        DB::transaction(function () use ($quotation, $data) {
            $update = array_intersect_key($data, array_flip(['discount_rate', 'tax_rate', 'valid_until', 'notes']));
            if (!empty($update)) $quotation->update($update);

            if (array_key_exists('items', $data)) {
                $items = $data['items'];
                $invIds = array_filter(array_column($items, 'inventory_item_id'));
                if (count($invIds) !== count(array_unique($invIds))) {
                    throw ValidationException::withMessages(['items' => '同一产品不可重复添加']);
                }
                QuotationItem::where('quotation_id', $quotation->id)->delete();
                foreach ($items as $it) {
                    $total = round(($it['quantity'] ?? 0) * ($it['unit_price'] ?? 0), 2);
                    QuotationItem::create([
                        'quotation_id'      => $quotation->id,
                        'inventory_item_id' => $it['inventory_item_id'] ?? null,
                        'name'              => $it['name'],
                        'specification'     => $it['specification'] ?? null,
                        'unit'              => $it['unit'] ?? '件',
                        'quantity'          => $it['quantity'],
                        'unit_price'        => $it['unit_price'],
                        'total_price'       => $total,
                        'remark'            => $it['remark'] ?? null,
                    ]);
                }
            }
            $this->recalcQuotation($quotation);
        });

        return response()->json([
            'code' => 0,
            'data' => $quotation->fresh()->load(['items.inventoryItem', 'opportunity.customer']),
        ]);
    }

    /**
     * DELETE /api/sales/quotations/{id}
     */
    public function quotationsDestroy(Quotation $quotation): JsonResponse
    {
        if ($quotation->status !== 'draft') {
            return response()->json(['code' => 1, 'message' => '只有草稿状态可删除'], 409);
        }
        $quotation->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    /**
     * POST /api/sales/quotations/{id}/accept - 客户接受
     */
    public function quotationsAccept(Quotation $quotation): JsonResponse
    {
        if ($quotation->status === 'accepted') {
            return response()->json(['code' => 0, 'data' => $quotation->fresh()]);
        }
        if (!in_array($quotation->status, ['submitted', 'negotiating'])) {
            return response()->json(['code' => 1, 'message' => '只有「已提交/谈判中」状态的报价可接受'], 409);
        }

        DB::transaction(function () use ($quotation) {
            // 同商机下其它非拒绝的报价单一并置为 rejected
            Quotation::where('opportunity_id', $quotation->opportunity_id)
                ->where('id', '!=', $quotation->id)
                ->where('status', '!=', 'rejected')
                ->update(['status' => 'rejected', 'responded_at' => now()]);

            $quotation->update([
                'status'       => 'accepted',
                'responded_at' => now(),
            ]);

            Opportunity::where('id', $quotation->opportunity_id)->update([
                'stage'       => 'contracting',
                'probability' => 80,
            ]);
        });

        return response()->json([
            'code' => 0,
            'data' => $quotation->fresh()->load(['items.inventoryItem', 'opportunity.customer']),
        ]);
    }

    /**
     * POST /api/sales/quotations/{id}/reject - 客户拒绝
     */
    public function quotationsReject(Request $request, Quotation $quotation): JsonResponse
    {
        if ($quotation->status === 'rejected') {
            return response()->json(['code' => 0, 'data' => $quotation->fresh()]);
        }
        if (!in_array($quotation->status, ['submitted', 'negotiating'])) {
            return response()->json(['code' => 1, 'message' => '只有「已提交/谈判中」状态的报价可拒绝'], 409);
        }

        $data = $request->validate([
            'reason' => 'nullable|string|max:500',
        ]);

        $quotation->update([
            'status'       => 'rejected',
            'responded_at' => now(),
            'notes'        => isset($data['reason']) ? ($quotation->notes ? $quotation->notes . "\n[客户拒绝] " . $data['reason'] : "[客户拒绝] " . $data['reason']) : $quotation->notes,
        ]);

        return response()->json([
            'code' => 0,
            'data' => $quotation->fresh()->load(['items.inventoryItem', 'opportunity.customer']),
        ]);
    }

    /**
     * POST /api/sales/quotations/{id}/revise - 客户要求修改(自动克隆新版本为草稿)
     */
    public function quotationsRevise(Request $request, Quotation $quotation): JsonResponse
    {
        if (!in_array($quotation->status, ['submitted', 'negotiating', 'rejected'])) {
            return response()->json(['code' => 1, 'message' => '当前状态不可发起修改'], 409);
        }

        $data = $request->validate([
            'reason' => 'nullable|string|max:500',
        ]);

        $new = DB::transaction(function () use ($quotation, $data) {
            $maxVersion = (int) Quotation::where('opportunity_id', $quotation->opportunity_id)->max('version');
            $newQuote = Quotation::create([
                'opportunity_id'   => $quotation->opportunity_id,
                'version'          => $maxVersion + 1,
                'subtotal'         => $quotation->subtotal,
                'discount_rate'    => $quotation->discount_rate,
                'discount_amount'  => $quotation->discount_amount,
                'tax_rate'         => $quotation->tax_rate,
                'tax_amount'       => $quotation->tax_amount,
                'total_amount'     => $quotation->total_amount,
                'valid_until'      => now()->addDays(30)->toDateString(),
                'status'           => 'draft',
                'notes'            => isset($data['reason'])
                    ? ($quotation->notes ? $quotation->notes . "\n[客户要求修改] " . $data['reason'] : "[客户要求修改] " . $data['reason'])
                    : $quotation->notes,
                'created_by'       => $quotation->created_by,
            ]);
            $newQuote->quote_no = 'QT-' . date('Ymd') . '-' . str_pad($newQuote->id, 4, '0', STR_PAD_LEFT);
            $newQuote->save();

            foreach ($quotation->items as $it) {
                QuotationItem::create([
                    'quotation_id'      => $newQuote->id,
                    'inventory_item_id' => $it->inventory_item_id,
                    'name'              => $it->name,
                    'specification'     => $it->specification,
                    'unit'              => $it->unit,
                    'quantity'          => $it->quantity,
                    'unit_price'        => $it->unit_price,
                    'total_price'       => $it->total_price,
                    'remark'            => $it->remark,
                ]);
            }

            // 旧报价置为 rejected
            $quotation->update([
                'status'       => 'rejected',
                'responded_at' => now(),
            ]);

            return $newQuote;
        });

        return response()->json([
            'code' => 0,
            'data' => $new->load(['items.inventoryItem', 'opportunity.customer']),
        ]);
    }

    // ============================================================
    // === 商机状态机 (子操作,opps/{id}/{action}) ===
    // ============================================================

    /**
     * POST /api/sales/opps/{id}/win - 成交
     * 与 oppsMarkWon 行为一致,作为规范化命名别名
     */
    public function oppsWin(Request $request, Opportunity $opp): JsonResponse
    {
        return $this->oppsMarkWon($request, $opp);
    }

    /**
     * POST /api/sales/opps/{id}/lose - 输单
     * 与 oppsMarkLost 行为一致
     */
    public function oppsLose(Request $request, Opportunity $opp): JsonResponse
    {
        return $this->oppsMarkLost($request, $opp);
    }

    /**
     * POST /api/sales/opps/{id}/hold - 搁置
     */
    public function oppsHold(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可搁置'], 409);
        }
        if ($opp->stage === 'hold') {
            return response()->json(['code' => 0, 'data' => $opp->fresh()]);
        }

        $data = $request->validate([
            'reason' => 'nullable|string|max:500',
        ]);

        $opp->update([
            'stage'       => 'hold',
            'probability' => 0,
            'notes'       => isset($data['reason'])
                ? ($opp->notes ? $opp->notes . "\n[搁置] " . $data['reason'] : "[搁置] " . $data['reason'])
                : $opp->notes,
        ]);

        return response()->json(['code' => 0, 'data' => $opp->fresh()]);
    }

    /**
     * POST /api/sales/opps/{id}/move-to-project-pool - 入项目池(等价于 win 但不入成交)
     * 用于「合同未签但已确定」的场景,先入项目池待施工分配
     */
    public function oppsMoveToProjectPool(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可入项目池'], 409);
        }
        if ($opp->pool_id) {
            return response()->json(['code' => 1, 'message' => '该商机已在项目池中'], 409);
        }

        $data = $request->validate([
            'contract_amount' => 'required|numeric|min:0',
            'signed_at'       => 'nullable|date',
            'notes'           => 'nullable|string',
        ]);

        $pool = DB::transaction(function () use ($opp, $data) {
            $pool = ProjectPool::create([
                'pool_no'         => 'POOL-' . date('Ymd') . '-' . str_pad(ProjectPool::whereDate('created_at', today())->count() + 1, 3, '0', STR_PAD_LEFT),
                'opportunity_id'  => $opp->id,
                'name'            => $opp->name,
                'customer_id'     => $opp->customer_id,
                'contract_amount' => $data['contract_amount'],
                'signed_at'       => $data['signed_at'] ?? null,
                'status'          => 'pending',
                'notes'           => $data['notes'] ?? null,
            ]);

            $opp->update([
                'pool_id' => $pool->id,
                'stage'   => 'contracting',
                'probability' => 80,
                'notes'   => $data['notes'] ?? $opp->notes,
            ]);

            return $pool;
        });

        return response()->json(['code' => 0, 'data' => $pool->load('opportunity')]);
    }

    /**
     * POST /api/sales/opps/{id}/assign - 分派销售
     */
    public function oppsAssign(Request $request, Opportunity $opp): JsonResponse
    {
        if (in_array($opp->stage, ['won', 'lost'])) {
            return response()->json(['code' => 1, 'message' => '已终结的商机不可分派'], 409);
        }

        $data = $request->validate([
            'sales_id'   => 'required|integer|exists:users,id',
            'presale_id' => 'nullable|integer|exists:users,id',
            'notes'      => 'nullable|string|max:500',
        ]);

        $update = ['sales_id' => $data['sales_id']];
        if (isset($data['presale_id'])) $update['presale_id'] = $data['presale_id'];
        if (isset($data['notes'])) {
            $update['notes'] = $opp->notes
                ? $opp->notes . "\n[分派] " . $data['notes']
                : "[分派] " . $data['notes'];
        }
        $opp->update($update);

        return response()->json([
            'code' => 0,
            'data' => $opp->fresh()->load(['customer', 'sales', 'presale']),
        ]);
    }
}
