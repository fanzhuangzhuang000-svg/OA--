# V0.5.8 收口报告 — 看板 7 段状态机 + 全模块真机点击测试 + 多 BUG 修复

> 日期: 2026-06-25
> 起点: V0.5.2 角色权限 + Audit 完工, 期间 0.5.3 ~ 0.5.7 走完 (看板 widget + B2 生产加固 + 工序 + 返修)
> 终点: 5 大看板 7 段状态机对齐 + 108 路由挨个点击 0 错 + 20 弹窗 + 17 提交 + 30 看板流转

## 1. 4 件事

### 1.1 线索 / 商机看板 7 段状态机 (A)
**问题**: 线索 + 商机看板第 3、4 列 (方案报价 / 谈判中) 永远空
**根因**: 后端 `boardMap` 把前端 7 段值压成 DB 5 段 (proposal→qualified, negotiating→negotiation)
**修法**:
- `SalesController::leadsUpdateStatus` 7 段独立成真值, won/lost 仍走 converted/discarded
- `SalesController::oppsUpdateStage` 同理, 加 inquiry/qualification/proposal/negotiating/quoted 7 段真值
- DB COMMENT 升级为 7 段 (string(20) 够装, 无结构变更)
- 前端 `LeadsBoard.vue` `STATUS_REVERSE` 修对
- 前端 `OppsBoard.vue` `STAGE_REVERSE` 修对, 删旧 STAGE_MAP

### 1.2 enum 兼容历史脏数据 (B)
**问题**: `WorkOrderStatus::CLOSED` 和 `RepairOrderStatus::SHIPPED_BACK` 缺失, 老数据有这 2 值 → 500
**修法**:
- `WorkOrderStatus` 加 CLOSED case, isTerminal + allowedTransitions 同步
- `RepairOrderStatus` 加 SHIPPED_BACK, 等价 SENT_BACK

### 1.3 全模块真机点击测试 (C)
**工具**: puppeteer-core 模拟登录 + 108 路由挨个跳转 + API 4xx/5xx 抓取 + page error 抓取
**3 轮覆盖**:
1. **108 路由** (`.workbuddy/click_through_all.js`): 第一轮 19 个问题, 修完 0 错
2. **20 列表弹窗** (`.workbuddy/click_forms_all.js`): 找"新建/创建"按钮, 验证弹窗打开
3. **17 直接表单提交** (`.workbuddy/click_submissions.js`): 找"保存/提交"按钮, 验证 API 触发

**修了 4 类 BUG** (合并到 commit):
- 500 严重 3 处 (WorkOrderStatus/RepairOrderStatus enum 缺 case)
- 404 路由缺失 8 处 (SupplierController/LedgerController 整组路由 + customers/industries + customers/health)
- 404 重复前缀 6 处 (SetupWizard/SystemDict/SystemMonitor 三个文件 API 常量写错)
- 422 service 方法缺失 1 处 (ConstructionLogService.listOverdue)

### 1.4 三视图收口 (D)
- 客户列表: 顶部统计卡 4 → 7 段 (new/contacting/contacted/qualified/proposal/negotiating/converted/discarded) 计数
- 商机池: 顶部统计卡 6 段 7 卡, 全部命中 7 段独立值
- 看板拖拽支持反向 (new→contacted, converted 不可流转)
- 看板流转 E2E 30/30 全过

## 2. 数据现状

- **users**: 17 个 (admin1/fin_wu/sales_yang/tech_qian/const_zheng, 都 admin123)
- **customers**: 40
- **projects**: 50
- **leads**: 30 (7 段全分布)
- **opportunities**: 24 (7 段: inquiry=0/qualification=0/proposal=3/negotiating=1/quoted=1/won=7/lost=3)
- **work_orders**: 30
- **repair_orders**: 32 (7 段全)
- **system_dicts**: 41

## 3. E2E 测试

| 工具 | 范围 | 结果 |
|---|---|---|
| `.workbuddy/click_through_all.js` | 108 路由挨个访问 | **108/108** 0 错 |
| `.workbuddy/click_forms_all.js` | 20 列表"新建"弹窗 | **20/20** 弹窗打开 |
| `.workbuddy/click_submissions.js` | 17 直接表单提交 | **17/17** 0 错 |
| `.workbuddy/e2e_all_boards_v058.py` | 5 大看板流转 | **30/30** 全过 |
| `.workbuddy/e2e_flow_v057.py` | 4 流全业务 | **25/25** 全过 |
| `.workbuddy/e2e_lead_board_v058.py` | 线索 7 段 | **24/24** 全过 |

## 4. 部署

- **服务器**: 192.168.3.117 (Ubuntu 26.04 + PHP 8.5 + PG 18.4)
- **代码**: `git commit` 推到本地 main
- **运维**: scp + sudo -n cp + systemctl restart php8.5-fpm
- **数据库**: 117 全量接替 172 (172 已关停)
- **生产加固**: 每日 02:00 自动备份 / 03:00 证书续期 / 每 15min 监控 / 每 5min 告警发送

## 5. 下一里程碑

- V0.5.9: 慢查询优化 (DBA 视角 EXPLAIN) + 真实业务后端 validation 补全 + 字段脱敏规则 UI
- B2 生产准备: HTTPS+备份+域名 (已部分就绪)
- C 新业务: 商机/报价/合同深度联动
- E 收工
