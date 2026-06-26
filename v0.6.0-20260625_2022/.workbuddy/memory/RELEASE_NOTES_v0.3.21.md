# Release Notes — v0.3.21 (2026-06-23)

> **C 路径画完美句号**：Dashboard 营收图接 ECharts（v0.3.14 C1 当时 TODO），原生 CSS → 专业 ECharts 升级。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **RevenueChart 接 ECharts** | 从 v0.3.14 原生 CSS 双柱图升级到 ECharts（专业图表库）|
| **tree-shaking ECharts** | 用 `echarts/core` + 按需 import，bundle 只增加 ~187KB（gzip 后）|
| **3 模式 + 汇总 + 回款率** | 合同/回款/双柱 三模式 + 总额+回款率汇总 + 自定义 tooltip |
| **C 路径 100% 收口 + 增强** | C 路径从拆分 100% 完成 → 升级到生产级图表能力 |

## 📦 改动详情

### 1. RevenueChart.vue 重写

| 维度 | v0.3.14 原生 CSS | v0.3.21 ECharts |
|---|---|---|
| 库依赖 | 0 | echarts + vue-echarts（已在 deps）|
| 柱体样式 | 单色 flat | LinearGradient（0C447C→185FA5 / 1D9E75→58C499）|
| 柱顶数值 | 永久显示 | hover tooltip 优先，label 顶部辅助 |
| 切换 | 2 模式（合同/回款）| **3 模式**（合同/回款/双柱）|
| 汇总 | 无 | 合同总额 / 回款总额 / 回款率（带颜色判断 ≥80/≥50）|
| tooltip | 0 | 自定义 HTML（彩色块 + 名称 + 千分位数值）|
| Y 轴 | 无格式化 | `formatMoney` 自动 万/亿 切换 |
| 动画 | 0 | 800ms cubicOut 渐入 |
| 响应式 | 静态 | `autoresize` 自适应容器 |

### 2. ECharts tree-shaking 模式

```ts
import * as echarts from 'echarts/core'             // 核心
import { BarChart, LineChart } from 'echarts/charts' // 用什么 chart 引什么
import { TooltipComponent, ... } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, LineChart, ...])  // 按需注册
```

**bundle 影响**：
- `echarts-vendor-Dg6nDalf.js` 558.95 kB / gzip 186.99 kB
- 整个 project 没引 echarts → **只在 dashboard 页加载**（动态 import by route 自动 code-split）
- 旧 RevenueChart（CSS 113 行）→ 新版 197 行（多 84 行，注释+3 模式+汇总+tooltip+动画）

### 3. C 路径累计（v0.3.14 → v0.3.21）

| 类别 | 文件 | 状态 |
|---|---|---|
| **拆分** | dashboard/customer/gantt/inventory/employee/process | 8 文件 -49% ✅ |
| **增强** | dashboard/RevenueChart 接 ECharts | v0.3.21 ✅ |
| **收口** | C 路径 100% 全部完成 + 升级 | v0.3.21 ✅ |

C 路径正式画上句号，从 v0.3.14 起到 v0.3.21 共 8 个小版本一气呵成。

## 🛡️ 设计模式沉淀

1. **ECharts tree-shaking 模板**（v0.3.21 新增）：
   - `echarts/core` + 按需 import → 188KB gzip
   - 路由级 code-split 自动生效
   - `autoresize` 处理响应式

2. **mode = computed 切换**（v0.3.21 新增）：
   - `revenueType` ref + chartOption computed 联动
   - 切换时 `notMerge: true` 强制重渲染

3. **回款率颜色判断**（v0.3.21 新增业务规则）：
   - `>= 80%` 绿色（rate-good）
   - `>= 50%` 橙色（rate-ok）
   - `< 50%` 红色（rate-bad）

## 🔗 累计统计

- **60+ 子组件** / **11 共享 types** / **88/88 migration 全幂等** / 43 Controller
- ECharts 接入（tree-shaking） / 4 部署脚本
- C 路径：**8 大文件拆分** + **1 图表升级** = 100% 收口

## ⏭️ 下一里程碑 v0.3.22 候选

- **D 路径继续**：finance/payment 模块拆组件（财务/付款流程）
- **vehicle 模块**：车辆管理（vehicle.vue 19KB？）
- 把"组件化拆分"模式做成 SkillManage 全局可复用
- 全量扫剩余 > 500 行的 Vue 页面（process/InstanceDetail 582 / employee/Organization 976）
- 把"接 ECharts"模式做成 SkillManage

## 📂 改动文件

```
pc-web/src/views/dashboard/components/RevenueChart.vue  (113 → 197 行，CSS → ECharts)
.workbuddy/memory/RELEASE_NOTES_v0.3.21.md
```
