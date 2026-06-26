<?php

namespace App\Services;

use App\Models\ProjectCommencementOrder;
use App\Models\RectificationDailyRequired;
use App\Models\WorkProcess;
use App\Models\WorkProcessProgress;
use Illuminate\Support\Facades\DB;

/**
 * V0.4.3 开工单服务
 *
 * 关键流程:
 *  - createOrder: 创建开工单 (生成 code) + 按起止日期批量生成 rectification_daily_required
 *  - approve:  审批 (状态机)
 *  - startWork: 开工 → 触发 work_process_progress 创建 (在 Observer 里)
 *  - complete:  完工
 */
class CommencementOrderService
{
    /**
     * 生成开工单编号 COMM-yyyy-NNNN
     */
    public function generateCode(): string
    {
        $year   = date('Y');
        $prefix = "COMM-{$year}-";
        $latest = ProjectCommencementOrder::where('code', 'like', $prefix . '%')
            ->orderByDesc('id')
            ->value('code');
        $next = 1;
        if ($latest && preg_match('/-(\d+)$/', $latest, $m)) {
            $next = ((int) $m[1]) + 1;
        }
        return $prefix . str_pad((string) $next, 4, '0', STR_PAD_LEFT);
    }

    /**
     * 创建开工单 + 日报需求单 + 工序进度
     */
    public function createOrder(int $projectId, array $data, int $userId): ProjectCommencementOrder
    {
        // V0.4.4: 默认 status = pending_approval (V0.4.3 留 draft, 但下游无 draft 流程, 故默认直接进审批队列)
        if (!isset($data['status'])) {
            $data['status'] = ProjectCommencementOrder::STATUS_PENDING_APPROVAL;
        }
        return DB::transaction(function () use ($projectId, $data, $userId) {
            $order = ProjectCommencementOrder::create([
                'project_id'           => $projectId,
                'team_id'              => $data['team_id']              ?? null,
                'code'                 => $this->generateCode(),
                'commencement_date'    => $data['commencement_date']    ?? $data['planned_start_date'] ?? now()->toDateString(),
                'planned_end_date'     => $data['planned_end_date']     ?? null,
                'work_content'         => $data['work_content']         ?? $data['work_scope']         ?? '',
                'quality_requirements' => $data['work_standard']        ?? null,
                'safety_requirements'  => $data['safety_requirements']  ?? null,
                'status'               => $data['status'],
                'created_by'           => $userId,
            ]);

            // 1) 工序 (可选)
            if (!empty($data['processes']) && is_array($data['processes'])) {
                $this->syncProcesses($order, $data['processes']);
            }

            // 2) 强制日报需求 (开工单创建即生成 — 大哥拍板)
            $this->generateDailyRequired($order);

            return $order->fresh(['team', 'project']);
        });
    }

    /**
     * 同步工序 + 同步工序进度
     */
    public function syncProcesses(ProjectCommencementOrder $order, array $processes): void
    {
        DB::transaction(function () use ($order, $processes) {
            // 删除老工序 & 进度 (仅 draft 可调)
            if ($order->status !== ProjectCommencementOrder::STATUS_DRAFT) {
                throw new \RuntimeException('只有草稿状态可同步工序');
            }
            $order->processes()->delete();
            $order->processes()->get()->each(function ($p) {
                WorkProcessProgress::where('process_id', $p->id)->delete();
            });

            $sort = 0;
            foreach ($processes as $row) {
                $proc = WorkProcess::create([
                    'project_id'            => $order->project_id,
                    'name'                  => $row['name'],
                    'sequence'              => $row['sequence']            ?? $sort++,
                    'description'           => $row['description']         ?? null,
                    'estimated_hours'       => $row['estimated_hours']     ?? null,
                    'status'                => $row['status']              ?? 'active',
                ]);

                // 创建对应 progress 记录 (completed=0)
                WorkProcessProgress::create([
                    'process_id'            => $proc->id,
                    'project_id'            => $order->project_id,
                    'team_id'               => $order->team_id,
                    'planned_quantity'      => $row['planned_quantity'] ?? 0,
                    'completed_quantity'    => 0,
                    'progress_percentage'   => 0,
                    'status'                => WorkProcessProgress::STATUS_NOT_STARTED ?? 'pending',
                ]);
            }
        });
    }

