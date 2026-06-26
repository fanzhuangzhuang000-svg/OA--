# 安防运维 OA 系统 — 全面系统笔记

> 用途：高级开发快速参考。Bug 修复 / 状态机排查 / E2E 测试 / 二次开发前必读。
> 更新：2026-06-23 / 配合 v0.3.10+ (~v1.0.1)

---

## 1. 项目地图

### 1.1 工作区结构
- pc-api/         Laravel 13 + PostgreSQL 15 + Sanctum（后端 API）
- pc-web/         Vue3 + Element Plus + TS + Vite + Pinia（PC 前端）
- mobile-app/     移动端（未深入）
- mp-miniapp/     微信小程序（未深入）
- pc-desktop/     桌面端（未深入）
- docs/           文档
- deploy/         部署脚本
- 安防运维OA系统设计大纲V2.html  (1192 行设计文档)
- .workbuddy/     工作区（memory/ _test/ _archive/ skills/ 等）

### 1.2 关键服务器
| 用途 | IP | 角色 | 备注 |
|---|---|---|---|
| **172.20.0.139** | 测试 | 开发联调 | FPM 80 workers, Redis 缓存, PG 16 |
| **152.136.115.121** | 展示 | 演示/生产 | 同上,演示账号 admin/Admin@2026 |
| 端口 | 80 (Nginx) | — | 3000/3001 已关 |

### 1.3 pc-api 业务模块 / 路由前缀 / Controller（44 个 Controller，38 业务模块）
| 前缀 | Controller | 模块 | 备注 |
|---|---|---|---|
| `/auth` | AuthController | 认证 | login(限流 5/m) / logout / userinfo / profile / change-password(限流) |
| `/dashboard` | DashboardController | 工作台 | stats/todo/project-progress/service-stats/revenue-trend/screen |
| `/attendance` | AttendanceController | 考勤 | overview/clock-in/leave/overtime/report |
| `/schedules` | ScheduleController | 排班 | shifts/groups/schedule/my-schedule |
| `/employees` | EmployeeController | 员工 | CRUD + tree + skills + departments + positions |
| `/employee-onboardings` | EmployeeOnboardingController | 入职 | 单独表 |
| `/employee-resignations` | EmployeeResignationController | 离职 | 单独表 |
| `/users` | AuthController | 用户 | 增删改查 + reset-password |
| `/customers` | CustomerController | 客户 | + pipeline/health/follow-calendar/map |
| `/projects` | ProjectController | 施工管理 | CRUD + dashboard-summary + members |
| `/process` | ProcessController | 工序 | templates/instances/inspections |
| `/service` | ServiceController | 售后 | orders CRUD + assign + start + complete + confirm + maintenance-contracts |
| `/expenses` | ExpenseController | 报销 | 报销单 + 审批 |
| `/vehicles` | VehicleController | 车辆 | fleet + usage + insurance + maintenance |
| `/fuel-cards` | FuelCardController | 油卡 | CRUD + recharge |
| `/inventory` | InventoryController | 库存 | items + inout + warehouses |
| `/inventory-categories` | InventoryCategoryController | 库存分类 | |
| `/finance` | FinanceController | 财务 | overview/receivable/payable/receipt/payment/invoice/transfer/account |
| `/disk` | DiskController | 网盘 | folders + files |
| `/knowledge` | KnowledgeController | 知识库 | categories + articles |
| `/backups` | BackupController | 备份 | mysqldump 流式 |
| `/notifications` | NotificationController | 消息 | unread-count/mark-read |
| `/sales/leads` | SalesController | 线索池 | **5 段状态机 (new/contacting/qualified/converted/discarded)** |
| `/sales/opps` | SalesController | 商机池 | **4+3 段 (requirement/solution/negotiation/contracting + won/lost/hold)** |
| `/sales/quotes` + `/quotations` | SalesController | 报价单 | draft/submitted/negotiating/accepted/rejected/expired |
| `/sales/referrers` | SalesController | 推荐人 | 居间费 + 累计 |
| `/sales/pool` | SalesController | 项目池 | pending/active/archived |
| `/sales/follow-ups` | SalesController | 跟进 | 通用 target_type=lead/opp/quote + 附件 |
| `/sales/products` | SalesProductController | 销售产品库 | 报价时选品 |
| `/purchase/requirements` | PurchaseRequirementController | 采购需求 | |
| `/purchase/plans` | PurchasePlanController | 采购计划 | |
| `/purchase/payment-requests` | PurchasePaymentRequestController | 付款申请 | |
| `/purchase/payments` | PurchasePaymentController | 财务付款 | |
| `/purchase/contracts` | PurchaseContractController | 采购合同 | |
| `/purchase/shipments` | PurchaseShipmentController | 供应商发货 | |
| `/purchase/logistics` | PurchaseLogisticsController | 物流跟踪 | |
| `/purchase/approvals` | PurchaseApprovalController | 采购审批 | |
| `/approvals/center` | ApprovalCenterController | 审批中心 | |
| `/approvals/finance` | FinanceApprovalController | 财务审批 | |
| `/approvals/operation` | OperationApprovalController | 运营审批 | |
| `/approvals/project` | ProjectApprovalController | 项目审批 | |
| `/approval-templates` | ApprovalTemplateController | 审批模板 | steps(json) + enabled |
| `/follow-up-calendar` | FollowUpCalendarController | 跟进日历 | |
| `/audit-logs` `/system-logs` | 日志 | |
| `/roles` | RoleController | RBAC | |
| `/settings` | SystemSettingsController | 系统设置 | port/idle-timeout 等 |

