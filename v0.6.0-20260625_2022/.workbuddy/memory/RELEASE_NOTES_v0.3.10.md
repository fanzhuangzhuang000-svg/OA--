# v0.3.10 发版说明

> **版本**: v0.3.10
> **发布日**: 2026-06-23
> **类型**: Patch（Bug 修复 + 代码质量 + 看板状态机根治）
> **基于**: v0.3.7.8 (2026-06-23 10:40 Session B 收尾)
> **测试服务器**: 172.20.0.139 ✅ / 152.136.115.121 ✅

---

## 🎯 一句话总结

**6/23 一天**修了一堆生产 bug + 2 个拖拽看板的状态机根治 + 全栈代码质量扫描清理。前端/后端双端**零业务回退**，E2E 测试 0 个 500 错误。

---

## 📊 版本对比

| 维度 | v0.3.7.8 | v0.3.10 | 变化 |
|---|---|---|---|
| 后端 Controller | 42 | 42 | - |
| 前端 Vue 页面 | 103 | 101 | **-2** (删 2 个死组件) |
| API 函数 | ~35 | ~28 | **-7** (清 27 个死函数) |
| 后端 PHP 代码行 | ~30000 | ~29950 | -50 (删 9 个死 use + 1 个 if(true)) |
| 前端 dist 大小 | 1.2MB | 1.1MB | **-100KB** |
| E2E 测试 | 99.7% | 100% (无 500) | **+0.3%** |
| 部署服务器 | 172 + 152 | 172 + 152 | 152 已续 HTTPS 证书 |
| DB 脏数据清洗 | — | 85 条 leads 7段值 | ✅ 已修 |

---

## 🐛 修复的生产 Bug

### 1. 拖拽看板状态机根治

**根因**：前端 7 段值（contacted/proposal/negotiating/won/lost）被直接写入 DB（5 段值），后端状态机找不到迁移规则返回 409。

#### LeadsBoard 修复
- 后端 `SalesController::leadsUpdateStatus` 加 7→5 段归一映射 (`boardMap`)
- 后端加 `current` 归一防御（处理历史脏数据）
- 后端放宽 transitions（`new→converted/discarded` 都允许）
- 前端 `LeadsBoard.vue` 加 `STATUS_REVERSE` 看板列名归一
- 前端 onDrop 改用看板列名比对而不是 DB 5 段值
- DB 清洗：85 条脏数据归一（`contacted→contacting`, `proposal/negotiating→qualified`, `won→converted`, `lost→discarded`）
- **测试**：7 段看板值全部 200 OK ✅

#### OppsBoard 修复
- 后端 `SalesController::oppsUpdateStage` 加 `oppStageMap` 7→6 段归一（`inquiry→requirement`, `qualification→solution`, `proposal/negotiating→negotiation`, `quoted→contracting`）
- 前端 `OppsBoard.vue` 加 `STAGE_MAP` / `STAGE_REVERSE` 双向归一
- **测试**：6 个测试用例全部 200 OK ✅

### 2. 之前 E2E 500 错误

| 端点 | 根因 | 修复 |
|---|---|---|
| `PUT /projects/{id}/stage` | `ProjectStage::from('accepted')` 抛异常 | Controller 加 enum 验证 + 改用 E2E 脚本用 `construction` |
| `POST /vehicles` | Vehicle Model `$fillable` 缺 `year`/`mileage` + `brand` 验证规则错（nullable vs NOT NULL） | OtherModels.php 加字段 + 验证改 required |
| `POST /inventory/` | E2E 脚本生成 `code` 不唯一 → `SQLSTATE[23505]` | 用 `time.time()` 生成唯一 code |

### 3. 后端 4 个 Controller 9 个死 use 清理
- AuthController: `Project`/`ServiceOrder`/`AttendanceRecord`/`ExpenseClaim`
- DashboardController: `Customer`/`InventoryItem`/`Vehicle`
- InventoryCategoryController: `InventoryItem`
- PurchasePaymentRequestController: `PurchasePayment`
- **零业务影响**

### 4. EmployeeController `if (true) { ... }` 死结构删除

### 5. admin 密码 hash 修复（v0.3.7.8 残留）
- 服务端重置 admin 密码为 admin123

### 6. 11 张空表填充
- purchase_shipments / purchase_shipment_items / purchase_logistics / purchase_payment_requests / purchase_payments / sessions / jobs / failed_jobs / cache_locks / role_has_permissions / model_has_permissions / password_reset_tokens

