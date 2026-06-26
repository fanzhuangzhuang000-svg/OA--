# B 数据权限 — 8 张表字段审计 (2026-06-24)

## created_by / 参与字段分布

| 表 | created_by | 其他参与字段 | 备注 |
|---|---|---|---|
| **projects** | ❌ 无 | `manager_id` + `project_members(user_id)` 中间表 | 自己创建的判定靠 project_members 或兜底 manager_id |
| **customer_receivables** | ✅ 有 | `customer_id` / `project_id` | 完美 |
| **purchase_orders** | ❌ 无 | `approved_by` / `project_id` / `supplier_id` | 自己创建的判定兜底 approved_by |
| **construction_logs** | ❌ 无 | `user_id` (操作人) / `project_id` | 自己创建的判定就是 user_id = me |
| **rectifications** | ✅ 有 | `responsible_id` / `created_by` | 完美 |
| **warranties** | ✅ 有 | `project_id` / `customer_id` / `created_by` | 完美 |
| **warranty_service_orders** | ✅ 有 | `technician_id` / `warranty_id` | 完美 |
| **warranty_deposits** | ✅ 有 | `project_id` / `approved_by` | 完美 |

## 关键发现

1. **projects 表没有 created_by** —— 自己创建的判定改为：
   - `manager_id = $user->id` (作为负责人)
   - 或 `id IN (SELECT project_id FROM project_members WHERE user_id = $user->id AND status='active')`
   - 即"自己创建" 改为"自己负责 / 自己参与"

2. **purchase_orders 表没有 created_by** —— 自己创建的判定改为：
   - `approved_by = $user->id` (审批人) 或 `project_id IN (我参与的项目)`
   - 不如 projects 干净，需要 trade-off

3. **service_order_technicians 表是空的**（0 列）—— 这个表不存在！service_order 的"技师"关系需要重新看

4. **users / roles 用 spatie/laravel-permission** —— `model_has_roles` 关系表存在

## Scope 设计调整

每张表的"自己创建 / 自己参与" 表达式：

| 表 | 表达式 |
|---|---|
| projects | `(manager_id = $me) OR (id IN my_projects_subquery)` |
| customer_receivables | `(created_by = $me) OR (project_id IN my_projects_subquery)` |
| purchase_orders | `(approved_by = $me) OR (project_id IN my_projects_subquery)` |
| construction_logs | `(user_id = $me) OR (project_id IN my_projects_subquery)` |
| rectifications | `(created_by = $me) OR (responsible_id = $me) OR (project_id IN my_projects_subquery)` |
| warranties | `(created_by = $me) OR (project_id IN my_projects_subquery)` |
| warranty_service_orders | `(created_by = $me) OR (technician_id = $me) OR (warranty_id IN my_warranties_subquery)` |
| warranty_deposits | `(created_by = $me) OR (approved_by = $me) OR (project_id IN my_projects_subquery)` |

其中 `my_projects_subquery` = `SELECT id FROM projects WHERE manager_id = $me OR id IN (SELECT project_id FROM project_members WHERE user_id = $me AND status='active')`

## 角色判定

- admin: `user->hasRole('admin')`
- finance: `user->hasRole('finance')`
- manager: `user->hasRole('manager')` 或 `user->hasAnyRole(['销售经理', '项目经理', '施工经理'])` （看实际角色名）
- 其他: 默认（普通员工）

## 角色判定（最终方案）

**所有 19 个用户的 `users.type` 字段都是 `staff`**，没有用 spatie 关系绑定角色（model_has_roles 空）。

**改用 `username` 前缀映射**：
- `admin` 或 `admin*`（admin1 / admin_zheng / admin_wang） → **admin** 角色
- `fin_*`（fin_wu / fin_zhou / fin_mgr） → **finance** 角色
- `sales_*` / `tech_mgr` / `proj_mgr` → **manager** 角色
- 其他（eng_* / 默认） → **普通员工**

**业务用户清单**（按 id）：
| id | name | username | 角色 |
|---|---|---|---|
| 1 | admin-test | admin | admin |
| 74 | 系统管理员 | admin1 | admin |
| 75 | 陈技术 | tech_mgr | manager |
| 76 | 林项目 | proj_mgr | manager |
| 77 | 赵销售 | sales_mgr | manager |
| 78 | 黄财务 | fin_mgr | finance |
| 79 | 周会计 | fin_zhou | finance |
| 80 | 吴出纳 | fin_wu | finance |
| 81-84 | eng_zhao/qian/sun/li | eng_* | staff |
| 85-86 | sales_chen/yang | sales_* | manager（推） |
| 87-88 | admin_zheng/wang | admin_* | admin（推） |

## 烟囱测试计划（24 用例）

| 角色 | 用户 | 用例 |
|---|---|---|
| admin | admin1 (id=74) | 列项目全量 / 列应收全量 / 列日志全量 / 列质保全量 / 列整改全量 / 列采购全量 = **6 期望 ≥ 实际数** |
| finance | fin_wu (id=80) | 同上 6 用例 |
| manager | sales_yang (id=86) | 列项目=18 个 / 列采购=自己参与项目内的 / 列日志=自己 user_id OR 自己参与项目 / 列质保=自己参与项目 / 列整改=自己 created_by OR 负责 / 列应收=自己参与项目内 = **6 期望** |
| staff | eng_zhao (id=81) | 列项目=0（不参与任何项目）/ 列日志=0 / 列质保=0 / 列采购=0 / 列整改=0 / 列应收=0 = **6 期望** |

**反向用例**：manager 直接 GET /projects/{id} (id=任意非自己) → 期望 404

## 待办
- [ ] 推 username 映射到 AuthScope::classify($user)
- [ ] test case 用现有真实数据跑（不动数据，只读）
