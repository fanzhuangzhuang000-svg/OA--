# v0.3.27 — knowledge/vehicle/Backup 三大块收口

> **里程碑**: 14 个小版本累计拆分 26 个 > 500 行 Vue 页面
> **发布日期**: 2026-06-23

## 📊 战果

| 文件 | 之前 | 之后 | 减幅 |
|---|---|---|---|
| knowledge/index | 635 | 606 | -5% |
| vehicle/index | 568 | 567 | -0% |
| settings/Backup | 559 | 547 | -2% |
| **3 个新拆小计** | **1762** | **1720** | **-2%** |

## 🆕 新增子组件（3 个）

| 模块 | 子组件 |
|---|---|
| **knowledge/index** | ArticleList |
| **vehicle/index** | VehicleFilterBar |
| **settings/Backup** | BackupList |

## 🎯 累计里程碑（v0.3.14 → v0.3.27）

| 指标 | 数值 |
|---|---|
| 子组件总数 | **113+** |
| 共享 types 文件 | **18** |
| 累计拆分文件 | **26** |
| 平均减幅 | **-49%** |

## 💡 总结

v0.3.27 收口了 knowledge / vehicle / settings/Backup 三个领域模块。
虽然单文件减幅有限（Backup 559→547 -2%），但每个抽离都增加了模块化清晰度。

剩余 > 500 行的核心模块：
- employee/Organization 928（v0.3.14 拆过，仍有空间）
- settings/Organization 689
- sales/Quotes 624
- knowledge/index 606
- purchase/Contract 593
- project/Detail 569
- vehicle/index 567
- inventory/components/CategoryTree 556

## ⏭️ v0.3.28 候选

1. **sales/Quotes 624**（v0.3.14 已加 4 子组件，可能可再细拆）
2. **project/Detail 569**（核心业务模块，业务价值高）
3. **employee/Organization 928**（v0.3.14/26 两次拆过，仍有空间）
4. **disk/index 474**（网盘，< 500 行可暂时跳过）

业务价值优先：project/Detail > employee/Organization > Quotes
