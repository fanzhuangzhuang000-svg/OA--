<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\RepairOrder;
use App\Models\RepairProgressLog;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * V0.5.5 维修进度日志
 */
class RepairProgressLogController extends Controller
{
    public function index(int $repairOrderId): JsonResponse
    {
        RepairOrder::findOrFail($repairOrderId);
        $list = RepairProgressLog::where('repair_order_id', $repairOrderId)
            ->with('actor:id,username,name')
            ->orderBy('action_at', 'desc')
            ->get()
            ->map(fn ($l) => $this->present($l));
        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function store(Request $request, int $repairOrderId): JsonResponse
    {
        $data = $request->validate([
            'method_id'     => 'nullable|integer',
            'progress'      => 'required|string|max:32',
            'status_before' => 'nullable|string|max:32',
            'status_after'  => 'nullable|string|max:32',
            'description'   => 'nullable|string|max:2000',
            'cost_added'    => 'nullable|numeric|min:0',
            'is_paid'       => 'boolean',
            'action_at'     => 'nullable|date',
        ]);
        $data['repair_order_id'] = $repairOrderId;
        $data['action_by'] = $request->user()?->id;
        $data['action_at'] = $data['action_at'] ?? now();
        $data['is_paid'] = $data['is_paid'] ?? false;
        $log = RepairProgressLog::create($data);
        return response()->json(['code' => 0, 'data' => $this->present($log->load('actor:id,username,name')), 'message' => '已添加']);
    }

    public function destroy(int $id): JsonResponse
    {
        $l = RepairProgressLog::findOrFail($id);
        $l->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    private function present(RepairProgressLog $l): array
    {
        return [
            'id' => $l->id,
            'repair_order_id' => $l->repair_order_id,
            'method_id' => $l->method_id,
            'progress' => $l->progress,
            'status_before' => $l->status_before,
            'status_after' => $l->status_after,
            'description' => $l->description,
            'cost_added' => (float) $l->cost_added,
            'is_paid' => $l->is_paid,
            'actor_id' => $l->action_by,
            'actor_name' => $l->actor?->name,
            'action_at' => $l->action_at?->toDateTimeString(),
            'created_at' => $l->created_at?->toDateTimeString(),
        ];
    }
}
