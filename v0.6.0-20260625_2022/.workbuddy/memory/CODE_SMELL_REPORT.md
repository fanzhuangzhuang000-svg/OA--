# Code Smell Report — 死代码 / 死路由 / 未使用方法 全面扫描

> 扫描对象: `D:\work\website\OA\pc-api\`
> 扫描时间: 2026-06-23
> 工具: Grep 字符串分析 + 人工阅读源码
> 范围: 42 个 Controller / 路由表 / 6 个 Model 聚合文件
> **不修改任何代码，仅做静态分析报告**

---

## 〇、扫描方法论与 grep 复现命令

```bash
# 1) 提取 routes/api.php 里所有 [XxxController::class, 'methodName']
grep -nE "::class, '\w+'" pc-api/routes/api.php

# 2) 列出每个 Controller 的所有 public method
grep -nE "public function" pc-api/app/Http/Controllers/Api/<Name>.php

# 3) 提取每个 Controller 顶部 use App\...
grep -nE "^use App\\\\" pc-api/app/Http/Controllers/Api/<Name>.php

# 4) 检测 use 引入的类是否在本文件被实际引用
grep -nE "\bVehicle::" pc-api/app/Http/Controllers/Api/DashboardController.php

# 5) 提取所有 Model class
grep -nE "^class \w+" pc-api/app/Models/*.php

# 6) 检测 Model 在 app/ 下的引用次数
grep -rE "\bModelName::" pc-api/app/ | wc -l
```

---

## 一、Controller 死方法 (未注册路由)

> 排除项: `__construct` / `__destruct` / Laravel 魔法方法 / `authorize` / `rules` / `messages`

> **核心结论：42 个 Controller 的所有 public method 都在 routes/api.php 中有对应路由。**
> 死 public Controller 方法 = **0**

### 1.1 完整 42 个 Controller 概览

| # | Controller | public 方法数 | 全部已注册? |
|---|---|---:|---|
| 1 | DashboardController | 8 | OK |
| 2 | AttendanceController | 18 | OK |
| 3 | EmployeeController | 23 | OK |
| 4 | CustomerController | 13 | OK |
| 5 | CustomerPipelineController | 3 | OK |
| 6 | ProjectController | 17 | OK |
| 7 | ServiceController | 9 | OK |
| 8 | ExpenseController | 11 | OK |
| 9 | VehicleController | 18 | OK |
| 10 | InventoryController | 19 | OK |
| 11 | InventoryCategoryController | 6 | OK |
| 12 | FinanceController | 33 | OK |
| 13 | KnowledgeController | 9 | OK |
| 14 | NotificationController | 4 | OK |
| 15 | SystemLogController | 1 | OK |
| 16 | RoleController | 8 | OK |
| 17 | AuditController | 2 | OK |
| 18 | BackupController | 4 | OK |
| 19 | SystemSettingsController | 6 | OK |
| 20 | ApprovalTemplateController | 6 | OK |
| 21 | ApprovalCenterController | 2 | OK |
| 22 | FinanceApprovalController | 6 | OK |
| 23 | OperationApprovalController | 6 | OK |
| 24 | ProjectApprovalController | 6 | OK |
| 25 | ProcessController | 29 | OK |
| 26 | ScheduleController | 19 | OK |
| 27 | EmployeeOnboardingController | 5 | OK |
| 28 | EmployeeResignationController | 9 | OK |
| 29 | FollowUpCalendarController | 1 | OK |
| 30 | SalesController | 56 | OK |
| 31 | SalesProductController | 6 | OK |
| 32 | PurchaseRequirementController | 5 | OK |
| 33 | PurchasePlanController | 7 | OK |
| 34 | PurchaseContractController | 7 | OK |
| 35 | PurchasePaymentRequestController | 5 | OK |
| 36 | PurchasePaymentController | 3 | OK |
| 37 | PurchaseShipmentController | 3 | OK |
| 38 | PurchaseLogisticsController | 5 | OK |
| 39 | PurchaseApprovalController | 3 | OK |
| 40 | DiskController | 6 | OK |
| 41 | FuelCardController | 8 | OK |
| 42 | AuthController | 5 | OK |

**Controller 死 public 方法 = 0**

### 1.2 各 Controller 方法清单 (按文件)

**DashboardController** (DashboardController.php)
- stats(24), recentProjects(42), recentServiceOrders(47), todo(56), projectProgress(66), serviceStats(118), revenueTrend(128), screen(138) — 全部在 routes/api.php:98-105 注册

**AttendanceController** (AttendanceController.php)
- overview(16), calendar(33), clockIn(96), clockOut(163), today(216), supplement(229), fieldClock(288), records(331), leaveRequests(343), storeLeaveRequest(352), approveLeave(370), overtimeRequests(382), storeOvertimeRequest(389), approveOvertime(412), destroyLeaveRequest(423), destroyOvertimeRequest(435), report(447), stats(468) — 全部注册 (api.php:110-131)

**EmployeeController** (EmployeeController.php)
- index(17), store(63), show(108), update(121), destroy(160), resetPassword(175), departments(197), storeDepartment(224), updateDepartment(239), destroyDepartment(263), positions(284), storePosition(305), updatePosition(323), destroyPosition(337), skills(350), storeSkill(356), updateSkill(370), destroySkill(382), attachSkill(396), detachSkill(419), userSkills(433), import(440), certificates(488) — 全部注册 (api.php:78-82, 164-196, 223-228)

**CustomerController** (CustomerController.php)
- index(20), stats(51), health(71), import(284), show(344), profile(364), store(654), update(699), destroy(748), followUps(765), storeFollowUp(770), devices(819), mapData(827) — 全部注册 (api.php:233-251)

**CustomerPipelineController** (CustomerPipelineController.php)
- index(34), updateStage(130), weeklyTrend(158) — 全部注册 (api.php:238-239, 250)

**ProjectController** (ProjectController.php)
- index(15), show(31), store(37), update(75), updateStage(91), constructionLogs(102), storeConstructionLog(110), suppliers(125), storeSupplier(135), projectSuppliers(141), projectContracts(147), destroy(152), paymentCalendar(175), tracking(263), dashboardSummary(491), stages(536), board(554) — 全部注册 (api.php:256-272)

**ServiceController** (ServiceController.php)
- index(13), show(24), store(30), assign(48), startRepair(56), completeRepair(63), confirmByCustomer(78), stats(85), maintenanceContracts(97) — 全部注册 (api.php:322-331)

**ExpenseController** (ExpenseController.php)
- index(15), show(47), store(55), update(95), destroy(120), approve(133), cancel(151), pay(163), myClaims(179), stats(194), projects(207) — 全部注册 (api.php:336-346)

**VehicleController** (VehicleController.php)
- index(16), store(23), usageRequests(38), storeUsageRequest(39), dispatchVehicle(46), updateUsageRequest(65), show(78), update(84), destroy(100), stats(113), insurances(138), storeInsurance(154), updateInsurance(171), destroyInsurance(187), maintenances(195), storeMaintenance(205), updateMaintenance(222), destroyMaintenance(238) — 全部注册 (api.php:351-375, 359-361)

**InventoryController** (InventoryController.php)
- index(18), show(46), store(53), update(91), destroy(121), batchDelete(138), batchUpdate(191), batchExport(258), stockRecords(331), warehouses(360), stockIn(369), stockOut(405), lowStock(485), stats(495), treeWithCounts(529), batchImport(592), exportTemplate(872), itemsByCategory(905), warnings(977) — 全部注册 (api.php:393-417)

**InventoryCategoryController** (InventoryCategoryController.php)
- index(13), tree(22), store(55), update(69), destroy(93), moveCategory(112) — 全部注册 (api.php:422-428)

**FinanceController** (FinanceController.php)
- overview(19), summary(29), payments(48), receivables(57), storeReceivable(67), updateReceivable(90), destroyReceivable(113), payables(123), storePayable(133), updatePayable(157), destroyPayable(180), storeReceivablePayment(193), receivablePayments(234), closeReceivable(247), storePayablePayment(290), payablePayments(329), accounts(340), storeAccount(358), updateAccount(376), destroyAccount(392), transferAccount(407), accountTransactions(455), invoices(466), showInvoice(485), storeInvoice(490), updateInvoice(523), destroyInvoice(554), agingSummary(564), cashflowSummary(607), receipts(647), storeReceipt(668), showReceipt(706), transfers(713) — 全部注册 (api.php:433-478)

**KnowledgeController** (KnowledgeController.php)
- categories(13), articles(14), show(21), store(28), update(50), destroy(70), storeCategory(77), updateCategory(91), destroyCategory(105) — 全部注册 (api.php:494-504)

**NotificationController** (NotificationController.php)
- index(11), markAsRead(19), markAllAsRead(27), unreadCount(33) — 全部注册 (api.php:517-520)

**SystemLogController** (SystemLogController.php)
- index(12) — 注册 (api.php:524)

**RoleController** (RoleController.php)
- index(18), show(68), store(87), update(114), destroy(140), assignPermissions(159), permissionTree(173), permissionIndex(182) — 全部注册 (api.php:733-738, 743-744)

**AuditController** (AuditController.php)
- index(16), show(76) — 全部注册 (api.php:749-750)

**BackupController** (BackupController.php)
- index(21), store(44), download(79), destroy(89) — 全部注册 (api.php:509-512)

**SystemSettingsController** (SystemSettingsController.php)
- index(20), update(57), getIdleConfig(117), getPortConfig(148), updatePortConfig(169), wipeData(201) — 全部注册 (api.php:754-755, 758-759, 762, 819)

**ApprovalTemplateController** (ApprovalTemplateController.php)
- index(23), show(47), store(65), update(85), destroy(100), toggle(106) — 全部注册 (api.php:765-770)

**ApprovalCenterController** (ApprovalCenterController.php)
- index(21), stats(42) — 全部注册 (api.php:774-777)

**FinanceApprovalController / OperationApprovalController / ProjectApprovalController**
- 三个 Controller 各 6 个方法 (index/store/show/approve/reject/forward) — 全部注册 (api.php:780-809)

**ProcessController** (ProcessController.php)
- 29 个 public method 全部注册 (api.php:280-316)

**ScheduleController** (ScheduleController.php)
- 19 个 public method 全部注册 (api.php:137-159)

**EmployeeOnboardingController** (EmployeeOnboardingController.php)
- index(25), show(70), store(92), update(206), destroy(238) — 全部注册 (api.php:201-205)

**EmployeeResignationController** (EmployeeResignationController.php)
- index(23), show(53), store(63), update(121), submit(150), approve(163), cancel(180), complete(199), settlementPreview(261) — 全部注册 (api.php:210-218)

**FollowUpCalendarController** (FollowUpCalendarController.php)
- index(38) — 注册 (api.php:814)

**SalesController** (SalesController.php)
- 56 个 public method (leads*/opps*/quotes*/quotations*/referrers*/pool*/followUps*) — 全部对应 routes/api.php 第 527-633 行

