<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\HandlesApproval;
use App\Models\ApprovalRecord;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * 财务审批（费用报销 / 付款单 / 应收应付 / 采购付款 / 居间费 / 薪资调整 / 差旅 / 借款 / 其他）
 *
 * GET    /api/approvals/finance                        列表
 * POST   /api/approvals/finance                        新建
 * GET    /api/approvals/finance/{approval}             详情
 * POST   /api/approvals/finance/{approval}/approve     通过
 * POST   /api/approvals/finance/{approval}/reject      拒绝
 * POST   /api/approvals/finance/{approval}/forward     转交
 */
class FinanceApprovalController extends Controller
{
    use HandlesApproval;

    public function index(Request $request): JsonResponse
    {
        $rows = $this->baseQuery($request, 'finance')->paginate($this->perPage($request));
        return response()->json(['code' => 0, 'data' => $this->transformPaginated($rows)]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'sub_type'     => 'required|string|max:50',
            'title'        => 'required|string|max:255',
            'priority'     => 'nullable|in:urgent,high,normal,low',
            'amount'       => 'nullable|numeric|min:0',
            'bank_account' => 'nullable|string|max:200',
            'payload'      => 'nullable|array',
            'cc'           => 'nullable|array',
        ]);

        $userId = $request->user()?->id;
        $record = ApprovalRecord::create([
            'code'         => $this->nextCode('FIN'),
            'type'         => 'finance',
            'sub_type'     => $data['sub_type'],
            'title'        => $data['title'],
            'priority'     => $data['priority'] ?? 'normal',
            'status'       => ApprovalRecord::STATUS_PENDING,
            'amount'       => $data['amount'] ?? 0,
            'bank_account' => $data['bank_account'] ?? null,
            'applicant_id' => $userId,
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
            'message' => '财务审批已提交',
            'data'    => ['id' => $record->id, 'code' => $record->code],
        ]);
    }

    public function show(ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'finance', 404, '资源不存在或参数错误');
        return response()->json(['code' => 0, 'data' => $this->transform($approval)]);
    }

    public function approve(Request $request, ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'finance', 404, '资源不存在或参数错误');
        if ($approval->status !== ApprovalRecord::STATUS_PENDING) {
            return response()->json(['code' => 1, 'message' => '该审批已结束，无法操作'], 422);
        }

        $comment = $request->input('comment', '同意');
        $this->appendFlow($approval, 'approve', $comment);
        $approval->status  = ApprovalRecord::STATUS_APPROVED;
        $approval->comment = $comment;
        $approval->save();

        return response()->json(['code' => 0, 'message' => '已通过', 'data' => ['status' => $approval->status]]);
    }

    public function reject(Request $request, ApprovalRecord $approval): JsonResponse
    {
        abort_unless($approval->type === 'finance', 404, '资源不存在或参数错误');
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
        abort_unless($approval->type === 'finance', 404, '资源不存在或参数错误');
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
