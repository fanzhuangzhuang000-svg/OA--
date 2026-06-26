<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\{ServiceOrder, ServiceOrderLog, ServiceOrderPart, MaintenanceContract, Customer};
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class ServiceController extends Controller
{
    /**
     * V0.5.6 B4 — 已废弃的写入方法统一拦截
     * 兼容期: 只允许 GET (index/show/stats/maintenanceContracts), 写入返回 410 Gone
     */
    private function gone(): JsonResponse
    {
        return response()->json([
            'code' => 410,
            'message' => '此接口已废弃, 请使用「维修中心」模块的 /api/work-orders 系列端点',
            'redirect' => '/api/work-orders',
        ], 410);
    }
    public function index(Request $request): JsonResponse
    {
        $query = ServiceOrder::with(['customer', 'assignedUser', 'device']);
        if ($request->filled('keyword')) $query->where('order_no', 'like', "%{$request->keyword}%")->orWhere('fault_description', 'like', "%{$request->keyword}%");
        if ($request->filled('status')) $query->where('status', $request->status);
        if ($request->filled('urgency')) $query->where('urgency', $request->urgency);
        if ($request->filled('customer_id')) $query->where('customer_id', $request->customer_id);

        $paginator = $query->orderBy('created_at', 'desc')->paginate($request->per_page ?? 15);

        // V0.5.6 B3 — 兼容期返回迁移横幅
        return response()->json([
            'code' => 0,
            'data' => $paginator,
            'meta' => [
                'migration_banner' => [
                    'type'    => 'info',
                    'title'   => '老工单模块已迁移到「维修中心」',
                    'message' => '请使用 /maintenance/work-orders 访问新的维修工单。老数据保留只读, 不会再创建新单。',
                    'target_url' => '/maintenance/work-orders',
                    'target_label' => '前往维修中心',
                ],
            ],
        ]);
    }

    public function show(ServiceOrder $serviceOrder): JsonResponse
    {
        $serviceOrder->load(['customer', 'project', 'device', 'assignedUser', 'creator', 'logs.user', 'parts']);
        return response()->json(['code' => 0, 'data' => $serviceOrder]);
    }

    public function store(Request $request): JsonResponse
    {
        return $this->gone();
    }

    public function assign(Request $request, ServiceOrder $serviceOrder): JsonResponse
    {
        return $this->gone();
    }

    public function startRepair(Request $request, ServiceOrder $serviceOrder): JsonResponse
    {
        return $this->gone();
    }

    public function completeRepair(Request $request, ServiceOrder $serviceOrder): JsonResponse
    {
        return $this->gone();
    }

    public function confirmByCustomer(Request $request, ServiceOrder $serviceOrder): JsonResponse
    {
        $data = $request->validate(['rating' => 'nullable|integer|min:1|max:5', 'review' => 'nullable|string']);
        $serviceOrder->update(['status' => 'confirmed', 'confirmed_at' => now(), 'rating' => $data['rating'] ?? null, 'review' => $data['review'] ?? null]);
        return response()->json(['code' => 0, 'message' => '已确认完工']);
    }

    public function stats(Request $request): JsonResponse
    {
        $monthStart = now()->startOfMonth();
        $totalOrders = ServiceOrder::where('created_at', '>=', $monthStart)->count();
        $completedOrders = ServiceOrder::where('created_at', '>=', $monthStart)->where('status', 'confirmed')->count();
        $slaRate = $totalOrders > 0 ? round($completedOrders / $totalOrders * 100, 1) : 100;
        $avgResponse = ServiceOrder::whereNotNull('assigned_at')->where('created_at', '>=', $monthStart)->selectRaw('AVG(EXTRACT(EPOCH FROM (assigned_at - created_at)) / 60) as avg_minutes')->value('avg_minutes') ?? 0;
        $avgRating = ServiceOrder::whereNotNull('rating')->where('created_at', '>=', $monthStart)->avg('rating') ?? 0;

        return response()->json(['code' => 0, 'data' => compact('totalOrders', 'completedOrders', 'slaRate', 'avgResponse', 'avgRating')]);
    }

    public function maintenanceContracts(Request $request): JsonResponse
    {
        $query = MaintenanceContract::with('customer');
        if ($request->filled('status')) $query->where('status', $request->status);
        return response()->json(['code' => 0, 'data' => $query->orderBy('created_at', 'desc')->paginate($request->per_page ?? 15)]);
    }
}
