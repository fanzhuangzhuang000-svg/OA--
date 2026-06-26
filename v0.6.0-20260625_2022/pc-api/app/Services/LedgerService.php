<?php

namespace App\Services;

use App\Models\CustomerReceipt;
use App\Models\CustomerReceivable;
use App\Models\SupplierPayment;
use App\Models\SupplierPayable;
use Illuminate\Support\Facades\DB;

/**
 * V0.4.2 总账服务 - 实时聚合查询
 *
 * 关注点:
 *  - getSupplierLedger:  供应商维度的"应付/已付/余额" + 付款流水
 *  - getCustomerLedger:  客户维度的"应收/已收/余额" + 收款流水
 *  - 多种聚合维度：by supplier / by project / by month
 */
class LedgerService
{
    /**
     * 供应商总账（按 supplier 聚合）
     *
     * @param int $supplierId
     * @return array{summary: array, payables: \Illuminate\Support\Collection, payments: \Illuminate\Support\Collection, monthly: array}
     */
    public function getSupplierLedger(int $supplierId, array $filters = []): array
    {
        $payableQuery = SupplierPayable::where('supplier_id', $supplierId);
        $paymentQuery = SupplierPayment::where('supplier_id', $supplierId);

        if (!empty($filters['project_id'])) {
            $payableQuery->where('project_id', $filters['project_id']);
        }
        if (!empty($filters['from'])) {
            $payableQuery->whereDate('due_date', '>=', $filters['from']);
            $paymentQuery->whereDate('payment_date', '>=', $filters['from']);
        }
        if (!empty($filters['to'])) {
            $payableQuery->whereDate('due_date', '<=', $filters['to']);
            $paymentQuery->whereDate('payment_date', '<=', $filters['to']);
        }

        $payables = (clone $payableQuery)->orderBy('due_date')->get();
        $payments = (clone $paymentQuery)->orderByDesc('payment_date')->limit(100)->get();

        // 实时聚合
        $totalAmount   = (float) $payables->sum('amount');
        $totalPaid     = (float) $payables->sum('paid_amount');
        $totalBalance  = (float) $payables->sum('balance');
        $overdueCount  = $payables->where('status', 'overdue')->count();
        $pendingCount  = $payables->where('status', 'pending')->count();

        // 按月聚合（应收发生额）
        $monthly = $payables->groupBy(fn ($p) => $p->due_date?->format('Y-m'))
            ->map(fn ($grp, $ym) => [
                'month'  => $ym,
                'amount' => (float) $grp->sum('amount'),
                'paid'   => (float) $grp->sum('paid_amount'),
            ])->values()->all();

        return [
            'summary' => [
                'total_amount'   => round($totalAmount, 2),
                'total_paid'     => round($totalPaid, 2),
                'total_balance'  => round($totalBalance, 2),
                'payable_count'  => $payables->count(),
                'overdue_count'  => $overdueCount,
                'pending_count'  => $pendingCount,
            ],
            'payables' => $payables,
            'payments' => $payments,
            'monthly'  => $monthly,
        ];
    }

    /**
     * 客户总账
     */
    public function getCustomerLedger(int $customerId, array $filters = []): array
    {
        $recQuery = CustomerReceivable::where('customer_id', $customerId);
        $rcvQuery = CustomerReceipt::where('customer_id', $customerId);

        if (!empty($filters['project_id'])) {
            $recQuery->where('project_id', $filters['project_id']);
        }
        if (!empty($filters['receivable_type'])) {
            $recQuery->where('receivable_type', $filters['receivable_type']);
        }
        if (!empty($filters['from'])) {
            $recQuery->whereDate('due_date', '>=', $filters['from']);
            $rcvQuery->whereDate('receipt_date', '>=', $filters['from']);
        }
        if (!empty($filters['to'])) {
            $recQuery->whereDate('due_date', '<=', $filters['to']);
            $rcvQuery->whereDate('receipt_date', '<=', $filters['to']);
        }

        $receivables = (clone $recQuery)->orderBy('due_date')->get();
        $receipts    = (clone $rcvQuery)->orderByDesc('receipt_date')->limit(100)->get();

        $totalAmount  = (float) $receivables->sum('amount');
        $totalReceived = (float) $receivables->sum('received_amount');
        $totalBalance = (float) $receivables->sum('balance');
        $overdueCount = $receivables->where('status', 'overdue')->count();

        $monthly = $receivables->groupBy(fn ($r) => $r->due_date?->format('Y-m'))
            ->map(fn ($grp, $ym) => [
                'month'  => $ym,
                'amount' => (float) $grp->sum('amount'),
                'received' => (float) $grp->sum('received_amount'),
            ])->values()->all();

        return [
            'summary' => [
                'total_amount'    => round($totalAmount, 2),
                'total_received'  => round($totalReceived, 2),
                'total_balance'   => round($totalBalance, 2),
                'receivable_count' => $receivables->count(),
                'overdue_count'   => $overdueCount,
            ],
            'receivables' => $receivables,
            'receipts'    => $receipts,
            'monthly'     => $monthly,
        ];
    }