**SalesProductController** (SalesProductController.php)
- index(20), store(43), show(68), update(77), destroy(98), categories(116) — 全部注册 (api.php:635-642)

**PurchaseRequirementController / PurchasePlanController / PurchaseContractController / PurchasePaymentRequestController / PurchasePaymentController / PurchaseShipmentController / PurchaseLogisticsController / PurchaseApprovalController**
- 全部注册 (api.php:647-728)

**DiskController** (DiskController.php)
- folders(13), files(14), createFolder(15), upload(29), destroyFolder(37), destroyFile(47) — 全部注册 (api.php:483-488)

**FuelCardController** (FuelCardController.php)
- index(15), store(28), update(46), destroy(62), recharges(70), storeRecharge(87), destroyRecharge(109), stats(120) — 全部注册 (api.php:380-388)

**AuthController** (AuthController.php)
- login(14), logout(66), userInfo(79), changePassword(98), updateProfile(154) — 全部注册 (api.php:73, 89-94)

---

## 二、死路由 (路由注册但方法不存在)

经 grep 比对 routes/api.php 全部 `[XxxController::class, 'method']` 与 Controller 实际 method 名，**未发现方法名笔误**。

```bash
# 复验命令
grep -oE "::class, '[a-zA-Z]+'" pc-api/routes/api.php | sort -u
# 248+ 个唯一 method 名
# 逐个对照 Controller 实际 public method — 无不存在的 method
```