    /**
     * 按起止日期每天生成 rectification_daily_required
     */
    private function generateDailyRequired(ProjectCommencementOrder $order): void
    {
        $start = \Carbon\Carbon::parse($order->planned_start_date)->startOfDay();
        $end   = \Carbon\Carbon::parse($order->planned_end_date)->startOfDay();

        if ($end->lt($start)) {
            throw new \RuntimeException('计划结束日期不能早于开始日期');
        }

        $rows = [];
        for ($d = $start->copy(); $d->lte($end); $d->addDay()) {
            $rows[] = [
                'project_id'            => $order->project_id,
                'commencement_order_id' => $order->id,
                'work_date'             => $d->toDateString(),
                'status'                => RectificationDailyRequired::STATUS_PENDING,
                'is_required'           => true,
                'created_at'            => now(),
                'updated_at'            => now(),
            ];
        }

        // 防止重复生成 (幂等) — 唯一键 (project_id, work_date) 表上存在
        RectificationDailyRequired::upsert(
            $rows,
            ['project_id', 'work_date'],          // 唯一键
            ['updated_at']                         // 仅更新时间
        );
    }

    /**
     * 提交审批 (draft → pending_approval)
     */
    public function submitForApproval(int $orderId): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if ($order->status !== ProjectCommencementOrder::STATUS_DRAFT) {
                throw new \RuntimeException('只有草稿状态可提交审批');
            }
            $order->update(['status' => ProjectCommencementOrder::STATUS_PENDING_APPROVAL]);
            return $order->fresh();
        });
    }

    /**
     * 审批通过
     */
    public function approve(int $orderId, int $approverId, ?string $comment = null): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId, $approverId, $comment) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if ($order->status !== ProjectCommencementOrder::STATUS_PENDING_APPROVAL) {
                throw new \RuntimeException('只有待审批状态可审批');
            }
            $order->update([
                'status'      => ProjectCommencementOrder::STATUS_APPROVED,
                'approved_by' => $approverId,
                'approved_at' => now(),
            ]);
            return $order->fresh();
        });
    }

    /**
     * 审批驳回
     */
    public function reject(int $orderId, int $approverId, string $reason): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId, $approverId, $reason) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if ($order->status !== ProjectCommencementOrder::STATUS_PENDING_APPROVAL) {
                throw new \RuntimeException('只有待审批状态可驳回');
            }
            if (trim($reason) === '') {
                throw new \InvalidArgumentException('驳回原因不能为空');
            }
            $order->update([
                'status'          => ProjectCommencementOrder::STATUS_REJECTED,
                'approver_id'     => $approverId,
                'approved_at'     => now(),
                'rejected_reason' => $reason,
            ]);
            return $order->fresh();
        });
    }

    /**
     * 开工 (approved → in_progress)
     * 触发工序进度激活 (Observer 同步)
     *
     * @param array $data 实际开工日期等可选数据
     */
    public function startWork(int $orderId, array $data = []): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId, $data) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if ($order->status !== ProjectCommencementOrder::STATUS_APPROVED) {
                throw new \RuntimeException('只有已批准状态可开工');
            }
            $order->update([
                'status' => ProjectCommencementOrder::STATUS_IN_PROGRESS,
            ]);
            // 激活该项目下 pending 工序进度 (V0.4.4 实际: work_process_progress 无 commencement_order_id 列, 走 project_id 激活)
            WorkProcessProgress::where('project_id', $order->project_id)
                ->where('status', WorkProcessProgress::STATUS_PENDING)
                ->update(['status' => WorkProcessProgress::STATUS_IN_PROGRESS]);
            return $order->fresh();
        });
    }

    /**
     * 完工 (in_progress → completed)
     */
    public function complete(int $orderId, array $data = []): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId, $data) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if ($order->status !== ProjectCommencementOrder::STATUS_IN_PROGRESS) {
                throw new \RuntimeException('只有施工中状态可完工');
            }
            $order->update([
                'status'           => ProjectCommencementOrder::STATUS_COMPLETED,
            ]);
            return $order->fresh();
        });
    }

    /**
     * 取消开工单
     */
    public function cancel(int $orderId, ?string $reason = null): ProjectCommencementOrder
    {
        return DB::transaction(function () use ($orderId, $reason) {
            $order = ProjectCommencementOrder::findOrFail($orderId);
            if (in_array($order->status, [
                ProjectCommencementOrder::STATUS_COMPLETED,
                ProjectCommencementOrder::STATUS_CANCELLED,
            ], true)) {
                throw new \RuntimeException('已完成/已取消的开工单不可再取消');
            }
            $order->update([
                'status' => ProjectCommencementOrder::STATUS_CANCELLED,
            ]);
            // 关闭日报需求
            RectificationDailyRequired::where('commencement_order_id', $order->id)
                ->where('status', RectificationDailyRequired::STATUS_PENDING)
                ->update([
                    'status'     => RectificationDailyRequired::STATUS_EXCUSED,
                    'updated_at' => now(),
                ]);
            return $order->fresh();
        });
    }
}
