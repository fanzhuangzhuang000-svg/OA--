<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\PurchaseRequirement;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * 采购需求 (Requirement) — 5 端点
 *
 *  GET    /api/purchase/requirements         列表 + 筛选
 *  POST   /api/purchase/requirements         新建
 *  GET    /api/purchase/requirements/stats   统计
 *  PUT    /api/purchase/requirements/{req}   更新
 *  DELETE /api/purchase/requirements/{req}   删除
 */
class PurchaseRequirementController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = PurchaseRequirement::query();
        if ($request->filled('project_id')) $query->where('project_id', $request->project_id);
        if ($request->filled('status'))     $query->where('status', $request->status);
        if ($request->filled('priority'))   $query->where('priority', $request->priority);
        if ($request->filled('keyword'))    $query->where(function ($q) use ($request) {
            $kw = '%' . $request->keyword . '%';
            $q->where('code', 'like', $kw)->orWhere('material', 'like', $kw);
        });

        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function stats(): JsonResponse
    {
        $rows = PurchaseRequirement::query()
            ->selectRaw('status, COUNT(*) as count')
            ->groupBy('status')
            ->pluck('count', 'status')
            ->toArray();

        return response()->json([
            'code' => 0,
            'data' => [
                'pending'   => $rows['pending']   ?? 0,
                'approved'  => $rows['approved']  ?? 0,
                'rejected'  => $rows['rejected']  ?? 0,
                'cancelled' => $rows['cancelled'] ?? 0,
                'total'     => array_sum($rows),
            ],
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'project_id' => 'nullable|integer|exists:projects,id',
            'material'   => 'required|string|max:200',
            'spec'       => 'nullable|string|max:200',
            'quantity'   => 'required|numeric|min:0',
            'unit'       => 'nullable|string|max:20',
            'need_date'  => 'nullable|date',
            'priority'   => 'nullable|string|in:low,medium,high,urgent',
            'creator'    => 'nullable|string|max:50',
            'remark'     => 'nullable|string',
        ]);

        $data['priority'] = $data['priority'] ?? 'medium';
        $data['unit']     = $data['unit'] ?? '件';
        $data['status']   = 'pending';

        $req = PurchaseRequirement::create($data);
        return response()->json(['code' => 0, 'data' => $req]);
    }

    public function update(Request $request, PurchaseRequirement $requirement): JsonResponse
    {
        if ($requirement->status === 'approved') {
            return response()->json(['code' => 1, 'message' => '已通过的需求不可编辑'], 409);
        }

        $data = $request->validate([
            'project_id' => 'nullable|integer|exists:projects,id',
            'material'   => 'sometimes|string|max:200',
            'spec'       => 'nullable|string|max:200',
            'quantity'   => 'sometimes|numeric|min:0',
            'unit'       => 'nullable|string|max:20',
            'need_date'  => 'nullable|date',
            'priority'   => 'sometimes|string|in:low,medium,high,urgent',
            'creator'    => 'nullable|string|max:50',
            'remark'     => 'nullable|string',
            'status'     => 'sometimes|string|in:pending,approved,rejected,cancelled',
        ]);

        // 审核动作
        if (isset($data['status']) && in_array($data['status'], ['approved', 'rejected'])) {
            $data['reviewed_by'] = $request->user()->id;
            $data['reviewed_at'] = now();
        }

        $requirement->update($data);
        return response()->json(['code' => 0, 'data' => $requirement->fresh()]);
    }

    public function destroy(PurchaseRequirement $requirement): JsonResponse
    {
        if ($requirement->status === 'approved') {
            return response()->json(['code' => 1, 'message' => '已通过的需求不可删除'], 409);
        }
        $requirement->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }
}