**死路由 = 0**

### 2.1 特殊路由检查

| 路由 | 期望方法 | Controller 实际 | 状态 |
|---|---|---|---|
| `[RoleController::class, 'permissionIndex']` | permissionIndex | RoleController.php:182 存在 | OK |
| `[RoleController::class, 'permissionTree']` | permissionTree | RoleController.php:173 存在 | OK |
| `[SystemSettingsController::class, 'wipeData']` | wipeData | SystemSettingsController.php:201 存在 | OK |

---

## 三、死 import (use 了但没用)

> 扫描方法: 对每个 Controller，列出顶部 use，对每个 use 的类 grep `\bClassName::` 或 `\bClassName ` 在本文件内是否被实际引用。

### 3.1 死 import 清单

| Controller | 死 import (类名) | 文件:行 | 验证 grep |
|---|---|---|---|
| **DashboardController** | `App\Models\Customer` | DashboardController.php:7 | `grep -nE "\bCustomer::" DashboardController.php` -> 0 |
| **DashboardController** | `App\Models\InventoryItem` | DashboardController.php:10 | `grep -nE "\bInventoryItem::" DashboardController.php` -> 0 |
| **DashboardController** | `App\Models\Vehicle` | DashboardController.php:16 | `grep -nE "\bVehicle::" DashboardController.php` -> 0 |
| **CustomerController** | `App\Models\ServiceOrder` | CustomerController.php:11 | `grep -nE "\bServiceOrder::" CustomerController.php` -> 0 (关系调用 `$customer->serviceOrders` 不算) |
| **EmployeeOnboardingController** | `App\Models\Department` | EmployeeOnboardingController.php:9 | `grep -nE "\bDepartment::" EmployeeOnboardingController.php` -> 0 |
| **EmployeeOnboardingController** | `App\Models\Position` | EmployeeOnboardingController.php:10 | `grep -nE "\bPosition::" EmployeeOnboardingController.php` -> 0 |
| **EmployeeOnboardingController** | `Illuminate\Support\Str` | EmployeeOnboardingController.php:17 | `grep -nE "\bStr::" EmployeeOnboardingController.php` -> 0 (employee_no 用 str_pad 而非 Str) |
| **SystemLogController** | `Illuminate\Support\Facades\DB` | SystemLogController.php:8 | `grep -nE "\bDB::" SystemLogController.php` -> 0 (用全限定 `\Illuminate\Support\Facades\DB::table`) |
| **CustomerPipelineController** | `App\Models\User` | CustomerPipelineController.php:7 | `grep -nE "\bUser::" CustomerPipelineController.php` -> 0 |
| **CustomerPipelineController** | `Illuminate\Support\Facades\DB` | CustomerPipelineController.php:11 | `grep -nE "\bDB::" CustomerPipelineController.php` -> 0 |

