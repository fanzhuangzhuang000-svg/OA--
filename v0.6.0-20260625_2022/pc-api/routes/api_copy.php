<?php

use App\Http\Controllers\Api\{
    AuthController, DashboardController,
    AttendanceController, EmployeeController,     CustomerController, CustomerPipelineController,
    ProjectController, ServiceController, ExpenseController,
    VehicleController, InventoryController, FinanceController,
    DiskController, KnowledgeController, NotificationController,
    SystemLogController, RoleController, AuditController, BackupController,
    SystemSettingsController, ApprovalTemplateController, FuelCardController,
    InventoryCategoryController, SalesController, SalesProductController,
    FinanceApprovalController, OperationApprovalController, ProjectApprovalController,
    ApprovalCenterController,
    PurchaseRequirementController, PurchasePlanController,
    PurchasePaymentRequestController, PurchasePaymentController,
    PurchaseContractController, PurchaseShipmentController,
    PurchaseLogisticsController, PurchaseApprovalController,
    ProcessController,
    ScheduleController,
    EmployeeOnboardingController, EmployeeResignationController,
    FollowUpCalendarController
};
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes - 安防运维OA系统
|--------------------------------------------------------------------------
*/

// ========== 健康检查端点 (T7) — 公开路由,无认证 ==========
// 放最前面: 1) 监控系统探活用  2) 负载均衡器后端健康检查
Route::get('/health', function () {
    $checks = [
        'status' => 'ok',
        'time'   => now()->toIso8601String(),
        'env'    => app()->environment(),
        'php'    => PHP_VERSION,
        'laravel'=> app()->version(),
    ];

    // DB 检查
    try {
        $r = DB::select('SELECT 1 AS ok');
        $checks['db'] = (! empty($r) && $r[0]->ok == 1) ? 'up' : 'down';
    } catch (\Throwable $e) {
        $checks['db'] = 'down';
        $checks['db_error'] = $e->getMessage();
    }

    // Cache 检查
    try {
        Cache::put('health_check', '1', 5);
        $v = Cache::get('health_check');
        $checks['cache'] = ($v === '1') ? 'up' : 'down';
    } catch (\Throwable $e) {
        $checks['cache'] = 'down';
    }

    $allUp = ($checks['db'] === 'up') && ($checks['cache'] === 'up');
    return response()->json([
        'code'    => $allUp ? 0 : 1001,
        'message' => $allUp ? 'healthy' : 'degraded',
        'data'    => $checks,
    ], $allUp ? 200 : 503);
});

// 公开路由（无需认证）
Route::prefix('auth')->group(function () {
    // T2 登录限流: 1 分钟 5 次 — 防止暴力破解
    Route::post('login', [AuthController::class, 'login'])->middleware('throttle:5,1');
});

// 顶层部门/岗位快捷路由（兼容前端 /departments 路径）
Route::middleware('auth:sanctum')->group(function () {
    Route::get('departments', [EmployeeController::class, 'departments']);
    Route::post('departments', [EmployeeController::class, 'storeDepartment']);
    Route::put('departments/{department}', [EmployeeController::class, 'updateDepartment']);
    Route::delete('departments/{department}', [EmployeeController::class, 'destroyDepartment']);
    Route::get('positions', [EmployeeController::class, 'positions']);
});