### 1.4 pc-web 业务模块（src/views/，25+ 模块）
| 模块 | 页面 |
|---|---|
| dashboard | index.vue |
| attendance | index/Record/Leave/Overtime/Report/Shifts/Groups/Schedule/MySchedule (9) |
| employee | Organization/Onboardings/Resignations/Skill (4) |
| customer | index/Health/Pipeline/FollowCalendar/CustomerMap/Detail (6) |
| **sales** | **Leads/LeadsBoard/Opps/OppsBoard/Quotes/Referrers (6) ⭐** |
| project | index/Board/Calendar/Create/Detail/Gantt/Pool (7) |
| purchase | Requirement/Plan/Approval/PaymentRequest/Payment/Contract/Shipment/Logistics (8) |
| service | index/Create/Detail/Contract/Stats (5) |
| expense | index/Apply/Approval (3) |
| vehicle | index/Apply/Dispatch/Insurance/Maintenance/FuelCard (6) |
| inventory | index/InOut/InboundOrder/OutboundOrder/MaterialRequest/MaterialReturn (6) |
| finance | index/Receipt/Payment/Receivable/Payable (5) |
| process | TemplateList/InstanceList/InspectionList/InstanceDetail (4) |
| approval | Center + finance/operation/project 三个 Index (4) |
| disk / knowledge / screen / message / settings | 标准 5 个 |

---

## 2. 销售模块深扒

### 2.1 线索 (leads)
| 字段 | 类型 | 备注 |
|---|---|---|
| lead_no | string(30) unique | 自动 LEAD-YYYYMMDDHHmmss+xxx |
| customer_id / customer_name | FK + 冗余 | 至少一个 |
| contact_name / contact_phone / contact_title | | 必填 name+phone |
| source | enum | `online/phone/exhibition/referral/other` |
| referrer_id | FK referrers | 可选 |
| estimated_amount | decimal(12,2) | 默认 0 |
| rating | enum | `A/B/C/D`，默认 C |
| **status** | string(20) | **`new/contacting/qualified/converted/discarded`** ⭐ |
| owner_id | FK users | 创建时自动 = 当前用户 |
| follow_up_at / last_contact_at | date / datetime | |
| discard_reason | text | 丢弃时填 |

**API 端点**：
- `GET /api/sales/leads` 列表（filter: status/source/keyword）
- `GET /api/sales/leads/{id}` 详情
- `GET /api/sales/leads/source-options` 来源下拉
- `POST /api/sales/leads` 新建
- `PUT /api/sales/leads/{id}` 编辑（**converted 状态不可编辑**）
- `DELETE /api/sales/leads/{id}` 删除（**仅 new/discarded 可删**）
- `PATCH /api/sales/leads/{id}/status` 看板拖拽（**支持 7 段前端值 → 5 段 DB 归一**）
- `POST /api/sales/leads/{id}/convert-to-opp` 转商机

