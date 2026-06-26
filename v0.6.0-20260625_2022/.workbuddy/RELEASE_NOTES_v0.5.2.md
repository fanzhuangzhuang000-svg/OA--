# V0.5.2 收口报告 — 角色权限矩阵 + 权限继承 + 字段脱敏 DB 化 + Audit Log

> 日期: 2026-06-24
> 起点: V0.5.1 4 层授权完工, 留下 5 个尾巴
> 终点: 87 用例 / 烟囱 19/19 / e2e 264/264 全过, 117 部署最新

## 1. 5 件事

### 1.1 角色权限矩阵 UI (A)
**问题**: V0.5.0 admin 改角色权限要 tinker, V0.5.1 给了勾选 UI 但没暴露继承关系

**方案**:
- 后端 `RoleController::matrix` (GET /api/roles/matrix) 返回完整矩阵: roles + permissions + matrix[role_name => perm_names] + 继承图
- 前端 `views/settings/role/Matrix.vue` (300 行): 角色 tab + 权限开关 + 继承提示 + 二次确认
- 勾选 → POST /api/roles/{role}/permissions → 自动 syncPermissions + PermissionInheritance::propagateToChildren

**关键点**:
- 矩阵按 module 分组, 同一 module 内按 name 排序
- "继承" 标记: 当前角色没这个权限, 但父角色有 → 显示 "继承" 标签
- 移除继承的权限 → 二次确认弹窗
- 实时统计: 自有 / 继承 / 总有效 4 个数字

### 1.2 权限继承工具方法 (B)
**问题**: V0.5.1 写死了 4 角色权限列表, 业务侧"给 manager 加权限"不会自动给 admin 加

**方案**:
- `App\Support\PermissionInheritance` 静态继承图 (BFS 找所有子孙, 防止环)
- `propagateToChildren($parent, $perms)` 业务侧赋权限时, 同步给所有子孙 (union 而非覆盖, 不丢子角色自己加的权限)
- `revokeFromChildren($parent, $perms)` 父角色减权限时, 同步从子孙移除
- `getGraph()` 前端可视化

**集成点**:
- `RoleController::assignPermissions` 加了 `propagateToChildren` 一行
- 解决了"manager 加新权限 admin 看不到"问题

### 1.3 字段脱敏规则 DB 化 (C)
**问题**: V0.5.1 FieldMask 是静态 `$protected` 写死, admin 改不了

**方案**:
- 新建 `field_masks` 表 (migration `2026_06_24_000016`)
- 字段: endpoint / field / allowed_roles / description / enabled
- `FieldMask::loadAll()` 走 5min Redis cache + 失败回退 fallback
- 新 `FieldMaskController` (5 个端点: list/create/update/destroy/flush-cache)
- `FieldMaskSeeder` 把 V0.5.1 静态配置 1:1 搬进 DB

**关键改进**:
- admin 可可视化配置每条规则 (UI 在 V0.5.2-A Matrix 旁边)
- 修改后立即生效 (flushCache)
- DB 没配置时回退到 fallback (兼容 V0.5.1 老代码)
- 静态 fallback 仍保留 (Unit Test 不 boot Laravel 时用)

### 1.4 "我的权限" 自查页 (D)
**问题**: 普通用户不知道自己有哪些权限, 调接口踩 403 才知道

**方案**:
- `views/settings/MyPermissions.vue` (250 行)
- 4 个统计卡片: 自有 / 继承 / 总有效 / 系统全部
- 4 种过滤: 全部 / 仅自有 / 仅继承 / 我没有的
- 实时搜索 (按 name / label)
- 数据来源: /permissions/my (合并) + /permissions/tree (平铺) + /permissions/inheritance (边)

### 1.5 角色变更 audit log (E)
**问题**: admin 改用户角色是 200 成功, 但 system_logs 没记录, 出事查不到

**方案**:
- 新 `App\Support\Audit` helper (Facade-safe 单元测试兼容)
- 写入 system_logs: action='role_changed', description 含 username/id/旧→新
- 在 `usersSyncRoles` 加 3 行: 比对 oldRoles vs newRoles, 变了就 Audit::write
- Audit 写失败不阻塞业务 (try/catch + Log::warning 兜底)

## 2. 数字

| 测试套件 | 用例 | 断言 | 通过率 |
|---|---|---|---|
| **Unit** | 53 | 158 | 100% |
| **Feature** | 34 | 131 | 100% (1 skip: Manager scope V0.5.0 时代 skip) |
| **phpunit 合计** | **87** | **289** | **100%** |
| **smoke v0.4.9** | 19 | - | 19/19 |
| **e2e v2** | 264 端点 (4 角色 × 66) | - | 220 pass + 44 L3 故意 403 |