// 需要认证的路由
Route::middleware('auth:sanctum')->group(function () {

    // 认证相关
    Route::post('auth/logout', [AuthController::class, 'logout']);
    Route::get('auth/userinfo', [AuthController::class, 'userInfo']);
    Route::get('auth/me', [AuthController::class, 'userInfo']); // 别名（前端 Leave/Overtime 用 me）
    Route::put('auth/profile', [AuthController::class, 'updateProfile']);
    // T2: 修改密码限流 1 分钟 5 次 — 防爆破
    Route::post('auth/change-password', [AuthController::class, 'changePassword'])->middleware('throttle:5,1');

    // 工作台
    Route::prefix('dashboard')->group(function () {
        Route::get('stats', [DashboardController::class, 'stats']);
        Route::get('recent-projects', [DashboardController::class, 'recentProjects']);
        Route::get('recent-service-orders', [DashboardController::class, 'recentServiceOrders']);
        Route::get('project-progress', [DashboardController::class, 'projectProgress']);
        Route::get('todo', [DashboardController::class, 'todo']);
        Route::get('service-stats', [DashboardController::class, 'serviceStats']);
        Route::get('revenue-trend', [DashboardController::class, 'revenueTrend']);
        Route::get('screen', [DashboardController::class, 'screen']);
    });

    // 考勤管理
    Route::prefix('attendance')->group(function () {
        Route::get('overview', [AttendanceController::class, 'overview']);
        Route::get('calendar', [AttendanceController::class, 'calendar']);
        Route::post('clock-in', [AttendanceController::class, 'clockIn']);
        Route::post('clock-out', [AttendanceController::class, 'clockOut']);
        Route::post('field-clock', [AttendanceController::class, 'fieldClock']);
        Route::get('today', [AttendanceController::class, 'today']);
        Route::post('supplement', [AttendanceController::class, 'supplement']);
        Route::get('records', [AttendanceController::class, 'records']);
        Route::get('report', [AttendanceController::class, 'report']);
        Route::get('leave', [AttendanceController::class, 'leaveRequests']);
        Route::post('leave', [AttendanceController::class, 'storeLeaveRequest']);
        Route::post('leave/{leave}/approve', [AttendanceController::class, 'approveLeave']);
        Route::delete('leave/{leave}', [AttendanceController::class, 'destroyLeaveRequest']);

        Route::get('overtime', [AttendanceController::class, 'overtimeRequests']);
        Route::post('overtime', [AttendanceController::class, 'storeOvertimeRequest']);
        Route::post('overtime/{overtime}/approve', [AttendanceController::class, 'approveOvertime']);
        Route::delete('overtime/{overtime}', [AttendanceController::class, 'destroyOvertimeRequest']);

        // 兼容前端直接 /attendance 调用
        Route::get('/', [AttendanceController::class, 'overview']);
        Route::get('stats', [AttendanceController::class, 'stats']);
    });

    // 排班管理
    Route::prefix('schedules')->group(function () {
        // 班次
        Route::get('shifts', [ScheduleController::class, 'listShifts']);
        Route::post('shifts', [ScheduleController::class, 'storeShift']);
        Route::put('shifts/{shift}', [ScheduleController::class, 'updateShift']);
        Route::delete('shifts/{shift}', [ScheduleController::class, 'destroyShift']);

        // 班组
        Route::get('groups', [ScheduleController::class, 'listGroups']);
        Route::post('groups', [ScheduleController::class, 'storeGroup']);
        Route::put('groups/{group}', [ScheduleController::class, 'updateGroup']);
        Route::delete('groups/{group}', [ScheduleController::class, 'destroyGroup']);
        Route::post('groups/{group}/members', [ScheduleController::class, 'syncGroupMembers']);
        Route::post('groups/{group}/add-member', [ScheduleController::class, 'addGroupMember']);
        Route::delete('groups/{group}/members/{user}', [ScheduleController::class, 'removeGroupMember']);

        // 排班
        Route::get('/', [ScheduleController::class, 'index']);
        Route::post('/', [ScheduleController::class, 'batchSave']);
        Route::post('batch-by-group', [ScheduleController::class, 'batchByGroup']);
        Route::delete('{schedule}', [ScheduleController::class, 'destroy']);
        Route::get('my-schedule', [ScheduleController::class, 'mySchedule']);
        Route::get('smart-suggest', [ScheduleController::class, 'smartSuggest']);
        Route::get('next-reminder', [ScheduleController::class, 'nextReminder']);
        Route::get('stats', [ScheduleController::class, 'stats']);
    });

    // 员工管理
    Route::prefix('employees')->group(function () {
        Route::get('/', [EmployeeController::class, 'index']);
        Route::post('/', [EmployeeController::class, 'store']);

        // 部门（必须在 {user} 之前注册，否则会被吞）
        Route::get('departments', [EmployeeController::class, 'departments']);
        Route::post('departments', [EmployeeController::class, 'storeDepartment']);
        Route::put('departments/{department}', [EmployeeController::class, 'updateDepartment']);
        Route::delete('departments/{department}', [EmployeeController::class, 'destroyDepartment']);

        // 岗位
        Route::get('positions', [EmployeeController::class, 'positions']);
        Route::post('positions', [EmployeeController::class, 'storePosition']);
        Route::put('positions/{position}', [EmployeeController::class, 'updatePosition']);
        Route::delete('positions/{position}', [EmployeeController::class, 'destroyPosition']);

        // 技能
        Route::get('skills', [EmployeeController::class, 'skills']);
        Route::post('skills', [EmployeeController::class, 'storeSkill']);
        Route::put('skills/{skillTag}', [EmployeeController::class, 'updateSkill']);
        Route::delete('skills/{skillTag}', [EmployeeController::class, 'destroySkill']);
        Route::post('skills/{skillTag}/attach', [EmployeeController::class, 'attachSkill']);
        Route::post('skills/{skillTag}/detach', [EmployeeController::class, 'detachSkill']);
        Route::get('{user}/skills', [EmployeeController::class, 'userSkills']);

        // 导入
        Route::post('import', [EmployeeController::class, 'import']);

        Route::get('certificates', [EmployeeController::class, 'certificates']);

        // 员工 CRUD（放最后 — 通配符会吞掉子路径）
        Route::get('{user}', [EmployeeController::class, 'show']);
        Route::put('{user}', [EmployeeController::class, 'update']);
        Route::delete('{user}', [EmployeeController::class, 'destroy']);
    });

    // 员工入职档案
    Route::prefix('employee-onboardings')->group(function () {
        Route::get('/', [EmployeeOnboardingController::class, 'index']);
        Route::post('/', [EmployeeOnboardingController::class, 'store']);
        Route::get('{onboarding}', [EmployeeOnboardingController::class, 'show']);
        Route::put('{onboarding}', [EmployeeOnboardingController::class, 'update']);
        Route::delete('{onboarding}', [EmployeeOnboardingController::class, 'destroy']);
    });

    // 员工离职记录
    Route::prefix('employee-resignations')->group(function () {
        Route::get('/', [EmployeeResignationController::class, 'index']);
        Route::post('/', [EmployeeResignationController::class, 'store']);
        Route::get('settlement-preview', [EmployeeResignationController::class, 'settlementPreview']);
        Route::get('{resignation}', [EmployeeResignationController::class, 'show']);
        Route::put('{resignation}', [EmployeeResignationController::class, 'update']);
        Route::post('{resignation}/submit', [EmployeeResignationController::class, 'submit']);
        Route::post('{resignation}/approve', [EmployeeResignationController::class, 'approve']);
        Route::post('{resignation}/cancel', [EmployeeResignationController::class, 'cancel']);
        Route::post('{resignation}/complete', [EmployeeResignationController::class, 'complete']);
    });

    // 员工管理 — /api/users 别名（前端某些模块用 users 路径，复用 EmployeeController）
    Route::prefix('users')->group(function () {
        Route::get('/', [EmployeeController::class, 'index']);
        Route::post('/', [EmployeeController::class, 'store']);
        Route::get('{user}', [EmployeeController::class, 'show']);
        Route::put('{user}', [EmployeeController::class, 'update']);
        Route::delete('{user}', [EmployeeController::class, 'destroy']);
        Route::post('{user}/reset-password', [EmployeeController::class, 'resetPassword']);
    });

    // 客户管理
    Route::prefix('customers')->group(function () {
        Route::get('/', [CustomerController::class, 'index']);
        Route::post('/', [CustomerController::class, 'store']);
        Route::get('stats', [CustomerController::class, 'stats']);
        Route::post('import', [CustomerController::class, 'import']);
        // 销售漏斗看板 (字面量必须在 {customer} 通配之前)
        Route::get('pipeline', [CustomerPipelineController::class, 'index']);
        Route::get('pipeline/weekly-trend', [CustomerPipelineController::class, 'weeklyTrend']);
        // 字面量路径必须在 {customer} 通配之前 — 否则会被吞
        Route::get('health', [CustomerController::class, 'health']);
        Route::get('map', [CustomerController::class, 'mapData']);
        Route::get('{customer}/profile', [CustomerController::class, 'profile']);
        Route::get('{customer}/follow-ups', [CustomerController::class, 'followUps']);
        Route::post('{customer}/follow-ups', [CustomerController::class, 'storeFollowUp']);
        Route::get('{customer}/devices', [CustomerController::class, 'devices']);
        // 放最后 — {customer} 通配符会吞掉子路径
        Route::get('{customer}', [CustomerController::class, 'show']);
        Route::put('{customer}', [CustomerController::class, 'update']);
        Route::put('{customer}/stage', [CustomerPipelineController::class, 'updateStage']);
        Route::delete('{customer}', [CustomerController::class, 'destroy']);
    });

    // 项目管理
    Route::prefix('projects')->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store']);
        Route::get('stages', [ProjectController::class, 'stages']);
        Route::get('dashboard-summary', [ProjectController::class, 'dashboardSummary']);
        Route::get('payment-calendar', [ProjectController::class, 'paymentCalendar']);
        Route::get('board', [ProjectController::class, 'board']);
        Route::get('suppliers', [ProjectController::class, 'suppliers']);
        Route::post('suppliers', [ProjectController::class, 'storeSupplier']);
        Route::put('{project}/stage', [ProjectController::class, 'updateStage']);
        Route::get('{project}/construction-logs', [ProjectController::class, 'constructionLogs']);
        Route::post('{project}/construction-logs', [ProjectController::class, 'storeConstructionLog']);
        Route::get('{project}/suppliers', [ProjectController::class, 'projectSuppliers']);
        Route::get('{project}/contracts', [ProjectController::class, 'projectContracts']);
        Route::get('{project}/tracking', [ProjectController::class, 'tracking']);
        Route::get('{project}', [ProjectController::class, 'show']);
        Route::put('{project}', [ProjectController::class, 'update']);
        Route::delete('{project}', [ProjectController::class, 'destroy']);
    });

    // 深化施工 V1.1 - 工序验收 + 影像档案
    Route::prefix('process')->group(function () {
        // ===== 字面量路由必须在 {process}/{inspection}/{image}/{signature} 通配之前 =====

        // 工序模板
        Route::get('industries',           [ProcessController::class, 'industries']);
        Route::get('templates',            [ProcessController::class, 'templates']);
        Route::post('templates',           [ProcessController::class, 'storeTemplate']);
        Route::post('templates/{template}/apply', [ProcessController::class, 'applyTemplate']);
        Route::get('templates/{template}', [ProcessController::class, 'showTemplate']);
        Route::put('templates/{template}', [ProcessController::class, 'updateTemplate']);
        Route::delete('templates/{template}', [ProcessController::class, 'destroyTemplate']);

        // 工序实例
        Route::get('instances',            [ProcessController::class, 'instances']);
        Route::post('instances',           [ProcessController::class, 'storeInstance']);
        Route::get('instances/{process}',  [ProcessController::class, 'showInstance']);
        Route::put('instances/{process}',  [ProcessController::class, 'updateInstance']);
        Route::delete('instances/{process}', [ProcessController::class, 'destroyInstance']);
        Route::post('instances/{process}/progress', [ProcessController::class, 'updateProgress']);
        Route::post('instances/{process}/accept',  [ProcessController::class, 'acceptInstance']);
        Route::post('instances/{process}/reject',  [ProcessController::class, 'rejectInstance']);

        // 验收记录
        Route::get('inspections',                 [ProcessController::class, 'inspections']);
        Route::post('inspections',                [ProcessController::class, 'storeInspection']);
        Route::get('inspections/{inspection}',    [ProcessController::class, 'showInspection']);
        Route::put('inspections/{inspection}',    [ProcessController::class, 'updateInspection']);
        Route::delete('inspections/{inspection}', [ProcessController::class, 'destroyInspection']);

        // 影像
        Route::get('images',                [ProcessController::class, 'images']);
        Route::post('images/upload',        [ProcessController::class, 'uploadImages']);
        Route::get('images/{image}',        [ProcessController::class, 'showImage']);
        Route::put('images/{image}',        [ProcessController::class, 'updateImageMeta']);
        Route::delete('images/{image}',     [ProcessController::class, 'destroyImage']);

        // 签字
        Route::get('signatures',                  [ProcessController::class, 'signatures']);
        Route::post('signatures',                 [ProcessController::class, 'storeSignature']);
        Route::post('signatures/{signature}/verify', [ProcessController::class, 'verifySignature']);
        Route::delete('signatures/{signature}',   [ProcessController::class, 'destroySignature']);
    });

    // 售后服务
    Route::prefix('service')->group(function () {
        // 字面量路径必须在通配前 — 否则会被吞
        Route::get('stats', [ServiceController::class, 'stats']);
        Route::get('maintenance-contracts', [ServiceController::class, 'maintenanceContracts']);
        Route::get('orders', [ServiceController::class, 'index']);
        Route::post('orders', [ServiceController::class, 'store']);
        Route::get('orders/stats', [ServiceController::class, 'stats']);
        Route::get('orders/{serviceOrder}', [ServiceController::class, 'show']);
        Route::post('orders/{serviceOrder}/assign', [ServiceController::class, 'assign']);
        Route::post('orders/{serviceOrder}/start', [ServiceController::class, 'startRepair']);
        Route::post('orders/{serviceOrder}/complete', [ServiceController::class, 'completeRepair']);
        Route::post('orders/{serviceOrder}/confirm', [ServiceController::class, 'confirmByCustomer']);
    });

    // 报销管理
    Route::prefix('expenses')->group(function () {
        Route::get('/', [ExpenseController::class, 'index']);
        Route::post('/', [ExpenseController::class, 'store']);
        Route::get('stats', [ExpenseController::class, 'stats']);
        Route::get('projects', [ExpenseController::class, 'projects']);
        Route::get('my', [ExpenseController::class, 'myClaims']);
        Route::get('{claim}', [ExpenseController::class, 'show']);
        Route::put('{claim}', [ExpenseController::class, 'update']);
        Route::delete('{claim}', [ExpenseController::class, 'destroy']);
        Route::post('{claim}/approve', [ExpenseController::class, 'approve']);
        Route::post('{claim}/cancel', [ExpenseController::class, 'cancel']);
        Route::post('{claim}/pay', [ExpenseController::class, 'pay']);
    });

    // 车辆管理
    Route::prefix('vehicles')->group(function () {
        Route::get('/', [VehicleController::class, 'index']);
        Route::post('/', [VehicleController::class, 'store']);
        Route::get('stats', [VehicleController::class, 'stats']);
        Route::get('usage', [VehicleController::class, 'usageRequests']);
        Route::post('usage', [VehicleController::class, 'storeUsageRequest']);
        Route::post('usage/{usageRequest}/dispatch', [VehicleController::class, 'dispatchVehicle']);
        Route::put('usage/{usageRequest}', [VehicleController::class, 'updateUsageRequest']);
        // 用车申请 — 别名 (前端 /vehicles/applies 和 /vehicles/apply)
        Route::get('applies', [VehicleController::class, 'usageRequests']);
        Route::get('apply', [VehicleController::class, 'usageRequests']);
        Route::post('apply', [VehicleController::class, 'storeUsageRequest']);
        // 保险
        Route::get('insurances', [VehicleController::class, 'insurances']);
        Route::post('insurances', [VehicleController::class, 'storeInsurance']);
        Route::put('insurances/{insurance}', [VehicleController::class, 'updateInsurance']);
        Route::delete('insurances/{insurance}', [VehicleController::class, 'destroyInsurance']);
        // 保养
        Route::get('maintenances', [VehicleController::class, 'maintenances']);
        Route::post('maintenances', [VehicleController::class, 'storeMaintenance']);
        Route::put('maintenances/{maintenance}', [VehicleController::class, 'updateMaintenance']);
        Route::delete('maintenances/{maintenance}', [VehicleController::class, 'destroyMaintenance']);
        // 单车详情/更新/删除 — 必须放最后
        Route::get('{vehicle}', [VehicleController::class, 'show']);
        Route::put('{vehicle}', [VehicleController::class, 'update']);
        Route::delete('{vehicle}', [VehicleController::class, 'destroy']);
    });

    // 油卡管理
    Route::prefix('fuel-cards')->group(function () {
        Route::get('stats', [FuelCardController::class, 'stats']);
        Route::get('/', [FuelCardController::class, 'index']);
        Route::post('/', [FuelCardController::class, 'store']);
        Route::get('recharges', [FuelCardController::class, 'recharges']);
        Route::post('recharges', [FuelCardController::class, 'storeRecharge']);
        Route::delete('recharges/{recharge}', [FuelCardController::class, 'destroyRecharge']);
        // 单卡详情/更新/删除 — 必须放最后
        Route::put('{card}', [FuelCardController::class, 'update']);
        Route::delete('{card}', [FuelCardController::class, 'destroy']);
    });

    // 库存管理
    Route::prefix('inventory')->group(function () {
        Route::get('/', [InventoryController::class, 'index']);
        Route::post('/', [InventoryController::class, 'store']);
        Route::get('stock-records', [InventoryController::class, 'stockRecords']);
        Route::get('warehouses', [InventoryController::class, 'warehouses']);
        Route::get('low-stock', [InventoryController::class, 'lowStock']);
        Route::get('stats', [InventoryController::class, 'stats']);
        Route::post('stock-in',  [InventoryController::class, 'stockIn']);
        Route::post('stock-out', [InventoryController::class, 'stockOut']);

        // 批量处理 (静态子路径必须在 {inventoryItem} 通配之前)
        Route::post('batch-delete', [InventoryController::class, 'batchDelete']);
        Route::post('batch-update', [InventoryController::class, 'batchUpdate']);
        Route::post('batch-export', [InventoryController::class, 'batchExport']);

        // v0.3.7.9 库存×分类打通 — 静态子路径必须放在 {inventoryItem} 通配之前
        Route::get('tree-with-counts',        [InventoryController::class, 'treeWithCounts']);
        Route::get('items-by-category',       [InventoryController::class, 'itemsByCategory']);
        Route::post('items/batch-import',     [InventoryController::class, 'batchImport']);
        Route::get('items/export-template',   [InventoryController::class, 'exportTemplate']);
        Route::get('warnings',                [InventoryController::class, 'warnings']);

        // 单物料 {inventoryItem} 通配必须放最后
        Route::get('{inventoryItem}', [InventoryController::class, 'show']);
        Route::put('{inventoryItem}', [InventoryController::class, 'update']);
        Route::delete('{inventoryItem}', [InventoryController::class, 'destroy']);
    });

    // 库存分类管理
    Route::prefix('inventory-categories')->group(function () {
        Route::get('/', [InventoryCategoryController::class, 'index']);
        Route::get('tree', [InventoryCategoryController::class, 'tree']);
        Route::post('/', [InventoryCategoryController::class, 'store']);
        // 子路径 /move 必须在 {category} 通配之前
        Route::post('{category}/move', [InventoryCategoryController::class, 'moveCategory']);
        Route::put('{category}', [InventoryCategoryController::class, 'update']);
        Route::delete('{category}', [InventoryCategoryController::class, 'destroy']);
    });

    // 财务管理
    Route::prefix('finance')->group(function () {
        Route::get('overview', [FinanceController::class, 'overview']);
        Route::get('summary', [FinanceController::class, 'summary']);
        Route::get('payments', [FinanceController::class, 'payments']);

        // 应收（子路径必须在 {receivable} 通配之前）
        Route::get('receivables', [FinanceController::class, 'receivables']);
        Route::post('receivables', [FinanceController::class, 'storeReceivable']);
        Route::get('receivables/{receivable}/payments', [FinanceController::class, 'receivablePayments']);
        Route::post('receivables/{receivable}/payments', [FinanceController::class, 'storeReceivablePayment']);
        Route::post('receivables/{receivable}/close', [FinanceController::class, 'closeReceivable']);
        Route::put('receivables/{receivable}', [FinanceController::class, 'updateReceivable']);
        Route::delete('receivables/{receivable}', [FinanceController::class, 'destroyReceivable']);

        // 应付（子路径必须在 {payable} 通配之前）
        Route::get('payables', [FinanceController::class, 'payables']);
        Route::post('payables', [FinanceController::class, 'storePayable']);
        Route::get('payables/{payable}/payments', [FinanceController::class, 'payablePayments']);
        Route::post('payables/{payable}/payments', [FinanceController::class, 'storePayablePayment']);
        Route::put('payables/{payable}', [FinanceController::class, 'updatePayable']);
        Route::delete('payables/{payable}', [FinanceController::class, 'destroyPayable']);

        // 资金账户（子路径必须在 {account} 通配之前）
        Route::get('accounts', [FinanceController::class, 'accounts']);
        Route::post('accounts', [FinanceController::class, 'storeAccount']);
        Route::post('accounts/transfer', [FinanceController::class, 'transferAccount']);
        Route::get('accounts/{account}/transactions', [FinanceController::class, 'accountTransactions']);
        Route::put('accounts/{account}', [FinanceController::class, 'updateAccount']);
        Route::delete('accounts/{account}', [FinanceController::class, 'destroyAccount']);

        // 发票管理
        Route::get('invoices', [FinanceController::class, 'invoices']);
        Route::post('invoices', [FinanceController::class, 'storeInvoice']);
        Route::get('invoices/{invoice}', [FinanceController::class, 'showInvoice']);
        Route::put('invoices/{invoice}', [FinanceController::class, 'updateInvoice']);
        Route::delete('invoices/{invoice}', [FinanceController::class, 'destroyInvoice']);

        // 应收应付报表
        Route::get('summary/aging', [FinanceController::class, 'agingSummary']);
        Route::get('summary/cashflow', [FinanceController::class, 'cashflowSummary']);

        // 收款单 (前端 /finance/receipts)
        Route::get('receipts', [FinanceController::class, 'receipts']);
        Route::post('receipts', [FinanceController::class, 'storeReceipt']);
        Route::get('receipts/{receipt}', [FinanceController::class, 'showReceipt']);
        // 转账记录 (前端 /finance/transfers)
        Route::get('transfers', [FinanceController::class, 'transfers']);
    });

    // 公司网盘
    Route::prefix('disk')->group(function () {
        Route::get('folders', [DiskController::class, 'folders']);
        Route::post('folders', [DiskController::class, 'createFolder']);
        Route::delete('folders/{folder}', [DiskController::class, 'destroyFolder']);
        Route::get('files', [DiskController::class, 'files']);
        Route::post('upload', [DiskController::class, 'upload']);
        Route::delete('files/{file}', [DiskController::class, 'destroyFile']);
    });

    // 知识库
    Route::prefix('knowledge')->group(function () {
        // 分类（子路径/通配放最后）
        Route::post('categories', [KnowledgeController::class, 'storeCategory']);
        Route::get('categories', [KnowledgeController::class, 'categories']);
        Route::put('categories/{category}', [KnowledgeController::class, 'updateCategory']);
        Route::delete('categories/{category}', [KnowledgeController::class, 'destroyCategory']);

        // 文章
        Route::get('articles', [KnowledgeController::class, 'articles']);
        Route::post('articles', [KnowledgeController::class, 'store']);
        Route::get('articles/{article}', [KnowledgeController::class, 'show']);
        Route::put('articles/{article}', [KnowledgeController::class, 'update']);
        Route::delete('articles/{article}', [KnowledgeController::class, 'destroy']);
    });

    // 数据备份
    Route::prefix('backups')->group(function () {
        Route::get('/', [BackupController::class, 'index']);
        Route::post('/', [BackupController::class, 'store']);
        Route::get('{filename}/download', [BackupController::class, 'download']);
        Route::delete('{filename}', [BackupController::class, 'destroy']);
    });

    // 消息中心
    Route::prefix('notifications')->group(function () {
        Route::get('/', [NotificationController::class, 'index']);
        Route::get('unread-count', [NotificationController::class, 'unreadCount']);
        Route::post('mark-read', [NotificationController::class, 'markAsRead']);
        Route::post('mark-all-read', [NotificationController::class, 'markAllAsRead']);
    });

    // 系统日志
    Route::get('system-logs', [SystemLogController::class, 'index']);

    // === 销售前链路 (P1 真实 CRUD) ===
    Route::prefix('sales')->group(function () {
        // 线索池
        Route::prefix('leads')->group(function () {
            Route::get('/',                          [SalesController::class, 'leadsIndex']);
            Route::get('source-options',             [SalesController::class, 'leadsSourceOptions']);
            // 子路径（{lead} 通配之前）
            Route::post('/',                         [SalesController::class, 'leadsStore']);
            // 通配放最后
            Route::patch('{lead}/status',            [SalesController::class, 'leadsUpdateStatus']);
            Route::post('{lead}/convert-to-opp',     [SalesController::class, 'leadsConvertToOpp']);
            Route::get('{lead}',                     [SalesController::class, 'leadsShow']);
            Route::put('{lead}',                     [SalesController::class, 'leadsUpdate']);
            Route::delete('{lead}',                  [SalesController::class, 'leadsDestroy']);
        });

        // 商机池
        Route::prefix('opps')->group(function () {
            Route::get('/',                          [SalesController::class, 'oppsIndex']);
            Route::get('stage-options',              [SalesController::class, 'oppsStageOptions']);
            Route::get('funnel',                     [SalesController::class, 'oppsFunnel']);
            Route::get('lost-reasons',               [SalesController::class, 'oppsLostReasons']);
            // 子路径（{opp} 通配之前）
            Route::post('/',                         [SalesController::class, 'oppsStore']);
            Route::patch('{opp}/stage',              [SalesController::class, 'oppsUpdateStage']);
            Route::post('{opp}/mark-won',            [SalesController::class, 'oppsMarkWon']);
            Route::post('{opp}/mark-lost',           [SalesController::class, 'oppsMarkLost']);
            // 商机下报价单（子操作）
            Route::get('{opp}/quotations',           [SalesController::class, 'oppsQuotationsIndex']);
            Route::post('{opp}/quotations',          [SalesController::class, 'oppsQuotationsStore']);
            // 商机状态机
            Route::post('{opp}/win',                 [SalesController::class, 'oppsWin']);
            Route::post('{opp}/lose',                [SalesController::class, 'oppsLose']);
            Route::post('{opp}/hold',                [SalesController::class, 'oppsHold']);
            Route::post('{opp}/move-to-project-pool',[SalesController::class, 'oppsMoveToProjectPool']);
            Route::post('{opp}/assign',              [SalesController::class, 'oppsAssign']);
            // 通配放最后
            Route::get('{opp}',                      [SalesController::class, 'oppsShow']);
            Route::put('{opp}',                      [SalesController::class, 'oppsUpdate']);
            Route::delete('{opp}',                   [SalesController::class, 'oppsDestroy']);
        });

        // 报价单
        Route::prefix('quotes')->group(function () {
            Route::get('/',                          [SalesController::class, 'quotesIndex']);
            Route::get('status-options',             [SalesController::class, 'quotesStatusOptions']);
            // 子路径（{quote} 通配之前）
            Route::post('/',                         [SalesController::class, 'quotesStore']);
            Route::put('{quote}/status',             [SalesController::class, 'quotesUpdateStatus']);
            Route::post('{quote}/items',             [SalesController::class, 'quotesStoreItems']);
            Route::post('{quote}/new-version',       [SalesController::class, 'quotesNewVersion']);
            // 客户动作（accept/reject/revise）
            Route::post('{quote}/accept',            [SalesController::class, 'quotationsAccept']);
            Route::post('{quote}/reject',            [SalesController::class, 'quotationsReject']);
            Route::post('{quote}/revise',            [SalesController::class, 'quotationsRevise']);
            // 通配放最后
            Route::get('{quote}',                    [SalesController::class, 'quotesShow']);
            Route::put('{quote}',                    [SalesController::class, 'quotesUpdate']);
            Route::delete('{quote}',                 [SalesController::class, 'quotesDestroy']);
        });

        // 报价单（quotations 别名路由 — 兼容前端可能的 /sales/quotations/{id}/... 调用）
        Route::prefix('quotations')->group(function () {
            Route::get('{quotation}',                [SalesController::class, 'quotationsShow']);
            Route::put('{quotation}',                [SalesController::class, 'quotationsUpdate']);
            Route::delete('{quotation}',             [SalesController::class, 'quotationsDestroy']);
            Route::post('{quotation}/accept',        [SalesController::class, 'quotationsAccept']);
            Route::post('{quotation}/reject',        [SalesController::class, 'quotationsReject']);
            Route::post('{quotation}/revise',        [SalesController::class, 'quotationsRevise']);
        });

        // 推荐人
        Route::prefix('referrers')->group(function () {
            Route::get('/',                          [SalesController::class, 'referrersIndex']);
            Route::post('/',                         [SalesController::class, 'referrersStore']);
            // 通配放最后
            Route::get('{referrer}',                 [SalesController::class, 'referrersShow']);
            Route::put('{referrer}',                 [SalesController::class, 'referrersUpdate']);
            Route::delete('{referrer}',              [SalesController::class, 'referrersDestroy']);
        });

        // 项目池
        Route::prefix('pool')->group(function () {
            Route::get('/',                          [SalesController::class, 'poolIndex']);
            // 子路径（{pool} 通配之前）
            Route::post('{pool}/convert-to-project', [SalesController::class, 'poolConvertToProject']);
            // 通配放最后
            Route::get('{pool}',                     [SalesController::class, 'poolShow']);
            Route::put('{pool}',                     [SalesController::class, 'poolUpdate']);
        });

        // 跟进记录 + 附件
        Route::prefix('follow-ups')->group(function () {
            Route::get('/',                          [SalesController::class, 'followUpsIndex']);
            Route::post('/',                         [SalesController::class, 'followUpsStore']);
            // 附件下载 — attachments/{att} 必须在 {followUp} 之后注册，但子路径先注册
            Route::get('attachments/{att}/download', [SalesController::class, 'followUpsDownloadAttachment']);
            Route::delete('attachments/{att}',       [SalesController::class, 'followUpsDeleteAttachment']);
            // 子路径（{followUp} 通配之前）
            Route::post('{followUp}/attachments',    [SalesController::class, 'followUpsUploadAttachment']);
            // 通配放最后
            Route::get('{followUp}',                 [SalesController::class, 'followUpsShow']);
            Route::put('{followUp}',                 [SalesController::class, 'followUpsUpdate']);
            Route::delete('{followUp}',              [SalesController::class, 'followUpsDestroy']);
        });

        // 产品库（独立 controller）
        Route::prefix('products')->group(function () {
            // 子路径（{product} 通配之前）
            Route::get('categories',                 [SalesProductController::class, 'categories']);
            // 列表/新建
            Route::get('/',                          [SalesProductController::class, 'index']);
            Route::post('/',                         [SalesProductController::class, 'store']);
            // 通配放最后
            Route::get('{product}',                  [SalesProductController::class, 'show']);
            Route::put('{product}',                  [SalesProductController::class, 'update']);
            Route::delete('{product}',               [SalesProductController::class, 'destroy']);
        });
    });

    // ========== 采购管理（P1 后端补齐 v0.3.8.1） ==========
    // ⚠ 路由顺序：所有 {xxx}/action 子路径必须放在 GET/PUT/DELETE {xxx} 通配之前
    //   否则通配会吞掉 /submit /approve /ship /decide 等子动作
    Route::prefix('purchase')->group(function () {

        // 采购需求 (5 端点)
        Route::prefix('requirements')->group(function () {
            Route::get('/',                                  [PurchaseRequirementController::class, 'index']);
            Route::get('stats',                             [PurchaseRequirementController::class, 'stats']);
            Route::post('/',                                [PurchaseRequirementController::class, 'store']);
            // 通配放最后
            Route::put('{requirement}',                     [PurchaseRequirementController::class, 'update']);
            Route::delete('{requirement}',                  [PurchaseRequirementController::class, 'destroy']);
        });

        // 采购计划 (7 端点)
        Route::prefix('plans')->group(function () {
            Route::get('/',                                  [PurchasePlanController::class, 'index']);
            Route::get('stats',                             [PurchasePlanController::class, 'stats']);
            Route::post('/',                                [PurchasePlanController::class, 'store']);
            // 子路径必须在 {plan} 通配之前
            Route::post('{plan}/submit',                    [PurchasePlanController::class, 'submit']);
            Route::post('{plan}/approve',                   [PurchasePlanController::class, 'approve']);
            // 通配放最后
            Route::put('{plan}',                            [PurchasePlanController::class, 'update']);
            Route::delete('{plan}',                         [PurchasePlanController::class, 'destroy']);
        });

        // 采购合同 (7 端点)
        Route::prefix('contracts')->group(function () {
            Route::get('/',                                  [PurchaseContractController::class, 'index']);
            Route::get('stats',                             [PurchaseContractController::class, 'stats']);
            Route::post('/',                                [PurchaseContractController::class, 'store']);
            // 子路径必须在 {contract} 通配之前
            Route::post('{contract}/ship',                  [PurchaseContractController::class, 'ship']);
            // 通配放最后
            Route::get('{contract}',                        [PurchaseContractController::class, 'show']);
            Route::put('{contract}',                        [PurchaseContractController::class, 'update']);
            Route::delete('{contract}',                     [PurchaseContractController::class, 'destroy']);
        });

        // 采购付款申请 (5 端点)
        Route::prefix('payment-requests')->group(function () {
            Route::get('/',                                  [PurchasePaymentRequestController::class, 'index']);
            Route::get('stats',                             [PurchasePaymentRequestController::class, 'stats']);
            Route::post('/',                                [PurchasePaymentRequestController::class, 'store']);
            // 子路径必须在 {req} 通配之前
            Route::post('{req}/approve',                    [PurchasePaymentRequestController::class, 'approve']);
            // 通配放最后
            Route::delete('{req}',                          [PurchasePaymentRequestController::class, 'destroy']);
        });

        // 采购付款 (3 端点)
        Route::prefix('payments')->group(function () {
            Route::get('/',                                  [PurchasePaymentController::class, 'index']);
            Route::get('stats',                             [PurchasePaymentController::class, 'stats']);
            Route::post('/',                                [PurchasePaymentController::class, 'store']);
        });

        // 采购发货 (3 端点)
        // ⚠ shipments/{shipment} 通配必须在 shipments/{shipment}/logistics* 子路径之后
        Route::prefix('shipments')->group(function () {
            Route::get('/',                                  [PurchaseShipmentController::class, 'index']);
            Route::get('stats',                             [PurchaseShipmentController::class, 'stats']);
            // 物流更新/轨迹/列表 — 子路径必须先注册
            Route::post('{shipment}/logistics-update',      [PurchaseLogisticsController::class, 'store']);
            Route::get('{shipment}/logistics',              [PurchaseLogisticsController::class, 'index']);
            Route::get('{shipment}/track',                  [PurchaseLogisticsController::class, 'track']);
            Route::put('{shipment}/logistics/{log}',        [PurchaseLogisticsController::class, 'update']);
            // 通配放最后
            Route::get('{shipment}',                        [PurchaseShipmentController::class, 'show']);
        });

        // 物流总览 (前端 /purchase/logistics)
        Route::get('logistics',                              [PurchaseLogisticsController::class, 'overview']);

        // 采购审批 (3 端点)
        Route::prefix('approvals')->group(function () {
            Route::get('/',                                  [PurchaseApprovalController::class, 'index']);
            Route::post('/',                                [PurchaseApprovalController::class, 'store']);
            // 子路径必须在 {appr} 通配之前 — 本组没有 {appr} 通配，decide 可放任意位置
            Route::post('{appr}/decide',                    [PurchaseApprovalController::class, 'decide']);
        });
    });

    // 角色权限管理 (RBAC)
    Route::prefix('roles')->group(function () {
        Route::get('/', [RoleController::class, 'index']);
        Route::post('/', [RoleController::class, 'store']);
        Route::get('{role}', [RoleController::class, 'show']);
        Route::put('{role}', [RoleController::class, 'update']);
        Route::delete('{role}', [RoleController::class, 'destroy']);
        Route::post('{role}/permissions', [RoleController::class, 'assignPermissions']);
    });

    // 权限字典
    Route::prefix('permissions')->group(function () {
        Route::get('/', [\App\Http\Controllers\Api\RoleController::class, 'permissionIndex']);
        Route::get('tree', [\App\Http\Controllers\Api\RoleController::class, 'permissionTree']);
    });

    // 审计日志 (C2)
    Route::prefix('audit-logs')->group(function () {
        Route::get('/', [AuditController::class, 'index']);
        Route::get('{id}', [AuditController::class, 'show']);
    });

    // ========== 系统设置（标题/版权/公告/备案号/联系邮箱） ==========
    Route::get('settings', [SystemSettingsController::class, 'index']);
    Route::put('settings', [SystemSettingsController::class, 'update']);

    // ========== 系统设置 — 自定义端口（与 settings 平级，便于前端独立调用） ==========
    Route::get('settings/port', [SystemSettingsController::class, 'getPortConfig']);
    Route::put('settings/port', [SystemSettingsController::class, 'updatePortConfig']);

    // ========== 系统设置 — 闲置超时（给前端 useIdleTimer 启动时拉） ==========
    Route::get('settings/idle-config', [SystemSettingsController::class, 'getIdleConfig']);

    // ========== 审批流程模板（CRUD — 替代前端 hardcoded） ==========
    Route::get('approval-templates', [ApprovalTemplateController::class, 'index']);
    Route::post('approval-templates', [ApprovalTemplateController::class, 'store']);
    Route::get('approval-templates/{approvalTemplate}', [ApprovalTemplateController::class, 'show']);
    Route::put('approval-templates/{approvalTemplate}', [ApprovalTemplateController::class, 'update']);
    Route::delete('approval-templates/{approvalTemplate}', [ApprovalTemplateController::class, 'destroy']);
    Route::post('approval-templates/{approvalTemplate}/toggle', [ApprovalTemplateController::class, 'toggle']);

    // ========== 审批中心（财务 / 运营 / 项目 3 大类 + 统一聚合） ==========
    // 统一聚合（center 必须在 finance/operation/project 之前注册，避免被通配吞掉）
    Route::get('approvals/center',       [ApprovalCenterController::class, 'index']);
    Route::get('approvals/center/stats', [ApprovalCenterController::class, 'stats']);
    // 兼容前端直接调用 /approvals
    Route::get('approvals',              [ApprovalCenterController::class, 'index']);

    // 财务审批
    Route::prefix('approvals/finance')->group(function () {
        Route::get('/',                 [FinanceApprovalController::class, 'index']);
        Route::post('/',                [FinanceApprovalController::class, 'store']);
        // 子动作路由必须在 {approval} 通配之前
        Route::post('{approval}/approve', [FinanceApprovalController::class, 'approve']);
        Route::post('{approval}/reject',  [FinanceApprovalController::class, 'reject']);
        Route::post('{approval}/forward', [FinanceApprovalController::class, 'forward']);
        // 通配放最后
        Route::get('{approval}',         [FinanceApprovalController::class, 'show']);
    });

    // 运营审批
    Route::prefix('approvals/operation')->group(function () {
        Route::get('/',                 [OperationApprovalController::class, 'index']);
        Route::post('/',                [OperationApprovalController::class, 'store']);
        Route::post('{approval}/approve', [OperationApprovalController::class, 'approve']);
        Route::post('{approval}/reject',  [OperationApprovalController::class, 'reject']);
        Route::post('{approval}/forward', [OperationApprovalController::class, 'forward']);
        Route::get('{approval}',         [OperationApprovalController::class, 'show']);
    });

    // 项目审批
    Route::prefix('approvals/project')->group(function () {
        Route::get('/',                 [ProjectApprovalController::class, 'index']);
        Route::post('/',                [ProjectApprovalController::class, 'store']);
        Route::post('{approval}/approve', [ProjectApprovalController::class, 'approve']);
        Route::post('{approval}/reject',  [ProjectApprovalController::class, 'reject']);
        Route::post('{approval}/forward', [ProjectApprovalController::class, 'forward']);
        Route::get('{approval}',         [ProjectApprovalController::class, 'show']);
    });

    // 客户跟进日历（与 /api/sales/follow-ups/* 不冲突）
    // calendar 是字面量，定义在 {followUp} 通配之前
    Route::prefix('follow-ups')->group(function () {
        Route::get('calendar', [FollowUpCalendarController::class, 'index']);
        // 通配放最后（预留后续 GET /{followUp} 详情，避免与 calendar 冲突）
    });

    // ========== admin 一键清理业务数据（高危） ==========
    Route::post('admin/wipe-data', [SystemSettingsController::class, 'wipeData']);
});