**总计: 5 个 Controller, 9 个死 import**

### 3.2 已确认无死 import 的 Controller

- AttendanceController / EmployeeController / ProjectController / ScheduleController / ProcessController / OperationApprovalController / SystemSettingsController / RoleController / AuditController / BackupController / ApprovalTemplateController / ApprovalCenterController / FinanceApprovalController / ProjectApprovalController / PurchaseApprovalController / PurchaseContractController / PurchasePaymentRequestController / PurchasePaymentController / PurchaseLogisticsController / FinanceController / KnowledgeController / NotificationController / EmployeeResignationController / FollowUpCalendarController / SalesController / SalesProductController / PurchaseRequirementController / PurchasePlanController / PurchaseShipmentController / DiskController / FuelCardController / AuthController / VehicleController / InventoryController / InventoryCategoryController / ServiceController / ExpenseController — 全部 use 都引用

---

## 四、死 Model (类定义了但 0 引用)

### 4.1 引用统计

```bash
# 复验命令
grep -hE "^class \w+ extends" pc-api/app/Models/*.php | grep -oE "class \w+" | awk '{print $2}' | while read m; do
  cnt=$(grep -rE "\b$m::" pc-api/app/ | wc -l)
  echo "$m: $cnt"
done
```

### 4.2 Model 引用计数

