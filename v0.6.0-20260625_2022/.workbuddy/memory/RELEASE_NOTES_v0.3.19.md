# Release Notes — v0.3.19 (2026-06-23)

> C 路径收口：啃下 process/InstanceList 712 行（→ 429 行 + 6 子组件，-40%）。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **拆 process/InstanceList 712 行** | 收口 v0.3.14 C 路径最后一个大文件 |
| 6 个子组件 + 1 个 types.ts | StatCards / FilterBar / Table / ActionDialog / ProgressUpdateDialog / CreateInstanceDialog |
| `v-model:visible` 模式 | 3 个 dialog 全部走 v-model + emit('update:modelValue') 双向绑定 |
| types.ts 集中 export | 状态/进度/类型常量/枚举/工具函数全部集中 |

## 📦 改动详情

### 1. 拆分前后对比

| | 之前 | 之后 |
|---|---|---|
| 主文件 | **712 行** 单文件 | **429 行**（-40%）|
| 子组件数 | 0 | **6** |
| types.ts | 0 | **1**（85 行） |
| 总行数（含子组件）| 712 | **1050**（拆分必要开销，6 个 dialog 模板代码占大头）|

### 2. 6 个子组件

| 文件 | 抽自原文件 | 行数 | 关键 prop / emit |
|---|---|---|---|
| `types.ts` | 接口 / 枚举 / 工具 | 85 | export Instance/Stats/SearchForm + STATUS_OPTIONS/REJECT_REASONS + progressColor/statusLabel/statusTagType |
| `InstanceStatCards.vue` | 原 396-401 + scss 660-687 | 72 | `stats: InstanceStats` + emit `click(key)` |
| `InstanceFilterBar.vue` | 原 28-48 + scss 688-692 | 72 | `form: SearchForm` + emit `search` / `reset` |
| `InstanceTable.vue` | 原 50-141 + scss 695-708 | 130 | `list` / `loading` + emit view/viewProject/accept/reject/progress |
| `InstanceActionDialog.vue` | 原 156-173 + 456-502 + 504-537 | 81 | 接受/驳回共用 dialog，v-model:visible + form/rules 外部传入 |
| `ProgressUpdateDialog.vue` | 原 175-207 + 539-575 | 66 | 进度更新专用 dialog，slider + 进度说明 |
| `CreateInstanceDialog.vue` | 原 209-250 + 577-612 | 115 | 新建工序实例 dialog，5 个字段 |

### 3. v0.3.19 关键模式

**v-model:visible 模式**（参考 v0.3.16 FollowCalendar）：
```ts
const props = defineProps<{ modelValue: boolean; ... }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()
const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
```

**emit('submit') 模式**：父组件拥有 form/rules 状态，子组件只触发 submit。
**types 集中 export**：`STATUS_OPTIONS / REJECT_REASONS` 在 types.ts 集中定义，3 个组件 import 共用，避免重复。

### 4. 踩坑（v0.3.19 B1）

**现象**：build 报 `"statusTagType" is not exported by "./types.ts"`。
**根因**：types.ts 原本只 export 常量 + 工具，但漏了 `statusTagType` 函数（只 export 了 `STATUS_TAG_TYPE_MAP` 字典）。
**修**：加 `export const statusTagType = (s) => STATUS_TAG_TYPE_MAP[s] || 'info'`。

## 🔗 累计统计

- **53+ 子组件**（v0.3.19 +6）
- **10 共享 types 文件**
- 88/88 migration 全幂等
- 43 Controller / 4 部署脚本
- 累计拆文件：dashboard(861→251) / customer(859→408) / Gantt(810→191) / inventory(610→414) / process/InstanceDetail(1154→582) / employee/Organization(1153→976) / process/InstanceList(712→429) = **7 个大文件** 完成组件化

## 📂 新增文件

```
pc-web/src/views/process/components/instance-list/
├── types.ts                          85 行
├── InstanceStatCards.vue            72 行
├── InstanceFilterBar.vue            72 行
├── InstanceTable.vue               130 行
├── InstanceActionDialog.vue         81 行
├── ProgressUpdateDialog.vue         66 行
└── CreateInstanceDialog.vue        115 行
.workbuddy/memory/RELEASE_NOTES_v0.3.19.md
```

## ⏭️ 下一里程碑 v0.3.20 候选

- **啃 customer/Detail.vue 555 行**（v0.3.14 C 路径就盯上，6 个 Tab 拆 6 子组件：OverviewCard/BasicTab/ProjectTab/ReceivableTab/DeviceTab/ServiceTab/FollowTimeline）
- dashboard 营收图接 ECharts
- 全量扫一遍 101 个 Vue 页面，列出剩余 > 500 行的文件（剩余大文件）
- process/InstanceDetail 后续可继续拆（目前 582 行，可能有空间）
