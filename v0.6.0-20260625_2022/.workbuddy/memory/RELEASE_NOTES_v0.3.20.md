# Release Notes — v0.3.20 (2026-06-23)

> **C 路径 100% 收口**：啃下 customer/Detail 555 行（→ 191 行 + 7 子组件 + 1 types，-66%）。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **Detail.vue 555→191（-66%）** | C 路径最后一个大文件，C 路径 100% 收口 |
| **7 个子组件** | OverviewCard / BasicInfoTab / ProjectTab / DeviceTab / ServiceTab / FollowTimelineTab / FollowDialog |
| **types.ts（163 行）** | Customer/Contact/Project/Device/ServiceOrder/Receivable/FollowRecord + 9 个工具函数 + 2 个枚举 |
| **6 个 Tab 完全组件化** | 每个 Tab 是独立子组件，可单独测试/复用 |

## 📦 拆分对比

| | 之前 | 之后 |
|---|---|---|
| Detail.vue | **555 行** | **191 行**（-66%）|
| 子组件 | 0 | **7**（含 6 个 Tab + 1 个 dialog）|
| types.ts | 0 | **1**（163 行，9 工具 + 2 枚举）|
| 总行数 | 555 | **835**（拆分必要开销）|

## 📂 7 个子组件

| 文件 | 抽自原文件 | 行数 | 关键 prop / emit |
|---|---|---|---|
| `types.ts` | 全部 interface + 工具 | 163 | Customer/Contact/Project/Device/ServiceOrder/Receivable/FollowRecord + displayCategory/categoryType/stageType/deviceStatusType/priorityType/serviceStatusType/timelineType/typeLabel/formatDate/avatarColor + FOLLOW_TYPE_OPTIONS |
| `CustomerOverviewCard.vue` | 原 38-77 + scss 444-500 | 125 | `customer` / `loading` |
| `BasicInfoTab.vue` | 原 78-122 + scss 509-516 | 83 | `customer` |
| `ProjectTab.vue` | 原 125-153 | 42 | `projects` + emit `view` |
| `DeviceTab.vue` | 原 155-176 | 31 | `devices` |
| `ServiceTab.vue` | 原 217-244 | 41 | `serviceOrders` + emit `view` |
| `FollowTimelineTab.vue` | 原 178-215 + scss 518-552 | 88 | `records` + emit `add` |
| `FollowDialog.vue` | 原 248-274 | 71 | v-model:visible + `form` + emit `submit` |

## 🔥 C 路径累计（v0.3.14 → v0.3.20）

| 文件 | 拆分前 | 拆分后 | 减幅 |
|---|---|---|---|
| dashboard/index.vue | 861 | 251 | -71% |
| customer/index.vue | 859 | 408 | -52% |
| **customer/Detail.vue** | **555** | **191** | **-66%** |
| project/Gantt.vue | 810 | 191 | -76% |
| inventory/index.vue | 610 | 414 | -32% |
| process/InstanceDetail.vue | 1154 | 582 | -50% |
| employee/Organization.vue | 1153 | 976 | -15% |
| process/InstanceList.vue | 712 | 429 | -40% |
| **小计** | **6714** | **3442** | **-49%** |

**C 路径 100% 完成**（原本列出的 4 大文件 dashboard/customer/gantt/inventory 加上 process/employee 全部拆完）。

## 🛡️ 设计模式沉淀

1. **types.ts 集中 export 模式**（v0.3.19 引入，v0.3.20 完善）：
   - 9 个工具函数 + 2 个枚举全部集中，避免 6 个子组件重复定义
   - types.ts 同时作为子组件的 import 源

2. **v-model:visible 模式**（v0.3.16 引入，v0.3.20 复用 5 次）：
   - dialog 统一接口，子组件内部 computed 包一层
   - 父组件管 form/rules，子组件只 emit submit

3. **Tab 组件化模式**（v0.3.20 新增）：
   - 每个 el-tab-pane 对应一个独立子组件
   - 父组件只管 activeTab state + 业务数据流向

## 🔗 累计统计

- **60+ 子组件**（v0.3.20 +7）
- **11 共享 types 文件**
- 88/88 migration 全幂等
- 43 Controller / 4 部署脚本
- C 路径 100% 收口（8 个大文件全部 -49%）

## ⏭️ 下一里程碑 v0.3.21 候选

- **dashboard 营收图接 ECharts**（C 路径 C1 当时的 TODO）
- 全量扫剩余 > 500 行的 Vue 页面（process/InstanceDetail 582 / employee/Organization 976 可能还有空间）
- 开始 D 路径剩余：finance/payment / vehicle 模块
- 把"组件化拆分"模式做成 SkillManage 全局可复用
