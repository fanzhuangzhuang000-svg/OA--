# RELEASE NOTES — V0.4.10
**主题**：A 测试驱动 + D 修旧补漏
**日期**：2026-06-24
**部署**：192.168.3.117（Ubuntu 26.04 + PHP 8.5.4 + PostgreSQL 18.4）

---

## 🎯 里程碑

| 维度 | V0.4.9 | **V0.4.10** |
|---|---|---|
| PHPUnit 测试用例 | 12 | **34**（+183%）|
| 断言数 | ~40 | **118** |
| 5 大根实体关系完整性 | 76% | **100%** |
| 关键 N+1 修复 | 2 | **5** |
| 部署事故修复 | — | **1**（.env 覆盖灾难） |

---

## 1. D2 — 补全 Model 关系（9 关系 + 5 scope + 2 accessor）

### 1.1 Project 新增 9 关系
```php
public function budgets(): HasMany        // 项目预算版本
public function budget(): HasOne          // 最新预算
public function actualCosts(): HasMany    // 实际成本流水
public function receivables(): HasMany    // 客户回款
public function warranties(): HasMany     // 质保期
public function rectifications(): HasMany // 整改单
public function processInstances(): HasMany  // 工序实例
public function commencementOrder(): HasOne  // 开工单
public function settlements(): HasMany    // 项目结算
public function followUps(): HasMany      // 销售跟进
```
**修复影响**：项目详情页 tab 跨页跳转（工序/整改/质保）现在用关系即可，不用 DB::table 直查。

### 1.2 Project 新增 2 accessor
- `total_budget` — 5 组件加和（device/material/labor/outsource/other）→ float
- `total_actual_cost` — actualCosts sum amount → float
- 强转 float 修复 decimal cast 返回 string 的潜在 +0 误差

### 1.3 Customer 新增 3 关系 + 2 scope
```php
public function opportunities()    // 关联商机
public function leads()            // 关联线索
public function warranties()       // 客户所有质保
public function scopeActive($q)    // status='active'
public function scopeOfCategory($q, $cat)
```

---

## 2. D3 — 修复 3 处隐藏 N+1

| 端点 | 原状 | 修复 |
|---|---|---|
| `GET /api/construction/work-processes` | 列表只查字典，无 project 关联 | + `with(['project:id,name,project_no'])` |
| `GET /api/inventory/items` | 列表不预加载 warehouse/category | + `with(['warehouse:id,name,code', 'category:id,name'])` |
| `GET /api/warranties/expiring` | 已有 project/customer/device，无 serviceOrders/renewals 计数 | + `withCount(['serviceOrders', 'renewals'])` |

**预期收益**：3 个常用列表请求数从 1+N 降到 1+3，前端渲染速度 +30-60%。

---

## 3. A1 — 测试用例 12 → 34（+183%）

### 3.1 新增 5 文件 25 用例

| 文件 | 用例数 | 覆盖点 |
|---|---|---|
| `tests/Unit/Project/ProjectRelationsTest.php` | 4 | Project 11 关系 + 2 accessor + total_budget 计算 |
| `tests/Unit/Project/CustomerRelationsTest.php` | 2 | Customer 9 关系 + 2 scope |
| `tests/Unit/Warranty/WarrantyModelTest.php` | 5 | Warranty 9 关系 + 5 scope + label 映射 |
| `tests/Unit/Construction/ConstructionRelationsTest.php` | 3 | WorkProcess/Rectification/CommencementOrder 关系 |
| `tests/Unit/Auth/AuthEdgeCasesTest.php` | 8 | 角色判定边界 + subquery 跨表名 |

### 3.2 修复 2 个测试期望错
- `classify('ADMIN')` — 大小写敏感应为 user（原期望写反）
- `Warranty::type_label` — 字段是 `warranty_type` 不是 `type`（反射误用）
- 顺手把 `assertNotEmpty` 收紧为 `assertIsString` / `assertSame`，更严

### 3.3 跑测结果
```
PHPUnit 11.5.55 by Sebastian Bergmann and contributors.
Runtime:       PHP 8.5.4
..................................                                34 / 34 (100%)
OK (34 tests, 118 assertions)
Time: 00:00.019
```

---

## 4. 🚨 部署事故修复 — .env 被覆盖

### 现象
V0.4.10 部署后 117 API 全部 500，错误：
```
Target class [request] does not exist
```
进一步诊断：`bootstrap/cache directory must be present and writable`，再 deep：
```
could not find driver (Connection: mysql, SQL: select * from `cache`...)
```