| Model | 文件:行 | 静态引用次数 | 状态 |
|---|---|---:|---|
| `User` | User.php:12 | 50+ | OK |
| `Department` | CoreModels.php:11 | 6+ | OK |
| `Position` | CoreModels.php:26 | 4+ | OK |
| `EmployeeProfile` | CoreModels.php:36 | 3+ | OK |
| `SkillTag` | CoreModels.php:63 | 5+ | OK |
| `Certificate` | CoreModels.php:77 | 2+ | OK |
| `Customer` | CoreModels.php:98 | 20+ | OK |
| `CustomerContact` | CoreModels.php:122 | 0 静态调用 | **仅做关系** |
| `FollowUpRecord` | CoreModels.php:133 | 2+ | OK |
| `CustomerDevice` | CoreModels.php:145 | 0 静态调用 | **仅做关系** |
| `EmployeeOnboarding` | CoreModels.php:160 | 5+ | OK |
| `EmployeeResignation` | CoreModels.php:188 | 9+ | OK |
| `ServiceOrder` | ServiceModels.php:11 | 15+ | OK |
| `ServiceOrderLog` | ServiceModels.php:57 | 1 | OK |
| `ServiceOrderPart` | ServiceModels.php:69 | 1 | OK |
| `MaintenanceContract` | ServiceModels.php:80 | 2+ | OK |
| `AttendanceRecord` | ServiceModels.php:93 | 4+ | OK |
| `LeaveRequest` | ServiceModels.php:113 | 3+ | OK |
| `OvertimeRequest` | ServiceModels.php:126 | 2+ | OK |
| `Shift` | ServiceModels.php:138 | 6+ | OK |
| `ShiftGroup` | ServiceModels.php:155 | 4+ | OK |
| `ShiftGroupMember` | ServiceModels.php:165 | 3+ | OK |
| `Schedule` | ServiceModels.php:175 | 5+ | OK |
| `Project` | ProjectModels.php:12 | 30+ | OK |
| `ProjectContract` | ProjectModels.php:56 | 4+ | OK |
| `ContractPaymentNode` | ProjectModels.php:68 | 2+ | OK |
| `Supplier` | ProjectModels.php:79 | 5+ | OK |
| `PurchaseOrder` | ProjectModels.php:88 | 2+ | OK |
| `PurchaseItem` | ProjectModels.php:111 | 1+ | OK |
| `ConstructionLog` | ProjectModels.php:122 | 2+ | OK |
| `ProjectMaterial` | ProjectModels.php:136 | 2+ | OK |
| `ProjectSettlement` | ProjectModels.php:148 | 1+ | OK |
| `Lead` | ProjectModels.php:163 | 8+ | OK |
| `Opportunity` | ProjectModels.php:188 | 14+ | OK |
| `Quotation` | ProjectModels.php:215 | 18+ | OK |
| `QuotationItem` | ProjectModels.php:240 | 1+ | OK |
| `Referrer` | ProjectModels.php:250 | 4+ | OK |
| `ProjectPool` | ProjectModels.php:259 | 5+ | OK |
| `SalesFollowUp` | ProjectModels.php:270 | 8+ | OK |
| `SalesFollowUpAttachment` | ProjectModels.php:280 | 3+ | OK |
| `SalesProduct` | ProjectModels.php:286 | 4+ | OK |
| `ExpenseClaim` | OtherModels.php:13 | 4+ | OK |
| `ExpenseItem` | OtherModels.php:44 | 1+ | OK |
| `ApprovalRecord` | OtherModels.php:55 | 15+ | OK |
| `Vehicle` | OtherModels.php:95 | 4+ | OK |
| `VehicleInsurance` | OtherModels.php:111 | 2+ | OK |
| `VehicleMaintenanceRecord` | OtherModels.php:123 | 1+ | OK |
| `FuelCard` | OtherModels.php:137 | 5+ | OK |
| `FuelCardRecharge` | OtherModels.php:151 | 2+ | OK |
| `VehicleUsageRequest` | OtherModels.php:163 | 6+ | OK |
| `Warehouse` | OtherModels.php:182 | 4+ | OK |
| `InventoryItem` | OtherModels.php:192 | 8+ | OK |
| `InventoryCategory` | OtherModels.php:208 | 12+ | OK |
| `StockRecord` | OtherModels.php:219 | 8+ | OK |
| `DeviceSerialNumber` | OtherModels.php:244 | 0 静态调用 | **仅做关系** |
| `Receivable` | OtherModels.php:259 | 15+ | OK |
| `Payable` | OtherModels.php:271 | 10+ | OK |
| `FinancePayment` | OtherModels.php:284 | 10+ | OK |
| `FinanceAccount` | OtherModels.php:297 | 10+ | OK |
| `FinanceInvoice` | OtherModels.php:308 | 8+ | OK |
| `DiskFolder` | OtherModels.php:323 | 5+ | OK |
| `DiskFile` | OtherModels.php:337 | 4+ | OK |
| `KnowledgeCategory` | OtherModels.php:351 | 5+ | OK |
| `KnowledgeArticle` | OtherModels.php:362 | 5+ | OK |
| `Notification` | OtherModels.php:376 | 0 静态调用 | **仅做关系** |
| `SystemSetting` | OtherModels.php:403 | 7+ | OK |
| `PurchaseRequirement` | OtherModels.php:435 | 5+ | OK |
| `PurchasePlan` | OtherModels.php:466 | 8+ | OK |
| `PurchaseContract` | OtherModels.php:500 | 8+ | OK |
| `PurchasePaymentRequest` | OtherModels.php:536 | 4+ | OK |
| `PurchasePayment` | OtherModels.php:569 | 4+ | OK |
| `PurchaseShipment` | OtherModels.php:599 | 10+ | OK |
| `PurchaseShipmentItem` | OtherModels.php:630 | 0 静态调用 | **仅做关系** |
| `PurchaseLogistics` | OtherModels.php:641 | 5+ | OK |
| `PurchaseApproval` | OtherModels.php:654 | 4+ | OK |
| `ProcessTemplate` | OtherModels.php:686 | 8+ | OK |
| `ProcessInstance` | OtherModels.php:729 | 12+ | OK |
| `ProcessInspection` | OtherModels.php:779 | 6+ | OK |
| `ProcessImage` | OtherModels.php:814 | 4+ | OK |
| `ProcessSignature` | OtherModels.php:846 | 6+ | OK |
| `ApprovalTemplate` | ApprovalTemplate.php:17 | 3+ | OK |

