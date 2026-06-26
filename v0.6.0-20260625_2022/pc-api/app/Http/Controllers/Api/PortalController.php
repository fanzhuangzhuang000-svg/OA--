<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TenderProject;
use App\Models\TenderBid;
use App\Models\TenderAttachment;
use App\Models\Supplier;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/**
 * V0.6.0 招标中心 — 供应商门户 API (免登录, token 鉴权)
 *
 * 路由: /api/portal
 *   GET  /portal/t/{token}                  通过 token 拿招标信息
 *   POST /portal/t/{token}/login            验证手机号 (如有)
 *   GET  /portal/t/{token}/bids             看我方对该招标的投标
 *   POST /portal/t/{token}/bids             提交/更新投标
 *   GET  /portal/suppliers                  供应商列表 (内部用, 管理 portal 账号)
 *   POST /portal/suppliers                  新增供应商 (内部)
 *   GET  /portal/invitations?phone=xxx      供应商查自己的邀请
 */
class PortalController extends Controller
{
    /**
     * 通过 public_token 拉取招标公开信息 (给外部供应商看)
     * 关键: 只返回公开字段, 内部信息 (评分配置等) 不返回
     */
    public function tenderByToken(string $token): JsonResponse
    {
        $t = TenderProject::where('public_token', $token)->firstOr(function () {
            abort(response()->json(['code' => 1001, 'message' => '链接无效或已过期'], 404));
        });
        if (!in_array($t->status, ['bidding', 'published', 'evaluating', 'awarded', 'closed'])) {
            return response()->json(['code' => 1001, 'message' => '该项目当前不可访问'], 403);
        }
        // 公开附件 (visibility=public, 且是项目级非投标级)
        $atts = $t->attachments()->whereNull('tender_bid_id')->where('visibility', 'public')->get();

        return response()->json(['code' => 0, 'data' => [
            'id'              => $t->id,
            'code'            => $t->code,
            'name'            => $t->name,
            'description'     => $t->description,
            'type'            => $t->type,
            'status'          => $t->status,
            'status_label'    => $t->status_label,
            'required_items'  => $t->required_items,
            'deadline'        => $t->deadline?->toIso8601String(),
            'open_at'         => $t->open_at?->toIso8601String(),
            'project'         => $t->project ? ['id' => $t->project->id, 'name' => $t->project->name] : null,
            'attachments'     => $atts->map(fn($a) => [
                'id' => $a->id, 'name' => $a->file_name, 'url' => $a->url,
                'size' => $a->file_size, 'mime' => $a->mime_type, 'category' => $a->category,
            ]),
            'public_token'    => $t->public_token,
        ]]);
    }

    /**
     * 供应商查自己对该招标的投标
     * 鉴权: 用 token + supplier_id (cookie 存 supplier_id 7 天)
     */
    public function myBid(Request $request, string $token): JsonResponse
    {
        $supplierId = $request->input('supplier_id') ?? $request->cookie('portal_supplier_id');
        if (!$supplierId) {
            return response()->json(['code' => 1001, 'message' => '请先选择/绑定供应商身份'], 401);
        }
        $t = TenderProject::where('public_token', $token)->firstOr(function () {
            abort(response()->json(['code' => 1001, 'message' => '链接无效'], 404));
        });
        $bid = $t->bids()->where('supplier_id', $supplierId)->with('items')->first();
        return response()->json(['code' => 0, 'data' => $bid]);
    }

