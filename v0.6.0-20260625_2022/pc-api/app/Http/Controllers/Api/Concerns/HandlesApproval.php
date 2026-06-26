<?php

namespace App\Http\Controllers\Api\Concerns;

use App\Models\ApprovalRecord;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Pagination\LengthAwarePaginator;

/**
 * 审批中心 3 大类 Controller 共享逻辑
 * 1) list 过滤 + 分页
 * 2) 详情字段转换
 * 3) 审批流程时间线追加
 * 4) 单号生成
 */
trait HandlesApproval
{
    protected function baseQuery(Request $request, string $type)
    {
        $q = ApprovalRecord::query()->where('type', $type)->orderByDesc('id');
        if ($request->filled('sub_type')) $q->where('sub_type', $request->sub_type);
        if ($request->filled('priority')) $q->where('priority', $request->priority);
        if ($request->filled('status'))   $q->where('status', $request->status);
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $q->where(function ($w) use ($kw) {
                $w->where('code', 'like', "%{$kw}%")->orWhere('title', 'like', "%{$kw}%");
            });
        }
        return $q;
    }

    protected function perPage(Request $request): int
    {
        $pp = (int) $request->input('per_page', 20);
        return $pp > 0 && $pp <= 200 ? $pp : 20;
    }

    protected function transformPaginated(LengthAwarePaginator $rows): array
    {
        return [
            'current_page' => $rows->currentPage(),
            'data'         => collect($rows->items())->map(fn (ApprovalRecord $r) => $this->transform($r))->all(),
            'total'        => $rows->total(),
            'per_page'     => $rows->perPage(),
        ];
    }

    protected function transform(ApprovalRecord $r): array
    {
        $applicant = $r->applicant_id ? User::find($r->applicant_id) : null;
        return [
            'id'                  => $r->id,
            'code'                => $r->code,
            'type'                => $r->type,
            'subType'             => $r->sub_type,
            'title'               => $r->title,
            'priority'            => $r->priority,
            'status'              => $r->status,
            'amount'              => (float) $r->amount,
            'bankAccount'         => $r->bank_account,
            'startDate'           => $r->start_date?->format('Y-m-d'),
            'endDate'             => $r->end_date?->format('Y-m-d'),
            'toStage'             => $r->to_stage,
            'applicantId'         => $r->applicant_id,
            'currentApproverId'   => $r->current_approver_id,
            'initiator'           => $applicant ? ['id' => $applicant->id, 'name' => $applicant->name] : null,
            'payload'             => $r->payload ?? new \stdClass(),
            'flow'                => $r->flow ?? [],
            'cc'                  => $r->cc ?? [],
            'comment'             => $r->comment,
            'created_at'          => $r->created_at?->toDateTimeString(),
            'updated_at'          => $r->updated_at?->toDateTimeString(),
        ];
    }

    protected function appendFlow(ApprovalRecord $r, string $action, string $comment, ?string $operatorName = null): void
    {
        $flow = is_array($r->flow) ? $r->flow : [];
        $flow[] = [
            'operator' => $operatorName ?? (request()->user()?->name ?? '—'),
            'action'   => $action,
            'time'     => now()->toDateTimeString(),
            'comment'  => $comment,
        ];
        $r->flow = $flow;
    }

    protected function nextCode(string $prefix): string
    {
        $year = date('Y');
        $count = ApprovalRecord::where('code', 'like', "{$prefix}-{$year}-%")->count() + 1;
        return sprintf('%s-%s-%04d', $prefix, $year, $count);
    }
}