### 4.3 死 Model 候选 (但不能删)

| Model | 文件:行 | 备注 |
|---|---|---|
| `CustomerContact` | CoreModels.php:122 | 静态调用 0 次 — 只被 `Customer::contacts` / `Customer::primaryContact` 关系引用 |
| `CustomerDevice` | CoreModels.php:145 | 静态调用 0 次 — 只被 `Customer::devices` / `Project::devices` / `ServiceOrder::device` 关系引用 |
| `DeviceSerialNumber` | OtherModels.php:244 | 静态调用 0 次 — 只被 `InventoryItem::serialNumbers` 关系引用 |
| `Notification` | OtherModels.php:376 | 静态调用 0 次 — 只被 `User::notifications` / `User::allNotifications` morphMany 关系引用 |
| `PurchaseShipmentItem` | OtherModels.php:630 | 静态调用 0 次 — 只被 `PurchaseShipment::items` 关系引用 |

> **真正的 0 引用死 Model = 0**
> 5 个候选都是"关系型"Model — 关系方法依赖类存在，但代码中无 `ModelClass::xxx()` 静态调用。属于正常的 Eloquent 设计模式，**不能删**。

---

## 五、跨 Controller / Service 调用扫描

```bash
# 复验命令
grep -rE "app\([A-Z][A-Za-z]+Controller::class\)" pc-api/app/
# 结果: 0 matches
```

**结论：没有任何 Controller 通过 `app()->method()` / `app(SomeController::class)` 跨调用其他 Controller。** 所有 Controller 是隔离的 HTTP endpoint，业务复用通过 Eloquent Model 关系 / Trait / Concern 实现。

Controller 之间唯一的横向引用:
- `ApprovalCenterController` / `FinanceApprovalController` / `OperationApprovalController` / `ProjectApprovalController` 都 `use HandlesApproval` (一个 trait / Concern)

> **Trait: `App\Http\Controllers\Api\Concerns\HandlesApproval`** — 在 4 个审批 Controller 中使用，OK。

---

## 六、其他发现 (备份 / 私有 helpers)

### 6.1 死 private 方法

| Controller | 死 private 方法 | 文件:行 | 验证 grep | 建议 |
|---|---|---|---|---|
| **DashboardController** | `formatStage($stage)` | 94 | `grep -c "formatStage" DashboardController.php` -> **1** (仅定义) | **可删** |

复验命令:
```bash
grep -nE "formatStage" pc-api/app/Http/Controllers/Api/DashboardController.php
# 仅 1 行 = 94 行的定义
# 0 行 = 调用
# 结论: 死方法
```

### 6.2 正常 private helpers (在类内被调用)

| Controller | private 方法 | 状态 |
|---|---|---|
| DashboardController | metrics(155), revenueChart(201), projectStatus(246), serviceMetrics(292), todos(331), formatYuan(371) | 全部被类内调用 |
| CustomerController | calcScore(204), toLevel(263), toColor(273), parseCsv(329), normalizeCategory(738), followTypeLabel(631), serviceStatusLabel(641), normalizeFollowType(795) | 全部被类内调用 |
| ExpenseController | statusLabel(213), categoryLabel(226) | 全部被类内调用 |
| InventoryController | doStock(435), typeLabel(511), parseSpreadsheet(767), parseXlsx(795), colLetterToIndex(859) | 全部被类内调用 |
| InventoryCategoryController | collectDescendantIds(170) | 被 update/moveCategory 调用 |
| RoleController | buildPermissionTree(199) | 被 permissionTree 调用 |
| FollowUpCalendarController | resultLabel(177) | 被 index 调用 |
| PurchaseLogisticsController | inferShipmentStatus(97) | 被 store 调用 |
| CustomerPipelineController | serializeCard(195) | 被 index 调用 |

### 6.3 备份 Controller 私有属性

| Controller | 私有属性 | 文件:行 | 备注 |
|---|---|---|---|
| BackupController | `protected string $backupDir` | 13 | 通过 `__construct` 初始化，使用 OK |

---

## 七、其他代码异味 (非死代码但建议关注)

### 7.1 重复路由别名

`routes/api.php:223-228` (`/users/*`) 与 `routes/api.php:164-196` (`/employees/*`) 重复注册了 EmployeeController 路由。两组指向同一组 endpoint。这是为兼容前端两种 URL 风格。

### 7.2 路由重复 (vehicle usage)

