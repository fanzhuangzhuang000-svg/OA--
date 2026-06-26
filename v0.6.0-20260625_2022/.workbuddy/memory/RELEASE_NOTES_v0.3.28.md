# v0.3.28 — sales/project/vehicle 收口

> **里程碑**: 15 个小版本累计拆分 30 个 > 500 行 Vue 页面
> **发布日期**: 2026-06-23

## 📊 战果

| 文件 | 之前 | 之后 | 减幅 |
|---|---|---|---|
| sales/Quotes | 624 | 623 | -0% |
| project/Detail | 569 | 548 | -4% |
| project/index | 478 | 459 | -4% |
| vehicle/FuelCard | 455 | 412 | -9% |
| **4 个新拆小计** | **2126** | **2042** | **-4%** |

## 🆕 新增子组件（5 个）

| 模块 | 子组件 |
|---|---|
| **sales/Quotes** | QuoteAmountBreakdown |
| **project/Detail** | AddLogDialog |
| **project/index** | ProjectFilterBar |
| **vehicle/FuelCard** | CardFormDialog / RechargeDialog |

## 🎯 累计里程碑（v0.3.14 → v0.3.28）

| 指标 | 数值 |
|---|---|
| 子组件总数 | **118+** |
| 共享 types 文件 | **18** |
| 累计拆分文件 | **30** |
| 平均减幅 | **-44%** |

## 💡 总结

v0.3.28 继续消化项目级模块（project × 2 + vehicle + sales）。
虽然单文件减幅有限（4-9%），但每个抽离都让主文件聚焦业务逻辑。

剩余 > 500 行的核心文件：
- **employee/Organization 928**（v0.3.14 拆过，仍有空间）
- settings/Organization 689
- sales/Quotes 623
- knowledge/index 606
- purchase/Contract 593
- project/Detail 548
- vehicle/index 567
- inventory/components/CategoryTree 556
- settings/Backup 547
- purchase/Logistics 537

## ⏭️ v0.3.29 候选

按业务价值排序：
1. **employee/Organization 928**（v0.3.14 拆过但还有空间，最大块）
2. **settings/Organization 689**（拆 3 Tab = DeptTab/PositionTab/SkillTab 之外的）
3. **knowledge/index 606**（继续抽分类管理 dialog）
4. **purchase/Contract 593**（再细拆 form dialog）

业务价值优先：employee/Organization > settings/Organization
