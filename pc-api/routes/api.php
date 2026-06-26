<?php

use App\Http\Controllers\Api\{
    AuthController, DashboardController,
    AttendanceController, EmployeeController,     CustomerController,     CustomerPipelineController,
    ProjectController, ServiceController, ExpenseController,
    VehicleController, InventoryController, FinanceController,
    ExternalQuoteController, TenderController, PortalController,
    DiskController, KnowledgeController, NotificationController,
    SystemLogController, RoleController, AuditController, BackupController, FieldMaskController,
    SystemSettingsController, ApprovalTemplateController, FuelCardController,
    HealthCheckController,
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
    FollowUpCalendarController,
    WarrantyController, WarrantyServiceOrderController, WarrantyDepositController,
    // V0.5.5 维修中心
    WorkOrderController, RepairOrderController, RepairShipmentController, RepairMethodController, RepairProgressLogController, RepairStepPhotoController, PortalRepairController,
    // V0.5.7 块4 维修成本归集
    RepairCostSummaryController,
    // V0.5.7 块A 系统初始化向导
    SetupWizardController,
    // V0.5.7 块B 数据字典中心
    SystemDictController,
    // V0.5.7 块C 系统监控面板
    SystemMonitorController,
    // V0.5.7 块5 Dashboard 多维度 widget
    DashboardWidgetController,
    // v0.5.8: 供应商管理 (路由缺失,前端 404)
    SupplierController,
    // v0.5.8: 总账 (路由缺失,前端 404)
    LedgerController
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
// V1.1: 增强为 HealthCheckController (DB/Redis/Cache/Storage/Disk/Queue 全检)
Route::get('/health', [HealthCheckController::class, 'check']);
Route::get('/health/ready', [HealthCheckController::class, 'ready']);
Route::get('/health/live', [HealthCheckController::class, 'live']);

// 公开路由（无需认证）
Route::prefix('auth')->group(function () {
    // T2 登录限流: 1 分钟 5 次 — 防止暴力破解
    // V0.4.8 A2: 登录限流 5/min → 30/min (烟囱 + 多角色测试不再假 429)
    // V0.4.9 C2: 加 LoginThrottle middleware (5 次失败 → 锁 30 分钟, 白名单豁免)
    Route::post('login', [AuthController::class, 'login'])
        ->middleware('throttle:30,1')
        ->middleware(\App\Http\Middleware\LoginThrottle::class);
});

// V0.5.7 块3 — 客户端查询入口 (公开, 无需登录, 双因子验证)
Route::prefix('portal/repair')->group(function () {
    // 限流 10/min 防暴力枚举
    Route::get('/', [PortalRepairController::class, 'query'])
        ->middleware('throttle:10,1');
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
        Route::get('overview', [DashboardController::class, 'overview']);
        Route::get('warranty-stats', [DashboardController::class, 'warrantyStats']);
        Route::get('maintenance-stats', [DashboardController::class, 'maintenanceStats']);
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
        // V0.5.1 角色同步子路径 (必须在 {user} 通配之前)
        Route::put('{user}/roles', [RoleController::class, 'usersSyncRoles']);
        Route::post('bulk-assign-role', [RoleController::class, 'usersBulkAssignRole']);
        // V0.5.3 临时角色 (字面量子路径必须在 {user} 通配之前) — 需要 system.role 权限
        Route::get('{user}/roles', [RoleController::class, 'usersListRoles'])->middleware('permission:system.role');
        Route::post('{user}/roles/temporary', [RoleController::class, 'usersGrantTemporary'])->middleware('permission:system.role');
        Route::get('{user}/roles/active', [RoleController::class, 'usersActiveRoles'])->middleware('permission:system.role');
        Route::delete('{user}/roles/{role}', [RoleController::class, 'usersRevokeRole'])->middleware('permission:system.role');
        Route::get('{user}', [EmployeeController::class, 'show']);
        Route::put('{user}', [EmployeeController::class, 'update']);
        Route::delete('{user}', [EmployeeController::class, 'destroy']);
        Route::post('{user}/reset-password', [EmployeeController::class, 'resetPassword']);
    });

    // V0.5.1 用户-角色管理 (admin 限定) — 路由合并到 230 行的 users group 内
    // 这里只保留注释, 实际定义在更早的 /users prefix group
    // 客户管理
    Route::prefix('customers')->middleware('permission:customer.view')->group(function () {
        Route::get('/', [CustomerController::class, 'index']);
        Route::post('/', [CustomerController::class, 'store'])->middleware('permission:customer.create');
        Route::get('stats', [CustomerController::class, 'stats']);
        Route::get('industries', [CustomerController::class, 'industries']);  // v0.5.8
        Route::get('health', [CustomerController::class, 'health']);         // v0.5.8 (兼容旧 /customer-health/list)
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
        // v0.5.8.9 联系人管理
        Route::get('{customer}/contacts', [CustomerController::class, 'listContacts']);
        Route::post('{customer}/contacts', [CustomerController::class, 'storeContact']);
        Route::put('{customer}/contacts/{contact}', [CustomerController::class, 'updateContact'])->whereNumber('contact');
        Route::delete('{customer}/contacts/{contact}', [CustomerController::class, 'destroyContact'])->whereNumber('contact');
        // v0.5.8.9 开票信息
        Route::get('{customer}/invoice-infos', [CustomerController::class, 'listInvoiceInfos']);
        Route::post('{customer}/invoice-infos', [CustomerController::class, 'storeInvoiceInfo']);
        Route::put('{customer}/invoice-infos/{info}', [CustomerController::class, 'updateInvoiceInfo'])->whereNumber('info');
        Route::delete('{customer}/invoice-infos/{info}', [CustomerController::class, 'destroyInvoiceInfo'])->whereNumber('info');
        // 放最后 — {customer} 通配符会吞掉子路径
        Route::get('{customer}', [CustomerController::class, 'show']);
        Route::put('{customer}', [CustomerController::class, 'update']);
        Route::put('{customer}/stage', [CustomerPipelineController::class, 'updateStage']);
        Route::delete('{customer}', [CustomerController::class, 'destroy']);
    });

    // v0.5.8: 供应商管理 (补 SupplierController 路由)
    Route::prefix('suppliers')->middleware('permission:supplier.view')->group(function () {
        Route::get('/', [SupplierController::class, 'index']);
        Route::post('/', [SupplierController::class, 'store'])->middleware('permission:supplier.create');
        Route::get('{id}', [SupplierController::class, 'show'])->whereNumber('id');
        Route::put('{id}', [SupplierController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [SupplierController::class, 'destroy'])->whereNumber('id');
        Route::post('{id}/change-status', [SupplierController::class, 'changeStatus'])->whereNumber('id');
        Route::post('{id}/sync-contacts', [SupplierController::class, 'syncContacts'])->whereNumber('id');
        Route::get('{id}/evaluations', [SupplierController::class, 'evaluations'])->whereNumber('id');
    });

    // v0.5.8: 总账 (补 LedgerController 路由, 财务模块用)
    Route::prefix('ledger')->group(function () {
        Route::get('suppliers', [LedgerController::class, 'suppliers']);
        Route::get('suppliers/{id}', [LedgerController::class, 'supplierLedger'])->whereNumber('id');
        Route::get('suppliers/{id}/payables', [LedgerController::class, 'supplierPayables'])->whereNumber('id');
        Route::post('supplier-payments', [LedgerController::class, 'createSupplierPayment']);
        Route::get('supplier-payments/{id}', [LedgerController::class, 'showSupplierPayment'])->whereNumber('id');
        Route::get('customers', [LedgerController::class, 'customers']);
        Route::get('customers/{id}', [LedgerController::class, 'customerLedger'])->whereNumber('id');
        Route::get('customers/{id}/receivables', [LedgerController::class, 'customerReceivables'])->whereNumber('id');
        Route::post('customer-receipts', [LedgerController::class, 'createCustomerReceipt']);
        Route::get('customer-receipts/{id}', [LedgerController::class, 'showCustomerReceipt'])->whereNumber('id');
        Route::get('summary', [LedgerController::class, 'summary']);
        Route::get('aging', [LedgerController::class, 'aging']);
    });

    // 项目管理
    // 项目管理 (V0.5.1 L4 字段脱敏: budget/contract_amount 对非财务角色 ***)
    Route::prefix('projects')->middleware(['permission:project.view', 'field_mask'])->group(function () {
        Route::get('/', [ProjectController::class, 'index']);
        Route::post('/', [ProjectController::class, 'store'])->middleware('permission:project.create');
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
        // V0.5.7 块1 — 项目售后记录 (工单+返修)
        Route::get('{project}/maintenance', [ProjectController::class, 'maintenance']);
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
        // V0.5.5: 旧的 service-orders 端点保留 (前端 ServiceController 还在用, 待 V0.5.6 移除)
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

    // ============== V0.5.5 维修中心 (利旧 + 重新设计) ==============

    // 维修工单 (10 端点)
    Route::prefix('work-orders')->group(function () {
        Route::get('stats', [WorkOrderController::class, 'stats']);
        Route::get('/', [WorkOrderController::class, 'index']);
        Route::post('/', [WorkOrderController::class, 'store']);
        Route::get('{id}', [WorkOrderController::class, 'show'])->whereNumber('id');
        Route::put('{id}', [WorkOrderController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [WorkOrderController::class, 'destroy'])->whereNumber('id');
        Route::post('{id}/assign', [WorkOrderController::class, 'assign'])->whereNumber('id');
        Route::post('{id}/start', [WorkOrderController::class, 'start'])->whereNumber('id');
        Route::post('{id}/resolve', [WorkOrderController::class, 'resolve'])->whereNumber('id');
        Route::post('{id}/cancel', [WorkOrderController::class, 'cancel'])->whereNumber('id');
        // 关键: 转返修
        Route::post('{id}/convert-to-repair', [WorkOrderController::class, 'convertToRepair'])->whereNumber('id');
    });

    // 返修管理 (主单 9 端点)
    Route::prefix('repair-orders')->group(function () {
        Route::get('stats', [RepairOrderController::class, 'stats']);
        Route::get('/', [RepairOrderController::class, 'index']);
        Route::post('/', [RepairOrderController::class, 'store']);
        Route::get('{id}', [RepairOrderController::class, 'show'])->whereNumber('id');
        Route::put('{id}', [RepairOrderController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [RepairOrderController::class, 'destroy'])->whereNumber('id');
        Route::post('{id}/cancel', [RepairOrderController::class, 'cancel'])->whereNumber('id');
        Route::post('{id}/ship-out', [RepairOrderController::class, 'shipOut'])->whereNumber('id');
        Route::post('{id}/ship-back', [RepairOrderController::class, 'shipBack'])->whereNumber('id');
        Route::post('{id}/in-repair', [RepairOrderController::class, 'markInRepair'])->whereNumber('id');
        Route::post('{id}/repaired', [RepairOrderController::class, 'markRepaired'])->whereNumber('id');
        Route::post('{id}/close', [RepairOrderController::class, 'close'])->whereNumber('id');
    });

    // 物流子资源 (按返修单 id 嵌套)
    Route::prefix('repair-orders/{repairOrderId}/shipments')->whereNumber('repairOrderId')->group(function () {
        Route::get('/', [RepairShipmentController::class, 'index']);
        Route::post('/', [RepairShipmentController::class, 'store']);
        Route::put('{id}', [RepairShipmentController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [RepairShipmentController::class, 'destroy'])->whereNumber('id');
    });

    // 维修方式 (按返修单 id 嵌套)
    Route::prefix('repair-orders/{repairOrderId}/methods')->whereNumber('repairOrderId')->group(function () {
        Route::get('/', [RepairMethodController::class, 'index']);
        Route::post('/', [RepairMethodController::class, 'store']);
        Route::put('{id}', [RepairMethodController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [RepairMethodController::class, 'destroy'])->whereNumber('id');
    });

    // 维修进度日志
    Route::prefix('repair-orders/{repairOrderId}/progress-logs')->whereNumber('repairOrderId')->group(function () {
        Route::get('/', [RepairProgressLogController::class, 'index']);
        Route::post('/', [RepairProgressLogController::class, 'store']);
        Route::delete('{id}', [RepairProgressLogController::class, 'destroy'])->whereNumber('id');
    });

    // 维修附件 (V0.5.5.2 A6 — 物流凭证图/过程照片)
    Route::prefix('repair-orders/{repairOrderId}/attachments')->whereNumber('repairOrderId')->group(function () {
        Route::get('/', [RepairOrderController::class, 'listAttachments']);
        Route::post('/', [RepairOrderController::class, 'uploadAttachment']);
        Route::delete('{id}', [RepairOrderController::class, 'deleteAttachment'])->whereNumber('id');
    });

    // V0.5.7 块2 — 维修过程照片 (7 步进度, 工单+返修共用)
    Route::prefix('step-photos')->group(function () {
        Route::get('/', [RepairStepPhotoController::class, 'index']);
        Route::post('/', [RepairStepPhotoController::class, 'store']);
        Route::delete('{id}', [RepairStepPhotoController::class, 'destroy'])->whereNumber('id');
    });

    // V0.5.7 块4 — 维修成本归集 (4 维度 + dashboard widget)
    Route::prefix('repair-cost')->group(function () {
        Route::get('overview',  [RepairCostSummaryController::class, 'overview']);
        Route::get('by-month',   [RepairCostSummaryController::class, 'byMonth']);
        Route::get('by-project', [RepairCostSummaryController::class, 'byProject']);
        Route::get('by-customer',[RepairCostSummaryController::class, 'byCustomer']);
        Route::get('by-method',  [RepairCostSummaryController::class, 'byMethod']);
    });

    // V0.5.7 块A — 系统初始化向导 (5 步)
    Route::prefix('setup')->group(function () {
        Route::get('summary',     [SetupWizardController::class, 'summary']);
        Route::post('step1',      [SetupWizardController::class, 'step1']);
        Route::post('step3',      [SetupWizardController::class, 'step3']);
        Route::post('step4',      [SetupWizardController::class, 'step4']);
        Route::post('complete',   [SetupWizardController::class, 'complete']);
        Route::get('sample-csv',  [SetupWizardController::class, 'sampleCsv']);
    });

    // V0.5.7 块B — 数据字典中心
    Route::prefix('dict')->group(function () {
        Route::get('kinds',         [SystemDictController::class, 'kinds']);
        Route::get('grouped',       [SystemDictController::class, 'grouped']);
        Route::get('/',             [SystemDictController::class, 'index']);
        Route::post('/',            [SystemDictController::class, 'store']);
        Route::post('reorder',      [SystemDictController::class, 'reorder']);
        Route::post('seed-defaults',[SystemDictController::class, 'seedDefaults']);
        Route::patch('{id}',        [SystemDictController::class, 'update'])->whereNumber('id');
        Route::delete('{id}',       [SystemDictController::class, 'destroy'])->whereNumber('id');
    });

    // V0.5.7 块C — 系统监控 (admin only)
    Route::prefix('admin/monitor')->group(function () {
        Route::get('metrics',    [SystemMonitorController::class, 'metrics']);
        Route::get('disk',       [SystemMonitorController::class, 'disk']);
        Route::get('db',         [SystemMonitorController::class, 'db']);
        Route::get('services',   [SystemMonitorController::class, 'services']);
        Route::get('errors',     [SystemMonitorController::class, 'errors']);
        Route::get('backups',    [SystemMonitorController::class, 'backups']);
    });

    // V1.1 — Prometheus 指标端点 (admin only, 供 Prometheus 抓取)
    Route::get('health/metrics', [HealthCheckController::class, 'metrics']);

    // V0.5.7 块5 — Dashboard 多维度 widget (4 维度)
    Route::prefix('dashboard/widget')->group(function () {
        Route::get('method-distribution', [DashboardWidgetController::class, 'methodDistribution']);
        Route::get('cycle-percentile',    [DashboardWidgetController::class, 'cyclePercentile']);
        Route::get('fault-top',           [DashboardWidgetController::class, 'faultTop']);
        Route::get('technician-rank',     [DashboardWidgetController::class, 'technicianRank']);
        Route::get('all',                 [DashboardWidgetController::class, 'all']);
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
    Route::prefix('inventory')->middleware('permission:inventory.view')->group(function () {
        Route::get('/', [InventoryController::class, 'index']);
        Route::post('/', [InventoryController::class, 'store'])->middleware('permission:inventory.create');
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

    // 财务管理 (V0.5.1 L4 字段脱敏: 金额对非财务角色 ***)
    Route::prefix('finance')->middleware(['permission:finance.view', 'field_mask'])->group(function () {
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
            Route::patch('{lead}/status',            [SalesController::class, 'leadsUpdateStatus'])->middleware('owns:lead');
            Route::post('{lead}/convert-to-opp',     [SalesController::class, 'leadsConvertToOpp'])->middleware('owns:lead');
            Route::get('{lead}',                     [SalesController::class, 'leadsShow'])->middleware('owns:lead');
            Route::put('{lead}',                     [SalesController::class, 'leadsUpdate'])->middleware('owns:lead');
            Route::delete('{lead}',                  [SalesController::class, 'leadsDestroy'])->middleware('owns:lead');
        });

        // 商机池
        Route::prefix('opps')->group(function () {
            Route::get('/',                          [SalesController::class, 'oppsIndex']);
            Route::get('stage-options',              [SalesController::class, 'oppsStageOptions']);
            Route::get('funnel',                     [SalesController::class, 'oppsFunnel']);
            Route::get('lost-reasons',               [SalesController::class, 'oppsLostReasons']);
            // 子路径（{opp} 通配之前）
            Route::post('/',                         [SalesController::class, 'oppsStore']);
            Route::patch('{opp}/stage',              [SalesController::class, 'oppsUpdateStage'])->middleware('owns:opp');
            Route::post('{opp}/mark-won',            [SalesController::class, 'oppsMarkWon'])->middleware('owns:opp');
            Route::post('{opp}/mark-lost',           [SalesController::class, 'oppsMarkLost'])->middleware('owns:opp');
            // 商机下报价单（子操作）
            Route::get('{opp}/quotations',           [SalesController::class, 'oppsQuotationsIndex'])->middleware('owns:opp');
            Route::post('{opp}/quotations',          [SalesController::class, 'oppsQuotationsStore'])->middleware('owns:opp');
            // 商机状态机
            Route::post('{opp}/win',                 [SalesController::class, 'oppsWin'])->middleware('owns:opp');
            Route::post('{opp}/lose',                [SalesController::class, 'oppsLose'])->middleware('owns:opp');
            Route::post('{opp}/hold',                [SalesController::class, 'oppsHold'])->middleware('owns:opp');
            Route::post('{opp}/move-to-project-pool',[SalesController::class, 'oppsMoveToProjectPool'])->middleware('owns:opp');
            Route::post('{opp}/assign',              [SalesController::class, 'oppsAssign'])->middleware('owns:opp');
            Route::post('{opp}/revive',              [SalesController::class, 'oppsRevive'])->middleware('owns:opp');
            // 通配放最后
            Route::get('{opp}',                      [SalesController::class, 'oppsShow'])->middleware('owns:opp');
            Route::put('{opp}',                      [SalesController::class, 'oppsUpdate'])->middleware('owns:opp');
            Route::delete('{opp}',                   [SalesController::class, 'oppsDestroy'])->middleware('owns:opp');
        });

        // 报价单
        Route::prefix('quotes')->group(function () {
            Route::get('/',                          [SalesController::class, 'quotesIndex']);
            Route::get('status-options',             [SalesController::class, 'quotesStatusOptions']);
            // 子路径（{quote} 通配之前）
            Route::post('/',                         [SalesController::class, 'quotesStore']);
            Route::put('{quote}/status',             [SalesController::class, 'quotesUpdateStatus'])->middleware('owns:quote');
            Route::post('{quote}/items',             [SalesController::class, 'quotesStoreItems'])->middleware('owns:quote');
            Route::post('{quote}/new-version',       [SalesController::class, 'quotesNewVersion'])->middleware('owns:quote');
            // 客户动作（accept/reject/revise）
            Route::post('{quote}/accept',            [SalesController::class, 'quotationsAccept'])->middleware('owns:quote');
            Route::post('{quote}/reject',            [SalesController::class, 'quotationsReject'])->middleware('owns:quote');
            Route::post('{quote}/revise',            [SalesController::class, 'quotationsRevise'])->middleware('owns:quote');
            // 通配放最后
            Route::get('{quote}',                    [SalesController::class, 'quotesShow'])->middleware('owns:quote');
            Route::put('{quote}',                    [SalesController::class, 'quotesUpdate'])->middleware('owns:quote');
            Route::delete('{quote}',                 [SalesController::class, 'quotesDestroy'])->middleware('owns:quote');
        });

        // 报价单（quotations 别名路由 — 兼容前端可能的 /sales/quotations/{id}/... 调用）
        Route::prefix('quotations')->group(function () {
            Route::get('{quotation}',                [SalesController::class, 'quotationsShow'])->middleware('owns:quotation');
            Route::put('{quotation}',                [SalesController::class, 'quotationsUpdate'])->middleware('owns:quotation');
            Route::delete('{quotation}',             [SalesController::class, 'quotationsDestroy'])->middleware('owns:quotation');
            Route::post('{quotation}/accept',        [SalesController::class, 'quotationsAccept'])->middleware('owns:quotation');
            Route::post('{quotation}/reject',        [SalesController::class, 'quotationsReject'])->middleware('owns:quotation');
            Route::post('{quotation}/revise',        [SalesController::class, 'quotationsRevise'])->middleware('owns:quotation');
        });

        // 推荐人
        Route::prefix('referrers')->group(function () {
            Route::get('/',                          [SalesController::class, 'referrersIndex']);
            Route::post('/',                         [SalesController::class, 'referrersStore']);
            // 通配放最后
            Route::get('{referrer}',                 [SalesController::class, 'referrersShow'])->middleware('owns:referrer');
            Route::put('{referrer}',                 [SalesController::class, 'referrersUpdate'])->middleware('owns:referrer');
            Route::delete('{referrer}',              [SalesController::class, 'referrersDestroy'])->middleware('owns:referrer');
        });

        // 项目池
        Route::prefix('pool')->group(function () {
            Route::get('/',                          [SalesController::class, 'poolIndex']);
            // 子路径（{pool} 通配之前）
            Route::post('{pool}/convert-to-project', [SalesController::class, 'poolConvertToProject'])->middleware('owns:pool');
            // 通配放最后
            Route::get('{pool}',                     [SalesController::class, 'poolShow'])->middleware('owns:pool');
            Route::put('{pool}',                     [SalesController::class, 'poolUpdate'])->middleware('owns:pool');
        });

        // 跟进记录 + 附件
        Route::prefix('follow-ups')->group(function () {
            Route::get('/',                          [SalesController::class, 'followUpsIndex']);
            Route::post('/',                         [SalesController::class, 'followUpsStore']);
            // 附件下载 — attachments/{att} 必须在 {followUp} 之后注册，但子路径先注册
            Route::get('attachments/{att}/download', [SalesController::class, 'followUpsDownloadAttachment'])->middleware('owns:att');
            Route::delete('attachments/{att}',       [SalesController::class, 'followUpsDeleteAttachment'])->middleware('owns:att');
            // 子路径（{followUp} 通配之前）
            Route::post('{followUp}/attachments',    [SalesController::class, 'followUpsUploadAttachment'])->middleware('owns:followUp');
            // 通配放最后
            Route::get('{followUp}',                 [SalesController::class, 'followUpsShow'])->middleware('owns:followUp');
            Route::put('{followUp}',                 [SalesController::class, 'followUpsUpdate'])->middleware('owns:followUp');
            Route::delete('{followUp}',              [SalesController::class, 'followUpsDestroy'])->middleware('owns:followUp');
        });

        // 推荐人居间费结算 (v0.3.11 P0 块六)
        Route::prefix('referral-settlements')->group(function () {
            Route::get('/',                                [SalesController::class, 'referralSettlementsIndex']);
            Route::get('stats',                           [SalesController::class, 'referralSettlementsStats']);
            // 子路径必须在 {settlement} 通配之前
            Route::post('{settlement}/approve',           [SalesController::class, 'referralSettlementsApprove']);
            Route::post('{settlement}/pay',               [SalesController::class, 'referralSettlementsPay']);
            // 通配放最后
            Route::get('{settlement}',                    [SalesController::class, 'referralSettlementsShow']);
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

    // ========== 招标中心 (V0.6.0 内部) ==========
    Route::prefix('tenders')->group(function () {
        Route::get('/',                      [TenderController::class, 'index']);
        Route::post('/',                     [TenderController::class, 'store']);
        // 子路径必须在 {id} 通配之前
        Route::post('{id}/publish',          [TenderController::class, 'publish'])->whereNumber('id');
        Route::post('{id}/close',            [TenderController::class, 'close'])->whereNumber('id');
        Route::post('{id}/cancel',           [TenderController::class, 'cancel'])->whereNumber('id');
        Route::post('{id}/evaluate',         [TenderController::class, 'evaluate'])->whereNumber('id');
        Route::post('{id}/award',            [TenderController::class, 'award'])->whereNumber('id');
        Route::get('{id}/bids',              [TenderController::class, 'bids'])->whereNumber('id');
        Route::post('{id}/bids',             [TenderController::class, 'storeBid'])->whereNumber('id');
        Route::get('{id}/attachments',       [TenderController::class, 'listAttachments'])->whereNumber('id');
        Route::post('{id}/attachments',      [TenderController::class, 'uploadAttachment'])->whereNumber('id');
        Route::delete('{id}/attachments/{att}', [TenderController::class, 'deleteAttachment'])->whereNumber(['id', 'att']);
        // 通配放最后
        Route::get('{id}',                   [TenderController::class, 'show'])->whereNumber('id');
        Route::put('{id}',                   [TenderController::class, 'update'])->whereNumber('id');
    });

    // ========== 供应商门户 (V0.6.0 外部免登录 — 必须在 auth:sanctum group 外) ==========
    // ⚠️ portal 块已移出此 group — 见文件末尾
    // 保留 placeholder 注释, 不再重复定义

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
        // V0.5.2 矩阵端点 (字面量必须在 {role} 通配之前)
        Route::get('matrix', [RoleController::class, 'matrix']);
        // V0.5.3 临时角色 — 7 天内即将过期 (字面量必须在 {role} 通配之前) — 需要 system.role 权限
        Route::get('expiring', [RoleController::class, 'expiringSoon'])->middleware('permission:system.role');
        // 限制 {role} 只匹配数字 id, 防止 'matrix' 'permissions' 'expiring' 等被当 name 强转 bigint 22P02
        Route::get('{role}', [RoleController::class, 'show'])->whereNumber('role');
        Route::put('{role}', [RoleController::class, 'update'])->whereNumber('role');
        Route::delete('{role}', [RoleController::class, 'destroy'])->whereNumber('role');
        Route::post('{role}/permissions', [RoleController::class, 'assignPermissions'])->whereNumber('role');
    });

    // V0.5.1 用户-角色管理 (admin 限定) — 路由合并到 230 行的 users group 内
    // 这里只保留注释, 实际定义在更早的 /users prefix group

    // 权限字典
    Route::prefix('permissions')->group(function () {
        Route::get('/', [\App\Http\Controllers\Api\RoleController::class, 'permissionIndex']);
        Route::get('tree', [\App\Http\Controllers\Api\RoleController::class, 'permissionTree']);
        // V0.5.0 L1: 当前用户的所有权限
        Route::get('my', [\App\Http\Controllers\Api\RoleController::class, 'myPermissions']);
    });

    // V0.5.2 角色权限矩阵 + 继承图 (admin 限定)
    Route::middleware('permission:system.role')->group(function () {
        Route::get('roles/matrix', [\App\Http\Controllers\Api\RoleController::class, 'matrix']);
        Route::get('permissions/inheritance', [\App\Http\Controllers\Api\RoleController::class, 'inheritanceGraph']);
    });

    // V0.5.2 字段脱敏规则管理 (admin 限定)
    // 字段脱敏 (V0.5.2 后端 + V0.5.4 端点元数据)
    Route::prefix('field-masks')->middleware('permission:system.role')->group(function () {
        Route::get('/', [FieldMaskController::class, 'index']);
        Route::get('endpoints', [FieldMaskController::class, 'endpoints']);
        Route::post('/', [FieldMaskController::class, 'store']);
        Route::put('{id}', [FieldMaskController::class, 'update'])->whereNumber('id');
        Route::delete('{id}', [FieldMaskController::class, 'destroy'])->whereNumber('id');
        Route::post('flush-cache', [FieldMaskController::class, 'flushCache']);
        // V0.5.6 B5 — 批量预览脱敏效果
        Route::post('preview', [FieldMaskController::class, 'preview']);
    });

    // 审计日志 (C2)
    Route::prefix('audit-logs')->group(function () {
        Route::get('/', [AuditController::class, 'index']);
        Route::get('{id}', [AuditController::class, 'show']);
    });

    // V0.4.10 对外报价 (ExternalQuote 控制器接入)
    Route::prefix('external-quotes')->group(function () {
        Route::get('requests',          [ExternalQuoteController::class, 'indexRequests']);
        Route::post('requests',         [ExternalQuoteController::class, 'storeRequest']);
        // 附件 (子路径必须在 {id} 通配之前)
        Route::post('requests/{id}/files',   [ExternalQuoteController::class, 'uploadRequiredFile'])->whereNumber('id');
        Route::delete('requests/{id}/files', [ExternalQuoteController::class, 'deleteRequiredFile'])->whereNumber('id');
        Route::get('requests/{id}',     [ExternalQuoteController::class, 'showRequest']);
        // v0.5.8.10 通用附件上传 (新建请求时使用, 不依赖 request id)
        Route::post('upload-attachment', [ExternalQuoteController::class, 'uploadAttachment']);
    });

    // 排班/班次/班组 (V0.4.10 兼容路径 - 实际是 /schedules/shifts /schedules/groups)
    Route::get('attendance/shifts', fn() => redirect()->to('/api/schedules/shifts'));
    Route::get('attendance/groups', fn() => redirect()->to('/api/schedules/groups'));

    // V0.4.9 C1: 数据权限审计报表
    Route::prefix('audit/data-scope')->group(function () {
        Route::get('denied',  [\App\Http\Controllers\Api\AuditController::class, 'dataScopeDenied']);
        Route::get('summary', [\App\Http\Controllers\Api\AuditController::class, 'dataScopeSummary']);
        Route::get('stats',   [\App\Http\Controllers\Api\AuditController::class, 'dataScopeStats']);
    });

    // V0.5.4 权限变更流水 (role_changed / temporary_role_granted / role_revoked)
    Route::prefix('audit')->group(function () {
        Route::get('role-changes', [\App\Http\Controllers\Api\AuditController::class, 'roleChanges'])
            ->middleware('permission:system.role');
        Route::get('role-changes/summary', [\App\Http\Controllers\Api\AuditController::class, 'roleChangesSummary'])
            ->middleware('permission:system.role');
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

    // =============================================
    // V0.4.1 项目预算 (Construction Budget)
    // =============================================
    Route::prefix('construction/budgets')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\BudgetController::class, 'index']);
        Route::get('/summary/{projectId}', [App\Http\Controllers\Api\Construction\BudgetController::class, 'summary']);
        Route::post('/', [App\Http\Controllers\Api\Construction\BudgetController::class, 'store']);
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\BudgetController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\BudgetController::class, 'update'])->where('id', '[0-9]+');
        Route::post('/{id}/approve', [App\Http\Controllers\Api\Construction\BudgetController::class, 'approve'])->where('id', '[0-9]+');
        Route::post('/{id}/revise', [App\Http\Controllers\Api\Construction\BudgetController::class, 'revise'])->where('id', '[0-9]+');
        Route::delete('/{id}', [App\Http\Controllers\Api\Construction\BudgetController::class, 'destroy'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.3 施工团队 (Construction Teams)
    // =============================================
    Route::prefix('construction/teams')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\TeamController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\TeamController::class, 'store']);
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\TeamController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\TeamController::class, 'update'])->where('id', '[0-9]+');
        Route::delete('/{id}', [App\Http\Controllers\Api\Construction\TeamController::class, 'destroy'])->where('id', '[0-9]+');
        // 子路径必须放在 {id} 通配之前
        Route::post('/{id}/members', [App\Http\Controllers\Api\Construction\TeamController::class, 'addMembers'])->where('id', '[0-9]+');
        Route::delete('/{id}/members/{memberId}', [App\Http\Controllers\Api\Construction\TeamController::class, 'removeMember'])->where('id', '[0-9]+')->where('memberId', '[0-9]+');
    });

    // =============================================
    // V0.4.3 开工单 (Commencement Orders)
    // =============================================
    Route::prefix('construction/commencement-orders')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'store']);
        // 子动作（approve/start/complete）必须放在 {id} 通配之前
        Route::post('/{id}/approve', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'approve'])->where('id', '[0-9]+');
        Route::post('/{id}/start', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'startWork'])->where('id', '[0-9]+');
        Route::post('/{id}/complete', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'complete'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\CommencementOrderController::class, 'update'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.3 施工日志 (Construction Logs / Daily Logs)
    // =============================================
    Route::prefix('construction/logs')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'store']);
        // 字面量路由 overdue 必须在 {id} 通配之前
        Route::get('/overdue', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'overdue']);
        // 子动作路由（submit/progress）必须放在 {id} 通配之前
        Route::post('/{id}/submit', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'submit'])->where('id', '[0-9]+');
        Route::post('/{id}/progress', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'updateProgress'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\ConstructionLogController::class, 'update'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.3 整改工单 (Rectifications) — V0.4.4 占位
    // =============================================
    Route::prefix('construction/rectifications')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\RectificationController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\RectificationController::class, 'store']);
        // 子动作路由（complete）必须放在 {id} 通配之前
        Route::post('/{id}/complete', [App\Http\Controllers\Api\Construction\RectificationController::class, 'complete'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\RectificationController::class, 'show'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.3 工序字典 (Work Processes Dictionary)
    // =============================================
    Route::prefix('construction/work-processes')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\WorkProcessController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\WorkProcessController::class, 'store']);
        // {id} 通配放最后
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\WorkProcessController::class, 'update'])->where('id', '[0-9]+');
        Route::delete('/{id}', [App\Http\Controllers\Api\Construction\WorkProcessController::class, 'destroy'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.3 施工发包 (External Construction / 公开+内部)
    // =============================================
    Route::prefix('construction/external-works')->group(function () {
        Route::get('/', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'index']);
        Route::post('/', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'store']);
        // 字面子路径 bids (GET) 必须放在 {id} 通配之前
        Route::get('/{id}/bids', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'listBids'])->where('id', '[0-9]+');
        // 子动作路由（close/bids POST/award）必须放在 {id} 通配之前
        Route::post('/{id}/close', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'close'])->where('id', '[0-9]+');
        Route::post('/{id}/bids', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'submitBid'])->where('id', '[0-9]+');
        Route::post('/{id}/award', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'award'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [App\Http\Controllers\Api\Construction\ExternalConstructionController::class, 'update'])->where('id', '[0-9]+');
    });

    // =============================================
    // V0.4.5 质保期管理 (Warranty)
    // =============================================
    // 质保期主表
    Route::prefix('warranties')->middleware('permission:warranty.view')->group(function () {
        // 字面量路由（expiring）必须在 /{id} 通配之前
        Route::get('expiring', [WarrantyController::class, 'expiring']);
        Route::get('/', [WarrantyController::class, 'index']);
        Route::post('/', [WarrantyController::class, 'store']);
        // 子动作（renew/terminate）必须在 /{id} 通配之前
        Route::post('/{id}/renew', [WarrantyController::class, 'renew'])->where('id', '[0-9]+');
        Route::post('/{id}/terminate', [WarrantyController::class, 'terminate'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [WarrantyController::class, 'show'])->where('id', '[0-9]+');
        Route::put('/{id}', [WarrantyController::class, 'update'])->where('id', '[0-9]+');
        Route::delete('/{id}', [WarrantyController::class, 'destroy'])->where('id', '[0-9]+');
    });

    // 质保期服务工单
    Route::prefix('warranty-service-orders')->group(function () {
        // 字面量路由（technician-stats）必须在 /{id} 通配之前
        Route::get('technician-stats', [WarrantyServiceOrderController::class, 'technicianStats']);
        Route::get('/', [WarrantyServiceOrderController::class, 'index']);
        Route::post('/', [WarrantyServiceOrderController::class, 'store']);
        // 子动作（assign/start/complete/cancel）必须在 /{id} 通配之前
        Route::post('/{id}/assign', [WarrantyServiceOrderController::class, 'assign'])->where('id', '[0-9]+');
        Route::post('/{id}/start', [WarrantyServiceOrderController::class, 'start'])->where('id', '[0-9]+');
        Route::post('/{id}/complete', [WarrantyServiceOrderController::class, 'complete'])->where('id', '[0-9]+');
        Route::post('/{id}/cancel', [WarrantyServiceOrderController::class, 'cancel'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [WarrantyServiceOrderController::class, 'show'])->where('id', '[0-9]+');
    });

    // 质保期保证金
    Route::prefix('warranty-deposits')->group(function () {
        Route::get('/', [WarrantyDepositController::class, 'index']);
        Route::post('/', [WarrantyDepositController::class, 'store']);
        // 子动作（partial-release/full-release/forfeit）必须在 /{id} 通配之前
        Route::post('/{id}/partial-release', [WarrantyDepositController::class, 'partialRelease'])->where('id', '[0-9]+');
        Route::post('/{id}/full-release', [WarrantyDepositController::class, 'fullRelease'])->where('id', '[0-9]+');
        Route::post('/{id}/forfeit', [WarrantyDepositController::class, 'forfeit'])->where('id', '[0-9]+');
        // 通配放最后
        Route::get('/{id}', [WarrantyDepositController::class, 'show'])->where('id', '[0-9]+');
    });
});

// ========== 供应商门户 (V0.6.0 外部免登录 — 必须在 auth:sanctum group 外) ==========
Route::prefix('portal')->group(function () {
    Route::get('invitations',                            [PortalController::class, 'invitations']);
    Route::get('t/{token}',                              [PortalController::class, 'tenderByToken']);
    Route::get('t/{token}/my-bid',                       [PortalController::class, 'myBid']);
    Route::post('t/{token}/bids',                        [PortalController::class, 'submitBid']);
    Route::post('t/{token}/bids/attachments',            [PortalController::class, 'uploadBidAttachment']);
});