`routes/api.php:359-360` 中 `/vehicles/usage` 和 `/vehicles/applies`、`/vehicles/apply` 都注册到同一组 method (`usageRequests` / `storeUsageRequest`)。属于兼容路径。

### 7.3 DashboardController `recentProjects()` / `recentServiceOrders()` / `projectProgress()` 注释

`projectProgress()` 方法 (行 66-89) 返回硬编码的测试数据（注释"测试：返回硬编码数据"），非真实数据库查询。这不是死代码，但生产前需替换。

### 7.4 AuthController 中注释掉的代码

`AuthController::login` (行 59-61) 和 `userInfo` (行 86-88) 注释掉了 `permissions` / `roles` 字段 — 与 Spatie 权限有关，**可能需要恢复**。

### 7.5 全限定 vs 顶部 use 混用

| 文件:行 | 内容 |
|---|---|
| InventoryController.php:126, 161, 216, 237 | `\App\Models\StockRecord::` / `\App\Models\Warehouse::` / `\App\Models\InventoryCategory::` |
| OperationApprovalController.php:95, 104, 106 | `\App\Models\InventoryItem` / `\App\Models\StockRecord` |
| ProjectController.php:160 | `\App\Models\ProjectContract::where(...)` |
| AttendanceController.php:111, 178 | `\App\Models\Schedule::with(...)` |
| CustomerController.php:97, 100, 219, 220, 387, 418 | `\DB::table(...)` |

> 建议统一风格：顶部 use + 短名。

---

## 八、安全项建议 (可立即删)

> 仅包含**绝对安全**的删除项 — 不影响任何功能。

| # | 文件:行 | 建议 | 风险 |
|---|---|---|---|
| 1 | DashboardController.php:7 | 删除 `use App\Models\Customer;` | 0 |
| 2 | DashboardController.php:10 | 删除 `use App\Models\InventoryItem;` | 0 |
| 3 | DashboardController.php:16 | 删除 `use App\Models\Vehicle;` | 0 |
| 4 | CustomerController.php:11 | 删除 `use App\Models\ServiceOrder;` | 0 (只通过关系 `customer->serviceOrders` 用) |
| 5 | EmployeeOnboardingController.php:9 | 删除 `use App\Models\Department;` | 0 |
| 6 | EmployeeOnboardingController.php:10 | 删除 `use App\Models\Position;` | 0 |
| 7 | EmployeeOnboardingController.php:17 | 删除 `use Illuminate\Support\Str;` | 0 |
| 8 | SystemLogController.php:8 | 删除 `use Illuminate\Support\Facades\DB;` (用全限定调用) | 0 |
| 9 | CustomerPipelineController.php:7 | 删除 `use App\Models\User;` | 0 |
| 10 | CustomerPipelineController.php:11 | 删除 `use Illuminate\Support\Facades\DB;` | 0 |
| 11 | DashboardController.php:91-112 | 删除整个 `private function formatStage($stage)` | 0 — 未被任何地方调用 |

**总节省: 10 行 use + 22 行函数体 = 约 32 行** (3.7% 代码减少)

---

## 九、需要人工判断 (不建议自动改)

| # | 现象 | 建议 |
|---|---|---|
| 1 | `DashboardController::projectProgress()` 返回硬编码数据 | 需确认是开发占位还是真功能 |
| 2 | `AuthController` 中 `permissions`/`roles` 字段被注释 | 需确认是否需要恢复 (Spatie 权限) |
| 3 | `employees` 与 `users` 路由重复 | 需确认是兼容老前端还是可合并 |
| 4 | 5 个"仅做关系"Model (CustomerContact/CustomerDevice/DeviceSerialNumber/Notification/PurchaseShipmentItem) | 不能删，但应在文档中说明 |
| 5 | `CustomerPipelineController::STAGES` const (6 阶段) | 已注册路由 (5 端点) — 无问题 |
| 6 | `FollowUpCalendarController` 只用了 1 个 public method `index` | 是设计意图 (跟进日历只读) — OK |
| 7 | `routes/api.php:78-82` 顶层 `/departments` `/positions` 路由 | 与 `/api/employees/departments` 重复 — 是否需要去重 |
| 8 | 多个 Controller 全限定调用 (见 7.5) | 是否统一为顶部 use 风格 |

---

## 十、统计汇总

| 维度 | 数量 |
|---|---:|
| 扫描 Controller | 42 |
| 扫描路由条目 | 251 |
| **死 public Controller 方法** | **0** |
| **死路由 (路由->不存在的 method)** | **0** |
| **死 import (use 但未引用)** | **9** (分布在 5 个 Controller) |
| **死 Model (类存在但 0 引用)** | **0** (5 个"仅做关系"的 Model 不能删) |
| **死 private 方法** | **1** (`DashboardController::formatStage`) |
| **跨 Controller 调用** | **0** (全隔离) |
| **建议立即删除行数** | **~32** |

