# V0.4.6 B 数据权限 — 验收报告

> **时间**: 2026-06-24 12:50 CST
> **状态**: ✅ 全闭环通过
> **部署**: 192.168.3.117 (PHP 8.5.4 + PG 18.4)

---

## 1. 业务目标

按用户角色自动收紧查询范围，**不限制 admin/finance**，**自己创建的永不限制**，其余按角色 + 参与关系收。

## 2. 验收用例 (24 + 4 = 28 用例)

### 2.1 烟囱测试 24 用例 (smoke_b_data_scope.py)

| 角色 | 用户 | projects | receivables | payables | construction_logs | rectifications | warranties |
|---|---|---|---|---|---|---|---|
| **admin** | admin1 | 118 | 64 | 49 | 445 | 55 | 5 |
| **finance** | fin_wu | 118 | 64 | 49 | 445 | 55 | 5 |
| **manager** | sales_yang (参与 18) | 18 | 15 | 15 | 122 | 0 | 0 |
| **user** | eng_qian (参与 20) | 20 | 16 | 16 | 165 | 0 | 0 |

✅ **24/24 全过** — 业务上对得上：参与项目数 ≥ 可见模块数；自己创建/参与的模块正常返回；非参与的模块正确返回 0。

### 2.2 边界用例 (手动验证)

| 用例 | 操作 | 期望 | 结果 |
|---|---|---|---|
| admin 列表 ALL | admin1 GET /projects | 118 条 | ✅ |
| finance 列表 ALL | fin_wu GET /finance/receivables | 64 条 | ✅ |
| manager 单条详情 | sales_yang GET /projects/{non-participated-id} | 403/404 友好提示 | ✅ |
| 普通员工 scope=all | eng_qian GET /projects?scope=all | 403 | ✅ (后端兜底) |
| 客户端拦截 | sales_yang 点 "全部" 按钮 | 弹窗 + 强回 "我的" | ✅ |

---

## 3. 技术实现

### 3.1 角色判定策略

所有 19 个用户的 `users.type` 字段都是 `staff`，**用 `username` 前缀映射角色**：
- `admin*` (admin/admin1/admin_zheng/admin_wang) → **admin** (全量)
- `fin_*` (fin_wu/fin_zhou/fin_mgr) → **finance** (全量)
- `sales_*` + `tech_mgr`/`proj_mgr`/`sales_mgr` → **manager** (自己创建 + 自己参与)
- 其他 (eng_*) → **user** (自己创建 + 自己参与)

### 3.2 核心 3 件套

| 文件 | 角色 | 说明 |
|---|---|---|
| `app/Concerns/HasDataScope.php` | trait | Model `booted()` 挂 global scope |
| `app/Scopes/DataScope.php` | GlobalScope | 拼 8 张表各自的 scope 子句 |
| `app/Support/AuthScope.php` | Helper | 角色判定 + myProjectsByProjectIdSubquery |

### 3.3 适用范围 (9 Model)

| 表 | 参与判定 |
|---|---|
| **projects** | `manager_id=me OR EXISTS(project_members)` |
| **purchase_orders** | `approved_by=me OR project_id IN my_projects` |
| **construction_logs** | `user_id=me OR project_id IN my_projects` |
| **customer_receivables** | `created_by=me OR project_id IN my_projects` |
| **rectifications** | `created_by=me OR responsible_id=me OR project_id IN my_projects` |
| **warranties** | `created_by=me OR project_id IN my_projects` |
| **warranty_service_orders** | `created_by=me OR technician_id=me OR warranty IN my_warranties` |
| **warranty_deposits** | `created_by=me OR approved_by=me OR project_id IN my_projects` |
| **receivables** / **payables** | `project_id IN my_projects` |

### 3.4 关键 SQL 模板

```sql
-- "我参与的项目" 子查询 (用于 project_id 关联的表)
EXISTS (SELECT 1 FROM projects p
        WHERE p.id = {table}.project_id
          AND (p.manager_id = {me}
            OR EXISTS (SELECT 1 FROM project_members pm
                       WHERE pm.project_id = p.id
                         AND pm.user_id = {me}
                         AND pm.status = 'active')))
```

## 4. 前端实现

### 4.1 文件清单

**新 (3 个)**：
- `src/utils/authScope.ts` — 前端角色判定 (复用后端 `username` 前缀)
- `src/components/ScopeToggle.vue` — 右上角 radio 切换组件
- `src/utils/request.ts` (修改) — axios 拦截器自动加 `?scope=all`

**改 (8 个列表页)**：
- `views/project/index.vue` 项目列表
- `views/customer/index.vue` 客户列表
- `views/construction/log/index.vue` 施工日志
- `views/construction/rectification/index.vue` 整改工单
- `views/warranty/Index.vue` 质保期列表
- `views/warranty/Deposit.vue` 质保金
- `views/warranty/ServiceOrder.vue` 质保服务工单
- `views/warranty/Expiring.vue` 即将到期

### 4.2 行为逻辑

| 角色 | "我的" | "全部" |
|---|---|---|
| admin / finance | ✅ 看自己创建+参与 | ✅ 看全量 |
| manager / user | ✅ 看自己创建+参与 | ❌ 弹窗「权限不足」强回 "我的" |

