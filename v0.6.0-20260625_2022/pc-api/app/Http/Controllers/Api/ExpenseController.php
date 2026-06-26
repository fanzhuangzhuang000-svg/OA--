<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ExpenseClaim;
use App\Models\ExpenseItem;
use App\Models\Project;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class ExpenseController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = ExpenseClaim::with(['user:id,name,username', 'project:id,name,project_no', 'approver:id,name', 'items']);
        if ($request->filled('status'))   $query->where('status', $request->status);
        if ($request->filled('category')) $query->where('category', $request->category);
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('claim_no', 'like', "%{$kw}%")
                  ->orWhere('description', 'like', "%{$kw}%")
                  ->orWhereHas('user', function ($uq) use ($kw) {
                      $uq->where('name', 'like', "%{$kw}%");
                  });
            });
        }
        if ($request->filled('user_id'))    $query->where('user_id', $request->user_id);
        if ($request->filled('project_id')) $query->where('project_id', $request->project_id);
        if ($request->filled('date_from')) $query->whereDate('created_at', '>=', $request->date_from);
        if ($request->filled('date_to'))   $query->whereDate('created_at', '<=', $request->date_to);

        $list = $query->orderBy('created_at', 'desc')->paginate($request->per_page ?? 15);

        // 加状态/分类的中文 label
        $list->getCollection()->transform(function ($c) {
            $c->status_label   = $this->statusLabel($c->status);
            $c->category_label = $this->categoryLabel($c->category);
            return $c;
        });

        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function show(Request $request, ExpenseClaim $claim): JsonResponse
    {
        $claim->load(['user:id,name,username', 'project:id,name,project_no', 'approver:id,name', 'items']);
        $claim->status_label   = $this->statusLabel($claim->status);
        $claim->category_label = $this->categoryLabel($claim->category);
        return response()->json(['code' => 0, 'data' => $claim]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'category'              => 'required|string',
            'description'           => 'nullable|string',
            'project_id'            => 'nullable|integer',
            'items'                 => 'required|array|min:1',
            'items.*.item_date'     => 'nullable|date',
            'items.*.description'   => 'nullable|string',
            'items.*.amount'        => 'required|numeric|min:0',
            'items.*.category'      => 'nullable|string',
        ]);
        $data['user_id']       = $request->user()->id;
        $data['status']        = 'submitted';
        $data['total_amount']  = collect($data['items'])->sum('amount');
        $data['claim_no']      = 'EXP' . date('Ymd') . strtoupper(Str::random(6));
        // 兜底: expense_claims.description NOT NULL
        if (empty($data['description'])) {
            $data['description'] = $data['category'] ?? '报销';
        }
        $items = $data['items']; unset($data['items']);
        $claim = ExpenseClaim::create($data);
        // 兜底: expense_items.item_date + description 都是 NOT NULL
        $today = now()->toDateString();
        foreach ($items as $item) {
            if (empty($item['item_date'])) {
                $item['item_date'] = $today;
            }
            if (empty($item['category'])) {
                $item['category'] = $data['category'] ?? '其他';
            }
            if (empty($item['description'])) {
                $item['description'] = $item['category'] ?? '报销明细';
            }
            $claim->items()->create($item);
        }
        $claim->load(['user', 'project', 'items']);
        return response()->json(['code' => 0, 'message' => '报销单已提交', 'data' => $claim]);
    }

    public function update(Request $request, ExpenseClaim $claim): JsonResponse
    {
        if ($claim->status !== 'draft' && $claim->status !== 'submitted') {
            return response()->json(['code' => 1001, 'message' => '只有草稿/待审批状态的报销单可以修改'], 422);
        }
        $data = $request->validate([
            'category'    => 'sometimes|string',
            'description' => 'sometimes|string|max:1000',
            'project_id'  => 'sometimes|nullable|integer',
            'items'       => 'sometimes|array|min:1',
            'items.*.item_date'   => 'required_with:items|date',
            'items.*.description' => 'required_with:items|string|max:200',
            'items.*.amount'      => 'required_with:items|numeric|min:0',
        ]);
        if (isset($data['items'])) {
            $data['total_amount'] = collect($data['items'])->sum('amount');
            $items = $data['items']; unset($data['items']);
            $claim->items()->delete();
            foreach ($items as $item) { $claim->items()->create($item); }
        }
        $claim->fill($data)->save();
        $claim->load(['user', 'project', 'items']);
        return response()->json(['code' => 0, 'message' => '已更新', 'data' => $claim]);
    }

    public function destroy(Request $request, ExpenseClaim $claim): JsonResponse
    {
        if ($claim->user_id !== $request->user()->id && !$request->user()->can('expense.delete')) {
            return response()->json(['code' => 1001, 'message' => '只能删除自己的报销单'], 403);
        }
        if (in_array($claim->status, ['approved', 'paid'])) {
            return response()->json(['code' => 1002, 'message' => '已审批/已支付的单据不能删除'], 422);
        }
        $claim->items()->delete();
        $claim->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    public function approve(Request $request, ExpenseClaim $claim): JsonResponse
    {
        $request->validate([
            'action'  => 'required|in:approved,rejected',
            'comment' => 'nullable|string|max:500',
        ]);
        if (!in_array($claim->status, ['submitted'], true)) {
            return response()->json(['code' => 1001, 'message' => '只能审批待审批状态的报销单'], 422);
        }
        $claim->update([
            'status'        => $request->action,
            'approver_id'   => $request->user()->id,
            'approved_at'   => now(),
            'reject_reason' => $request->action === 'rejected' ? $request->comment : null,
        ]);
        return response()->json(['code' => 0, 'message' => '审批完成']);
    }

    public function cancel(Request $request, ExpenseClaim $claim): JsonResponse
    {
        if ($claim->user_id !== $request->user()->id) {
            return response()->json(['code' => 1001, 'message' => '只能撤销自己的报销单'], 403);
        }
        if (in_array($claim->status, ['approved', 'paid'], true)) {
            return response()->json(['code' => 1002, 'message' => '已审批/已支付的单据不能撤销'], 422);
        }
        $claim->update(['status' => 'cancelled']);
        return response()->json(['code' => 0, 'message' => '已撤销']);
    }

    public function pay(Request $request, ExpenseClaim $claim): JsonResponse
    {
        $data = $request->validate([
            'paid_amount' => 'required|numeric|min:0',
        ]);
        if ($claim->status !== 'approved') {
            return response()->json(['code' => 1001, 'message' => '只有已审批的单据可以标记付款'], 422);
        }
        $claim->update([
            'status'      => 'paid',
            'paid_at'     => now(),
            'paid_amount' => $data['paid_amount'],
        ]);
        return response()->json(['code' => 0, 'message' => '已标记付款']);
    }

    public function myClaims(Request $request): JsonResponse
    {
        $list = $request->user()->expenseClaims()
            ->with(['project:id,name,project_no', 'items'])
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 15);
        $list->getCollection()->transform(function ($c) {
            $c->status_label   = $this->statusLabel($c->status);
            $c->category_label = $this->categoryLabel($c->category);
            return $c;
        });
        return response()->json(['code' => 0, 'data' => $list]);
    }

    // 报销统计
    public function stats(Request $request): JsonResponse
    {
        $uid = $request->user()->id;
        $total    = ExpenseClaim::where('user_id', $uid)->count();
        $pending  = ExpenseClaim::where('user_id', $uid)->where('status', 'submitted')->count();
        $approved = ExpenseClaim::where('user_id', $uid)->where('status', 'approved')->count();
        $paid     = ExpenseClaim::where('user_id', $uid)->where('status', 'paid')->count();
        $totalAmount = ExpenseClaim::where('user_id', $uid)->sum('total_amount');
        $paidAmount  = ExpenseClaim::where('user_id', $uid)->where('status', 'paid')->sum('paid_amount');
        return response()->json(['code' => 0, 'data' => compact('total', 'pending', 'approved', 'paid', 'totalAmount', 'paidAmount')]);
    }

    // 项目下拉
    public function projects(Request $request): JsonResponse
    {
        $projects = Project::select('id', 'name', 'project_no')->orderBy('name')->limit(200)->get();
        return response()->json(['code' => 0, 'data' => $projects]);
    }

    private function statusLabel(string $s): string
    {
        return match($s) {
            'draft'     => '草稿',
            'submitted' => '待审批',
            'approved'  => '已审批',
            'rejected'  => '已驳回',
            'paid'      => '已付款',
            'cancelled' => '已撤销',
            default     => $s,
        };
    }

    private function categoryLabel(string $c): string
    {
        return match($c) {
            'travel'        => '差旅费',
            'hospitality'   => '招待费',
            'office'        => '办公费',
            'transport'     => '交通费',
            'project_cost'  => '项目成本',
            'other'         => '其他',
            default         => $c,
        };
    }
}
