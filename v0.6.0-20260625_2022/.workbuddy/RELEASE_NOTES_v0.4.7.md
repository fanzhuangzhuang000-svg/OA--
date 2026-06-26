# V0.4.7 安全收口 (B 数据权限补完) — 验收报告

> **时间**: 2026-06-24 13:30 CST
> **状态**: ✅ 全闭环通过
> **部署**: 192.168.3.117 (PHP 8.5.4 + PG 18.4)

---

## 1. 业务目标

V0.4.6 B 数据权限发布后，RELEASE_NOTES_v0.4.6.md §9 列出 4 条「后续可优化」。V0.4.7 收口其中 3 条：

| § | 优化项 | V0.4.7 状态 |
|---|---|---|
| 9-1 | 统计/导出绕过二次校验 | ✅ dashboard + inventory export |
| 9-2 | scope 拦截审计日志 | ✅ DataScope::logDeniedAccess |
| 9-3 | Redis 缓存 | ❌ 暂不做 (牵涉多) |
| 9-4 | 部门级子管理员 | ❌ 需求不明确 |

**额外**（V0.4.6 验收时发现但未修）：
- 详情页 404 vs 403 友好提示 → ✅ HandlesDataScope::respondNotFound
- Dashboard cache 跨用户污染 (key 不含 user) → ✅ cache key 加 user_id
- 旁路 scope 找不到 vs 真找不到区分 → ✅ findScoped 二次查

---

## 2. 验收用例 (5 + 24 回归 = 29 用例)

### 2.1 V0.4.7 新增 5 用例 (smoke_v047.py) ✅

| 用例 | 操作 | 期望 | 结果 |
|---|---|---|---|
| 1 | admin1 GET /warranties/2 | 200 (admin 创建的) | ✅ |
| 2 | eng_qian GET /warranties/3 | 403 (非自己) | ✅ |
| 3 | eng_qian GET /dashboard/stats | 200 + isFull=false | ✅ |
| 4 | admin1 GET /dashboard/stats | 200 + isFull=true | ✅ |
| 5 | eng_qian GET /warranties/99999 (不存在) | 403 + 友好提示 | ✅ |

**5/5 全过** ✅

### 2.2 V0.4.6 回归 24 用例 (smoke_b_data_scope.py) ✅

| 角色 | 模块 | 结果 |
|---|---|---|
| admin1 | projects 118 / receivables 64 / payables 49 / logs 445 / rects 55 / warr 5 | ✅ |
| fin_wu | 同上 6 模块 | ✅ |
| sales_yang (参与 18) | projects 18 / receivables 15 / payables 15 / logs 122 / rects 0 / warr 0 | ✅ |
| eng_qian (参与 20) | projects 20 / receivables 16 / payables 16 / logs 165 / rects 0 / warr 0 | ✅ |

**24/24 全过** ✅ — 无回归

---

## 3. 技术实现

### 3.1 详情页 404/403 区分 (HandlesDataScope 重写)

**关键改进**：
- `findScoped()` — 第一次带 scope 查 → 找不到 → bypass 再查一次
  - 找到 → 被 scope 拦 → 写审计 → 返回 null
  - 找不到 → 真不存在 → 返回 null
- `respondNotFound()` — admin/finance 一律 404，普通员工 403 + 友好提示

**示例**：
```php
class WarrantyController {
    use HandlesDataScope;

    public function show(Request $request, int $id): JsonResponse
    {
        $w = $this->findScoped($request, Warranty::class, $id);
        return $w
            ? response()->json(['code' => 0, 'data' => $this->service->getWarranty($id)])
            : $this->respondNotFound($request, '质保期', $id);
    }
}
```

### 3.2 审计日志 (DataScope::logDeniedAccess)

**写 system_logs 表**（已存在），新增 `action='data_scope_denied'`：
- 触发时机：`findScoped` 找到 scope 拦的记录
- 字段：user_id / module(=表名) / action / description / ip / user_agent
- 失败不抛异常（审计不影响主流程）

### 3.3 Dashboard 二次校验

- `DashboardController::stats()` — cache key 加 `user_id`（防跨用户污染），加 `isFull` 标志
- `DashboardController::overview()` — cache key 加 `user_id`，加 `is_full_data` 标志
- `InventoryController::batchExport()` — 拦截 `?scope_all=true` + 非 admin/finance → 403

### 3.4 单元测试 (12 用例)