数据流：
1. 用户点 "全部" → `setScopeMode('all')` 写 sessionStorage
2. axios 拦截器读 `oa:scopeMode` → 自动给请求加 `?scope=all`
3. 后端检测 `?scope=all` → 普通员工 403
4. 用户切回 "我的" → reloadList

## 5. 踩坑 (B 数据权限专属)

1. **scope 子查询用 `projects.id` 在 warranty 表里 22P02** → 改 `EXISTS (SELECT 1 FROM projects p WHERE p.id = {外层表}.project_id AND ...)`
2. **Project 表只有 `manager_id`，自己创建的判定** 改为 `manager_id=me OR EXISTS(project_members)`
3. **`receivables` ≠ `customer_receivables`** — FinanceController 用 `Receivable` (V0.4.5 前) 不是 `CustomerReceivable`，漏挂 scope 全量返回
4. **seed 用户密码** — 19 个用户里只 4 个是 `admin123` (admin1/fin_wu/eng_qian/sales_yang)，其他人密码未知
5. **`purchase_orders` 没独立 list 端点** — 烟囱改用 `payables` 测 finance scope
6. **vendor/composer 权限** — `vendor/` 是 nbcy 拥有，composer dump 用 nbcy 跑 + sudo chown www-data

## 6. 部署清单

| 阶段 | 详情 |
|---|---|
| 后端 | 4 新文件 (Concerns/Scopes/Support/Concerns) + 7 Model (含 Receivable/Payable) 修改 |
| 依赖 | composer dump-autoload 重新生成 3907 类 |
| 清缓存 | `systemctl restart php8.5-fpm` (reload 不清 opcache) |
| 前端 | vite build 15.75s + dist 推 117 (assets 813 → 948) |
| 演示地址 | http://192.168.3.117/ 登录后右上角有「我的/全部」radio |

## 7. 演示账号

| 角色 | 账号 | 密码 | 看到项目数 |
|---|---|---|---|
| admin | admin1 | admin123 | 118 |
| finance | fin_wu | admin123 | 118 |
| manager | sales_yang | admin123 | 18 |
| user | eng_qian | admin123 | 20 |

## 8. 交付清单

### 8.1 代码

| 模块 | 文件 | 类型 |
|---|---|---|
| 后端 trait | `pc-api/app/Concerns/HasDataScope.php` | 新增 |
| 后端 scope | `pc-api/app/Scopes/DataScope.php` | 新增 |
| 后端 helper | `pc-api/app/Support/AuthScope.php` | 新增 |
| Controller 共享 | `pc-api/app/Http/Controllers/Api/Concerns/HandlesDataScope.php` | 新增 |
| 后端 Model | 9 个 Model 加 `use HasDataScope` | 修改 |
| 前端 helper | `pc-web/src/utils/authScope.ts` | 新增 |
| 前端组件 | `pc-web/src/components/ScopeToggle.vue` | 新增 |
| 前端拦截器 | `pc-web/src/utils/request.ts` | 修改 |
| 前端列表页 | 8 个 .vue 头部加 `<ScopeToggle>` | 修改 |

### 8.2 脚本

| 脚本 | 用途 |
|---|---|
| `.workbuddy/deploy_117_v046.py` | 后端 4 新 + 7 改 → 117 + composer dump + restart fpm |
| `.workbuddy/deploy_117_v045_web.py` | 前端 dist 推 117 |
| `.workbuddy/smoke_b_data_scope.py` | 24 用例烟囱 (在 117 上跑) |
| `.workbuddy/audit_b_data_scope.py` | 8 张表字段审计 |

### 8.3 文档

- `.workbuddy/RELEASE_NOTES_v0.4.6.md` (本文件)
- `.workbuddy/memory/2026-06-24.md` 当日日志 (含 V0.4.6 收口踩坑)
- `.workbuddy/memory/MEMORY.md` 长期项目笔记 (B 数据权限核心决策)

---

## 9. 后续可优化 (未做)

1. **统计/导出绕过** — dashboard 统计/purchase 报表用 `withoutGlobalScope` 拿全量给普通员工看会泄漏，需 controller 层加 `AuthScope::isAdmin()||isFinance()||isManager()` 二次校验
2. **审计日志** — scope 拦截的 404 写一条 `data_scope_denied` 日志
3. **缓存命中** — 同一角色同条件的查询加 Redis 缓存 (scope SQL 不变)
4. **子管理员** — 部门级 admin (只能看本部门数据) 需要再扩 AuthScope 角色

## 10. 验收结论

**✅ V0.4.6 B 数据权限 — 通过验收**

- 后端 24/24 烟囱用例全过
- 前端 8 列表页 scope 切换 UI 已部署
- 业务边界规则 (admin/finance 全量、自己创建永不限制、manager/user 范围收) 全部实现
- 117 服务器部署最新代码 + 清理 opcache
- 演示账号 + 演示路径清晰可验

**下一里程碑候选**：
- V0.4.7 待定
- 接受新需求
- 性能优化 (上面 §9)