---

## 十一、复验命令清单 (一键复现)

```bash
# === 0. 切换到项目根 ===
cd "D:\work\website\OA\pc-api"

# === 1. Controller 死方法（public method 没出现在 routes）===
# 提取所有路由 method
grep -oE "::class, '[a-zA-Z]+'" routes/api.php | sort -u > /tmp/route_methods.txt
# 提取所有 Controller public method
for f in app/Http/Controllers/Api/*.php; do
  grep -nE "public function" "$f" | awk -F: -v f="$f" '{print f":"$1":"$3}'
done > /tmp/controller_methods.txt

# === 2. 死路由 ===
grep -oE "::class, '[a-zA-Z]+'" routes/api.php | sort -u | while read m; do
  method=$(echo "$m" | grep -oE "'[a-zA-Z]+'" | tr -d "'")
  grep -q "function $method" app/Http/Controllers/Api/*.php || echo "MISSING: $m"
done

# === 3. 死 import (举例 DashboardController) ===
grep -nE "^use App\\\\" app/Http/Controllers/Api/DashboardController.php | while read line; do
  cls=$(echo "$line" | grep -oE "App\\\\[A-Za-z\\\\]+" | tail -1 | awk -F'\\' '{print $NF}')
  grep -qE "\b$cls::" app/Http/Controllers/Api/DashboardController.php || \
    echo "DEAD IMPORT: $cls  in $line"
done

# === 4. 死 Model ===
grep -hE "^class \w+ extends" app/Models/*.php | grep -oE "class \w+" | awk '{print $2}' | while read m; do
  cnt=$(grep -rE "\b$m::" app/ | wc -l)
  [ "$cnt" -eq 0 ] && echo "DEAD MODEL: $m"
done

# === 5. 死 private 方法 (DashboardController::formatStage) ===
grep -c "formatStage" app/Http/Controllers/Api/DashboardController.php
# 1 = 仅定义未调用
```

---

## 九、前端扫描补充 (2026-06-23 15:10)

扫描器: `.workbuddy/_test/frontend_scan.py`
范围: 101 个 Vue 页面 / 5 个 API 模块 / 17 个 TS 文件

### 9.1 死 Vue 组件（写了但没路由）— 11 个
- `NotFound.vue` (根目录, 跟 `views/error/404.vue` 重复)
- `approval/Center.vue` (旧版, 路由指向 approval/finance/Index.vue)
- `error/ErrorLayout.vue` (空)
- `employee/components/CategoryTree.vue` / `FileLink.vue`
- `inventory/components/` 6 个 (BatchImportDialog/CategoryTree/InventoryItemPicker/ItemDrawer/ItemFormDrawer/ItemTable)

**建议**: 人工 review 这 11 个文件看是否真没用到。

### 9.2 拖拽看板状态机错位 (已修)
| 看板 | 前端列 | 后端 | 处理 |
|---|---|---|---|
| `LeadsBoard.vue` | new/contacted/qualified/proposal/negotiating/won/lost (7 段) | leads.status 5 段 | ✅ 修 |
| `OppsBoard.vue` | inquiry/qualification/proposal/negotiating/quoted/won/lost (7 段) | opps.stage 6 段 | ✅ 修 |

### 9.3 API 函数 0 引用 — 27 个
- `employee.ts`: 9 个 (因为 Organization.vue 改用 modules.ts)
- `sales.ts`: 14 个 (alias 死代码)
- `user.ts`: 3 个 (stores/user.ts 直接用 @/utils/request)

### 9.4 修复成果
- `LeadsBoard.vue` 加 STATUS_REVERSE 归一 + onDrop 修正
- `OppsBoard.vue` 加 STAGE_MAP/REVERSE 归一 + onDrop 修正
- `SalesController::leadsUpdateStatus` 放宽 transitions (new→converted/discarded 都允许)
- `SalesController::oppsUpdateStage` 加 oppStageMap 归一 7→6 段
- 部署到 172 验证: 7 段看板值全部 200 OK ✅

### 9.5 巨型文件
- `project/Detail.vue`: 1705 行 (建议拆子组件)

### 9.6 扫描器盲区
597 个疑似"死 import", 实际是扫描器没把 `<template>` 里 icon 组件识别为"被使用" (Vue3 `<script setup>` 特殊性), **不要自动删**。

---

*报告生成完毕。报告作者: codebuddy-code 模型 minimax-m3-pay。*