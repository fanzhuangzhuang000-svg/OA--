<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\TenderProject;
use App\Models\TenderBid;
use App\Models\TenderAttachment;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/**
 * V0.6.0 招标中心 — 内部 API
 *
 * 路由: /api/tenders
 *   GET    /tenders                       项目列表
 *   POST   /tenders                       新建项目 (草稿)
 *   GET    /tenders/{id}                  项目详情
 *   PUT    /tenders/{id}                  修改项目
 *   POST   /tenders/{id}/publish          发布 (生成 public_token)
 *   POST   /tenders/{id}/close            关闭
 *   POST   /tenders/{id}/cancel           取消
 *   POST   /tenders/{id}/evaluate         评标打分
 *   POST   /tenders/{id}/award            中标 (自动生成 PO + 应付)
 *   GET    /tenders/{id}/bids             投标列表
 *   POST   /tenders/{id}/bids             新建投标 (内部代理用, 正常走 PortalController)
 *   GET    /tenders/{id}/attachments      附件列表
 *   POST   /tenders/{id}/attachments      上传附件
 *   DELETE /tenders/{id}/attachments/{att} 删除附件
 */
class TenderController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $q = TenderProject::query();
        if ($kw = $request->input('keyword')) {
            $q->where(function ($qq) use ($kw) {
                $qq->where('name', 'like', "%{$kw}%")
                   ->orWhere('code', 'like', "%{$kw}%");
            });
        }
        if ($status = $request->input('status')) {
            $q->where('status', $status);
        }
        if ($pid = $request->input('project_id')) {
            $q->where('project_id', $pid);
        }
        $total = (clone $q)->count();
        $list  = $q->with(['awardedSupplier:id,name,code', 'creator:id,name', 'project:id,name,code'])
                    ->orderByDesc('id')
                    ->paginate($request->input('per_page', 20));
        return response()->json(['code' => 0, 'data' => ['items' => $list->items(), 'total' => $total]]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'        => 'required|string|max:200',
            'project_id'  => 'nullable|integer|exists:projects,id',
            'rfq_id'      => 'nullable|integer|exists:external_quote_requests,id',
            'type'        => 'nullable|in:rfq,tender,negotiation',
            'description' => 'nullable|string|max:2000',
            'required_items'   => 'nullable|array',
            'invited_supplier_ids' => 'nullable|array',
            'invited_supplier_ids.*' => 'integer|exists:suppliers,id',
            'deadline'    => 'nullable|date',
            'open_at'     => 'nullable|date',
            'score_config' => 'nullable|array',
        ]);
        $data['code'] = 'T-' . date('Ymd') . '-' . str_pad((string)(TenderProject::whereDate('created_at', today())->count() + 1), 3, '0', STR_PAD_LEFT);
        $data['status']      = 'draft';
        $data['public_token'] = (string) Str::uuid();
        $data['created_by']  = $request->user()->id;
        $t = TenderProject::create($data);
        return response()->json(['code' => 0, 'data' => $t], 201);
    }

    public function show(int $id): JsonResponse
    {
        $t = TenderProject::with([
            'project:id,name,code',
            'creator:id,name',
            'awardedSupplier:id,name,code',
            'attachments' => fn($q) => $q->whereNull('tender_bid_id'),
        ])->findOrFail($id);
        // 投标摘要 (轻量, 不含 items)
        $bids = $t->bids()->with('supplier:id,name,code')->orderBy('total_score', 'desc')->get();
        return response()->json(['code' => 0, 'data' => array_merge($t->toArray(), ['bids_summary' => $bids])]);
    }

    public function update(Request $request, int $id): JsonResponse
    {
        $t = TenderProject::findOrFail($id);
        if (in_array($t->status, ['awarded', 'cancelled', 'closed'])) {
            return response()->json(['code' => 1001, 'message' => '该状态不可修改'], 422);
        }
        $data = $request->validate([
            'name'      => 'sometimes|required|string|max:200',
            'description' => 'nullable|string|max:2000',
            'required_items'   => 'nullable|array',
            'invited_supplier_ids' => 'nullable|array',
            'invited_supplier_ids.*' => 'integer|exists:suppliers,id',
            'deadline'  => 'nullable|date',
            'open_at'   => 'nullable|date',
            'score_config' => 'nullable|array',
        ]);
        $t->fill($data)->save();
        return response()->json(['code' => 0, 'data' => $t]);
    }

    public function publish(int $id): JsonResponse
    {
        $t = TenderProject::findOrFail($id);
        if ($t->status !== 'draft') {
            return response()->json(['code' => 1001, 'message' => '仅草稿状态可发布'], 422);
        }
        $t->status     = 'bidding';
        $t->publish_at = now();
        if (!$t->public_token) {
            $t->public_token = (string) Str::uuid();
        }
        $t->save();
        return response()->json(['code' => 0, 'message' => '已发布', 'data' => $t]);
    }

    public function close(int $id): JsonResponse
    {
        $t = TenderProject::findOrFail($id);
        $t->status = 'closed';
        $t->save();
        return response()->json(['code' => 0, 'message' => '已关闭']);
    }

    public function cancel(int $id): JsonResponse
    {
        $t = TenderProject::findOrFail($id);
        $t->status = 'cancelled';
        $t->save();
        return response()->json(['code' => 0, 'message' => '已取消']);
    }

    // 评标打分 (内部用) — 接收 { bid_id, scores: { technical, price, business } }
    public function evaluate(Request $request, int $id): JsonResponse
    {
        $data = $request->validate([
            'evaluations' => 'required|array|min:1',
            'evaluations.*.bid_id'   => 'required|integer|exists:tender_bids,id',
            'evaluations.*.technical' => 'required|numeric|min:0|max:100',
            'evaluations.*.price'     => 'required|numeric|min:0|max:100',
            'evaluations.*.business'  => 'required|numeric|min:0|max:100',
        ]);
        $t = TenderProject::findOrFail($id);
        // 评分权重 (从 score_config 读, 缺省 40/40/20)
        $cfg = $t->score_config ?: ['technical' => 40, 'price' => 40, 'business' => 20];
        $wT = (float)($cfg['technical'] ?? 40);
        $wP = (float)($cfg['price'] ?? 40);
        $wB = (float)($cfg['business'] ?? 20);
        $wSum = max(0.0001, $wT + $wP + $wB);

        foreach ($data['evaluations'] as $e) {
            $bid = TenderBid::where('tender_project_id', $id)->find($e['bid_id']);
            if (!$bid) continue;
            $score = [
                'technical' => (float)$e['technical'],
                'price'     => (float)$e['price'],
                'business'  => (float)$e['business'],
            ];
            $total = round(($score['technical'] * $wT + $score['price'] * $wP + $score['business'] * $wB) / $wSum, 2);
            $bid->scores = $score;
            $bid->total_score = $total;
            $bid->status = 'shortlisted';
            $bid->save();
        }
        $t->status = 'evaluating';
        $t->save();
        return response()->json(['code' => 0, 'message' => '已记录评分']);
    }

    // 中标 (自动生成 PO + 应付)
    public function award(Request $request, int $id): JsonResponse
    {
        $data = $request->validate([
            'bid_id' => 'required|integer|exists:tender_bids,id',
        ]);
        $t = TenderProject::with('bids')->findOrFail($id);
        if (in_array($t->status, ['awarded', 'cancelled', 'closed'])) {
            return response()->json(['code' => 1001, 'message' => '该状态不可定标'], 422);
        }
        $bid = $t->bids()->find($data['bid_id']);
        if (!$bid) {
            return response()->json(['code' => 1001, 'message' => '投标不属于该项目'], 422);
        }
        // 中标
        $bid->status = 'awarded';
        $bid->save();
        $t->bids()->where('id', '!=', $bid->id)->update(['status' => 'rejected']);

        $t->awarded_bid_id      = $bid->id;
        $t->awarded_supplier_id = $bid->supplier_id;
        $t->awarded_at          = now();
        $t->status              = 'awarded';
        $t->save();

        // 自动落账: PO + 应付
        $result = ['po' => null, 'payable' => null];
        try {
            $po = \App\Models\PurchaseOrder::create([
                'code'           => 'PO-' . date('Ymd') . '-' . str_pad((string)(\App\Models\PurchaseOrder::whereDate('created_at', today())->count() + 1), 4, '0', STR_PAD_LEFT),
                'supplier_id'    => $bid->supplier_id,
                'tender_id'      => $t->id,
                'title'          => "招标中标: {$t->name}",
                'total_amount'   => $bid->total_amount,
                'status'         => 'pending',
                'created_by'     => $request->user()->id,
            ]);
            $result['po'] = $po->only(['id', 'code', 'total_amount']);

            $payable = \App\Models\Payable::create([
                'ref_no'         => 'PAY-' . date('Ymd') . '-' . str_pad((string)(\App\Models\Payable::whereDate('created_at', today())->count() + 1), 4, '0', STR_PAD_LEFT),
                'supplier_id'    => $bid->supplier_id,
                'po_id'          => $po->id,
                'tender_id'      => $t->id,
                'amount'         => $bid->total_amount,
                'paid_amount'    => 0,
                'remaining_amount' => $bid->total_amount,
                'due_date'       => now()->addDays(30)->toDateString(),
                'description'    => "招标中标应付款: {$t->name}",
                'status'         => 'pending',
            ]);
            $result['payable'] = $payable->only(['id', 'ref_no', 'amount']);
        } catch (\Exception $e) {
            \Log::warning('招标中标自动落账失败: ' . $e->getMessage());
        }

        return response()->json(['code' => 0, 'message' => '定标成功', 'data' => ['tender' => $t, 'bid' => $bid, 'auto' => $result]]);
    }

    // 投标列表 (内部)
    public function bids(Request $request, int $id): JsonResponse
    {
        $t = TenderProject::findOrFail($id);
        $bids = $t->bids()
                   ->with(['supplier:id,name,code', 'items'])
                   ->orderByRaw('total_score DESC NULLS LAST, total_amount ASC')
                   ->get();
        return response()->json(['code' => 0, 'data' => $bids]);
    }

    // 内部代供应商提交投标 (调试/E2E 用)
    public function storeBid(Request $request, int $id): JsonResponse
    {
        $data = $request->validate([
            'supplier_id' => 'required|integer|exists:suppliers,id',
            'total_amount' => 'required|numeric|min:0',
            'lead_time_days' => 'nullable|integer|min:0',
            'technical_proposal' => 'nullable|string|max:5000',
            'remark' => 'nullable|string|max:1000',
            'items'  => 'nullable|array',
            'items.*.name'       => 'required|string',
            'items.*.spec'       => 'nullable|string',
            'items.*.unit'       => 'nullable|string',
            'items.*.quantity'   => 'required|numeric|min:0',
            'items.*.unit_price' => 'required|numeric|min:0',
            'auto_submit' => 'sometimes|boolean',
        ]);
        $t = TenderProject::findOrFail($id);
        if (!in_array($t->status, ['bidding', 'published'])) {
            return response()->json(['code' => 1001, 'message' => '该项目不在投标期'], 422);
        }
        // 防止重复投标
        $exists = $t->bids()->where('supplier_id', $data['supplier_id'])->first();
        if ($exists) {
            return response()->json(['code' => 1002, 'message' => '该供应商已投标'], 422);
        }
        $bid = $t->bids()->create([
            'supplier_id'    => $data['supplier_id'],
            'total_amount'   => $data['total_amount'],
            'lead_time_days' => $data['lead_time_days'] ?? null,
            'technical_proposal' => $data['technical_proposal'] ?? null,
            'remark'         => $data['remark'] ?? null,
            'status'         => !empty($data['auto_submit']) ? 'submitted' : 'draft',
            'submitted_at'   => !empty($data['auto_submit']) ? now() : null,
            'code'           => 'BID-' . date('Ymd') . '-' . str_pad((string)(TenderBid::whereDate('created_at', today())->count() + 1), 3, '0', STR_PAD_LEFT),
        ]);
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
        return response()->json(['code' => 0, 'data' => $bid->load('items', 'supplier')], 201);
    }

    // 附件上传 (内部 — 招标文件)
    public function uploadAttachment(Request $request, int $id): JsonResponse
    {
        $request->validate([
            'file'     => 'required|file|max:51200',
            'category' => 'nullable|in:tender_doc,drawing,technical,qualification,other',
            'visibility' => 'nullable|in:public,eval_only',
        ]);
        $t = TenderProject::findOrFail($id);
        $file = $request->file('file');
        $ext  = strtolower($file->getClientOriginalExtension());
        $dir  = "tenders/{$t->id}/" . date('Ymd');
        $path = $file->storeAs($dir, uniqid('att_') . ($ext ? ".{$ext}" : ''), 'public');
        $att  = TenderAttachment::create([
            'tender_project_id' => $t->id,
            'uploaded_by_user_id' => $request->user()->id,
            'file_name' => $file->getClientOriginalName(),
            'file_path' => $path,
            'mime_type' => $file->getMimeType(),
            'file_size' => $file->getSize(),
            'category'  => $request->input('category', 'other'),
            'visibility' => $request->input('visibility', 'public'),
        ]);
        return response()->json(['code' => 0, 'data' => $att]);
    }

    public function listAttachments(int $id): JsonResponse
    {
        $list = TenderAttachment::where('tender_project_id', $id)
                                ->whereNull('tender_bid_id')
                                ->orderBy('id')->get();
        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function deleteAttachment(int $id, int $att): JsonResponse
    {
        $a = TenderAttachment::where('tender_project_id', $id)->findOrFail($att);
        \Storage::disk('public')->delete($a->file_path);
        $a->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }
}