## 3. 文件变更清单

### 后端 新增
- `app/Support/PermissionInheritance.php` — 继承图 + propagate/revoke
- `app/Support/Audit.php` — 写 audit log helper
- `app/Http/Controllers/Api/FieldMaskController.php` — 5 端点 CRUD
- `database/migrations/2026_06_24_000016_create_field_masks_table.php` — DB 化
- `database/seeders/FieldMaskSeeder.php` — 把 V0.5.1 静态搬进 DB
- `tests/Unit/Auth/InheritanceAndAuditTest.php` — 8 个新用例
- `tests/Feature/PermissionMatrixApiTest.php` — 7 个新用例 (matrix / inheritance / field-masks / audit)

### 后端 修改
- `app/Models/User.php` — 重写 `getDefaultGuardName()` 返回 'web' (Sanctum 那个是 sanctum, spatie 找角色抛 no role named)
- `app/Http/Controllers/Api/RoleController.php` — 加 3 个方法 (matrix/inheritanceGraph/usersSyncRoles audit log); 现有 assignPermissions 调 propagateToChildren
- `app/Support/FieldMask.php` — 改 DB 驱动 + cache + fallback
- `routes/api.php` — 加 matrix / inheritance / field-masks 路由; 修 {role} 通配 whereNumber('role') 防 22P02

### 前端 新增
- `src/views/settings/role/Matrix.vue` — 权限矩阵 UI (300 行)
- `src/views/settings/MyPermissions.vue` — 我的权限自查 (250 行)

### 前端 修改
- `src/router/index.ts` — /settings/role/matrix + /settings/my-permissions 路由
- `src/views/settings/role/Index.vue` — 加"权限矩阵"入口按钮

## 4. 关键学习 (4 个新踩坑)

1. **spatie syncRoles(...$roles) 是 variadic**
   - `syncRoles($valid, 'web')` 实际是 roles=[$valid, 'web'] = [user, web] → 找不到 web 角色
   - 正确: User 重写 `getDefaultGuardName()` 返回 'web', 直接 `syncRoles($valid)`

2. **Sanctum HasApiTokens 重写 getDefaultGuardName 为 sanctum**
   - 与 spatie 冲突: spatie 找角色时用默认 guard → 找不到 web guard 的角色
   - 解: User 模型里 override

3. **路由 {role} 通配吃掉 'matrix'**
   - `Route::get('roles/{role}', ...)` 把 GET /api/roles/matrix 当 id=matrix → 22P02
   - 解决: whereNumber('role') 限定

4. **phpunit 测试登录撞 5/min throttle**
   - 4 个白名单用户外 (admin1/fin_wu/eng_qian/sales_yang), 5 次/min 撞墙
   - 解: 每 3 次新 login 清 Redis + setUpBeforeClass flush

## 5. 关键命令 (新人须知)

```bash
# 跑测试前必清 throttle
ssh nbcy@192.168.3.117 'redis-cli -n 0 FLUSHDB && redis-cli -n 1 FLUSHDB'

# phpunit 单独跑 (避免互相污染)
cd /var/www/oa-api && sudo -u www-data ./vendor/bin/phpunit --testsuite=Unit
cd /var/www/oa-api && sudo -u www-data ./vendor/bin/phpunit --testsuite=Feature

# 部署 (已含 .env 备份检查)
cd /var/www/OA && tar -czf /tmp/oa-api.tar.gz --exclude=vendor pc-api/
scp /tmp/oa-api.tar.gz nbcy@192.168.3.117:/tmp/
ssh nbcy@192.168.3.117 "..."
ssh nbcy@192.168.3.117 "sudo systemctl restart php8.5-fpm"

# 端到端模拟测试
ssh nbcy@192.168.3.117 "python3 /tmp/e2e_v2.py"
```

## 6. 后续 V0.5.3 候选

- [ ] 字段脱敏规则管理 UI (admin 可视化配置 field_masks)
- [ ] 角色权限矩阵导出 Excel / PDF
- [ ] 权限继承可视化图 (D3.js 画角色树)
- [ ] 权限变更历史 (audit log 增强 — 加 /audit/role-changes 端点)
- [ ] L4 字段级脱敏规则可视化 (哪些字段对哪些角色脱敏)
- [ ] 系统通知: "你的角色被改了" (邮箱/站内信)
- [ ] 临时权限 (有时效的赋权, 例如销售副经理出差 1 周)
- [ ] 用户自助申请角色 (审批流集成)