| Test | 用例 |
|---|---|
| **AuthScopeTest** (8 个) | admin/finance/manager/user 角色判定 + null user + isUnrestricted + canViewAll + myProjectsByProjectIdSubquery SQL |
| **DataScopeTest** (4 个) | projects / construction_logs / warranty_service_orders / unknown table 子句 |

**注**：phpunit 测试框架在 117 还没装（composer dev 依赖），本地测试通过；远端靠烟囱补全。

---

## 4. 关键修复

### 4.1 索引缺失列修复
- `WarrantyService::getWarranty` 的 eager load:
  - `customer:id,name,phone` → `customer:id,name` (customers 表无 phone 列)
  - `serviceOrders:id,order_no,status,technician_id,scheduled_at,completed_at` → `scheduled_date,completed_date` (warranty_service_orders 表字段名是 *_date)

### 4.2 Cache 跨用户污染
**根因**：`Cache::remember('dashboard:stats', ...)` 同一 key 给所有用户用
**修法**：`'dashboard:stats:' . $user->id` 按用户分 cache

### 4.3 烟囱与回归的时序坑
**根因**：连续跑 5 个 login 时触发 throttle 限流（429）
**修法**：smoke 脚本 2 次跑之间 sleep 30 秒，或调高 rate limit

---

## 5. 部署清单

| 阶段 | 详情 |
|---|---|
| 后端新增 | 2 个 (test) + WarrantyService 修 + DashboardController 修 |
| 后端修改 | 5 个 (DashboardController / InventoryController / DataScope / HandlesDataScope / WarrantyController) |
| 测试 | 12 个 phpunit 用例 (本地跑通，远端靠烟囱 5 + 24) |
| 重启 | `systemctl restart php8.5-fpm` (清 opcache) |
| 缓存清理 | dashboard:stats 5 分钟过期 + key 加 user_id 自动隔离 |

## 6. 交付清单

### 6.1 代码

| 模块 | 文件 | 类型 |
|---|---|---|
| 详情页处理 | `pc-api/app/Http/Controllers/Api/Concerns/HandlesDataScope.php` | 重写 |
| 审计日志 | `pc-api/app/Scopes/DataScope.php` | 加 `logDeniedAccess()` |
| Dashboard 二次校验 | `pc-api/app/Http/Controllers/Api/DashboardController.php` | 加 isFull + cache key |
| 库存导出 | `pc-api/app/Http/Controllers/Api/InventoryController.php` | 加 scope_all 校验 |
| 质保详情 | `pc-api/app/Http/Controllers/Api/WarrantyController.php` | 用 trait |
| 索引修复 | `pc-api/app/Services/WarrantyService.php` | 字段名修复 |
| 单测 | `pc-api/tests/Unit/Scopes/AuthScopeTest.php` | 新增 |
| 单测 | `pc-api/tests/Unit/Scopes/DataScopeTest.php` | 新增 |

### 6.2 脚本

| 脚本 | 用途 |
|---|---|
| `.workbuddy/deploy_117_v047.py` | 后端 5 改 + 2 新 + 1 修 → 117 + restart fpm |
| `.workbuddy/smoke_v047.py` | 5 用例烟囱 (admin/user × detail/stats/notfound) |
| `.workbuddy/smoke_b_data_scope.py` | 24 用例回归 (V0.4.6 不退化) |

### 6.3 文档

- `.workbuddy/RELEASE_NOTES_v0.4.7.md` (本文件)
- `.workbuddy/memory/2026-06-24.md` 当日日志
- `.workbuddy/memory/MEMORY.md` 长期项目笔记 (V0.4.7 收口)

---

## 7. 验收结论

**✅ V0.4.7 安全收口 — 通过验收**

- 新增 5 用例全过 (smoke_v047.py)
- V0.4.6 24 用例回归全过 (无退化)
- 详情页 404/403 区分清晰
- 审计日志生效 (system_logs.action='data_scope_denied')
- Dashboard 二次校验 (isFull 标志)
- Inventory export 二次校验
- 117 部署最新代码 + 清理 opcache

## 8. 后续可优化 (V0.4.7 后)

- Redis 缓存（§9-3）：dashboard overview 5min cache 命中率提高后考虑
- 部门级子管理员（§9-4）：需求明确后加
- phpunit 跑通：composer install --dev 在 117 + 跑 12 用例
- 限流策略：throttle:api 在 117 上调到 100/min，避免烟囱假 401

---

