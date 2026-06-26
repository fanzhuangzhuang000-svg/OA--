<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\PurchaseContract;
use App\Models\PurchasePayment;
use App\Models\PurchasePaymentRequest;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * 采购付款 (Payment) — 3 端点
 *
 *  GET   /api/purchase/payments           列表
 *  POST  /api/purchase/payments           新建（落地实付）
 *  GET   /api/purchase/payments/stats     统计
 */
class PurchasePaymentController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = PurchasePayment::query();
        if ($request->filled('supplier_id'))  $query->where('supplier_id', $request->supplier_id);
        if ($request->filled('contract_id'))  $query->where('contract_id', $request->contract_id);
        if ($request->filled('status'))       $query->where('status', $request->status);
        if ($request->filled('payment_method'))$query->where('payment_method', $request->payment_method);
        if ($request->filled('date_from'))    $query->whereDate('paid_at', '>=', $request->date_from);
        if ($request->filled('date_to'))      $query->whereDate('paid_at', '<=', $request->date_to);

        $perPage = (int) ($request->per_page ?? 15);
        return response()->json(['code' => 0, 'data' => $query->orderBy('paid_at', 'desc')->paginate(max(1, min($perPage, 200)))]);
    }

    public function stats(): JsonResponse
    {
        $rows = PurchasePayment::query()
            ->selectRaw('status, COUNT(*) as count, COALESCE(SUM(amount),0) as amount')
            ->groupBy('status')
            ->get();
        $by = $rows->pluck('count', 'status')->toArray();
        $amountBy = $rows->pluck('amount', 'status')->toArray();

        $totalAmount = PurchasePayment::where('status', 'success')->sum('amount');

        return response()->json([
            'code' => 0,
            'data' => [
                'success'      => $by['success']   ?? 0,
                'failed'       => $by['failed']    ?? 0,
                'reversed'     => $by['reversed']  ?? 0,
                'total'        => array_sum($by),
                'total_amount' => (float) $totalAmount,
            ],
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'payment_request_id' => 'nullable|integer|exists:purchase_payment_requests,id',
            'contract_id'        => 'required|integer|exists:purchase_contracts,id',
            'supplier_id'        => 'nullable|integer|exists:suppliers,id',
            'amount'             => 'required|numeric|min:0',
            'payment_method'     => 'nullable|string|in:transfer,cash,check,other',
            'paid_at'            => 'nullable|date',
            'voucher_no'         => 'nullable|string|max:80',
            'operator'           => 'nullable|string|max:50',
            'remark'             => 'nullable|string',
        ]);

        $data['payment_method'] = $data['payment_method'] ?? 'transfer';
        $data['paid_at']        = $data['paid_at'] ?? now()->toDateString();
        $data['status']         = 'success';
        $data['operator_id']    = $request->user()->id;

        // 若没传 supplier_id，从合同里取
        if (empty($data['supplier_id']) && $contract = PurchaseContract::find($data['contract_id'])) {
            $data['supplier_id'] = $contract->supplier_id;
        }

        $result = DB::transaction(function () use ($data) {
            $payment = PurchasePayment::create($data);

            // 同步付款申请状态为 paid
            if (!empty($data['payment_request_id'])) {
                PurchasePaymentRequest::where('id', $data['payment_request_id'])
                    ->update(['status' => 'paid']);
            }

            return $payment;
        });

        return response()->json(['code' => 0, 'data' => $result]);
    }
}