**前端页面**：
- `Leads.vue` 列表
- `LeadsBoard.vue` **7 列拖拽看板**

### 2.2 商机 (opportunities)
| 字段 | 类型 | 备注 |
|---|---|---|
| opp_no | string(30) unique | OPP-YYYYMMDDHHmmss+xxx |
| name | string(200) | |
| customer_id / lead_id | FK | lead_id 转化时填 |
| type | string(50) | `comprehensive` 默认（DB enum: camera/access_control/alarm/comprehensive/network/cloud_platform）|
| estimated_amount | decimal(12,2) | |
| expected_sign_date | date | |
| **stage** | string(20) | **`requirement/solution/negotiation/contracting/won/lost/hold`** ⭐ |
| probability | smallint | 0-100，按 stage 自动 20/40/60/80，won=100，lost=0 |
| sales_id / presale_id | FK users | |
| competitor / lost_reason | | lost_reason enum: `price_high/competitor/budget/tech/relation/other` |
| project_id / pool_id | FK | won 后填 |
| next_action / next_action_at | | |
| notes | text | 状态变更时会 append `[分派]/[搁置]` |

**API 端点**：
- `GET /api/sales/opps` 列表
- `GET /api/sales/opps/stage-options` 阶段下拉
- `GET /api/sales/opps/funnel` 漏斗统计
- `GET /api/sales/opps/lost-reasons` 战败原因下拉
- `POST /api/sales/opps` 新建
- `PUT /api/sales/opps/{id}` 编辑
- `DELETE /api/sales/opps/{id}` 删除
- `PATCH /api/sales/opps/{id}/stage` 阶段更新（**仅 4 段可改，won/lost 不可拖**）
- `POST /api/sales/opps/{id}/mark-won` 成交（自动建项目池）
- `POST /api/sales/opps/{id}/mark-lost` 战败
- `POST /api/sales/opps/{id}/win` / `/lose` / `/hold`（别名/扩展）
- `POST /api/sales/opps/{id}/move-to-project-pool` 入项目池（不进成交）
- `POST /api/sales/opps/{id}/assign` 分派销售
- `GET /api/sales/opps/{id}/quotations` 商机下报价单
- `POST /api/sales/opps/{id}/quotations` 新建报价单

**前端页面**：
- `Opps.vue` 列表（含 markWon/markLost 按钮）
- `OppsBoard.vue` **7 列拖拽看板：inquiry/qualification/proposal/negotiating/quoted/won/lost** ⚠️ 与后端 stage 值**不一致**（前 4 段语义相同但 value 命名不同）
- `Quotes.vue` 报价单（在 `/sales/opps/:id/quote` 路由下，**视图组件名是 Quotes.vue 不是 Quotations.vue**）

### 2.3 报价单 (quotations / quotes 双前缀)
| 字段 | 类型 | 备注 |
|---|---|---|
| quote_no | string(30) unique | QT-YYYYMMDDHHmmss+xxx |
| opportunity_id | FK | |
| version | unsignedInt | 默认 1，支持 new-version |
| subtotal / discount_rate / discount_amount / tax_rate / tax_amount / total_amount | decimal | |
| valid_until | date | |
| **status** | string(20) | `draft/submitted/negotiating/accepted/rejected/expired` |
| created_by / approved_by / sent_at / responded_at | | |

`quotation_items` 子表：name/specification/unit/quantity/unit_price/total_price/inventory_item_id

### 2.4 推荐人 (referrers)
- name / phone / customer_id / bank_account / bank_name / commission_rate(默认5%) / total_commission / notes

### 2.5 项目池 (project_pool) ⚠️ 表名单数
| 字段 | 类型 | 备注 |
|---|---|---|
| pool_no | unique | POOL-YYYYMMDD-xxx |
| opportunity_id / name / customer_id | | |
| contract_amount / signed_at | | |
| **status** | string(20) | `pending/active/archived` |
| related_project_id | FK projects | convert-to-project 时填 |

### 2.6 销售产品库 (sales_products)
- code (auto SP-...) / name / category_id (→ inventory_categories) / unit / spec / sale_price / cost_price / description / status (active/inactive)

