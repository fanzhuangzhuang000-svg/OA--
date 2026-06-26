# Release Notes — v0.3.22 (2026-06-23)

> **D 路径破冰**：开启 27 个 > 500 行页面全量拆分，第 1 批：employee/Onboardings 1026→419（-59%）。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **D 路径大规模拆分启动** | 22 个 > 500 行 + 21 个 400-500 行 页面分 4 批（v0.3.22-25）拆完 |
| **第 1 批 Onboardings 1026→419（-59%）** | employee 模块 3 大件之一，复杂向导 3 步 + drawer + renew dialog 拆 6 子组件 |
| **6 子组件 + 1 types** | StatCards / FilterBar / Table / WizardDialog / DetailDrawer / RenewContractDialog |
| **defineExpose 双向通信** | StatCards 的 `stats` 用 ref+expose 模式，父组件不直接管 state |

## 📦 v0.3.22 拆分对比

| | 之前 | 之后 |
|---|---|---|
| Onboardings.vue | **1026 行** | **419 行**（-59%）|
| 子组件 | 0 | **6** |
| types.ts | 0 | **1**（95 行，6 接口 + 5 枚举/工具）|
| 总行数 | 1026 | 1378（拆分必要开销）|

## 📂 6 子组件

| 文件 | 抽自 | 行数 | 关键 |
|---|---|---|---|
| `types.ts` | 全部 | 95 | Onboarding/Department/Position/UserOption + STATUS/EDUCATION 枚举 + 5 工具函数 |
| `OnboardingStatCards.vue` | 4-32 | 98 | 4 卡片 + 快捷操作 + `defineExpose({ stats })` |
| `OnboardingFilterBar.vue` | 35-73 | 98 | 搜索 + 部门/状态 + 2 switch + 操作按钮 |
| `OnboardingTable.vue` | 76-150 | 145 | 9 列 + archive popconfirm + 分页 |
| `OnboardingWizardDialog.vue` | 153-378 | **321** | **3 步向导**（账号/岗位/证件）+ 4 文件 upload + 8 表单字段 |
| `OnboardingDetailDrawer.vue` | 381-442 | 103 | 右抽屉档案详情（基础 + 证件）|
| `RenewContractDialog.vue` | 444-486 | 99 | 续签合同 dialog + form ref defineExpose |

## 🛡️ 设计模式沉淀（v0.3.22 新增）

1. **`defineExpose` 双向通信**：
   ```ts
   // 子组件: defineExpose({ formRef, stats })
   // 父组件: 子组件ref.value?.formRef?.validate()
   ```
   - StatCards 的 `stats` 不通过 prop 传（避免父组件维护 5 个 ref），用 ref + defineExpose
   - WizardDialog 的 form ref 也走 expose 模式

2. **Wizard 3 步表单一文件**：
   - 把 3 个 form 放在一个 wizard 内（form1/form2/form3）而不是拆 3 子组件
   - 因为 step 切换时 ref/form 状态共享方便，UI 切换用 `v-show` 而非 v-if

3. **uploader 事件冒泡模式**：
   - el-upload 的 `:http-request` 用 `(opt) => handleFileUpload(opt, 'field_id')`
   - 父组件通过 emit('upload', opt, field) 接收，handleFileUpload 内部写 file_id + file_name

## 🔗 累计统计

- **66+ 子组件**（v0.3.22 +6）
- **12 共享 types 文件**
- 88/88 migration 全幂等 / ECharts / 4 部署脚本

## ⏭️ 下一里程碑 v0.3.23

- **第 2 批：purchase × 7**（Requirement 727 / Contract 642 / Logistics 558 / Approval 498 / PaymentRequest 466 / Payment 448 / Plan 444）
- 第 3 批 customer × 3 / 第 4 批 process × 3 + finance × 3
- v0.3.22-25 完成后 > 500 行页面仅剩 5-7 个
