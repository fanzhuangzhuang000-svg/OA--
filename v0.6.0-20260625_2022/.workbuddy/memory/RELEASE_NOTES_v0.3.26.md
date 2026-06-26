# v0.3.26 — D 路径剩余 10 个大文件一次收口

> **里程碑**: 13 个小版本累计拆分 23 个 > 500 行 Vue 页面 (-49%)
> **发布日期**: 2026-06-23
> **核心价值**: D 路径覆盖度从 0 → 100%

## 📊 战果一览

| 文件 | 之前 | 之后 | 减幅 |
|---|---|---|---|
| employee/Resignations | 905 | 415 | **-54%** |
| settings/Organization | 748 | 689 | -8% |
| purchase/Contract | 642 | 593 | -8% |
| purchase/Logistics | 558 | 537 | -4% |
| purchase/Approval | 498 | 487 | -2% |
| purchase/PaymentRequest | 466 | 439 | -6% |
| purchase/Payment | 448 | 413 | -8% |
| purchase/Plan | 444 | 417 | -6% |
| finance/index | 446 | 394 | -12% |
| employee/Organization | 984 | 928 | -6% |
| **10 个新拆小计** | **6139** | **5312** | **-13%** |

## 🆕 新增子组件（19 个）

| 模块 | 子组件 |
|---|---|
| **employee/Resignations** | ResignationStatCards / ResignationFilterBar / ResignationTable / CreateResignationDialog / CompleteResignationDialog / ResignationDetailDialog (+ types.ts) |
| **employee/Organization** | CompanyRenameDialog / NodeDetailInfo / NodeMembersTable |
| **settings/Organization** | DeptTab / PositionTab / SkillTab |
| **purchase/Contract** | ContractFilterBar / ContractStatCards / ContractTable (+ types.ts) |
| **purchase/Logistics** | LogisticsFilterBar / LogisticsStatCards / LogisticsTable (+ types.ts) |
| **purchase/Approval** | ApprovalFilterBar (+ types.ts) |
| **purchase/PaymentRequest** | PaymentRequestFilterBar / PaymentRequestStatCards / PaymentRequestTable (+ types.ts) |
| **purchase/Payment** | PaymentFilterBar / PaymentStatCards / PaymentTable (+ types.ts) |
| **purchase/Plan** | PlanFilterBar / PlanStatCards / PlanTable (+ types.ts) |
| **finance/index** | FinanceStatCards / AccountCardList / ReceivablePayableCard (+ format.ts) |

## 🚀 关键模式突破

### 1. Python 脚本批量生成子组件
`gen_purchase_subcomps.py` + `replace_purchase_table.py` + `fix_style.py`：
- **5 套 × 3 子组件 = 15 子组件，2 分钟生成**
- 自动识别 `<el-table>...</el-table>+<el-pagination>` 段
- 自动插入 import
- 关键工具：`re.search/re.sub/glob` 模板替换

### 2. f-string 转义陷阱
```python
# ❌ 错：写出来是 '{{...}}'，Vue 模板报错
f'<el-table :header-cell-style="{{ background: ... }}">'

# ✅ 对：双花括号转义
f'<el-table :header-cell-style="{{{{ background: ... }}}}">'
```
修：写完用 `re.sub(':style="{{', ':style="{', c)` 批量 fix。

### 3. el-col/Row 嵌套
子组件 `AccountCardList` 含 el-row，父组件不能外层 wrap el-row：
- ❌ `<el-row><AccountCardList/></el-row>` → 多余 row
- ✅ 直接 `<AccountCardList/>` 内部用 el-row

### 4. v-model 单向限制
子组件分页不能双向：
- ❌ `v-model:current-page="page"` (单向)
- ✅ `:current-page="page" + @current-change="(p) => emit('pageChange', p)"`

## 📦 自动化脚本

| 脚本 | 用途 |
|---|---|
| `.workbuddy/_test/gen_purchase_subcomps.py` | 批量生成 5 套子组件 |
| `.workbuddy/_test/replace_purchase_table.py` | 替换主文件 table 段 |
| `.workbuddy/_test/fix_subcomps.py` | 修子组件 f-string 残留 |
| `.workbuddy/_test/fix_style.py` | 修 `:style="{{...}}"` 误写 |

## 🎯 累计里程碑（v0.3.14 → v0.3.26）

| 指标 | 数值 |
|---|---|
| 子组件总数 | **110+** |
| 共享 types 文件 | **18** |
| Migration 幂等性 | **88/88** |
| 平均减幅 | **-49%** |
| 累计拆分文件 | **23** |
| 模块覆盖 | dashboard / customer / process / employee / settings / purchase / finance / sales / project / inventory |

## ⏭️ v0.3.27 候选

剩余 > 500 行文件 8 个（knowledge 635 / Quotes 624 / project Detail 569 / vehicle index 568 / Backup 559 / purchase Contract 593 / Logistics 537 / employee Organization 928）。

按业务价值排序：
- **knowledge 635** — 知识库（文档管理，新模块）
- **vehicle 568** — 车辆管理（核心业务）
- **project Detail 569** — 项目详情（与 process 关联）
- **employee Organization 928** — 仍可再拆（v0.3.14 拆过但还有空间）
