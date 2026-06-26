# Release Notes — v0.3.23 (2026-06-23)

> **D 路径第 2 批**：拆 purchase/Requirement 727→349（-52%），含子组件内部**form 副本 + defineExpose** 模式。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **Requirement.vue 727→349（-52%）** | purchase 模块最大文件，含动态物资行 + drawer + 多状态过滤 |
| **5 子组件 + 1 types** | FilterBar / StatCards / Table / FormDialog / DetailDrawer |
| **form 副本 + defineExpose 模式** | 子组件内部维护 form 副本（深拷贝 + watch 同步），父组件只 emit submit |
| **emptyForm() 工厂函数** | 重置表单用工厂函数，避开 Object.assign 漏字段 |

## 📦 v0.3.23 拆分对比

| | 之前 | 之后 |
|---|---|---|
| Requirement.vue | **727 行** | **349 行**（-52%）|
| 子组件 | 0 | **5** |
| types.ts | 0 | **1**（114 行，5 接口 + 2 枚举 + 6 工具）|
| 总行数 | 727 | 1022（拆分必要开销）|

## 📂 5 子组件

| 文件 | 抽自 | 行数 | 关键 |
|---|---|---|---|
| `types.ts` | 全部 | 114 | Requirement/Form/MaterialItem/ProjectOption + STATUS/PRIORITY 枚举 + statusLabel/statusTagType/priorityLabel/priorityTagType/isOverdue/parseMaterials + emptyForm() 工厂 |
| `RequirementFilterBar.vue` | 11-36 | 92 | 4 字段 + 查询/重置 |
| `RequirementStatCards.vue` | 40-50 + 376-381 | 52 | 4 stat-card + 紧急/项目去重 |
| `RequirementTable.vue` | 52-114 | 103 | 10 列 + 操作 (查看/编辑/删除) |
| `RequirementFormDialog.vue` | 131-240 | 191 | 新建/编辑 dialog + 动态物资行（v-for 数组）+ 表单校验 |
| `RequirementDetailDrawer.vue` | 242-310 | 121 | 右抽屉详情（基础 + 物资明细 + 备注 + 审核） |

## 🛡️ 设计模式沉淀（v0.3.23 新增）

1. **form 副本 + defineExpose 模式**：
   ```ts
   // 子组件内部维护副本
   const localForm = reactive<RequirementForm>(JSON.parse(JSON.stringify(props.form)))
   watch(() => props.form, (v) => {
     Object.assign(localForm, JSON.parse(JSON.stringify(v)))
   }, { deep: true })
   // 暴露给父组件访问（不通过 emit）
   defineExpose({ formRef, localForm })
   ```
   - 父组件传 form 进来，子组件维护副本
   - 副本变化不影响父组件（Vue 3 v-model 限制）
   - deep clone 避免 reactive ref 共享

2. **emptyForm() 工厂函数**：
   ```ts
   export const emptyForm = (): RequirementForm => ({
     id: 0, project_id: null, need_date: '',
     priority: 'medium', creator: '',
     materials: [{ name: '', spec: '', quantity: 1, unit: '件' }],
     remark: '',
   })
   ```
   - 重置时 `Object.assign(formData, emptyForm())` 不会漏字段
   - 类型安全（不用 any）

3. **解析器单条转数组模式**：
   ```ts
   export const parseMaterials = (row: Requirement): MaterialItem[] => [{
     name: row.material, spec: row.spec || '',
     quantity: row.quantity, unit: row.unit || '件',
   }]
   ```
   - 后端 schema 是单条 material/spec/quantity/unit，前端 UI 用表格展示
   - parseMaterials 统一转换

## 🔗 累计统计

- **71+ 子组件**（v0.3.23 +5）
- **13 共享 types 文件**
- 88/88 migration 全幂等 / ECharts / 4 部署脚本
- D 路径：v0.3.22 employee/Onboardings + v0.3.23 purchase/Requirement = 2/22 完成

## ⏭️ 下一里程碑 v0.3.24 计划

- **v0.3.24 第 3 批**：customer × 3（CustomerMap 696 / Pipeline 625 / Health 506）
- v0.3.25 第 4 批：process × 3 + finance × 3

剩余 5 个 purchase 文件（Contract 642 / Logistics 558 / Approval 498 / PaymentRequest 466 / Payment 448 / Plan 444）按需可放 v0.3.24 后续批次。

## 📂 改动文件

```
pc-web/src/views/purchase/components/requirement/
├── types.ts                            114 行
├── RequirementFilterBar.vue             92 行
├── RequirementStatCards.vue             52 行
├── RequirementTable.vue                103 行
├── RequirementFormDialog.vue           191 行
└── RequirementDetailDrawer.vue         121 行
.workbuddy/memory/RELEASE_NOTES_v0.3.23.md
```
