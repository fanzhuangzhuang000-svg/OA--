<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\PurchasePlan;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * 采购计划 (Plan) — 7 端点
 *
 *  GET    /api/purchase/plans             列表
 *  POST   /api/purchase/plans             新建
 *  GET    /api/purchase/plans/stats       统计
 *  PUT    /api/purchase/plans/{plan}      更新
 *  DELETE /api/purchase/plans/{plan}      删除
 *  POST   /api/purchase/plans/{plan}/submit  提交审批
 *  POST   /api/purchase/plans/{plan}/approve 审批通过/拒绝
 */
class PurchasePlanController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = PurchasePlan::query();
        if ($request->filled('project_id'))    $query->where('project_id', $request->project_id);
        if ($request->filled('requirement_id'))$query->where('requirement_id', $request->requirement_id);
        if ($request->filled('status'))        $query->where('status', $request->status);
        if ($request->filled('priority'))      $query->where('priority', $request->priority);
        if ($request->filled('keyword'))       $query->where(function ($q) use ($request) {
            $kw = '%' . $request->keyword . '%';
            $q->where('code', 'like', $kw)->orWhere('title', 'like', $kw);
        });

        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function stats(): JsonResponse
    {
        $rows = PurchasePlan::query()
            ->selectRaw('status, COUNT(*) as count, COALESCE(SUM(total_amount),0) as amount')
            ->groupBy('status')
            ->get();

        $by = $rows->pluck('count', 'status')->toArray();
        $amountBy = $rows->pluck('amount', 'status')->toArray();
        return response()->json([
            'code' => 0,
            'data' => [
                'draft'     => $by['draft']     ?? 0,
                'submitted' => $by['submitted'] ?? 0,
                'approved'  => $by['approved']  ?? 0,
                'rejected'  => $by['rejected']  ?? 0,
                'cancelled' => $by['cancelled'] ?? 0,
                'total'     => array_sum($by),
                'total_amount' => array_sum($amountBy),
            ],
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'requirement_id' => 'nullable|integer|exists:purchase_requirements,id',
            'project_id'     => 'nullable|integer|exists:projects,id',
            'title'          => 'required|string|max:200',
            'total_amount'   => 'nullable|numeric|min:0',
            'plan_date'      => 'nullable|date',
            'priority'       => 'nullable|string|in:low,medium,high,urgent',
            'remark'         => 'nullable|string',
        ]);

        $data['priority']     = $data['priority'] ?? 'medium';
        $data['total_amount'] = $data['total_amount'] ?? 0;
        $data['status']       = 'draft';

        $plan = PurchasePlan::create($data);
        return response()->json(['code' => 0, 'data' => $plan]);
    }

    public function update(Request $request, PurchasePlan $plan): JsonResponse
    {
        if (in_array($plan->status, ['approved', 'submitted'])) {
            return response()->json(['code' => 1, 'message' => '草稿状态可编辑，提交后请走审批流'], 409);
        }

        $data = $request->validate([
            'requirement_id' => 'nullable|integer|exists:purchase_requirements,id',
            'project_id'     => 'nullable|integer|exists:projects,id',
            'title'          => 'sometimes|string|max:200',
            'total_amount'   => 'sometimes|numeric|min:0',
            'plan_date'      => 'nullable|date',
            'priority'       => 'sometimes|string|in:low,medium,high,urgent',
            'remark'         => 'nullable|string',
        ]);

        $plan->update($data);
        return response()->json(['code' => 0, 'data' => $plan->fresh()]);
    }

    public function destroy(PurchasePlan $plan): JsonResponse
    {
        if ($plan->status === 'approved') {
            return response()->json(['code' => 1, 'message' => '已审批的计划不可删除'], 409);
        }
        $plan->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }

    public function submit(Request $request, PurchasePlan $plan): JsonResponse
    {
        if ($plan->status !== 'draft') {
            return response()->json(['code' => 1, 'message' => '只有草稿状态可提交'], 409);
        }

        $plan->update([
            'status'       => 'submitted',
            'submitter_id' => $request->user()->id,
            'submitted_at' => now(),
        ]);

        return response()->json(['code' => 0, 'data' => $plan->fresh()]);
    }

    public function approve(Request $request, PurchasePlan $plan): JsonResponse
    {
        if ($plan->status !== 'submitted') {
            return response()->json(['code' => 1, 'message' => '只有已提交状态可审批'], 409);
        }

        $data = $request->validate([
            'decision' => 'required|string|in:approve,reject',
            'remark'   => 'nullable|string|max:500',
        ]);

        $plan->update([
            'status'         => $data['decision'] === 'approve' ? 'approved' : 'rejected',
            'approver_id'    => $request->user()->id,
            'approved_at'    => now(),
            'approve_remark' => $data['remark'] ?? null,
        ]);

        return response()->json(['code' => 0, 'data' => $plan->fresh()]);
    }
}