    /**
     * 全局供应商应付出账（所有供应商）
     * 用于 ledger/supplier-ledger.vue 汇总页
     */
    public function getSupplierLedgerOverview(array $filters = []): array
    {
        $query = SupplierPayable::query();
        if (!empty($filters['supplier_id'])) {
            $query->where('supplier_id', $filters['supplier_id']);
        }
        if (!empty($filters['project_id'])) {
            $query->where('project_id', $filters['project_id']);
        }
        if (!empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }
        if (!empty($filters['from'])) {
            $query->whereDate('due_date', '>=', $filters['from']);
        }
        if (!empty($filters['to'])) {
            $query->whereDate('due_date', '<=', $filters['to']);
        }

        $total = (clone $query)->count();
        $page  = max(1, (int) ($filters['page'] ?? 1));
        $size  = min(100, max(1, (int) ($filters['per_page'] ?? 20)));

        $items = $query->with(['supplier:id,name,code', 'project:id,name,project_no'])
            ->orderByDesc('id')
            ->skip(($page - 1) * $size)->take($size)->get();

        $sumAmount  = (float) $query->sum('amount');
        $sumPaid    = (float) $query->sum('paid_amount');
        $sumBalance = (float) $query->sum('balance');

        return [
            'items'   => $items,
            'total'   => $total,
            'summary' => [
                'total_amount'  => round($sumAmount, 2),
                'total_paid'    => round($sumPaid, 2),
                'total_balance' => round($sumBalance, 2),
            ],
        ];
    }

    /**
     * 全局客户应收总账
     */
    public function getCustomerLedgerOverview(array $filters = []): array
    {
        $query = CustomerReceivable::query();
        if (!empty($filters['customer_id'])) {
            $query->where('customer_id', $filters['customer_id']);
        }
        if (!empty($filters['project_id'])) {
            $query->where('project_id', $filters['project_id']);
        }
        if (!empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }
        if (!empty($filters['receivable_type'])) {
            $query->where('receivable_type', $filters['receivable_type']);
        }
        if (!empty($filters['from'])) {
            $query->whereDate('due_date', '>=', $filters['from']);
        }
        if (!empty($filters['to'])) {
            $query->whereDate('due_date', '<=', $filters['to']);
        }

        $total = (clone $query)->count();
        $page  = max(1, (int) ($filters['page'] ?? 1));
        $size  = min(100, max(1, (int) ($filters['per_page'] ?? 20)));

        $items = $query->with(['customer:id,name', 'project:id,name,project_no'])
            ->orderByDesc('id')
            ->skip(($page - 1) * $size)->take($size)->get();

        $sumAmount  = (float) $query->sum('amount');
        $sumReceived = (float) $query->sum('received_amount');
        $sumBalance = (float) $query->sum('balance');

        return [
            'items'   => $items,
            'total'   => $total,
            'summary' => [
                'total_amount'    => round($sumAmount, 2),
                'total_received'  => round($sumReceived, 2),
                'total_balance'   => round($sumBalance, 2),
            ],
        ];
    }

    /**
     * 记录供应商付款 → 自动更新对应 payable 的 paid_amount / status
     *
     * @param int $paymentId supplier_payments.id
     */
    public function applySupplierPayment(int $paymentId): SupplierPayment
    {
        return DB::transaction(function () use ($paymentId) {
            $payment = SupplierPayment::findOrFail($paymentId);
            $allocations = $payment->allocations ?? [];

            foreach ($allocations as $row) {
                $payableId = (int) ($row['payable_id'] ?? 0);
                $amount    = (float) ($row['amount'] ?? 0);
                if ($payableId <= 0 || $amount <= 0) {
                    continue;
                }
                $payable = SupplierPayable::where('id', $payableId)
                    ->where('supplier_id', $payment->supplier_id)
                    ->lockForUpdate()
                    ->first();
                if (!$payable) {
                    continue;
                }
                $newPaid = round((float) $payable->paid_amount + $amount, 2);
                $payable->update([
                    'paid_amount' => $newPaid,
                    'status'      => $newPaid >= (float) $payable->amount
                        ? SupplierPayable::STATUS_PAID
                        : SupplierPayable::STATUS_PARTIAL,
                ]);
            }

            return $payment->fresh();
        });
    }

    /**
     * 客户收款分摊（同样逻辑）
     */
    public function applyCustomerReceipt(int $receiptId): CustomerReceipt
    {
        return DB::transaction(function () use ($receiptId) {
            $receipt = CustomerReceipt::findOrFail($receiptId);
            $allocations = $receipt->allocations ?? [];

            foreach ($allocations as $row) {
                $rid    = (int) ($row['receivable_id'] ?? 0);
                $amount = (float) ($row['amount'] ?? 0);
                if ($rid <= 0 || $amount <= 0) {
                    continue;
                }
                $rec = CustomerReceivable::where('id', $rid)
                    ->where('customer_id', $receipt->customer_id)
                    ->lockForUpdate()
                    ->first();
                if (!$rec) {
                    continue;
                }
                $newRecv = round((float) $rec->received_amount + $amount, 2);
                $rec->update([
                    'received_amount' => $newRecv,
                    'status'          => $newRecv >= (float) $rec->amount
                        ? CustomerReceivable::STATUS_PAID
                        : CustomerReceivable::STATUS_PARTIAL,
                ]);
            }
            return $receipt->fresh();
        });
    }
}
