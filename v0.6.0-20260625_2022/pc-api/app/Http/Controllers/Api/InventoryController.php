<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Support\AuthScope;
use App\Models\InventoryItem;
use App\Models\InventoryCategory;
use App\Models\StockRecord;
use App\Models\Warehouse;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\StreamedResponse;

class InventoryController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = InventoryItem::with('warehouse');
        if ($request->filled('category')) $query->where('category', $request->category);
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('name', 'like', "%{$kw}%")
                  ->orWhere('code', 'like', "%{$kw}%")
                  ->orWhere('specification', 'like', "%{$kw}%");
            });
        }
        if ($request->filled('warehouse_id')) $query->where('warehouse_id', $request->warehouse_id);
        if ($request->filled('low_stock')) {
            $query->whereColumn('current_stock', '<=', 'safety_stock');
        }

        $list = $query->with(['warehouse:id,name,code', 'categoryRef:id,name'])
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 15);

        // 补一个 low_stock 标志位（前端可读）
        $list->getCollection()->transform(function ($it) {
            $it->is_low_stock = $it->current_stock <= $it->safety_stock;
            return $it;
        });

        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function show(Request $request, InventoryItem $inventoryItem): JsonResponse
    {
        $inventoryItem->load('warehouse', 'stockRecords.operator:id,name');
        $inventoryItem->is_low_stock = $inventoryItem->current_stock <= $inventoryItem->safety_stock;
        return response()->json(['code' => 0, 'data' => $inventoryItem]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'required|string|max:200',
            'code'         => 'required|string|max:64',
            'category'     => 'nullable|string|max:50',
            'category_id'  => 'nullable|integer',
            'specification'=> 'nullable|string|max:255',
            'unit'         => 'required|string|max:20',
            'safety_stock' => 'nullable|integer',
            'current_stock'=> 'nullable|integer',
            'cost_price'   => 'nullable|numeric',
            'sell_price'   => 'nullable|numeric',
            'warehouse_id' => 'nullable|integer',
            'location'     => 'nullable|string|max:100',
            'has_serial'   => 'nullable|boolean',
            'status'       => 'nullable|string',
        ]);
        $data['status'] = $data['status'] ?? 'active';

        // 同步 category_id ↔ category 字符串：
        // 1) 若传了 category_id, 解析分类名, 把 category 字符串同步为分类名
        // 2) 若只传了 category 字符串, 不动 (保持旧行为)
        if (!empty($data['category_id'])) {
            $cat = InventoryCategory::find($data['category_id']);
            if ($cat) {
                $data['category'] = $cat->name;
            } else {
                return response()->json(['code' => 1001, 'message' => '分类不存在'], 422);
            }
        } elseif (empty($data['category'])) {
            return response()->json(['code' => 1001, 'message' => 'category 或 category_id 至少传一个'], 422);
        }

        $item = InventoryItem::create($data);
        return response()->json(['code' => 0, 'message' => '物料已创建', 'data' => $item->load('warehouse', 'categoryRef')]);
    }

    public function update(Request $request, InventoryItem $inventoryItem): JsonResponse
    {
        $data = $request->validate([
            'name'         => 'sometimes|required|string|max:200',
            'code'         => 'sometimes|string|max:64',
            'category'     => 'nullable|string|max:50',
            'category_id'  => 'nullable|integer',
            'specification'=> 'nullable|string|max:255',
            'unit'         => 'sometimes|string|max:20',
            'safety_stock' => 'sometimes|integer|min:0',
            'cost_price'   => 'nullable|numeric|min:0',
            'sell_price'   => 'nullable|numeric|min:0',
            'warehouse_id' => 'sometimes|nullable|integer',
            'location'     => 'nullable|string|max:100',
            'has_serial'   => 'nullable|boolean',
            'status'       => 'nullable|string|in:active,inactive',
        ]);

        // 同步 category_id ↔ category 字符串
        if (!empty($data['category_id'])) {
            $cat = InventoryCategory::find($data['category_id']);
            if ($cat) {
                $data['category'] = $cat->name;
            }
        }

        $inventoryItem->update($data);
        return response()->json(['code' => 0, 'message' => '已更新', 'data' => $inventoryItem->load('warehouse', 'categoryRef')]);
    }

    public function destroy(Request $request, InventoryItem $inventoryItem): JsonResponse
    {
        if ($inventoryItem->current_stock > 0) {
            return response()->json(['code' => 1001, 'message' => '当前库存 > 0，不允许删除（请先做库存出库）'], 422);
        }
        if (\App\Models\StockRecord::where('inventory_item_id', $inventoryItem->id)->exists()) {
            return response()->json(['code' => 1003, 'message' => '该物料存在出入库流水记录，不允许删除（请使用"禁用"功能）'], 422);
        }
        $inventoryItem->delete();
        return response()->json(['code' => 0, 'message' => '已删除']);
    }

    /**
     * POST /api/inventory/batch-delete
     * body: { ids: [1,2,3] }
     * 仅删除: 库存=0 且 无流水记录 (与 destroy() 同规则)
     */
    public function batchDelete(Request $request): JsonResponse
    {
        $data = $request->validate([
            'ids'   => 'required|array|min:1|max:200',
            'ids.*' => 'integer|min:1',
        ]);
        $ids = array_unique(array_map('intval', $data['ids']));

        $deleted = [];
        $skipped = [];

        DB::beginTransaction();
        try {
            foreach ($ids as $id) {
                $item = InventoryItem::find($id);
                if (!$item) {
                    $skipped[] = ['id' => $id, 'reason' => '物料不存在'];
                    continue;
                }
                if ($item->current_stock > 0) {
                    $skipped[] = ['id' => $id, 'name' => $item->name, 'reason' => "当前库存 {$item->current_stock} > 0"];
                    continue;
                }
                if (\App\Models\StockRecord::where('inventory_item_id', $id)->exists()) {
                    $skipped[] = ['id' => $id, 'name' => $item->name, 'reason' => '存在出入库流水记录'];
                    continue;
                }
                $item->delete();
                $deleted[] = $id;
            }
            DB::commit();
        } catch (\Throwable $e) {
            DB::rollBack();
            return response()->json(['code' => 1001, 'message' => '批量删除失败: ' . $e->getMessage()], 422);
        }

        return response()->json([
            'code'    => 0,
            'message' => '批量删除完成',
            'data'    => [
                'deleted' => $deleted,
                'deleted_count' => count($deleted),
                'skipped' => $skipped,
                'skipped_count' => count($skipped),
            ],
        ]);
    }

    /**
     * POST /api/inventory/batch-update
     * body: { ids: [1,2,3], fields: { warehouse_id: 11, status: 'inactive', unit: '台' } }
     * 仅白名单字段: warehouse_id / status / unit / safety_stock / min_stock / location / category_id
     */
    public function batchUpdate(Request $request): JsonResponse
    {
        $data = $request->validate([
            'ids'         => 'required|array|min:1|max:200',
            'ids.*'       => 'integer|min:1',
            'fields'      => 'required|array|min:1',
        ]);

        $ids = array_unique(array_map('intval', $data['ids']));
        $input = $data['fields'];

        // 白名单: 只允许这些字段被批量改
        $allowed = ['warehouse_id', 'status', 'unit', 'safety_stock', 'min_stock', 'location', 'category_id', 'specification'];
        $fields = [];
        foreach ($allowed as $k) {
            if (array_key_exists($k, $input)) {
                $fields[$k] = $input[$k];
            }
        }
        if (empty($fields)) {
            return response()->json(['code' => 1001, 'message' => '没有可更新的字段'], 422);
        }

        // 单字段类型校验
        if (isset($fields['warehouse_id'])) {
            if (!is_numeric($fields['warehouse_id']) || !\App\Models\Warehouse::find($fields['warehouse_id'])) {
                return response()->json(['code' => 1002, 'message' => '目标仓库不存在'], 422);
            }
            $fields['warehouse_id'] = (int) $fields['warehouse_id'];
        }
        if (isset($fields['category_id'])) {
            $fields['category_id'] = $fields['category_id'] ? (int) $fields['category_id'] : null;
        }
        if (isset($fields['status']) && !in_array($fields['status'], ['active', 'inactive'], true)) {
            return response()->json(['code' => 1003, 'message' => 'status 必须是 active/inactive'], 422);
        }
        foreach (['min_stock', 'safety_stock'] as $n) {
            if (isset($fields[$n]) && (!is_numeric($fields[$n]) || (int) $fields[$n] < 0)) {
                return response()->json(['code' => 1004, 'message' => "{$n} 必须是非负整数"], 422);
            }
        }

        $updated = InventoryItem::whereIn('id', $ids)->update($fields);

        // 同步 category 字符串列 (与 store() 一致)
        if (isset($fields['category_id']) && $fields['category_id']) {
            $cat = \App\Models\InventoryCategory::find($fields['category_id']);
            if ($cat) {
                InventoryItem::whereIn('id', $ids)->update(['category' => $cat->name]);
            }
        }

        return response()->json([
            'code'    => 0,
            'message' => '批量更新完成',
            'data'    => [
                'updated_count' => $updated,
                'fields'        => $fields,
            ],
        ]);
    }

    /**
     * POST /api/inventory/batch-export
     * body: { ids: [1,2,3] (可选, 空则按当前搜索条件) } 或 query: keyword/warehouse_id/category_id/status
     * 流式 CSV 下载 (UTF-8 BOM)
     */
    public function batchExport(Request $request): \Symfony\Component\HttpFoundation\StreamedResponse
    {
        // V0.4.7 收口: 导出只允许 admin/finance 走 ALL, 其他角色用各自 scope
        // 拦截违规的 ?scope=all (InventoryItem 暂未挂 scope, 但避免误开 ALL)
        $user = $request->user();
        if ($request->boolean('scope_all') && !AuthScope::isUnrestricted($user)) {
            abort(403, '权限不足: 仅管理员/财务可导出全部库存');
        }

        $ids = $request->input('ids');
        if (is_string($ids)) {
            $ids = array_filter(explode(',', $ids));
            $ids = array_map('intval', $ids);
        }
        $ids = is_array($ids) ? array_filter(array_map('intval', $ids)) : [];

        $query = InventoryItem::with(['warehouse:id,name', 'categoryRef:id,name']);
        if (!empty($ids)) {
            $query->whereIn('id', $ids);
        } else {
            if ($request->filled('keyword')) {
                $kw = $request->keyword;
                $query->where(function ($q) use ($kw) {
                    $q->where('name', 'like', "%{$kw}%")
                      ->orWhere('code', 'like', "%{$kw}%")
                      ->orWhere('specification', 'like', "%{$kw}%");
                });
            }
            if ($request->filled('warehouse_id')) $query->where('warehouse_id', (int) $request->warehouse_id);
            if ($request->filled('category_id'))  $query->where('category_id', (int) $request->category_id);
            if ($request->filled('status'))       $query->where('status', $request->status);
        }

        $filename = 'inventory_export_' . date('Ymd_His') . '.csv';
        $headers = [
            'Content-Type'        => 'text/csv; charset=UTF-8',
            'Content-Disposition' => 'attachment; filename="' . $filename . '"',
            'Pragma'              => 'no-cache',
            'Cache-Control'       => 'must-revalidate, post-check=0, pre-check=0',
            'Expires'             => '0',
        ];

        $callback = function () use ($query) {
            $handle = fopen('php://output', 'w');
            // UTF-8 BOM
            fwrite($handle, "\xEF\xBB\xBF");
            // 表头
            fputcsv($handle, [
                '编码', '名称', '分类', '规格', '单位',
                '当前库存', '最小库存', '安全库存', '最低库存',
                '仓库', '货位', '状态', '成本价', '销售价', '更新时间',
            ]);
            // 分块流式输出, 避免内存爆
            $query->orderBy('id')->chunk(200, function ($items) use ($handle) {
                foreach ($items as $it) {
                    fputcsv($handle, [
                        $it->code,
                        $it->name,
                        $it->categoryRef?->name ?: $it->category,
                        $it->specification,
                        $it->unit,
                        $it->current_stock,
                        $it->min_stock,
                        $it->safety_stock,
                        $it->min_stock,
                        $it->warehouse?->name,
                        $it->location,
                        $it->status,
                        $it->cost_price,
                        $it->sell_price,
                        optional($it->updated_at)->format('Y-m-d H:i:s'),
                    ]);
                }
            });
            fclose($handle);
        };

        return response()->stream($callback, 200, $headers);
    }

    public function stockRecords(Request $request): JsonResponse
    {
        $query = StockRecord::with(['inventoryItem:id,name,code,unit', 'warehouse:id,name,code', 'operator:id,name', 'project:id,name']);
        if ($request->filled('type'))         $query->where('type', $request->type);
        if ($request->filled('warehouse_id')) $query->where('warehouse_id', $request->warehouse_id);
        if ($request->filled('keyword')) {
            $kw = $request->keyword;
            $query->where(function ($q) use ($kw) {
                $q->where('record_no', 'like', "%{$kw}%")
                  ->orWhereHas('inventoryItem', function ($iq) use ($kw) {
                      $iq->where('name', 'like', "%{$kw}%")->orWhere('code', 'like', "%{$kw}%");
                  });
            });
        }
        if ($request->filled('date_from')) $query->whereDate('created_at', '>=', $request->date_from);
        if ($request->filled('date_to'))   $query->whereDate('created_at', '<=', $request->date_to);

        $list = $query->orderBy('created_at', 'desc')->paginate($request->per_page ?? 15);

        $list->getCollection()->transform(function ($r) {
            $r->type_label = $this->typeLabel($r->type);
            // 动态 load 往来单位 (party_type 决定 Customer / Supplier)
            $r->load('party');
            return $r;
        });

        return response()->json(['code' => 0, 'data' => $list]);
    }

    public function warehouses(): JsonResponse { return response()->json(['code' => 0, 'data' => Warehouse::all()]); }

    /**
     * 入库（采购/退库）：增加 current_stock
     * body: {
     *   inventory_item_id, warehouse_id, quantity, type=inbound|return,
     *   party_type=customer|supplier, party_id, settle_id?, project_id?, remark?
     * }
     */
    public function stockIn(Request $request): JsonResponse
    {
        $data = $request->validate([
            'inventory_item_id' => 'required|exists:inventory_items,id',
            'warehouse_id'      => 'required|exists:warehouses,id',
            'quantity'          => 'required|integer|min:1',
            'type'              => 'required|string|in:inbound,return',
            'party_type'        => 'nullable|string|in:customer,supplier',
            'party_id'          => 'nullable|integer',
            'settle_id'         => 'nullable|integer',
            'project_id'        => 'nullable|integer',
            'remark'            => 'nullable|string|max:500',
            'logistics_company' => 'nullable|string|max:50',
            'logistics_no'      => 'nullable|string|max:100',
        ]);
        // 入库默认往来单位为供应商
        if (empty($data['party_type'])) {
            $data['party_type'] = 'supplier';
        }
        if (empty($data['party_id'])) {
            $data['party_id'] = null;
        }
        if (empty($data['settle_id'])) {
            $data['settle_id'] = $data['party_id'];
        }
        return $this->doStock($data, $request, 'RK');
    }

    /**
     * 出库（领用/销售）：减少 current_stock
     * body: {
     *   inventory_item_id, warehouse_id, quantity, type=outbound|sale|scrap,
     *   out_method=pickup|transfer|sale|scrap|lend|gift,
     *   party_type=customer|supplier, party_id, settle_id?, project_id?, remark?
     * }
     */
    public function stockOut(Request $request): JsonResponse
    {
        $data = $request->validate([
            'inventory_item_id' => 'required|exists:inventory_items,id',
            'warehouse_id'      => 'required|exists:warehouses,id',
            'quantity'          => 'required|integer|min:1',
            'type'              => 'required|string|in:outbound,sale,scrap',
            'out_method'        => 'nullable|string|in:pickup,transfer,sale,scrap,lend,gift',
            'party_type'        => 'nullable|string|in:customer,supplier',
            'party_id'          => 'nullable|integer',
            'settle_id'         => 'nullable|integer',
            'project_id'        => 'nullable|integer',
            'remark'            => 'nullable|string|max:500',
        ]);
        // 出库默认往来单位为客户
        if (empty($data['party_type'])) {
            $data['party_type'] = 'customer';
        }
        if (empty($data['party_id'])) {
            $data['party_id'] = null;
        }
        if (empty($data['settle_id'])) {
            $data['settle_id'] = $data['party_id'];
        }
        return $this->doStock($data, $request, 'CK');
    }

    /**
     * $prefix: RK (入库) / CK (出库) - 用于自动生成单号
     */
    private function doStock(array $data, Request $request, string $prefix = 'SR'): JsonResponse
    {
        $isInbound = in_array($data['type'], ['inbound', 'return'], true);
        $isOutbound = in_array($data['type'], ['outbound', 'sale', 'scrap'], true);

        try {
            $result = DB::transaction(function () use ($data, $request, $isInbound, $isOutbound, $prefix) {
                $item = InventoryItem::lockForUpdate()->findOrFail($data['inventory_item_id']);
                if ($isOutbound && $item->current_stock < $data['quantity']) {
                    throw new \RuntimeException("库存不足（当前 {$item->current_stock}，申请出库 {$data['quantity']}）");
                }
                $newStock = $isInbound
                    ? $item->current_stock + $data['quantity']
                    : $item->current_stock - $data['quantity'];
                $item->current_stock = $newStock;
                $item->save();

                // 自动生成单号: PREFIX-YYYYMMDD-XXXX (XXXX 当日累计顺序)
                $today = date('Ymd');
                $pattern = $prefix . '-' . $today . '-%';
                $todayCount = StockRecord::where('record_no', 'like', $pattern)->count();
                $seq = str_pad((string)($todayCount + 1), 4, '0', STR_PAD_LEFT);
                $recordNo = $prefix . '-' . $today . '-' . $seq;

                $record = StockRecord::create([
                    'record_no'         => $recordNo,
                    'inventory_item_id' => $item->id,
                    'warehouse_id'      => $data['warehouse_id'],
                    'type'              => $data['type'],
                    'quantity'          => $data['quantity'],
                    'remaining_stock'   => $newStock,
                    'party_type'        => $data['party_type'] ?? null,
                    'party_id'          => $data['party_id'] ?? null,
                    'settle_id'         => $data['settle_id'] ?? null,
                    'project_id'        => $data['project_id'] ?? null,
                    'out_method'        => $data['out_method'] ?? null,
                    'logistics_company' => $data['logistics_company'] ?? null,
                    'logistics_no'      => $data['logistics_no'] ?? null,
                    'operator_id'       => $request->user()->id,
                    'remark'            => $data['remark'] ?? null,
                ]);
                return $record;
            });
        } catch (\Throwable $e) {
            return response()->json(['code' => 1002, 'message' => $e->getMessage()], 422);
        }

        return response()->json(['code' => 0, 'message' => '操作成功', 'data' => $result->load(['inventoryItem', 'warehouse', 'operator:id,name', 'project:id,name'])]);
    }

    public function lowStock(Request $request): JsonResponse
    {
        $items = InventoryItem::with('warehouse')
            ->whereColumn('current_stock', '<=', 'safety_stock')
            ->orderBy('current_stock', 'asc')
            ->limit(50)
            ->get();
        return response()->json(['code' => 0, 'data' => $items]);
    }

    public function stats(Request $request): JsonResponse
    {
        $totalItems   = InventoryItem::count();
        $totalStock   = InventoryItem::sum('current_stock');
        $lowStock     = InventoryItem::whereColumn('current_stock', '<=', 'safety_stock')->count();
        $totalValue   = InventoryItem::selectRaw('SUM(current_stock * cost_price) as v')->value('v') ?? 0;
        $warehouses   = Warehouse::count();

        // 近 30 天出入库次数
        $monthStart = now()->subDays(30);
        $inboundCount  = StockRecord::whereIn('type', ['inbound', 'return'])->where('created_at', '>=', $monthStart)->count();
        $outboundCount = StockRecord::whereIn('type', ['outbound', 'sale', 'scrap'])->where('created_at', '>=', $monthStart)->count();

        return response()->json(['code' => 0, 'data' => compact('totalItems', 'totalStock', 'lowStock', 'totalValue', 'warehouses', 'inboundCount', 'outboundCount')]);
    }

    private function typeLabel(string $t): string
    {
        return match($t) {
            'inbound'  => '入库',
            'return'   => '退库',
            'outbound' => '出库',
            'sale'     => '销售',
            'scrap'    => '报废',
            default    => $t,
        };
    }

    // ========== v0.3.7.9 库存×分类打通 ==========

    /**
     * GET /api/inventory/tree-with-counts
     * 完整分类树 + 每节点物品数 + 低库存数（递归聚合子分类）
     */
    public function treeWithCounts(Request $request): JsonResponse
    {
        // 1) 拉全部分类
        $flat = InventoryCategory::orderBy('sort_order')->orderBy('id')->get();

        // 2) 按父聚合 item 总数和 low_stock 数量
        //    schema 字段: current_stock / safety_stock（min_stock 已加但低库存判断沿用 safety_stock，保持和 stats() 一致）
        $stats = DB::table('inventory_items')
            ->selectRaw('category_id,
                COUNT(*) as item_count,
                SUM(CASE WHEN current_stock <= safety_stock AND safety_stock > 0 THEN 1 ELSE 0 END) as low_stock_count')
            ->whereNotNull('category_id')
            ->groupBy('category_id')
            ->get()
            ->keyBy('category_id');

        // 3) 构造 id -> node (含递归聚合字段)
        $byId = [];
        foreach ($flat as $c) {
            $s = $stats->get($c->id);
            $c->item_count      = (int) ($s->item_count ?? 0);
            $c->low_stock_count = (int) ($s->low_stock_count ?? 0);
            $c->children_list   = [];
            $byId[$c->id] = $c;
        }

        // 4) 拼树 + 递归聚合子分类的计数
        $roots = [];
        foreach ($byId as $c) {
            if ($c->parent_id && isset($byId[$c->parent_id])) {
                $byId[$c->parent_id]->children_list[] = $c;
            } else {
                $roots[] = $c;
            }
        }

        $aggregate = function ($node) use (&$aggregate, $byId) {
            $items = $node->item_count;
            $low   = $node->low_stock_count;
            foreach ($node->children_list as $child) {
                [$ci, $cl] = $aggregate($child);
                $items += $ci;
                $low   += $cl;
            }
            $node->total_item_count      = $items;
            $node->total_low_stock_count = $low;
            return [$items, $low];
        };
        foreach ($roots as $r) $aggregate($r);

        return response()->json(['code' => 0, 'data' => $roots]);
    }

    /**
     * POST /api/inventory/items/batch-import
     * multipart/form-data 字段 file
     * 支持 CSV/Excel（自动检测 .xlsx/.xls 用 SimpleXlsx 风格实现，CSV 用 fgetcsv）
     * 列定义（首行表头必填，UTF-8 BOM 自动跳过）：
     *   name 名称* | code 编码* | category_name 分类名称* | specification 规格 | unit 单位* |
     *   min_stock 最低库存 | safety_stock 安全库存 | current_stock 当前库存 |
     *   cost_price 成本价 | sell_price 销售价 | warehouse_name 仓库 | location 库位
     * 返回 {created, skipped, errors}
     */
    public function batchImport(Request $request): JsonResponse
    {
        $request->validate([
            'file' => 'required|file|max:10240', // 10MB
        ]);

        $file = $request->file('file');
        $ext  = strtolower($file->getClientOriginalExtension());
        if (!in_array($ext, ['csv', 'xlsx', 'xls'], true)) {
            return response()->json(['code' => 1001, 'message' => '仅支持 CSV/XLS/XLSX 文件'], 422);
        }

        $rows = $this->parseSpreadsheet($file->getRealPath(), $ext);
        if (empty($rows)) {
            return response()->json(['code' => 1001, 'message' => '文件为空或解析失败'], 422);
        }

        // 表头 → 字段映射
        $header = array_map(function ($h) {
            $h = preg_replace('/^\xEF\xBB\xBF/', '', (string) $h); // 去 BOM
            $h = trim((string) $h);
            $h = strtolower($h);
            $map = [
                '名称' => 'name', 'name' => 'name',
                '编码' => 'code', '物料编码' => 'code', 'code' => 'code',
                '分类' => 'category_name', '分类名称' => 'category_name', 'category' => 'category_name', 'category_name' => 'category_name',
                '规格' => 'specification', '规格型号' => 'specification', 'specification' => 'specification',
                '单位' => 'unit', 'unit' => 'unit',
                '最低库存' => 'min_stock', 'min_stock' => 'min_stock',
                '安全库存' => 'safety_stock', 'safety_stock' => 'safety_stock',
                '当前库存' => 'current_stock', 'current_stock' => 'current_stock',
                '成本价' => 'cost_price', 'cost_price' => 'cost_price',
                '销售价' => 'sell_price', 'sell_price' => 'sell_price',
                '仓库' => 'warehouse_name', 'warehouse_name' => 'warehouse_name',
                '库位' => 'location', 'location' => 'location',
            ];
            return $map[$h] ?? null;
        }, $rows[0]);

        // 检查关键列
        $idxName = array_search('name', $header, true);
        $idxCode = array_search('code', $header, true);
        $idxCat  = array_search('category_name', $header, true);
        $idxUnit = array_search('unit', $header, true);
        if ($idxName === false || $idxCode === false || $idxCat === false || $idxUnit === false) {
            return response()->json([
                'code'    => 1001,
                'message' => '表头缺少必填列: name, code, category_name, unit',
                'header'  => $header,
            ], 422);
        }

        // 预加载分类 + 仓库缓存（按名查 id）
        $categories = InventoryCategory::all()->keyBy('name');
        $warehouses = Warehouse::all()->keyBy('name');

        $created = [];
        $skipped = [];
        $errors  = [];

        // 已有 code 集合
        $existingCodes = InventoryItem::pluck('code')->map(fn($c) => (string) $c)->flip()->toArray();

        foreach (array_slice($rows, 1) as $lineNo => $row) {
            // 跳过空行
            if (!is_array($row) || count(array_filter($row, fn($v) => $v !== null && $v !== '')) === 0) {
                continue;
            }
            $get = function ($key) use ($row, $header) {
                $i = array_search($key, $header, true);
                if ($i === false) return null;
                $v = $row[$i] ?? null;
                return is_string($v) ? trim($v) : $v;
            };

            $name     = $get('name');
            $code     = $get('code');
            $catName  = $get('category_name');
            $unit     = $get('unit');
            $spec     = $get('specification');
            $min      = $get('min_stock');
            $safety   = $get('safety_stock');
            $current  = $get('current_stock');
            $cost     = $get('cost_price');
            $sell     = $get('sell_price');
            $whName   = $get('warehouse_name');
            $loc      = $get('location');

            $excelLine = $lineNo + 2; // 标题行 + 数据行偏移

            // 行级必填校验
            $missing = [];
            if (!$name)    $missing[] = 'name';
            if (!$code)    $missing[] = 'code';
            if (!$catName) $missing[] = 'category_name';
            if (!$unit)    $missing[] = 'unit';
            if ($missing) {
                $errors[] = ['row' => $excelLine, 'code' => $code, 'reason' => '缺少必填字段: ' . implode(',', $missing)];
                continue;
            }

            // 重名 code 跳过
            if (isset($existingCodes[(string) $code])) {
                $skipped[] = ['row' => $excelLine, 'code' => $code, 'name' => $name, 'reason' => '编码已存在'];
                continue;
            }

            // 查 / 自动建分类
            if (!isset($categories[$catName])) {
                $cat = InventoryCategory::create([
                    'name'        => $catName,
                    'code'        => 'CAT-' . strtoupper(Str::random(6)),
                    'parent_id'   => null,
                    'sort_order'  => 999,
                    'description' => '批量导入自动创建',
                ]);
                $categories[$catName] = $cat;
            }
            $categoryId = $categories[$catName]->id;

            $warehouseId = null;
            if ($whName) {
                if (isset($warehouses[$whName])) {
                    $warehouseId = $warehouses[$whName]->id;
                } else {
                    $errors[] = ['row' => $excelLine, 'code' => $code, 'reason' => "仓库不存在: {$whName}"];
                    continue;
                }
            }

            try {
                $item = InventoryItem::create([
                    'name'          => $name,
                    'code'          => $code,
                    'category'      => $catName,    // 兼容旧字段
                    'category_id'   => $categoryId,
                    'specification' => $spec,
                    'unit'          => $unit,
                    'min_stock'     => is_numeric($min) ? (int) $min : 0,
                    'safety_stock'  => is_numeric($safety) ? (int) $safety : 0,
                    'current_stock' => is_numeric($current) ? (int) $current : 0,
                    'cost_price'    => is_numeric($cost) ? (float) $cost : 0,
                    'sell_price'    => is_numeric($sell) ? (float) $sell : 0,
                    'warehouse_id'  => $warehouseId,
                    'location'      => $loc,
                    'status'        => 'active',
                ]);
                $existingCodes[(string) $code] = true;
                $created[] = ['row' => $excelLine, 'id' => $item->id, 'code' => $code, 'name' => $name];
            } catch (\Throwable $e) {
                $errors[] = ['row' => $excelLine, 'code' => $code, 'reason' => '数据库错误: ' . $e->getMessage()];
            }
        }

        return response()->json([
            'code' => 0,
            'data' => [
                'created' => $created,
                'skipped' => $skipped,
                'errors'  => $errors,
                'summary' => [
                    'created_count' => count($created),
                    'skipped_count' => count($skipped),
                    'error_count'   => count($errors),
                ],
            ],
        ]);
    }

    /**
     * 简单 CSV/XLSX 解析（不依赖 maatwebsite/excel）
     * - CSV: fgetcsv
     * - XLSX: 解析 OOXML 共享字符串 + sheet1
     * - XLS: 不支持（提示用 CSV）
     */
    private function parseSpreadsheet(string $path, string $ext): array
    {
        if ($ext === 'csv') {
            $rows = [];
            if (($h = fopen($path, 'r')) !== false) {
                // 检测 BOM
                $bom = fread($h, 3);
                if ($bom !== "\xEF\xBB\xBF") rewind($h);
                while (($r = fgetcsv($h)) !== false) {
                    $rows[] = $r;
                }
                fclose($h);
            }
            return $rows;
        }

        if ($ext === 'xlsx') {
            return $this->parseXlsx($path);
        }

        // .xls (BIFF) 不支持，提示用 CSV
        return [];
    }

    /**
     * 简易 XLSX 解析（仅支持共享字符串 + sheet1 inlineStr）
     * 用 ZipArchive 读 OOXML 包
     */
    private function parseXlsx(string $path): array
    {
        if (!class_exists(\ZipArchive::class)) {
            return [];
        }
        $zip = new \ZipArchive();
        if ($zip->open($path) !== true) return [];

        // 1) 共享字符串
        $shared = [];
        $ssXml = $zip->getFromName('xl/sharedStrings.xml');
        if ($ssXml !== false) {
            $ssXml = preg_replace('/xmlns[^=]*="[^"]*"/i', '', $ssXml, 1);
            $sx = @simplexml_load_string($ssXml);
            if ($sx) {
                foreach ($sx->si as $si) {
                    if (isset($si->t)) {
                        $shared[] = (string) $si->t;
                    } else {
                        // 富文本拼接
                        $txt = '';
                        foreach ($si->r as $r) $txt .= (string) $r->t;
                        $shared[] = $txt;
                    }
                }
            }
        }

        // 2) sheet1
        $sheetXml = $zip->getFromName('xl/worksheets/sheet1.xml');
        $zip->close();
        if ($sheetXml === false) return [];
        $sheetXml = preg_replace('/xmlns[^=]*="[^"]*"/i', '', $sheetXml, 1);
        $sheet = @simplexml_load_string($sheetXml);
        if (!$sheet) return [];

        $rows = [];
        foreach ($sheet->sheetData->row as $row) {
            $rowArr = [];
            $maxCol = 0;
            foreach ($row->c as $c) {
                $ref = (string) $c['r'];       // e.g. "B3"
                $col = preg_replace('/[0-9]/', '', $ref);
                $colIdx = $this->colLetterToIndex($col);
                $maxCol = max($maxCol, $colIdx);

                $type = (string) $c['t'];
                $val  = (string) ($c->v ?? '');
                if ($type === 's') {
                    $val = $shared[(int) $val] ?? '';
                } elseif ($type === 'inlineStr' && isset($c->is)) {
                    $val = (string) ($c->is->t ?? '');
                } elseif ($type === 'b') {
                    $val = $val === '1' ? 'TRUE' : 'FALSE';
                }
                $rowArr[$colIdx] = $val;
            }
            $line = [];
            for ($i = 0; $i <= $maxCol; $i++) $line[] = $rowArr[$i] ?? '';
            $rows[] = $line;
        }
        return $rows;
    }

    private function colLetterToIndex(string $letters): int
    {
        $n = 0;
        for ($i = 0; $i < strlen($letters); $i++) {
            $n = $n * 26 + (ord($letters[$i]) - 64);
        }
        return $n - 1;
    }

    /**
     * GET /api/inventory/items/export-template
     * 返回 CSV 模板（含表头 + 1 行示例）
     */
    public function exportTemplate(Request $request): StreamedResponse
    {
        $filename = 'inventory_items_template_' . date('Ymd') . '.csv';
        $headers = [
            'Content-Type'        => 'text/csv; charset=UTF-8',
            'Content-Disposition' => "attachment; filename=\"{$filename}\"",
            'Cache-Control'       => 'no-store, no-cache, must-revalidate',
        ];
        $columns = [
            'name', 'code', 'category_name', 'specification', 'unit',
            'min_stock', 'safety_stock', 'current_stock',
            'cost_price', 'sell_price', 'warehouse_name', 'location',
        ];
        $example = [
            '示例-海康威视摄像头', 'CAM-HK-001', '监控设备', 'DS-2CD2T47 400万', '台',
            '5', '10', '20', '350.00', '500.00', '主仓库', 'A-01-03',
        ];
        $callback = function () use ($columns, $example) {
            $out = fopen('php://output', 'w');
            // UTF-8 BOM 让 Excel 识别中文
            fwrite($out, "\xEF\xBB\xBF");
            fputcsv($out, $columns);
            fputcsv($out, $example);
            fclose($out);
        };
        return response()->stream($callback, 200, $headers);
    }

    /**
     * GET /api/inventory/items-by-category?category_id=X&page=Y&per_page=N&keyword=K
     * 按分类（含子分类递归）查物品
     * category_id 可选：不传/0 时返回全部（前端"未分类"视图）
     */
    public function itemsByCategory(Request $request): JsonResponse
    {
        $data = $request->validate([
            'category_id' => 'nullable|integer|min:1',
            'per_page'    => 'nullable|integer|min:1|max:200',
            'keyword'     => 'nullable|string|max:200',
        ]);

        $rootId  = !empty($data['category_id']) ? (int) $data['category_id'] : null;
        $perPage = (int) ($data['per_page'] ?? 15);

        if ($rootId) {
            // BFS 收集所有子分类 id
            $allIds = [$rootId];
            $queue  = [$rootId];
            $cats   = InventoryCategory::all()->keyBy('id');
            while ($queue) {
                $next = array_shift($queue);
                foreach ($cats as $c) {
                    if ((int) $c->parent_id === (int) $next && !in_array((int) $c->id, $allIds, true)) {
                        $allIds[] = (int) $c->id;
                        $queue[]  = (int) $c->id;
                    }
                }
            }

            $query = InventoryItem::with('warehouse', 'categoryRef')
                ->whereIn('category_id', $allIds);

            // Fallback：部分老数据 category_id 为 NULL 但 category 字符串名匹配
            $nameSet = InventoryCategory::whereIn('id', $allIds)->pluck('name')->all();
            if (!empty($nameSet)) {
                $query->orWhere(function ($q) use ($nameSet) {
                    $q->whereNull('category_id')->whereIn('category', $nameSet);
                });
            }
        } else {
            // 不传 category_id：返回全部物品
            $allIds = [];
            $query  = InventoryItem::with('warehouse', 'categoryRef');
        }

        if (!empty($data['keyword'])) {
            $kw = $data['keyword'];
            $query->where(function ($q) use ($kw) {
                $q->where('name', 'like', "%{$kw}%")
                  ->orWhere('code', 'like', "%{$kw}%");
            });
        }

        $list = $query->orderBy('created_at', 'desc')->paginate($perPage);
        $list->getCollection()->transform(function ($it) {
            $it->is_low_stock  = $it->min_stock > 0 && $it->current_stock <= $it->min_stock;
            $it->category_name = $it->categoryRef?->name;
            return $it;
        });

        return response()->json([
            'code' => 0,
            'data' => [
                'list'         => $list,
                'category_id'  => $rootId,
                'category_ids' => $rootId ? $allIds : null,
            ],
        ]);
    }

    /**
     * GET /api/inventory/warnings
     * 低库存 + 临期物品聚合（dashboard 用）
     * 返回 {low_stock_count, expiring_count, items: [...]}
     */
    public function warnings(Request $request): JsonResponse
    {
        $days = (int) $request->input('days', 30);
        if ($days < 1 || $days > 365) $days = 30;

        // 低库存
        $lowStockQ = InventoryItem::with('warehouse')
            ->where('min_stock', '>', 0)
            ->whereColumn('current_stock', '<=', 'min_stock');

        $lowStock = $lowStockQ->orderBy('current_stock', 'asc')->limit(100)->get();
        $lowStockCount = (clone $lowStockQ)->count();

        // 临期（30 天内到期）
        $expiringQ = InventoryItem::with('warehouse')
            ->whereNotNull('expiry_date')
            ->whereDate('expiry_date', '<=', now()->addDays($days))
            ->whereDate('expiry_date', '>=', now()->subDays(7)); // 已过期 7 天内也警告

        $expiring = $expiringQ->orderBy('expiry_date', 'asc')->limit(100)->get();
        $expiringCount = (clone $expiringQ)->count();

        $items = [];
        foreach ($lowStock as $it) {
            $items[] = [
                'id'              => $it->id,
                'name'            => $it->name,
                'code'            => $it->code,
                'category_id'     => $it->category_id,
                'type'            => 'low_stock',
                'severity'        => $it->current_stock == 0 ? 'critical' : 'warning',
                'current_stock'   => $it->current_stock,
                'min_stock'       => $it->min_stock,
                'days_remaining'  => null,
                'expiry_date'     => $it->expiry_date?->toDateString(),
                'warehouse_name'  => $it->warehouse?->name,
            ];
        }
        foreach ($expiring as $it) {
            $daysLeft = (int) now()->diffInDays($it->expiry_date, false); // 负数=已过期
            $items[] = [
                'id'              => $it->id,
                'name'            => $it->name,
                'code'            => $it->code,
                'category_id'     => $it->category_id,
                'type'            => 'expiring',
                'severity'        => $daysLeft < 0 ? 'critical' : ($daysLeft <= 7 ? 'warning' : 'info'),
                'current_stock'   => $it->current_stock,
                'min_stock'       => $it->min_stock,
                'days_remaining'  => $daysLeft,
                'expiry_date'     => $it->expiry_date?->toDateString(),
                'warehouse_name'  => $it->warehouse?->name,
            ];
        }

        // 按 severity 排序: critical > warning > info
        usort($items, function ($a, $b) {
            $rank = ['critical' => 0, 'warning' => 1, 'info' => 2];
            return ($rank[$a['severity']] ?? 9) - ($rank[$b['severity']] ?? 9);
        });

        return response()->json([
            'code' => 0,
            'data' => [
                'low_stock_count'  => $lowStockCount,
                'expiring_count'   => $expiringCount,
                'days_window'      => $days,
                'items'            => $items,
            ],
        ]);
    }
}