### 2.7 跟进 (sales_follow_ups)
- target_type (lead/opp/quote) + target_id 多态
- contact_method (phone/wechat/visit/email/other)
- content / result / next_action / next_action_at / user_id
- 子表：sales_follow_up_attachments (多文件)

---

## 3. 状态机真值表 ⭐（重点）

### 3.1 线索状态机（leads.status）
**后端定义**（`SalesController::leadsUpdateStatus` line 117-147）：
```
DB 5 段 (DB列约束):
  new → contacting → qualified → converted (终)
                              ↘ discarded (终)
  new → discarded
  contacting → new (回退)
```

**前端看板**（`LeadsBoard.vue` 7 列）→ **后端 PATCH /status 接受 7 段 boardMap 归一**：
| 前端列 (LeadsBoard) | boardMap → DB | DB label |
|---|---|---|
| new | new | 新线索 |
| contacted | contacting | 跟进中 |
| qualified | qualified | 合格 |
| proposal | qualified | 方案报价 |
| negotiating | qualified | 谈判中 |
| **won** | **converted** | 成交（实际是已转商机） |
| **lost** | **discarded** | 战败（实际是已丢弃） |
| (特殊) | (拖入时拒绝) | **converted 必须用「转商机」按钮触发，discarded 需二次确认** |

**状态机白名单**（line 140-146）：
```
new        → [contacting, qualified, discarded]
contacting → [qualified, discarded, new]      ← 允许回退
qualified  → [converted, discarded]
converted  → []                                ← 终态
discarded  → []                                ← 终态
```

**前端 Drop 处理**（`LeadsBoard.vue` line 107-137）：
- converted 拖入前端拦截（必须用「转商机」按钮）
- discarded 拖入需 ElMessageBox 二次确认
- 其他直接调 `PATCH /api/sales/leads/{id}/status` 让后端 boardMap 归一

### 3.2 商机状态机（opportunities.stage）
**后端 7 段**（`SalesController::oppsUpdateStage` line 319-349）：
```
拖动可用: requirement(20) → solution(40) → negotiation(60) → contracting(80)  ← 4 段
按钮可用: won(100) / lost(0) / hold(0)                                        ← 3 段
```
**概率自动设置**（`stageProb`）：requirement=20, solution=40, negotiation=60, contracting=80, won=100, lost=0, hold=0

**前端看板**（`OppsBoard.vue` 7 列）⚠️ value 与后端不一致：
| 前端列 value | 前端 label | 实际后端 stage 是什么？⚠️ 错位 |
|---|---|---|
| `inquiry` | 需求确认 | **后端是 `requirement`** |
| `qualification` | 方案制定 | **后端是 `solution`** |
| `proposal` | 方案报价 | 后端是 `negotiation` |
| `negotiating` | 报价谈判 | 后端是 `contracting` |
| `quoted` | 合同拟定 | ⚠️ 后端没此值，会被 422 拒绝 |
| `won` | 成交 | won ✅ |
| `lost` | 战败 | lost ✅ |

**⚠️ 重大已知 Bug**：OppsBoard 前端 columns.value 跟后端 stage 不一致，拖到 `quoted` 列会触发 422（stage 不在白名单）。修复方案：把前端 columns.value 改成 `requirement/solution/negotiation/contracting/won/lost/hold` 7 段，或后端 `stage-options` 加 quote 等。

**前端 Drop 处理**（`OppsBoard.vue` line 98-124）：
- won/lost 拖入前端拦截（必须用「成交/战败」按钮）
- 前端 `probabilityMap` 写的是 `requirement:20, solution:40, negotiation:60, contracting:80`（**但前端 columns.value 是 inquiry/qualification/proposal/negotiating，不会命中 probabilityMap 任何 key，全走 fallback 用 opp 原 probability**）

### 3.3 报价单状态机（quotations.status）
```
draft → submitted → negotiating → accepted / rejected
                                         → expired (系统)
```
前端 Quotes.vue (line 109-112) 也有 fallback：draft/submitted/negotiating/accepted/rejected/expired

### 3.4 项目池状态机（project_pool.status）
```
pending → active → archived
```

