# Release Notes — v0.3.12 (2026-06-23) ✅ 完结

> **里程碑**: 前端组件化深推 — project 模块 3 大文件全拆
> **部署**: 172 默认推送 ✅ / 152 手动待发布
> **类型**: 纯重构（零业务变更，零行为变更）

## 🎯 核心成果

### project 模块 3 大单文件全拆

| 文件 | 拆分前 | 拆分后 | 变化 |
|---|---|---|---|
| `Detail.vue` | 1716 | **569** | **-66%** |
| `Create.vue` | 866 | **242** | **-72%** |
| `Pool.vue` | 238 | **235** | -1% (ConvertDialog 外提) |

### 最终目录结构

```
pc-web/src/views/project/
├── Detail.vue (569)         ← orchestration
├── Create.vue (242)         ← orchestration
├── Pool.vue (235)           ← orchestration
├── types.ts (219)           ← Detail 共享类型
├── createTypes.ts (146)     ← Create 共享类型
└── components/
    ├── BasicInfoTab.vue (110)        ← Detail tab 1
    ├── StageFlowTab.vue (249)        ← Detail tab 2
    ├── ConstructionLogTab.vue (120)  ← Detail tab 3
    ├── CostTab.vue (202)             ← Detail tab 4
    ├── ProcessTab.vue (445)          ← Detail tab 5
    ├── BasicStep.vue (139)           ← Create 步骤 1
    ├── BudgetStep.vue (367)          ← Create 步骤 2
    ├── TeamStep.vue (139)            ← Create 步骤 3
    ├── ConfirmStep.vue (78)          ← Create 步骤 4
    └── ConvertDialog.vue (183)       ← Pool 转为施工 dialog
└── composables/ (1)
    └── useProjectDetail.ts (122)     ← Detail 共享数据
```

### 跨文件行数

| 模块 | 旧 | 新 | 注释 |
|---|---|---|---|
| **Detail** | 1716 (1) | 1894 (8) | +178 模板/样式补全 |
| **Create** | 866 (1) | 1111 (6) | +245 模板/样式补全 |
| **Pool** | 238 (1) | 418 (2) | +180 dialog 样式 |
| **共享 types** | 0 | 365 | 新增 (types.ts + createTypes.ts) |
| **composables** | 0 | 122 | 新增 |

> 行数增加是因为拆出后样式更规整（scoped 边界 + section 重复），但单文件复杂度大幅降低

## 🛠️ 技术亮点

### 1. 类型边界清晰
- **`types.ts`** (Detail) — Project / Tracking / PaymentNode / MaterialStats / Risk / TimelineEntry / ConstructionLog / ProcessInstance / ProcessInspection / STAGES / STAGE_INDEX_MAP / STATUS_LABEL_MAP / RISK_ACTION_MAP
- **`createTypes.ts`** (Create) — ProjectForm / BudgetKey / TYPE_TO_ENUM / PRIORITY_TO_ENUM / newBudgetRow / formatMoney / createEmptyForm

### 2. 共享 composable (Detail)
- `useProjectDetail(() => projectId)` 返回响应式状态 + 5 个 load 方法 + addLog
- 父组件按需调用，子组件只接收 props

### 3. 父子组件契约
- **Detail tabs**: 纯展示，0 状态修改
- **Detail construction log**: emit `add/export/view`，dialog 在父
- **Detail process**: emit `open-instance/refresh`，创建 dialog 内置
- **Create steps**: 通过 v-model 双向绑定 form reactive，预算加减用 props.form.budget
- **Pool ConvertDialog**: `v-model:visible` + emit `confirm(formData)`

### 4. vite 按需 chunk (Detail)
- `Detail-DzCHtKiY.js` 45 kB（gzip 13.75 kB） — 父编排
- `Detail-Cyxjiu-l.js` 14 kB — 子组件 (basic + stage)
- `Detail-ClCsm65b.js` 6.8 kB — 子组件 (cost + process)

## ✅ 验证

- [x] `vite build` 通过 11.67s
- [x] 部署 172 (241 files, nginx reload OK)
- [x] 根路径 HTTP 200 / 48ms
- [x] `POST /api/auth/login` 正常返回 token
- [x] 4 个关键 API 验证: customers/employees/projects/{id}/sales/pool 全 200

## 📊 拆分对比

```
v0.3.11 (拆前):
  Detail.vue  ████████████████████ 1716
  Create.vue  ████████████ 866
  Pool.vue    ███ 238
              ───────────────
              2820 行 (3 文件)

v0.3.12 (拆后):
  Detail.vue  ███████ 569
  Create.vue  ███ 242
  Pool.vue    ███ 235
  8 子组件    ██████████ 1756 (按需加载)
  2 types.ts  ████ 365 (开发时用)
  1 composable ██ 122
              ───────────────
              单文件最大 569 行 (-66%)
```

## 🐛 关键决策

1. **字段适配器放 types.ts 公共位置** — `getCustomerName/getManagerName/computeTotalBudgetWan` 5 tab 都用
2. **composable 暴露数据 + load 方法** — 父组件按需调用，子组件纯 props
3. **报告生成留在 Detail 父组件** — 跨多 tab 数据
4. **工序验收 dialog 内置 ProcessTab** — 纯局部 UI
5. **Create 各 step 通过 v-model 改 form reactive** — 共享同一 form 对象，无 props/emits 双向
6. **ConvertDialog v-model:visible + emit confirm** — 标准 Element Plus 模式
7. **useProjectDetail(() => projectId.value) 传 getter** — 响应式不丢

## 📦 备份

`backups/v0.3.12-20260623_1700/`  — 13MB 完整快照

## 🚀 后续 (v0.3.13+)

- v0.3.13 候选: Gantt.vue 22KB / index.vue 19KB 同样按业务域拆分
- v0.3.14: 销售模块 (Leads.vue / Opps.vue / Quotes.vue) 拆 dialog 子组件
- v0.4: 第三方对接（钉钉/企业微信）

## 🔗 关联

- v0.3.11: 销售前链路 P0 安全 + 推荐人结算（已完结）
- v0.3.10: 拖拽看板状态机根治 / 全栈代码质量清理