    /**
     * 供应商提交/更新投标 (公开)
     */
    public function submitBid(Request $request, string $token): JsonResponse
    {
        $data = $request->validate([
            'supplier_id'        => 'required|integer|exists:suppliers,id',
            'total_amount'       => 'required|numeric|min:0',
            'lead_time_days'     => 'nullable|integer|min:0',
            'technical_proposal' => 'nullable|string|max:5000',
            'remark'             => 'nullable|string|max:1000',
            'items'              => 'nullable|array',
            'items.*.name'       => 'required|string',
            'items.*.spec'       => 'nullable|string',
            'items.*.unit'       => 'nullable|string',
            'items.*.quantity'   => 'required|numeric|min:0',
            'items.*.unit_price' => 'required|numeric|min:0',
        ]);
        $t = TenderProject::where('public_token', $token)->firstOr(function () {
            abort(response()->json(['code' => 1001, 'message' => '链接无效'], 404));
        });
        if (!in_array($t->status, ['bidding', 'published'])) {
            return response()->json(['code' => 1001, 'message' => '该项目已截止投标'], 422);
        }
        // 校验是否在邀请名单
        $invited = $t->invited_supplier_ids ?? [];
        if ($invited && !in_array($data['supplier_id'], $invited)) {
            return response()->json(['code' => 1002, 'message' => '该供应商未在邀请名单中'], 403);
        }
        $bid = $t->bids()->where('supplier_id', $data['supplier_id'])->first();
        if ($bid && in_array($bid->status, ['awarded', 'rejected', 'withdrawn'])) {
            return response()->json(['code' => 1003, 'message' => '该投标已定标或撤回, 不可修改'], 422);
        }
        if (!$bid) {
            $bid = $t->bids()->create([
                'supplier_id'    => $data['supplier_id'],
                'total_amount'   => $data['total_amount'],
                'lead_time_days' => $data['lead_time_days'] ?? null,
                'technical_proposal' => $data['technical_proposal'] ?? null,
                'remark'         => $data['remark'] ?? null,
                'status'         => 'submitted',
                'submitted_at'   => now(),
                'code'           => 'BID-' . date('Ymd') . '-' . str_pad((string)(TenderBid::whereDate('created_at', today())->count() + 1), 3, '0', STR_PAD_LEFT),
            ]);
        } else {
            $bid->fill([
                'total_amount'   => $data['total_amount'],
                'lead_time_days' => $data['lead_time_days'] ?? null,
                'technical_proposal' => $data['technical_proposal'] ?? null,
                'remark'         => $data['remark'] ?? null,
                'status'         => 'submitted',
                'submitted_at'   => now(),
            ])->save();
            $bid->items()->delete();
        }
        if (!empty($data['items'])) {
            foreach ($data['items'] as $it) {
                $bid->items()->create([
                    'name'        => $it['name'],
                    'spec'        => $it['spec'] ?? null,
                    'unit'        => $it['unit'] ?? '件',
                    'quantity'    => $it['quantity'],
                    'unit_price'  => $it['unit_price'],
                    'total_price' => round($it['quantity'] * $it['unit_price'], 2),
                ]);
            }
        }
        return response()->json(['code' => 0, 'message' => '投标已提交', 'data' => $bid->load('items')]);
    }

    /**
     * 供应商上传投标附件
     */
    public function uploadBidAttachment(Request $request, string $token): JsonResponse
    {
        $data = $request->validate([
            'supplier_id' => 'required|integer|exists:suppliers,id',
            'bid_id'      => 'required|integer|exists:tender_bids,id',
            'file'        => 'required|file|max:51200',
            'category'    => 'nullable|in:technical,business,qualification,bid_file,other',
            'visibility'  => 'nullable|in:public,eval_only',
        ]);
        $t = TenderProject::where('public_token', $token)->firstOrFail();
        $bid = $t->bids()->where('id', $data['bid_id'])->where('supplier_id', $data['supplier_id'])->firstOrFail();
        $file = $request->file('file');
        $ext  = strtolower($file->getClientOriginalExtension());
        $dir  = "tenders/{$t->id}/bids/{$bid->id}";
        $path = $file->storeAs($dir, uniqid('att_') . ($ext ? ".{$ext}" : ''), 'public');
        $att  = TenderAttachment::create([
            'tender_project_id' => $t->id,
            'tender_bid_id'     => $bid->id,
            'uploaded_by_supplier_id' => $data['supplier_id'],
            'file_name' => $file->getClientOriginalName(),
            'file_path' => $path,
            'mime_type' => $file->getMimeType(),
            'file_size' => $file->getSize(),
            'category'  => $data['category'] ?? 'bid_file',
            'visibility' => $data['visibility'] ?? 'eval_only',
        ]);
        return response()->json(['code' => 0, 'data' => $att]);
    }

    /**
     * 供应商用手机号查自己的邀请
     */
    public function invitations(Request $request): JsonResponse
    {
        $phone = $request->input('phone');
        if (!$phone) {
            return response()->json(['code' => 1001, 'message' => '请提供手机号'], 422);
        }
        // 找供应商 (按联系人手机号匹配, 简化用 supplier.phone)
        $supplier = Supplier::where('phone', $phone)->first();
        if (!$supplier) {
            return response()->json(['code' => 0, 'data' => ['supplier' => null, 'invitations' => []]]);
        }
        // 该供应商被邀请的招标 (在 invited_supplier_ids 数组中)
        $list = TenderProject::whereJsonContains('invited_supplier_ids', $supplier->id)
                              ->whereIn('status', ['bidding', 'published', 'evaluating', 'awarded', 'closed'])
                              ->orderByDesc('publish_at')
                              ->get(['id', 'code', 'name', 'status', 'deadline', 'public_token']);
        return response()->json(['code' => 0, 'data' => ['supplier' => ['id' => $supplier->id, 'name' => $supplier->name, 'phone' => $supplier->phone], 'invitations' => $list] ->map(fn($i) => [
            'id' => $i->id, 'code' => $i->code, 'name' => $i->name, 'status' => $i->status,
            'deadline' => $i->deadline, 'public_token' => $i->public_token,
        ])]);
    }
}
