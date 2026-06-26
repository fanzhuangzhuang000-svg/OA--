# Release Notes — v0.3.24 (2026-06-23)

> **D 路径第 3 批**：拆 customer/CustomerMap 696→149（-79%），纯 CSS SVG 地图（高德/百度/腾讯）占位视图。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **CustomerMap.vue 696→149（-79%）** | D 路径最大减幅，含 SVG 地图 + 客户列表 + 浮层图例 + 详情卡 |
| **3 子组件 + 1 types** | MapSidebar（左侧列表+搜索+统计）/ MapCanvas（SVG 地图+marker）/ MapOverlayPanels（图例+详情卡）|
| **`normalizeCustomer` 工厂函数** | 后端数据 → MapCustomer 一处转换，3 子组件共享 |
| **`.sync` 双向绑定** | keyword/filterCategory/filterIndustry 用 `:keyword.sync` 模式 |

## 📦 v0.3.24 拆分对比

| | 之前 | 之后 |
|---|---|---|
| CustomerMap.vue | **696 行** | **149 行**（-79%）|
| 子组件 | 0 | **3**（MapSidebar 245 / MapCanvas 180 / MapOverlayPanels 112）|
| types.ts | 0 | **1**（91 行，1 接口 + 3 枚举 + 6 工具 + 1 工厂）|
| 总行数 | 696 | 777（拆分必要开销）|

## 📂 3 子组件

| 文件 | 抽自 | 行数 | 关键 |
|---|---|---|---|
| `types.ts` | 全部 | 91 | MapCustomer 接口 + 5 枚举（CATEGORY/INDUSTRY/MAP_TYPE/categoryLabel/categoryType）+ mapTypeName + fakeXY + normalizeCustomer 工厂 |
| `MapSidebar.vue` | 16-96 | 245 | 搜索 + 2 select 过滤 + 3 stat-item + scrollbar 客户列表 + .sync 双向 |
| `MapCanvas.vue` | 109-168 | 180 | SVG 渐变地图 + 12 个 marker（VIP/普通/潜在三色 + pulse 动画）+ 占位信息 |
| `MapOverlayPanels.vue` | 99-107 + 170-197 | 112 | 左上图例 + 底部选中客户详情卡 |

## 🛡️ 设计模式沉淀（v0.3.24 新增）

1. **`.sync` 双向绑定**：
   ```vue
   <MapSidebar
     :keyword.sync="keyword"
     :filter-category.sync="filterCategory"
     :filter-industry.sync="filterIndustry"
   />
   ```
   - 子组件内部 `keyword = computed({ get, set: (v) => emit('update:keyword', v) })`
   - 父组件不需要 `:keyword + @update:keyword` 双写
   - Vue 3 标准双向模式

2. **`normalizeCustomer` 工厂函数**（v0.3.24 新增）：
   ```ts
   export function normalizeCustomer(c: any): MapCustomer {
     const xy = c.longitude && c.latitude
       ? { x: ..., y: ... }
       : fakeXY(c.id)
     return { ...c, color: avatarColor(c.id), mapX: ..., ... }
   }
   ```
   - 后端数据 → 前端 map-ready 格式一处转换
   - 3 子组件共用，避免重复字段映射

3. **SVG 占位 + 真实 API 切换模式**：
   - 模板用 `{{ mapTypeLabel }}` 显示当前地图名
   - 集成说明 alert 提示如何在 `public/index.html` 引入 SDK
   - 未来切换真实地图时，子组件 props 不变，只换 `<MapCanvas>` 内部

## 🔗 累计统计

- **74+ 子组件**（v0.3.24 +3）
- **14 共享 types 文件**
- 88/88 migration 全幂等 / ECharts / 4 部署脚本
- D 路径：v0.3.22-24 完成 3 个文件

## ⏭️ 下一里程碑 v0.3.25 计划

- **customer/Pipeline 625**（销售漏斗，drag-drop 看板）
- **customer/Health 506**（健康度评分）
- 完成 D 路径 22 个 > 500 行页面拆分后，仅剩 17 个

## 📂 改动文件

```
pc-web/src/views/customer/components/map/
├── types.ts                          91 行
├── MapSidebar.vue                   245 行
├── MapCanvas.vue                    180 行
└── MapOverlayPanels.vue             112 行
.workbuddy/memory/RELEASE_NOTES_v0.3.24.md
```
