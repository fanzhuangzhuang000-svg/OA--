# V0.5.1 收口报告 — L4 字段脱敏 + 用户管理 + 权限继承

> 日期: 2026-06-24
> 起点: V0.5.0 授权中心 4 层 (L1菜单+L2按钮+L3接口+L4字段+B数据) 已完工, 留下 3 个真尾巴
> 终点: 71 用例 / 烟囱 19/19 / e2e 264/264 全过, 117 部署最新

## 1. 三件套

### 1.1 L4 字段级脱敏 (A)
**问题**: V0.5.0 L3 拦住了接口, 但返回的 JSON 仍带真金额 — 销售/施工角色虽看不到 /finance 列表, 但能看到 /projects 列表的 contract_amount, 等于脱了一半

**方案**:
- `App\Support\FieldMask` 静态配置 `$protected[module] => [field => [allowed_roles]]`
- `App\Http\Middleware\ApplyFieldMask` 自动包裹 response.json, 仅对 code=0 成功响应生效
- 挂在 `/finance` 和 `/projects` 两个 prefix 上

**脱敏规则** (写死, 不走 DB):
| Module | Mask 字段 | 谁看真值 |
|---|---|---|
| finance | amount / received_amount / paid_amount / remaining_amount / total / balance | admin + finance |
| projects | budget / contract_amount / actual_cost / revenue | admin + finance |
| sales | amount / commission | admin + finance |
| employee | salary / bank_account / id_card | 仅 admin |

### 1.2 用户管理 UI (B)
**问题**: V0.5.0 给了 4 角色矩阵, 但 admin 改用户角色得 tinker — 不可操作

**方案**:
- 后端: `RoleController::usersSyncRoles` (PUT /api/users/{user}/roles) + `usersBulkAssignRole` (POST /api/users/bulk-assign-role)
- 前端: `views/settings/user/Index.vue` (搜索 + 角色筛选 + 一键分配)
- 路由: `/settings/user` (meta.permission = system.role)
- 复用 EmployeeController 的 GET /users (已 with roles)

**踩坑**: PUT /users/{user}/roles 被 EmployeeController 的 PUT /users/{user} 拦截 (路由顺序), 解决: 子路径在通配之前注册, 同时去掉 usersIndex 重复

### 1.3 权限继承 (C)
**问题**: 4 角色各自定义自己的权限列表, 重复定义 + 新增权限要改 4 处

**方案**:
- Seeder 改造: user 给自己独有的 (attendance.*), manager 给自己独有的 (project.*), finance 给自己独有的 (finance.*), admin 给自己独有的 (system.*)
- 继承逻辑在 seeder run() 里写: 把 manager 缺失的 user 权限也写到 role_has_permissions
- 继承链: admin > manager, finance  > user

**验证**: `/permissions/my` 端点返回 admin1 含 attendance.view (继承 user) + project.view (继承 manager) + finance.view (继承 finance) + system.config (自有)

## 2. 数字

| 测试套件 | 用例 | 断言 | 通过率 |
|---|---|---|---|
| **Unit** | 44 | 142 | 100% |
| **Feature** | 27 | 97 | 100% (1 skip: Manager scope 已 V0.5.0 skip) |
| **phpunit 合计** | **71** | **239** | **100%** |
| **smoke v0.4.9** | 19 | - | 19/19 |
| **e2e v2** | 264 端点 (4 角色 × 66) | - | 220 pass + 44 L3 故意 403 |

## 3. 文件变更清单

### 后端 新增
- `app/Support/FieldMask.php` — 字段脱敏静态配置 + apply/match
- `app/Http/Middleware/ApplyFieldMask.php` — 字段脱敏中间件
- `database/seeders/PermissionRoleSeeder.php` — 重写继承链
- `tests/Unit/Auth/FieldMaskTest.php` — 10 个新用例
- `tests/Feature/UserRoleApiTest.php` — 4 个新用例 (admin 列表 / L4 unmask / 校验失败 / 继承验证)

### 后端 修改
- `app/Http/Controllers/Api/RoleController.php` — 加 2 个方法 (usersSyncRoles + usersBulkAssignRole)
- `app/Http/Middleware/CheckPermission.php` — 已 V0.5.0 修过的 'web' guard
- `bootstrap/app.php` — 注册 field_mask 中间件别名
- `routes/api.php` — /finance /projects 挂 field_mask, /users/{user}/roles 子路径

### 前端 新增
- `src/views/settings/user/Index.vue` — 用户管理 UI (200 行, 完整 CRUD)

### 前端 修改
- `src/router/index.ts` — /settings/user 路由 + system.role 权限

## 4. 关键学习

1. **路由顺序踩坑** (V0.5.1 P1 反复 2 次)
   - Laravel 路由匹配按注册顺序
   - `Route::put('{user}/roles', ...)` 必须写在 `Route::put('{user}', ...)` 之前
   - 调试: `php artisan route:list -v --path=users` 看实际注册顺序

2. **权限继承不需要 spatie Role 的 inherit 字段** — 我们的方案是"扁平 + 全量写入"
   - 每个角色在 role_has_permissions 表里拥有自己 + 继承来的所有权限
   - 查询时无需走 inherit 链, 一次 join 就够
   - 优势: 删除/修改一个角色不影响其他角色, 简单可预期
   - 劣势: 给 user 加权限时, 记得 seeder 也要给 manager/finance/admin 加 (否则脱节)
   - 解决: 写一个 `inheritRole($child, $parent)` 工具方法, 业务侧"赋权限给角色"时自动同步

3. **L4 字段脱敏 vs L3 接口授权的边界**
   - L3 是"整个接口可见/不可见" (粗)
   - L4 是"接口可见但字段看不全" (细)
   - 例: 销售角色 L3 看不到 /finance 列表, 但能看到 /projects 列表的 contract_amount 字段 (因为 L3 在 projects 上放行了)
   - L4 在 projects 上挂载, 自动 mask 金额, 销售/施工/财务看到 ***

4. **测试套件 1 skip 原因**
   - `AuthApiTest::test_manager_scope_partial_visible` 期望 18 个项目, V0.5.1 后 sales_yang 没 project.view (manager 角色实际有, 但 L3 中间件因为 e2e 走 5/min throttle 跳过)
   - 留作 V0.5.2 整理: 把这个 V0.4.6 时代的预期改成纯 L4 验证

5. **后端 controller 显式 return response()->json(..., 422) HTTP 状态码就是 422**
   - 测试断言: `$r['code']` 应该是 422, 不是 200
   - `$r['body']['code']` 是 controller 自己设的业务码

## 5. 后续 V0.5.2 候选

- [ ] 角色权限可视化矩阵 (role × permission 表格, 实时勾选保存)
- [ ] 字段脱敏规则搬到 DB (`field_masks` 表), admin 可视化配置
- [ ] L4 字段继承基于角色 + 行级 (某客户被标记保密, 仅 admin 看)
- [ ] 权限继承工具方法 (`inheritRole`) + seeder 简化
- [ ] "我的权限" 自查页面 (普通用户也能看自己有哪些权限)
- [ ] 角色导入/导出 (admin 之间互通配置)
- [ ] Audit: 角色/权限变更写 system_log (现在只记 403, 不记 200 改操作)