### 3.5 项目状态机（projects.stage + projects.status）
**7 段 stage**（`ProjectStage` enum）：`initiation(立项) → inquiry(询价) → contract(合同) → purchase(采购) → construction(施工) → settlement(结算) → warranty(质保)`，enum 自带 order() 1-7
**4 段 status**：pending / in_progress / completed / cancelled

### 3.6 售后工单状态机（service_orders.status）
**7 段**（`ServiceOrderStatus` enum + DB enum）：
```
pending → assigned → in_progress → completed → confirmed → archived
                                            ↘ cancelled (可从任意状态)
```
**Urgency 枚举**（`Urgency` enum）：`normal / urgent / critical`（**注意 v0.3.7.8 改过，之前是 low/high 冲突**）

### 3.7 审批状态机（approval_records.status）
**4 段**（`ApprovalStatus` enum）：`pending / approved / rejected / cancelled`

---

## 4. 已知坑位速查 ⭐

### 4.1 路由顺序（Laravel 关键）
- `{lead}` 等通配路由**必须放最后**，子路径（`status` `convert-to-opp`）先注册
- 路由 line 532: `// 子路径（{lead} 通配之前）`
- 例子：修复 follow-up 附件路由时 `attachments/{att}/download` 必须在 `{followUp}` 之后但因为是更具体的子路径所以先注册（line 622）

### 4.2 表名复数化（Eloquent 默认）
- **默认**：models 不写 `protected $table` 时用**复数类名** → Opportunity → `opportunities`
- **特殊单数**：
  - `ProjectPool` → `project_pool`（line 261）
  - `Referrer` → `referrers`（复数正常，line 252）
  - `Quotation` → `quotations`（正常）
- **服务工单**：`service_order_logs` `service_order_parts`（snake case）
- **项目**：`project_pool` / `project_settlements`（snake case）

### 4.3 admin 密码 hash
- DB password 用 bcrypt `$2y$...` 60 字符
- PHP one-liner 生成：`php -r "echo password_hash('admin123', PASSWORD_BCRYPT);"`
- 直接 psql UPDATE（不要走 PHP 容易被 `$` 转义坑）
- 172 admin 密码 = `admin123`（2026-06-23 修复过）
- 152 admin 密码 = `Admin@2026`（演示平台）

### 4.4 PG 序列滞后
- 表现：`duplicate key value violates unique constraint` 报错
- 修复：手动 `SELECT setval('table_id_seq', (SELECT MAX(id) FROM table))`
- 每次部署后跑 `.workbuddy/_test/fix_seq.sql`

### 4.5 enum 冲突（v0.3.7.8 已踩）
- `service_orders.urgency`：原 `low/medium/high/urgent` → 改为 `normal/urgent/critical`（**Urgency enum**）
- 改 enum 时**必须 ALTER TABLE** + **更新 model 注释** + **前端 fallback 默认值**
- 172 服务器 service_orders.urgency 已被 fix

### 4.6 API_TOKEN query 无效
- Sanctum 默认只接受 `Authorization: Bearer` header
- **不要用** `?api_token=` query 形式（会 401）
- 前端 `request.ts` 统一走 header

### 4.7 Nginx Authorization 头
- 必须 `proxy_pass_header Authorization;` 或 `proxy_set_header Authorization $http_authorization;`
- 否则 nginx 转发会丢 Authorization 头
- 教训：172 之前 deploy 时漏配，导致 login 之后 401

### 4.8 reload 不清 opcache
- PHP 改了代码**必须** `sudo systemctl reload php8.3-fpm`（不是 restart）
- 或者用 `php artisan optimize:clear` 清 opcache + route/config cache
- 部署后 smoke 仍跑老代码 → 99% 是 opcache
- 终极解：CLI `php artisan optimize:clear` 然后 fpm reload

### 4.9 service_orders.customer_id 外键错指 users
- 早期 migration 把 `customer_id` 写错 `references('id')->on('users')` → ALTER 改回 customers
- 2026-06-19 修过

### 4.10 system_settings.updated_by 缺列
- 172 早期表缺 `updated_by` → `ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS updated_by INTEGER`
- **必须 sudo -u postgres**（表 owner 是 postgres，oa_user 无 ALTER 权限）

