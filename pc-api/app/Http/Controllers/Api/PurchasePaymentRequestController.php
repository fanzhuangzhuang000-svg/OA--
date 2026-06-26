<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\PurchaseContract;
use App\Models\PurchasePaymentRequest;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * 采购付款申请 (Payment Request) — 5 端点
 *
 *  GET    /api/purchase/payment-requests             列表
 *  POST   /api/purchase/payment-requests             新建
 *  GET    /api/purchase/payment-requests/stats       统计
 *  POST   /api/purchase/payment-requests/{req}/approve  审批
 *  DELETE /api/purchase/payment-requests/{req}       撤回/删除
 */
class PurchasePaymentRequestController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = PurchasePaymentRequest::query();
        if ($request->filled('contract_id'))   $query->where('contract_id', $request->contract_id);
        if ($request->filled('supplier_id'))   $query->where('supplier_id', $request->supplier_id);
        if ($request->filled('status'))        $query->where('status', $request->status);
        if ($request->filled('payment_type'))  $query->where('payment_type', $request->payment_type);

        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function stats(): JsonResponse
    {
        $rows = PurchasePaymentRequest::query()
            ->selectRaw('status, COUNT(*) as count, COALESCE(SUM(amount),0) as amount')
            ->groupBy('status')
            ->get();
        $by = $rows->pluck('count', 'status')->toArray();
        $amountBy = $rows->pluck('amount', 'status')->toArray();

        return response()->json([
            'code' => 0,
            'data' => [
                'pending'  => $by['pending']  ?? 0,
                'approved' => $by['approved'] ?? 0,
                'rejected' => $by['rejected'] ?? 0,
                'paid'     => $by['paid']     ?? 0,
                'total'    => array_sum($by),
                'total_amount' => array_sum($amountBy),
            ],
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'contract_id'   => 'required|integer|exists:purchase_contracts,id',
            'supplier_id'   => 'nullable|integer|exists:suppliers,id',
            'amount'        => 'required|numeric|min:0',
            'payment_type'  => 'nullable|string|in:full,advance,progress,retention',
            'request_date'  => 'nullable|date',
            'applicant'     => 'nullable|string|max:50',
            'reason'        => 'nullable|string',
        ]);

        $data['payment_type'] = $data['payment_type'] ?? 'full';
        $data['status']       = 'pending';
        $data['applicant_id'] = $request->user()->id;

        // 若没传 supplier_id，从合同里取
        if (empty($data['supplier_id']) && $contract = PurchaseContract::find($data['contract_id'])) {
            $data['supplier_id'] = $contract->supplier_id;
        }

        $pr = PurchasePaymentRequest::create($data);
        return response()->json(['code' => 0, 'data' => $pr]);
    }

    public function approve(Request $request, PurchasePaymentRequest $pr): JsonResponse
    {
        if ($pr->status !== 'pending') {
            return response()->json(['code' => 1, 'message' => '只有待审批状态可审批'], 409);
        }

        $data = $request->validate([
            'decision' => 'required|string|in:approve,reject',
            'remark'   => 'nullable|string|max:500',
        ]);

        $pr->update([
            'status'         => $data['decision'] === 'approve' ? 'approved' : 'rejected',
            'approver_id'    => $request->user()->id,
            'approved_at'    => now(),
            'approve_remark' => $data['remark'] ?? null,
        ]);

        return response()->json(['code' => 0, 'data' => $pr->fresh()]);
    }

    public function destroy(PurchasePaymentRequest $pr): JsonResponse
    {
        if ($pr->status === 'paid') {
            return response()->json(['code' => 1, 'message' => '已付款的申请不可删除'], 409);
        }
        $pr->delete();
        return response()->json(['code' => 0, 'data' => ['deleted' => true]]);
    }
}