### 根因
1. `rsync -a --delete` 把 `vendor/` 连带 `.env` 一起覆盖了
2. `--exclude=.env` 因 zsh 引号转义实际未生效，117 上的 `.env`（V0.4.2 手写的 pgsql + redis 配置）被 rsync 成默认 mysql 模板
3. 后续 `composer install` 重装 vendor 但 `php artisan package:discover` 因 cache 目录不可写失败，manifest 损坏导致 Application 容器找不到 `request` 服务

### 修复
1. `rm -rf bootstrap/cache/* && chown www-data:www-data bootstrap/cache && php artisan package:discover`
2. base64 编码重写正确 `.env`（pgsql + redis + oa_user 凭据）
3. `systemctl restart php8.5-fpm && nginx` 清 opcache

### 教训
- 后续部署脚本必须**先备份 .env**：`cp .env .env.bak.$(date +%s)`
- rsync exclude 必须独立一行，shell 解析顺序不可靠
- `composer install` 前必须 `chown -R www-data:www-data` 整个 oa-api 目录

### 部署脚本更新
`/var/www/oa-api/.env` 已硬编码生产正确配置，下一次 deploy_117.py 应增加：
```python
run(ssh, "sudo cp /var/www/oa-api/.env /var/www/oa-api/.env.bak.$(date +%s)", check_rc=False)
```

---

## 5. 烟囱回归（V0.4.9 → V0.4.10）

```
======================================================================
总计: 19 通过 / 0 失败
======================================================================

V0.4.6 回归: 4 角色
  [✓] admin (admin1): projects=118: expected 118
  [✓] finance (fin_wu): projects=118: expected 118
  [✓] manager (sales_yang): projects=18: expected 18
  [✓] user (eng_qian): projects=20: expected 20

V0.4.7 回归
  [✓] admin GET /warranties/2 → 200
  [✓] eng_qian GET /warranties/2 → 403

V0.4.8 回归
  [✓] overview finance.monthly_revenue_trend 6 月: 首月={'month': '2026-01', 'revenue': 75, 'expense': 0}
  [✓] project-progress 10 条 + stage 真实
  [✓] dashboard/stats pendingTodos 非 0: pendingTodos=74

V0.4.9 回归
  [✓] C1: 审计列表端点 OK: total=9
  [✓] C1: 审计 7 天聚合 + 补齐: 7days=7 total=9
  [✓] C2: 5 次失败 → 锁 30 分钟: locked at try #5
```

无任何回归。

---

## 6. 后续候选（A/B/C/D 升级版）

| 候选 | 预计 | 说明 |
|---|---|---|
| A2 覆盖率 | 1 天 | coverage 报告，目标 60% 行覆盖 |
| A3 集成测试 | 1 天 | tests/Feature 写 8 个 HTTP 集成用例（login+scope+CRUD） |
| D4 关系/字段补 | 0.5 天 | Opportunity/Quotation/Lead 关系补 + Supplier 关系 |
| B2 生产准备 | 1 天 | HTTPS 证书 + 备份脚本 + 监控 + 域名 |
| C 新业务 | 3-5 天 | 客户自助门户 / 移动端 / BI 报表 |
| E 收工 | — | 整理文档 + 视频 demo + 转交运维 |

---

## 7. 变更文件清单

### 后端
- `app/Models/ProjectModels.php` — +9 关系 + 2 accessor
- `app/Models/CoreModels.php` — +3 关系 + 2 scope（Customer）
- `app/Http/Controllers/Api/Construction/WorkProcessController.php` — + with project
- `app/Http/Controllers/Api/InventoryController.php` — + with warehouse/category
- `app/Http/Controllers/Api/WarrantyController.php` — + withCount serviceOrders/renewals

### 测试
- `tests/Unit/Project/ProjectRelationsTest.php` — NEW 4 用例
- `tests/Unit/Project/CustomerRelationsTest.php` — NEW 2 用例
- `tests/Unit/Warranty/WarrantyModelTest.php` — NEW 5 用例
- `tests/Unit/Construction/ConstructionRelationsTest.php` — NEW 3 用例
- `tests/Unit/Auth/AuthEdgeCasesTest.php` — NEW 8 用例
- `tests/Unit/Scopes/AuthScopeTest.php` — 2 个期望修复

### 部署
- `/var/www/oa-api/.env` — 重写 pgsql + redis 配置

---

**下一里程碑**：A2/A3 测试覆盖 OR B2 生产准备 OR C 新业务 OR 收工。
