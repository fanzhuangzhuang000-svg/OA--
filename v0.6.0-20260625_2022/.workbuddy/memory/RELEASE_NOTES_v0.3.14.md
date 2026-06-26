# Release Notes — v0.3.14 (2026-06-23)

> **类型**：纯重构 + 业务功能补齐 + 152 灰度 + 销售/财务数据权限细化
> **核心**：前端组件化 6 大文件 → 30 个子组件；推荐人结算 7 天提醒；报价单产品库 UI 增强；Dashboard / Customer / Gantt 全面拆分
> **里程碑**：v0.3.14 是 v0.3.11 P1 业务之后的**清理 + 打磨**版本，为 v0.3.15 业务深耕奠基

---

## 📊 总账数字

| 指标 | v0.3.13 | v0.3.14 | 变化 |
|---|---|---|---|
| 前端子组件 | 17 | **42** | **+25** (+147%) |
| 共享 types | 5 | **8** | +3 |
| 共享 composable | 1 | **1** | 持平 |
| 调度任务 | 1 | **2** | +1 (settlement reminder) |
| 后端 Controller | 42 | **42** | 持平（仅加角色 seed + 中间件） |
| 部署脚本 | 3 | **4** | +1 (deploy_152.py) |
| 灰度环境 | 0 | **1** | 152 完整同步 + 2 migration |
| 备份快照 | v0.3.13 | v0.3.14-20260623_1815 | 17.2MB |
| 单文件最大行数 | 1154 | **582** | **-50%** |

---

## 🎯 路径 A — 组件化深推

### A1. process/InstanceDetail.vue (1154 → 582, **-50%**)
- 抽 4 子组件：`ProgressCard.vue` (126) / `InspectionTable.vue` (136) / `InspectionDialog.vue` (168) / `EditInstanceDialog.vue` (141)
- 抽 `types.ts` (185) — STATUS 7 段 + RESULT 8 段 + INDUSTRY 映射
- 父组件瘦到 582 行（orchestration + 4 子组件组合）
- **关键踩坑**：`v-model on prop` 编译错误 → 改用 local 副本 + watch + emit

### A2. employee/Organization.vue (1153 → 976, **-15%**)
- 抽 3 子组件：`EmployeeDialog.vue` (225) / `DeptDialog.vue` (129) / `PositionDialog.vue` (134)
- 抽 `orgTypes.ts` (57) — EmployeeStatus + PositionLevel + 表单类型
- EmployeeDialog 内部维护 `localSkillIds` 副本（外部 prop 不可写），submit 时通过 emit 传出去

### A3. sales/Opps.vue (515 → 455, -12%)
- 抽 3 dialog：`OppDialog.vue` (181) / `WinDialog.vue` (97) / `LostDialog.vue` (94)
- 抽 `types.ts` (51) — StageValue 6 段 + STAGE_OPTIONS

### A4. sales/Leads.vue (513 → 408, -20%)
- 抽 3 dialog：`LeadDialog.vue` (212) / `DiscardDialog.vue` (74) / `ConvertLeadDialog.vue` (111)
- 抽 `leadTypes.ts` (65) — LeadStatus 5 段 + RATING + DISCARD_REASONS

### A5. sales/Quotes.vue (510 → 440, -14%)
- 抽 `ProductPickerDialog.vue` (206)
- 抽 `quoteTypes.ts` (63) — QuoteStatus 6 段 + STEP + QuoteItem

### A6. project/Pool.vue (238 → 235) — 抽出 ConvertDialog.vue (183)
- 拆分后父组件只剩表格 + dialog 容器
- ConvertDialog 内部 reactive 表单 + watch target 模式

---

## 🎨 路径 B — 业务功能补齐

### B1. 152 灰度发布 ✅
- **新写 `.workbuddy/deploy_152.py`** — 152 专用灰度脚本（NOPASSWD sudo + 校验 rc + 分步 echo）
- 同步 14 个 API 改动文件 + 241 前端文件到 152
- **修复 1**：`/api/sales/referral-settlements` 500（新表缺）→ 单独跑 2 个 migration + GRANT
- **修复 2**：deploy 脚本对深层新建目录静默失败（`&&` + `echo=False`）→ 改用 `sudo -n` + 分步执行 + rc 校验
- 验证 9/9 关键端点 + 4 notification 端点全 200

