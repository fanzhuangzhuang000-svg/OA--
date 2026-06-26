<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ApprovalTemplate;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * 审批流程模板 CRUD
 *
 * GET    /api/approval-templates         列表（可按 module 过滤）
 * POST   /api/approval-templates         新建
 * GET    /api/approval-templates/{id}    详情
 * PUT    /api/approval-templates/{id}    更新
 * DELETE /api/approval-templates/{id}    删除
 * POST   /api/approval-templates/{id}/toggle  启停切换
 */
class ApprovalTemplateController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = ApprovalTemplate::with(['creator', 'updater'])->orderBy('id');
        if ($request->filled('module')) {
            $query->where('module', $request->module);
        }
        $rows = $query->get()->map(function (ApprovalTemplate $t) {
            $steps = is_array($t->steps) ? $t->steps : [];
            return [
                'id'         => $t->id,
                'name'       => $t->name,
                'module'     => $t->module,
                'description'=> $t->description ?? '',
                'nodes'      => $steps,
                'nodeCount'  => count($steps),
                'status'     => $t->enabled ? '启用' : '停用',
                'updatedBy'  => $t->updater?->name ?? $t->creator?->name ?? '—',
                'updatedAt'  => $t->updated_at?->format('Y-m-d H:i:s'),
                'createdAt'  => $t->created_at?->format('Y-m-d H:i:s'),
            ];
        });
        return response()->json(['code' => 0, 'data' => $rows]);
    }

    public function show(ApprovalTemplate $approvalTemplate): JsonResponse
    {
        $approvalTemplate->load(['creator', 'updater']);
        $t = $approvalTemplate;
        $steps = is_array($t->steps) ? $t->steps : [];
        return response()->json(['code' => 0, 'data' => [
            'id'         => $t->id,
            'name'       => $t->name,
            'module'     => $t->module,
            'description'=> $t->description ?? '',
            'nodes'      => $steps,
            'nodeCount'  => count($steps),
            'status'     => $t->enabled ? '启用' : '停用',
            'updatedBy'  => $t->updater?->name ?? $t->creator?->name ?? '—',
            'updatedAt'  => $t->updated_at?->format('Y-m-d H:i:s'),
        ]]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'required|string|max:100',
            'type'         => 'nullable|string|max:50',
            'module'       => 'required|string|max:50',
            'description'  => 'nullable|string',
            'steps'        => 'nullable|array',
            'enabled'      => 'nullable|boolean',
            'sort_order'   => 'nullable|integer',
        ]);
        $data['steps']      = $data['steps'] ?? [];
        $data['enabled']    = $data['enabled'] ?? true;
        $data['sort_order'] = $data['sort_order'] ?? 0;
        $data['created_by'] = $request->user()?->id;

        $t = ApprovalTemplate::create($data);
        return response()->json(['code' => 0, 'message' => '流程模板已创建', 'data' => ['id' => $t->id]]);
    }

    public function update(Request $request, ApprovalTemplate $approvalTemplate): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'sometimes|required|string|max:100',
            'type'         => 'sometimes|nullable|string|max:50',
            'module'       => 'sometimes|required|string|max:50',
            'description'  => 'sometimes|nullable|string',
            'steps'        => 'sometimes|nullable|array',
            'enabled'      => 'sometimes|nullable|boolean',
            'sort_order'   => 'sometimes|nullable|integer',
        ]);
        $approvalTemplate->fill($data)->save();
        return response()->json(['code' => 0, 'message' => '流程模板已更新']);
    }

    public function destroy(ApprovalTemplate $approvalTemplate): JsonResponse
    {
        $approvalTemplate->delete();
        return response()->json(['code' => 0, 'message' => '流程模板已删除']);
    }

    public function toggle(ApprovalTemplate $approvalTemplate): JsonResponse
    {
        $newEnabled = ! $approvalTemplate->enabled;
        $approvalTemplate->enabled = $newEnabled;
        $approvalTemplate->save();
        $label = $newEnabled ? '启用' : '停用';
        return response()->json(['code' => 0, 'message' => "已切换为{$label}", 'data' => ['status' => $label, 'enabled' => $newEnabled]]);
    }
}
