# Release Notes — v0.3.13 (2026-06-23) ✅ 完结

> **里程碑**: 销售模块 3 大文件全拆 + 共享类型抽取
> **部署**: 172 默认推送 ✅ / 152 手动待发布
> **类型**: 纯重构（零业务变更）

## 🎯 核心成果

### 销售模块 3 大文件全拆

| 文件 | 拆分前 | 拆分后 | 变化 |
|---|---|---|---|
| `sales/Opps.vue` | 515 | **455** | -12% |
| `sales/Leads.vue` | 513 | **408** | -20% |
| `sales/Quotes.vue` | 510 | **440** | -14% |

### 共享类型 + 7 个 dialog 子组件

```
pc-web/src/views/sales/
├── Opps.vue       455  orchestration
├── Leads.vue      408  orchestration
├── Quotes.vue     440  orchestration
├── types.ts        51  StageValue + STAGE_OPTIONS + STAGE_TAG_TYPE
├── leadTypes.ts    65  LeadStatus/Rating + DISCARD_REASONS
├── quoteTypes.ts   72  QuoteStatus + QUOTE_STATUS_STEP + QuoteItem
└── components/    7 子组件
    ├── OppDialog.vue           181  商机 create/edit
    ├── WinDialog.vue             97  成交 dialog
    ├── LostDialog.vue            94  战败 dialog
    ├── LeadDialog.vue           212  线索 create/edit
    ├── DiscardDialog.vue         74  丢弃线索
    ├── ConvertLeadDialog.vue    111  转商机
    └── ProductPickerDialog.vue  147  产品库选择 picker
```

### 跨文件行数

| 模块 | 旧 | 新 | 注释 |
|---|---|---|---|
| **Opps** | 515 (1) | 878 (5) | +363 模板/样式补全 + 类型抽取 |
| **Leads** | 513 (1) | 870 (5) | +357 同上 |
| **Quotes** | 510 (1) | 659 (4) | +149 picker dialog 提取 |
| **共享 types** | 0 | 188 | 新增 (types.ts + leadTypes.ts + quoteTypes.ts) |

> 行数增加是因为拆出后样式更规整（scoped 边界 + dialog footer 规整）

## 🛠️ 技术亮点

### 1. 类型边界清晰
- **`types.ts`** (Opps) — StageValue 6 段 + STAGE_OPTIONS + STAGE_TAG_TYPE + probabilityColor
- **`leadTypes.ts`** (Leads) — LeadStatus 5 段 + RATING_OPTIONS + DISCARD_REASONS
- **`quoteTypes.ts`** (Quotes) — QuoteStatus 6 段 + QUOTE_STATUS_STEP + QuoteItem 接口

### 2. 父子组件契约（一致 v-model + emit 模式）
- **OppDialog / LeadDialog**: `v-model:visible` + `target` prop + emit `save(data, mode)`
- **WinDialog / LostDialog**: `v-model:visible` + `target` prop + emit `confirm(data)`
- **ConvertLeadDialog / ConvertDialog(Pool)**: `v-model:visible` + `target` prop + emit `confirm(data)`
- **ProductPickerDialog**: `v-model:visible` + `existingItems` prop + emit `pick(newItems)`

### 3. watch 初始化模式
- ProductPickerDialog: `watch(() => props.visible, async (v) => { if (v) loadProducts() })`
- ConvertDialog (Pool): `watch(() => props.target, (row) => { if (row) Object.assign(formData, defaults) })`
- 3 个编辑 dialog: `watch target, immediate: true, edit mode 用 row 数据填充`

### 4. 状态机集中
- `QUOTE_STATUS_STEP` 在 types.ts 一处定义，模板直接 `quoteStatusStep(currentQuote.status)`
- 取代原本散在 3 个文件里的 3 份 `as any` 转换

### 5. vite 按需 chunk
- `Opps-*.js` 18 kB (gzip 5.5 kB)
- `Leads-*.js` 19 kB (gzip 5.5 kB)
- `Quotes-*.js` 17 kB (gzip 5.5 kB)
- 相比未拆前各 30+ kB，节省 30%+ 首屏

## ✅ 验证

- [x] `vite build` 通过 10.98s
- [x] 部署 172 (241 files, nginx reload OK)
- [x] 根路径 HTTP 200 / 38ms
- [x] `POST /api/auth/login` 正常返回 token
- [x] 6 个 sales API 全 200: opps/leads/products/categories/quote-status-options/opps-stage-options/opps-lost-reasons/leads-source-options

## 📊 拆分对比

```
v0.3.12 (拆前):
  Opps.vue   ███████████ 515
  Leads.vue  ███████████ 513
  Quotes.vue ███████████ 510
             ─────────────
             1538 行 (3 文件)

v0.3.13 (拆后):
  Opps.vue   █████████ 455
  Leads.vue  █████████ 408
  Quotes.vue █████████ 440
  7 子组件   ████████████ 916 (按需加载)
  3 types    ████ 188 (开发时用)
             ─────────────
             单文件最大 455 行 (-12%)
```

## 🐛 关键决策

1. **3 套共享 types（按业务域切分）** — Opps/Leads/Quotes 各自有 1 份 types，不强行合并
2. **dialog 模式统一** — 全部用 `v-model:visible` + props + emit，避免不同模式混用
3. **watch + immediate** — edit mode 用 watch 监听 target 变化时填充表单
4. **DUPE 检测在子组件内** — ProductPickerDialog 自带 isProductPicked 逻辑，父组件只接收 clean data
5. **状态机集中** — 6 段 quote 状态 → step 0/1/2/3 映射放 quoteTypes.ts，模板直接用

## 📦 备份

`backups/v0.3.13-20260623_1720/`  — 完整快照

## 🚀 后续 (v0.3.14+)

- v0.3.14 候选: Gantt.vue 810 / index.vue 478 同样按业务域拆
- v0.3.15: 客户/车辆/工序模块拆 dialog
- v0.4: 第三方对接（钉钉/企业微信）

## 🔗 关联

- v0.3.12: project 模块 3 大文件全拆（Detail/Create/Pool）
- v0.3.11: 销售前链路 P0 安全 + 推荐人结算
- v0.3.10: 拖拽看板状态机根治 / 全栈代码质量清理