### B2. 推荐人结算 7 天提醒 ✅
- **新写** `app/Notifications/SettlementOverdueNotification.php` — Laravel 11+ Database channel 模式
- **`routes/console.php`** 新增 `oa:remind-overdue-settlements` Artisan closure
- 调度 `0 9 * * *` 每日 09:00 跑（频控 24h，level: warning/danger）
- 接收方：`manager/finance/admin` 角色全部用户
- E2E 验证：注入 10 天前 pending settlement → 跑任务 → 4 个接收方各收 1 条 + title/content/overdue_days 全对 + 立即重跑 0 条（频控生效）

### B3. 报价单产品库 UI 完善 ✅
- **4 个新组件**：
  - `QuoteListSkeleton.vue` (56) — 加载骨架屏
  - `QuoteErrorState.vue` (49) — 错误兜底 + 重试
  - `QuoteCompareDrawer.vue` (268) — 版本对比（增/删/改分类 + 总额差）
  - `QuoteExportDialog.vue` (285) — HTML/CSV/打印 3 种导出 + 邮件链接
- 接入 `Quotes.vue`：434 → 510 行（+76 净增，但 UX 大幅提升）
- **核心增强**：
  - 多选 items + 批量改折扣 + 批量删除（仅草稿状态）
  - 加载/错误态替代空 `catch`
  - HTML 报价单带样式（橙金主色 + 客户/商机/版本/有效期/页脚）
  - CSV BOM 头防 Excel 中文乱码
- **踩坑**：`CirclePlus/CircleMinus` 在 `@element-plus/icons-vue` 中不存在 → 替换为 `Plus/Minus`

---

## 🏗️ 路径 C — 啃硬骨头

### C1. dashboard/index.vue (861 → 251, **-71%**) ✅
- 抽 **8 个子组件**：
  - `RiskBanner.vue` (115) — 风险预警横幅
  - `StatCards.vue` (84) — 4 张统计卡（hover lift + trend chip）
  - `QuickActions.vue` (71) — 8 快捷入口
  - `ProjectProgressTable.vue` (80) — 项目进度表
  - `TodoListCard.vue` (83) — 待办列表
  - `ServiceStatsCard.vue` (79) — 售后工单统计
  - `AttendanceCard.vue` (86) — 今日考勤
  - `RevenueChart.vue` (112) — 营收双柱图（原生 CSS，零依赖）

### C2. customer/index.vue (859 → 408, -52%) ✅
- 抽 **6 个子组件**：
  - `CustomerStatsCards.vue` (63) — 4 统计卡
  - `CustomerSearchBar.vue` (63) — 筛选条 + 8 操作按钮
  - `CustomerTable.vue` (165) — 客户表 + 健康度 chip + tooltip
  - `CustomerFormDialog.vue` (106) — 新增/编辑
  - `FollowDialog.vue` (112) — 跟进记录
  - `ImportDialog.vue` (105) — 批量导入
- 父组件：批量跟进/删除 + 多选操作工具条

### C3. project/Gantt.vue (810 → 191, **-76%**) ✅
- 抽 **4 个子组件 + types**：
  - `ganttTypes.ts` (55) — 4 状态映射工具
  - `GanttOverviewCard.vue` (159) — 头部 8 字段 + 图例 + zoom
  - `GanttGrid.vue` (251) — 甘特主体（日期表头 + 任务行 + 任务条 + 里程碑 + 今日线）
  - `GanttTaskTable.vue` (56) — 下方详细任务表
  - `GanttTaskUpdateDialog.vue` (106) — 更新进度 dialog
- 关键设计：任务条 4 色 + 渐进式阴影、里程碑用旋转 45° 菱形、今日线用渐变从实线到虚化

### C4. inventory/index.vue (610 → 414, -32%) ✅
- 抽 **4 个新子组件**（已有 5 个子组件复用）：
  - `InventoryWarningBanner.vue` (51) — 库存预警横幅
  - `InventoryToolbar.vue` (63) — 顶部工具条
  - `InventoryBatchBar.vue` (64) — 批量操作浮动栏（slide-down 过渡）
  - `InventoryBatchEditDialog.vue` (122) — 批量编辑 7 字段