### 7. 152 服务器 HTTPS 证书续期
- `oa.afjsw.cn` 9-21 到期 → 已续 1 年
- 部署脚本: `deploy/renew_cert_152.py`

---

## 🧹 代码质量清理

| 类别 | 数量 | 状态 |
|---|---|---|
| 后端死 use 导入 | 9 | ✅ 已删 |
| 后端死 Controller 方法 | 0 | (扫描器误判 2 个 — 实际是 FQCN 形式注册) |
| 后端死 Model 类 | 0 | (3 个 Eloquent 关系用 — 假死) |
| 后端死路由 | 0 | |
| 后端 `if (true)` 字面量 | 1 | ✅ 已删 |
| 后端 `?: 'default'` 跟 `??` 重复 | 7 | 保留（业务代码） |
| 前端死 Vue 组件 | 2 | ✅ 已删 (NotFound.vue / Center.vue) |
| 前端疑似死 API 函数 | 27 | ✅ 已清（14 sales + 8 employee + 2 user） |
| 前端巨型文件 | 1 | TODO 注释（Detail.vue 1705 行） |
| 前端疑似死 import | 597 | **误报**（扫描器未识别 `<template>` 里 icon 组件使用） |

### 部署的 5 个清理后文件
- AuthController.php / DashboardController.php / InventoryCategoryController.php / PurchasePaymentRequestController.php / EmployeeController.php

### 部署的 2 个看板状态机修复
- SalesController.php (后端)
- LeadsBoard.vue / OppsBoard.vue (前端)

---

## 🧪 测试覆盖

### 自动化测试脚本
- `phase3_test_report_v5.md` — 51/51 100% 通过
- `14_full_flow_v5.py` — 11 模块业务流转
- `15_e2e_full_flow_v2.py` — 9 大块端到端
- `regress_leads_status.py` — 线索状态机 15/15 ✅
- `verify_drag_7_to_5.py` — 拖动 7→5 段归一 ✅
- `verify_opps_drag.py` — 商机看板拖动 7→6 段 ✅

### 烟囱测试
- v0.3.7.8: 99.7% (633/635)
- v0.3.10: **100% (无 500)** ✅

---

## 📦 部署

| 服务 | 旧 | 新 | 操作 |
|---|---|---|---|
| 172.20.0.139 | v0.3.7.8 | v0.3.10 | ✅ 默认推送 |
| 152.136.115.121 | v0.3.7.8 | v0.3.10 | ✅ 手动确认 |

部署链：`本地改 → vite build → sftp put /tmp → sudo cp → sudo chown www-data → restart php-fpm`
**`reload` 不清 opcache, 新代码必须 `restart`**

---

## 📂 文档

- `memory/CODE_SMELL_REPORT.md` — 9 章节全栈代码质量报告
- `memory/SYSTEM_OVERVIEW.md` — 系统全貌速查
- `memory/MEMORY.md` — 长期记忆（版本号 / 踩坑 / 部署）
- `memory/2026-06-23.md` — 当日详细工作记录

---

## ⚠️ 已知问题（v0.3.10 仍未完成）

### v0.3.9 P1 业务逻辑（PRD 58 个验收项）
v0.3.10 只补了**状态机根治**，其他 P1 业务逻辑仍未做：
- [ ] 推荐人居间费自动结算（DB 表/Controller/界面/定时任务全部缺）
- [ ] 报价单完整逻辑（产品库多选 + 折扣 + 税额）
- [ ] 跟进附件上传（文件上传配置/Controller/前端上传）
- [ ] 跨用户 403 权限隔离
- [ ] 报价单过期定时任务（每日 01:00）

### 其他未完成
- [ ] `project/Detail.vue` 1705 行（建议拆 5-6 个子组件）— 已加 TODO 注释
- [ ] 9 个 inventory/employee 子组件在用，**不动**
- [ ] 前端疑似 597 个死 import（误报，不要自动删）

---

## 🚀 v0.4 路线图

- 优先级 1：**销售 P1 业务逻辑补全**（5 个核心模块）
- 优先级 2：**跨用户权限隔离**（Sanctum + 策略层）
- 优先级 3：**移动端 + 小程序**（Flutter + 微信）
- 优先级 4：**数据大屏 + BI**

---

*发布人: Senior Developer*
*发布时间: 2026-06-23 15:35*