### 4.11 double Model namespace
- 写 SQL 时 `App\\Models\\User`（双反斜杠）会作为字面量写进 model_type 列
- 正确：`App\Models\User`（PHP 字符串，单反斜杠），Python 用 raw string `r'App\Models\User'`

### 4.12 phone UNIQUE 空串冲突
- `phone VARCHAR(20) UNIQUE NOT NULL`，不填时默认 `''` 触发 PG 23505
- 修复：nullable + 不传时 `null`（不要 `unset` 改 null）
- 占位 phone 生成 `mb_substr('TEL-{username}-{4hex}', 0, 20)` 必须 ≤20 字符
- 2026-06-21 修过 500 错误

### 4.13 字段名/外键易错
- `project_settlements.total_income`（不是 `settlement_no/settlement_amount`）
- `project_members.join_date`（不是 `joined_at`），UNIQUE(project_id, user_id)
- `overtime_requests.overtime_date/start_time/compensation_type`（不是 `date/hours`）
- `vehicle_usage_requests.applicant_id/usage_date/purpose`（不是 `user_id/start_date/reason`）
- `construction_logs.user_id`（Controller 用 `operator:id,name` 走 user_id 别名）
- `project_settlements.contract_id`（外键名是 contract_id 不是 project_contract_id）
- `Customer.tags` 是 json/array cast
- `Customer.longitude/latitude` decimal(7) cast
- `EmployeeOnboarding` 表名 `employee_onboardings`（复数 + snake）
- `EmployeeResignation` 表名 `employee_resignations`

### 4.14 数据库 schema 跳号 id
- customers 缺 28、suppliers 缺 1-5 和 6-10、projects 缺 71
- 测试时用现有 id 即可，不要假定连号

### 4.15 业务流速查
- 客户: leads → 转化 → opportunities → 报价 → won → project_pool → projects(施工) → settlements
- 采购: requirements → plans → payment-requests → payments → contracts → shipments → logistics
- 资金: receivables(应收) → receipts(收款) → 系统自动 mark closed
- 售后: service_orders (pending→assigned→in_progress→completed→confirmed) + maintenance_contracts
- 审批: approval_records 多态(approvable_type + approvable_id) → approval_templates(steps json)

### 4.16 测试数据格式易错
- `source` 枚举值：`online` (不是 'web' / '其他')，`referral` (不是 'old_customer')
- `urgency` 已改：`normal / urgent / critical` (不是 low/high)
- 入库/出库要 `warehouse_id` + `type` (inbound/outbound)
- 排班查询必须带 `?start=&end=`
- 报销审批要 `action: 'approved'`
- 采购需求要 `material` 字段
- 物资要 `code` 字段

### 4.17 部署链
- 172 走 `sftp → sudo cp → chown www-data → fpm reload`
- 不要 cp 整个目录覆盖，会丢新文件 → 改用 `rsync -av` 或单文件覆盖
- 部署后必须 `php artisan optimize:clear && sudo systemctl reload php8.3-fpm`

### 4.18 限流 & 监控
- 全局限流 300/min by IP（`AppServiceProvider.php`）
- smoke 638 端点要带 `X-Forwarded-For` 模拟多 IP
- 监控脚本 `.workbuddy/oa-monitor-v2.sh`

### 4.19 approval_records.approvable 多态
- 表用 `approvable_type` + `approvable_id`（不是 `type` + `id`）
- 14 类审批类型（expense_claims / project_contracts / purchase_contracts / etc.）

### 4.20 报表/导出
- `/api/finance/payments` 字段 `transfer_date` 兼容 `payment_date`（FinanceController line 413-421）
- 应收款自动 mark closed（收款 = 应收金额时）

---

## 5. E2E 测试现状

### 5.1 脚本位置
- 历史: `.workbuddy/_archive/_e2e/` (47 个，2026-06-23 归档)
- 当前: `.workbuddy/_test/api_tests/` (用 `php artisan route:list` 实时拉路由)
- 阶段3 报告: `.workbuddy/_test/api_tests/phase3_test_report_v5.md` (51/51 100% 通过)

