<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\HandlesApproval;
use App\Models\ApprovalRecord;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * 运营审批（请假 / 加班 / 用车 / 报销以外的运营事项）
 *
 * GET    /api/approvals/operation                       列表
 * POST   /api/approvals/operation                       新建
 * GET    /api/approvals/operation/{approval}            详情
 * POST   /api/approvals/operation/{approval}/approve    通过
 * POST   /api/approvals/operation/{approval}/reject     拒绝
 * POST   /api/approvals/operation/{approval}/forward    转交
 */
class OperationApprovalController extends Controller
{
    use HandlesApproval;

    public function index(Request $request): JsonResponse
    {
        $rows = $this->baseQuery($request, 'operation')->paginate($this->perPage($request));
        return response()->json(['code' => 0, 'data' => $this->transformPaginated($rows)]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'sub_type'   => 'required|string|max:50',
            'title'      => 'required|string|max:255',
            'priority'   => 'nullable|in:urgent,high,normal,low',
            'start_date' => 'nullable|date',
            'end_date'   => 'nullable|date|after_or_equal:start_date',
            'payload'    => 'nullable|array',
            'cc'         => 'nullable|array',
        ]);

        $userId = $request->user()?->id;
        $record = ApprovalRecord::create([
            'code'         => $this->nextCode('OPS'),
            'type'         => 'operation',
            'sub_type'     => $data['sub_type'],
            'title'        => $data['title'],
            'priority'     => $data['priority'] ?? 'normal',
            'status'       => ApprovalRecord::STATUS_PENDING,
            'start_date'   => $data['start_date'] ?? null,
            'end_date'     => $data['end_date'] ?? null,
            'applicant_id' => $userId,
            'current_approver_id' => 1,
            'payload'      => $data['payload'] ?? [],
            'flow'         => [[
                'operator' => User::find($userId)?->name ?? '—',
                'action'   => 'submit',
                'time'     => now()->toDateTimeString(),
                'comment'  => '提交申请',
            ]],
            'cc'           => $data['cc'] ?? [],
        ]);

        return response()->json([
            'code'    => 0,
            'message' => '运营审批已提交',
            'data'    => ['id' => $record->id, 'code' => $record->code],
        ]);
    }

    public function show(ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'operation', 404, '资源不存在或参数错误');
        return response()->json(['code' => 0, 'data' => $this->transform($approval)]);
    }

    public function approve(Request $request, ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'operation', 404, '资源不存在或参数错误');
        if ($approval->status !== ApprovalRecord::STATUS_PENDING) {
            return response()->json(['code' => 1, 'message' => '该审批已结束，无法操作'], 422);
        }

        // 物料申领审批通过后自动扣减库存
        if ($approval->sub_type === 'material-request') {
            $payload = $approval->payload;
            $items = $payload['items'] ?? [];
            $projectId = $payload['project_id'] ?? null;
            if (!empty($items)) {
                try {
                    \DB::transaction(function () use ($items, $projectId, $approval) {
                        foreach ($items as $item) {
                            $invItem = \App\Models\InventoryItem::lockForUpdate()->findOrFail($item['inventory_item_id']);
                            $qty = (int)($item['quantity'] ?? 1);
                            if ($invItem->current_stock < $qty) {
                                throw new \RuntimeException("物料 {$invItem->name} 库存不足（当前 {$invItem->current_stock}，需要 {$qty}）");
                            }
                            $newStock = $invItem->current_stock - $qty;
                            $invItem->current_stock = $newStock;
                            $invItem->save();
                            $today = date('Ymd');
                            $cnt = \App\Models\StockRecord::where('record_no', 'like', "MR-{$today}-%")->count();
                            $seq = str_pad((string)($cnt + 1), 4, '0', STR_PAD_LEFT);
                            \App\Models\StockRecord::create([
                                'record_no'         => "MR-{$today}-{$seq}",
                                'inventory_item_id' => $item['inventory_item_id'],
                                'warehouse_id'      => $item['warehouse_id'] ?? 1,
                                'type'              => 'outbound',
                                'quantity'          => $qty,
                                'remaining_stock'   => $newStock,
                                'out_method'        => 'pickup',
                                'project_id'        => $projectId,
                                'operator_id'       => $approval->applicant_id,
                                'remark'            => '物料申领 #' . $approval->code,
                            ]);
                        }
                    });
                } catch (\Throwable $e) {
                    return response()->json(['code' => 1002, 'message' => '出库失败：' . $e->getMessage()], 422);
                }
            }
        }

        $comment = $request->input('comment', '同意');
        $this->appendFlow($approval, 'approve', $comment);
        $approval->status  = ApprovalRecord::STATUS_APPROVED;
        $approval->comment = $comment;
        $approval->save();

        return response()->json(['code' => 0, 'message' => '已通过', 'data' => ['status' => $approval->status, 'remark' => $approval->sub_type === 'material-request' ? '物料已出库' : null]]);
    }

    public function reject(Request $request, ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'operation', 404, '资源不存在或参数错误');
        if ($approval->status !== ApprovalRecord::STATUS_PENDING) {
            return response()->json(['code' => 1, 'message' => '该审批已结束，无法操作'], 422);
        }

        $request->validate(['comment' => 'required|string|max:500']);
        $this->appendFlow($approval, 'reject', $request->input('comment'));
        $approval->status  = ApprovalRecord::STATUS_REJECTED;
        $approval->comment = $request->input('comment');
        $approval->save();

        return response()->json(['code' => 0, 'message' => '已驳回', 'data' => ['status' => $approval->status]]);
    }

    public function forward(Request $request, ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'operation', 404, '资源不存在或参数错误');
        if ($approval->status !== ApprovalRecord::STATUS_PENDING) {
            return response()->json(['code' => 1, 'message' => '该审批已结束，无法操作'], 422);
        }

        $request->validate(['target' => 'required|string|max:100']);
        $target = $request->input('target');
        $this->appendFlow($approval, 'transfer', "转交给 {$target}");
        $approval->current_approver_id = null;
        $approval->status  = ApprovalRecord::STATUS_TRANSFERRED;
        $approval->comment = "已转交：{$target}";
        $approval->save();

        return response()->json(['code' => 0, 'message' => "已转交 {$target}"]);
    }
}