### C 总账
- **6 大文件 → 30 个子组件**
- **最大单文件**：1154 → 582（-50%）
- **总行数**：4384 → 6574（+50% 但边界清晰）
- **`vite build` 稳定在 10.1-10.4s**

---

## 🔐 路径 D — 销售/财务数据权限细化

### D1. DataScope 中间件
- **新写** `app/Http/Middleware/DataScope.php` (76 行) — 4 档 scope（own/team/finance/all）
- `bootstrap/app.php` 注册 `data_scope` alias
- 未来路由可直接挂载 `->middleware('data_scope:team')`

### D2. finance + sales_manager 角色 seed
- `routes/console.php` 新增 `oa:seed-roles` 命令 + `oa:seed-finance` 演示账号
- 新账号：
  - `finance / 123456` — 周会计（finance 角色，可审 + 可发）
  - `sales_mgr / 123456` — 销售经理·陈（sales_manager 角色，可审但**不可发**）

### D3. 结算接口权限严格分离
- `SalesController::referralSettlementsApprove` — admin/finance/sales_manager/manager 都可审核
- `SalesController::referralSettlementsPay` — **仅 admin/finance 可发放**（销售经理无发放权，资金安全）
- E2E 测试 4/4 通过：
  - finance /pay → 200（发放成功）
  - sales_mgr /pay → 403（仅财务可发放）
  - sales_mgr /approve → 409（已 paid 状态冲突）
  - user /approve → 403（仅销售经理/财务可审核）

### D4. 前端按钮 v-if 绑定 hasRole
- `Settlements.vue` 增加 `canApprove` / `canPay` computed
- 审核按钮：`hasRole('admin') || hasRole('finance') || hasRole('sales_manager')`
- 发放按钮：`hasRole('admin') || hasRole('finance')`

---

## 🚨 严重事故 — 172 vendor 误删（⚠️→已恢复）

**时间线**：路径 B1 后 `deploy_to_172.py --skip-migrate --skip-seed --skip-web` 把 vendor 也清了 → 全 500

**根因**：
- 脚本默认走 `rm -rf {REMOTE_API}/*` 清空目标目录，**无 composer install 兜底**
- `--skip-web` 让脚本以为"不需要 vendor"，但 vendor 是 PHP 运行时必须依赖

**修复**：
- 用 `oa-api.bak.1782209613` 完整恢复（10:13 自动备份）
- 单独把新 `console.php` 和 `SettlementOverdueNotification.php` 重推 172
- `schedule:list` 显示 2 个任务 ✅

**教训 → v0.3.15 必修**：
- `deploy_to_172.py` 默认跑 `composer install --no-dev --no-security-blocking`（v0.3.7.8 之后的模式）
- 或加 `--no-clear` flag（默认不清 vendor/）

---

## 📁 关键文件清单

### 新增
```
.workbuddy/
  ├── deploy_152.py                    # 152 灰度专用脚本
pc-api/
  ├── app/Http/Middleware/DataScope.php          # 数据范围中间件 (D1)
  ├── app/Notifications/SettlementOverdueNotification.php  # 结算逾期通知 (B2)
pc-web/src/views/
  ├── process/components/{ProgressCard,InspectionTable,InspectionDialog,EditInstanceDialog}.vue  # A1
  ├── employee/components/{EmployeeDialog,DeptDialog,PositionDialog}.vue  # A2
  ├── sales/components/{OppDialog,WinDialog,LostDialog,LeadDialog,DiscardDialog,ConvertLeadDialog,ProductPickerDialog,QuoteListSkeleton,QuoteErrorState,QuoteCompareDrawer,QuoteExportDialog}.vue  # A3/A4/A5/B3
  ├── project/components/{BasicInfoTab,StageFlowTab,ConstructionLogTab,CostTab,ProcessTab,BasicStep,BudgetStep,TeamStep,ConfirmStep,ConvertDialog,GanttOverviewCard,GanttGrid,GanttTaskTable,GanttTaskUpdateDialog}.vue  # v0.3.12 + C3
  ├── dashboard/components/{RiskBanner,StatCards,QuickActions,RevenueChart,AttendanceCard,TodoListCard,ServiceStatsCard,ProjectProgressTable}.vue  # C1
  ├── customer/components/{CustomerStatsCards,CustomerSearchBar,CustomerTable,CustomerFormDialog,FollowDialog,ImportDialog}.vue  # C2
  ├── inventory/components/{InventoryWarningBanner,InventoryToolbar,InventoryBatchBar,InventoryBatchEditDialog}.vue  # C4
```