### 5.2 测试覆盖
| 模块 | 覆盖 | 备注 |
|---|---|---|
| 财务(应付/发票) | 100% | |
| 报销 | 100% | 审批 action="approved" 必填 |
| 审批中心 | 100% | 14 类 approval_records |
| 采购全流程 | 100% | 字段 supplier_id nullable |
| 库存 | 100% | warehouse_id + type 必填 |
| 销售 | 100% | leads/opps/quotes/referrers 完整 |
| 车辆 | 100% | |
| 员工 | 100% | phone nullable 修复后 |
| 知识库/其他 | 100% | |
| **总通过率** | **100% (51/51)** | v0.3.10 阶段3 |

### 5.3 性能（172 服务器实测）
- 10 并发: QPS 599, P95 29ms
- 20 并发: QPS 1037, P95 38ms
- 50 并发: QPS 1031, P95 80ms
- FPM 80 workers + Redis 缓存（5 个只读端点）+ PG 16
- vs Round1: QPS +187%~+298%, P95 -65%~-74%

### 5.4 缓存覆盖
- `VehicleController::index()` → `vehicles:all`
- `EmployeeController::departments()` → `departments:all`
- `EmployeeController::positions()` → `positions:all`
- `CustomerController::stats()` → `customers:stats`
- `ProjectController::dashboardSummary()` → `projects:dashboard_summary`
- TTL 300s，写操作 `Cache::forget()` 失效

### 5.5 当前限流
- 全局：`Limit::perMinute(300)->by($request->ip())` （`AppServiceProvider.php`）
- 单 IP 跑 smoke 638 端点会触发 429 → 测试用 `X-Forwarded-For` 模拟多 IP

### 5.6 端到端业务流已跑通
- 资金流转：应收→收款→自动 closed
- 项目流转：创建→阶段更新→施工日志→项目跟踪
- 采购流转：需求→计划→合同→付款→发货→物流

---

## 6. 建议优先熟悉顺序

时间紧的话按这个顺序读（~30 分钟）：

1. **`README.md`** (1 min) — 项目元信息
2. **`.workbuddy/memory/2026-06-23.md`** (5 min) — 最近 24h 干的事 + 6 个生产 bug 修复
3. **`pc-api/routes/api.php`** (5 min) — 看全部 38 路由前缀，建立模块心智地图
4. **`pc-api/app/Models/ProjectModels.php`** (3 min) — 销售 6 大 Model：Lead/Opportunity/Quotation/Referrer/ProjectPool/SalesProduct
5. **`pc-api/app/Http/Controllers/Api/SalesController.php`** line 115-200 + 319-410 (5 min) — 线索/商机状态机实现
6. **`pc-web/src/views/sales/LeadsBoard.vue` + `OppsBoard.vue`** (5 min) — 看板前端，**OppsBoard 有 value 错位 bug**（第3节）
7. **`pc-api/app/Enums/index.php`** (2 min) — 9 个 PHP 枚举的 backing value
8. **本笔记第3节状态机表** (3 min) — 真值表速查
9. **本笔记第4节踩坑清单** (2 min) — 避免重复踩

### 关键文件路径速查
| 内容 | 路径 |
|---|---|
| 后端入口 | `pc-api/routes/api.php` |
| 销售业务 | `pc-api/app/Http/Controllers/Api/SalesController.php` (1373 行) |
| 销售模型 | `pc-api/app/Models/ProjectModels.php` (309 行含 Lead/Opportunity/Quotation/Project 等 17 个类) |
| 枚举 | `pc-api/app/Enums/index.php` (9 个 enum) |
| 数据库 schema | `pc-api/database/migrations/` (95 个文件) |
| 前端销售 | `pc-web/src/views/sales/*.vue` (6 个) + `pc-web/src/api/sales.ts` |
| 前端路由 | `pc-web/src/router/index.ts` (421 行) |
| API 层 | `pc-web/src/api/{dashboard,employee,modules,sales,user}.ts` |
| 测试报告 | `.workbuddy/_test/api_tests/phase3_test_report_v5.md` |
| Daily log | `.workbuddy/memory/2026-06-{15..23}*.md` |

---

## 7. 一句话提醒

**销售模块当前最大隐患**：OppsBoard.vue 前端列 value 跟后端 stage 不一致（inquiry/qualification/proposal/negotiating/quoted vs requirement/solution/negotiation/contracting），拖到 `quoted` 列会 422。这是当前看板状态机问题的根因。
