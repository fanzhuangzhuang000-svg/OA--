# Session A 阶段 1：数据现状诊断报告

**扫描时间**: 2026-06-23 08:18
**目标**: 172.20.0.139 / security_oa
**总表数**: 94 个业务表
**总行数**: 4493 行

## 关键缺口（要补的）

### 🔴 严重缺口

| 表 | 当前 | 目标 | 缺口 | 原因 |
|---|---|---|---|---|
| **users** | 4 | 20 | +16 | 4 用户无法覆盖 5 角色 + 4 部门 + 端到端测试 |
| **approval_records** 类型 | 4 类 | 15+ 类 | +11 类 | 现在只有 Project/LeaveRequest/ExpenseClaim/PurchaseOrder，**差 11 类审批没进审批中心** |
| **projects** 阶段完成度 | 0% | 100% | 71 项目全没 actual_end_date | **没一个项目跑完 7 阶段**！这是核心问题 |
| **project_settlements** | 0 行 | 15+ | +15 | 项目结算完全空 |
| **customers** 商机转化 | 16:6:8 | 10:5:20 | - | 客户数太少（30），商机不够 |
| **service_orders** 状态 | 只有 confirmed | 全状态 | - | 工单只走完一种状态 |
| **receivables** 状态 | 只有 fully_paid | pending/partial | - | 应收台账全结清，无测试价值 |
| **expense_claims** | 13 | 50 | +37 | 报销样本少 |

### 🟡 中等缺口

| 表 | 当前 | 目标 | 缺口 |
|---|---|---|---|
| project_contracts | 70 | 80 | +10 |
| contract_payment_nodes | 90 | 240 | +150（合同平均 3 节点） |
| purchase_orders | 30 | 50 | +20 |
| purchase_payment_requests | 25 | 80 | +55 |
| purchase_payments | 20 | 60 | +40 |
| construction_logs | 150 | 500 | +350 |
| project_materials | 100 | 200 | +100 |
| attendance_records | 206 | 1000 | +800 |
| leave_requests | 20 | 50 | +30 |
| overtime_requests | 11 | 30 | +19 |
| vehicle_usage_requests | 50 | 100 | +50 |
| notifications | 100 | 200 | +100 |

### 🟢 已够用

| 表 | 当前 | 评估 |
|---|---|---|
| suppliers | 5 | 够 |
| warehouses | 6 | 够 |
| inventory_items | 10 | 边缘够用 |
| inventory_categories | 1 | 太少（应 ≥30）|
| leads | 120 | 够 |
| opportunities | 60 | 够 |
| knowledge_articles | 50 | 够 |
| disk_files | 50 | 够 |
| fuel_cards | 8 | 边缘够用 |
| maintenance_contracts | 15 | 够 |

## 数据生成策略

**原则**：
1. **不破坏现有数据**（保留闭环测试已有链路）
2. **补数据要"成对"**（补项目必须补合同+付款节点+工单+结算，缺一不可）
3. **项目要跑完 7 阶段**（大哥重点要求"确认环节"）
4. **审批进审批中心**（所有新审批都走 `approval_records`，统一类型名）

**优先级**：
1. **P0**：users + 4 角色覆盖 → 审批类型补全 → 项目跑完 7 阶段 → 资金闭环
2. **P1**：扩考勤/请假/报销/工单到合理规模
3. **P2**：库存/油卡/维保补足

## 下一步

写 5 个数据生成脚本：
- `03_gen_users.py` — 20 用户 + 角色 + 部门分配
- `04_gen_projects_full_flow.py` — 50 项目（每项目跑完 7 阶段）
- `05_gen_finance_full_flow.py` — 资金闭环（合同→付款节点→申请→打款→台账）
- `06_gen_approval_all_types.py` — 15 类审批全覆盖
- `07_gen_attendance_extend.py` — 1000 考勤 + 请假/加班/报销扩展

写完用 heredoc 传 SQL 到 172 执行（参考 skill `oa-pg-bulk-insert`）。