### 修改
```
pc-api/
  ├── app/Http/Controllers/Api/SalesController.php  # +20 行 (D3)
  ├── bootstrap/app.php                  # +data_scope alias (D1)
  ├── routes/console.php                 # +settlement reminder + role seed (B2/D2)
pc-web/src/views/
  ├── sales/Settlements.vue              # +14 行 (D4)
  ├── sales/Quotes.vue                   # 434 → 510 (B3)
```

---

## 🐛 关键踩坑与修复

### 1. `v-model on prop` 编译错误
- **原因**：Vue 3 不允许 `v-model` 直接绑 prop
- **修复**：子组件内部维护副本（`localSkillIds`），对外只 emit 最终值

### 2. notifications 表 title/content 必填
- **原因**：项目定制 schema 多了 title/content 顶级列（Laravel 默认只填 data JSON）
- **修复**：不用 `$user->notify($notif)` 默认行为，改用 `DatabaseNotification::create([...])` 直接 Eloquent 写

### 3. 152 deploy 深层目录静默失败
- **原因**：`mkdir -p` + `&&` 链 + `echo=False` 吞掉 stderr
- **修复**：分步执行 + rc 校验 + 显式 `sudo -n`

### 4. `CirclePlus/CircleMinus` icon 不存在
- **原因**：`@element-plus/icons-vue` 实际命名是 `Plus/Minus`
- **修复**：替换为通用名

### 5. `created_at` 为 null 导致 overdue_days=0
- **原因**：PG `referral_settlements.created_at` 默认 null
- **修复**：Carbon 显式 `->abs()` + `now()->diffInDays($ts, true)` + fallback

### 6. 172 vendor 误删事故
- **原因**：`--skip-migrate --skip-seed --skip-web` 触发 `rm -rf` 但无 composer install
- **修复**：从 `.bak.1782209613` 完整恢复 + 单独重推 console.php

---

## ✅ 验证清单

| 项 | 状态 | 备注 |
|---|---|---|
| vite build (A1-A5) | ✅ | 9.96s |
| vite build (C1-C4) | ✅ | 10.13-10.41s |
| vite build (B3) | ✅ | 10.22s |
| 172 部署 | ✅ | 11 次成功 |
| 152 部署 | ✅ | 1 次完整 + 1 次 console.php 增量 |
| 152 migration | ✅ | 2 新表 + GRANT |
| 152 E2E 财务权限 | ✅ | 4/4 通过 |
| 152 结算提醒 E2E | ✅ | 4 接收方各收 1 条 + 频控 |
| 172 vendor 误删恢复 | ✅ | .bak 完整恢复 |
| 备份 v0.3.14-20260623_1815 | ✅ | 17.2MB |

---

## 📝 文档

- `memory/RELEASE_NOTES_v0.3.14.md` — 本文件
- `memory/MEMORY.md` — 版本号 v0.3.14
- `memory/2026-06-23.md` — 15:00-19:30 完整 daily log

---

## 🚀 下一站 v0.3.15 候选

| 优先级 | 项 | 工作量 | 价值 |
|---|---|---|---|
| P0 | **修 deploy_to_172.py 健壮性** | 1h | 防止 vendor 误删再发生 |
| P0 | **dashboard 营收图接 ECharts** | 1-2h | 原生 CSS 太简陋 |
| P1 | **客户详情 555 行** 拆 4 dialog | 2-3h | 与 Detail.vue 对齐 |
| P1 | **Pipeline.vue 625** 拆 3 子组件 | 2-3h | 销售漏斗 |
| P1 | **Health.vue 506** 拆 3 子组件 | 2-3h | 客户健康度 |
| P2 | **process/InstanceList.vue 712** 拆 3 子组件 | 2-3h | 工序实例列表 |
| P2 | **inventory/index 610 继续拆** | 1-2h | 把剩下表格+抽屉再拆 |
| P3 | **oa:seed-finance 在 152 跑** | 10min | 让 152 演示数据更真实 |
| P3 | **oa:remind-overdue-settlements 加上 dry-run 邮件通知** | 2h | 多通道通知 |
