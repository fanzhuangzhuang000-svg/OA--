# 🔍 OA 项目 API 测试覆盖分析报告

**分析人**: API Tester (API 测试专家)  
**分析日期**: 2026-06-26  
**项目**: 安防运维 OA 系统  
**技术栈**: Laravel 13 (PHP 8.3) + PostgreSQL 15 + Sanctum  
**仓库**: https://github.com/fanzhuangzhuang000-svg/OA--

---

## 📊 一、覆盖率概览

| 指标 | 数值 | 说明 |
|------|------|------|
| **API 路由总数** | 671 | api.php 中定义的 HTTP 端点 |
| **路由前缀模块** | 75 | 独立业务模块 |
| **控制器数** | 73 | app/Http/Controllers/Api/ |
| **现有测试用例** | 102 | 5 Feature + 11 Unit |
| **覆盖端点估算** | ~25 | 仅约 **3.7%** 路由被直接测试 |
| **未覆盖端点** | ~646 | **96.3%** 路由缺少测试 |

### 测试文件清单

| 文件 | 用例数 | 覆盖范围 |
|------|--------|----------|
| `Feature/AuthApiTest.php` | 8 | 登录、认证、数据作用域 |
| `Feature/BootTest.php` | 7 | 模型启动、作用域基础 |
| `Feature/BusinessApiTest.php` | 8 | 质保、仪表盘、施工、审计 |
| `Feature/PermissionMatrixApiTest.php` | 7 | 角色矩阵、字段脱敏 |
| `Feature/UserRoleApiTest.php` | 11 | 用户角色管理、临时角色 |
| `Unit/Auth/*.php` | 43 | 认证分类、作用域、继承、字段脱敏 |
| `Unit/Project/*.php` | 6 | 项目/客户关系 |
| `Unit/Construction/*.php` | 3 | 施工关系 |
| `Unit/Warranty/*.php` | 5 | 质保模型 |

---

## 🚨 二、缺失测试的关键端点 (按优先级排序)

### P0 — 核心业务 CRUD (无任何测试, 影响所有用户)

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **员工管理** `/employees` | 15+ | ❌ 无测试 | 🔴 极高 |
| **考勤管理** `/attendance` | 14 | ❌ 无测试 | 🔴 极高 |
| **客户管理** `/customers` | 18+ | ❌ 无测试 | 🔴 极高 |
| **项目管理** `/projects` | 13 | ❌ 无测试 | 🔴 极高 |
| **售后服务** `/service` | 8 | ❌ 无测试 | 🔴 极高 |
| **报销管理** `/expenses` | 10 | ❌ 无测试 | 🔴 极高 |
| **仪表盘** `/dashboard` | 16 | ❌ 无测试 | 🟡 高 |

### P1 — 财务 & 采购 (敏感数据, 金额相关)

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **财务管理** `/finance` | 22 | ❌ 无测试 | 🔴 极高 |
| **采购需求** `/purchase/requirements` | 5 | ❌ 无测试 | 🔴 极高 |
| **采购计划** `/purchase/plans` | 7 | ❌ 无测试 | 🔴 极高 |
| **采购合同** `/purchase/contracts` | 7 | ❌ 无测试 | 🔴 极高 |
| **采购付款** `/purchase/payments` | 3 | ❌ 无测试 | 🔴 极高 |
| **采购审批** `/purchase/approvals` | 3 | ❌ 无测试 | 🔴 极高 |
| **供应商管理** `/suppliers` | 8 | ❌ 无测试 | 🟡 高 |
| **总账** `/ledger` | 12 | ❌ 无测试 | 🔴 极高 |

### P2 — 销售全流程 (状态机复杂, 业务关键)

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **线索管理** `/sales/leads` | 7 | ❌ 无测试 | 🟡 高 |
| **商机管理** `/sales/opps` | 15 | ❌ 无测试 | 🔴 极高 |
| **报价单** `/sales/quotes` | 12 | ❌ 无测试 | 🔴 极高 |
| **推荐人** `/sales/referrers` | 5 | ❌ 无测试 | 🟡 中 |
| **项目池** `/sales/pool` | 4 | ❌ 无测试 | 🟡 中 |
| **跟进记录** `/sales/follow-ups` | 8 | ❌ 无测试 | 🟡 高 |
| **推荐人结算** `/sales/referral-settlements` | 4 | ❌ 无测试 | 🟡 高 |
| **产品库** `/sales/products` | 6 | ❌ 无测试 | 🟡 中 |

### P3 — 维修中心 (V0.5.5 新模块, 无测试)

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **维修工单** `/work-orders` | 11 | ❌ 无测试 | 🟡 高 |
| **返修管理** `/repair-orders` | 12 | ❌ 无测试 | 🟡 高 |
| **物流管理** `/repair-orders/{id}/shipments` | 4 | ❌ 无测试 | 🟡 中 |
| **维修方式** `/repair-orders/{id}/methods` | 4 | ❌ 无测试 | 🟡 中 |
| **进度日志** `/repair-orders/{id}/progress-logs` | 3 | ❌ 无测试 | 🟡 中 |
| **过程照片** `/step-photos` | 3 | ❌ 无测试 | 🟡 中 |
| **成本归集** `/repair-cost` | 5 | ❌ 无测试 | 🟡 中 |

### P4 — 系统管理 (权限/配置)

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **排班管理** `/schedules` | 14 | ❌ 无测试 | 🟡 中 |
| **车辆管理** `/vehicles` | 16 | ❌ 无测试 | 🟡 中 |
| **油卡管理** `/fuel-cards` | 6 | ❌ 无测试 | 🟡 低 |
| **库存管理** `/inventory` | 16 | ❌ 无测试 | 🟡 中 |
| **库存分类** `/inventory-categories` | 5 | ❌ 无测试 | 🟡 低 |
| **网盘** `/disk` | 5 | ❌ 无测试 | 🟡 中 |
| **知识库** `/knowledge` | 9 | ❌ 无测试 | 🟡 低 |
| **消息中心** `/notifications` | 4 | ❌ 无测试 | 🟡 低 |
| **数据备份** `/backups` | 4 | ❌ 无测试 | 🟡 中 |
| **审批模板** `/approval-templates` | 6 | ❌ 无测试 | 🟡 中 |
| **审批中心** `/approvals/*` | 13 | ❌ 无测试 | 🟡 高 |
| **数据字典** `/dict` | 7 | ❌ 无测试 | 🟡 低 |
| **系统监控** `/admin/monitor` | 6 | ❌ 无测试 | 🟡 中 |
| **系统设置** `/settings` | 5 | ❌ 无测试 | 🟡 中 |
| **外部报价** `/external-quotes` | 6 | ❌ 无测试 | 🟡 中 |
| **流程管理** `/process` | 24 | ❌ 无测试 | 🟡 高 |

### P5 — 施工管理

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **施工预算** `/construction/budgets` | 7 | ❌ 无测试 | 🟡 中 |
| **施工团队** `/construction/teams` | 6 | ❌ 无测试 | 🟡 中 |
| **开工单** `/construction/commencement-orders` | 6 | ❌ 无测试 | 🟡 中 |
| **施工日志** `/construction/logs` | 6 | ❌ 无测试 | 🟡 中 |
| **整改工单** `/construction/rectifications` | 3 | ❌ 无测试 | 🟡 中 |
| **工序字典** `/construction/work-processes` | 4 | ❌ 无测试 | 🟡 低 |
| **施工发包** `/construction/external-works` | 7 | ❌ 无测试 | 🟡 中 |

### P6 — 质保 & 招标

| 模块 | 端点数 | 状态 | 风险等级 |
|------|--------|------|----------|
| **质保期管理** `/warranties` | 7 | 部分测试 | 🟡 中 |
| **质保工单** `/warranty-service-orders` | 7 | ❌ 无测试 | 🟡 中 |
| **质保保证金** `/warranty-deposits` | 5 | ❌ 无测试 | 🟡 中 |
| **招标中心** `/tenders` | 14 | ❌ 无测试 | 🟡 高 |
| **供应商门户** `/portal` | 5 | ❌ 无测试 | 🟡 中 |

---

## 🔒 三、需要安全测试的端点

### 🔴 高危 — 无权限校验或权限校验不足

| 端点 | 方法 | 风险 | 建议 |
|------|------|------|------|
| `POST /admin/wipe-data` | DELETE | **数据毁灭性操作**, 需验证仅 admin 可调用 | 必须测试 403 拒绝非 admin |
| `POST /backups` | POST | 创建备份可能消耗大量资源 | 验证权限 + 限流 |
| `GET /backups/{filename}/download` | GET | 路径遍历风险 (`../`) | 验证 filename 参数过滤 |
| `GET /admin/monitor/*` | GET | 系统敏感信息泄露 | 验证仅 admin 可访问 |
| `POST /auth/change-password` | POST | 密码修改 — 已有 throttle:5,1 | 验证旧密码校验 |
| `POST /employees/import` | POST | CSV 上传 — 注入风险 | 验证文件类型 + 大小限制 |
| `POST /customers/import` | POST | CSV 上传 — 注入风险 | 验证文件类型 + 大小限制 |
| `POST /inventory/items/batch-import` | POST | 批量导入 — 数据污染 | 验证事务回滚 |

### 🟡 中危 — 需要验证权限边界

| 端点 | 风险 | 测试要点 |
|------|------|----------|
| `PUT/DELETE /employees/{user}` | 越权修改他人信息 | IDOR 测试: 用 user A 的 token 操作 user B |
| `POST /employees/{user}/reset-password` | 越权重置他人密码 | 验证 admin-only |
| `POST /expenses/{claim}/approve` | 审批越权 | 验证审批人角色校验 |
| `POST /expenses/{claim}/pay` | 财务操作越权 | 验证财务角色校验 |
| `POST /purchase/approvals/{appr}/decide` | 采购审批越权 | 验证审批链校验 |
| `POST /finance/receivables` | 创建应收 | 验证 finance.create 权限 |
| `POST /roles/{role}/permissions` | 权限分配 | 验证 system.role 权限 |
| `PUT /users/{user}/roles` | 角色同步 | 验证 admin-only, 防止提权 |
| `DELETE /roles/{role}` | 删除角色 | 验证级联影响 |

### 🟡 限流测试

| 端点 | 当时限流 | 测试建议 |
|------|----------|----------|
| `POST /auth/login` | 30/min + LoginThrottle | 验证 30 次后 429, 5 次失败锁 30 分钟 |
| `POST /auth/change-password` | 5/min | 验证限流生效 |
| `GET /portal/repair` | 10/min | 验证公开查询限流 |
| `POST /portal/t/{token}/bids` | 无 | ⚠️ **缺少限流** — 建议添加 |
| 所有写入端点 | 无 | ⚠️ 建议全局 API 限流 |

### 🔓 公开端点安全

| 端点 | 风险 | 测试要点 |
|------|------|----------|
| `GET /health` | 信息泄露 | 验证不暴露敏感环境变量 |
| `GET /portal/repair` | 枚举攻击 | 验证双因子校验 |
| `GET /portal/t/{token}` | Token 猜测 | 验证 token 熵值足够, 过期机制 |
| `POST /portal/t/{token}/bids` | 伪造投标 | 验证 token 一次性/过期机制 |

---

## ⚡ 四、需要性能测试的端点

### 🔴 高负载端点 (聚合查询/报表)

| 端点 | 预期瓶颈 | 测试建议 |
|------|----------|----------|
| `GET /dashboard/stats` | 多表 JOIN, 聚合 | P95 < 500ms, 100 并发 |
| `GET /dashboard/screen` | 大屏数据聚合 | P95 < 1000ms |
| `GET /dashboard/widget/*` (5 个) | 复杂统计 | P95 < 800ms |
| `GET /finance/overview` | 财务汇总 | P95 < 500ms |
| `GET /finance/summary/aging` | 账龄分析 | P95 < 800ms |
| `GET /finance/summary/cashflow` | 现金流分析 | P95 < 800ms |
| `GET /repair-cost/overview` | 成本归集 | P95 < 500ms |
| `GET /ledger/aging` | 账龄报表 | P95 < 800ms |
| `GET /purchase/*/stats` (6 个) | 各模块统计 | P95 < 500ms |
| `GET /customers/map` | 地图数据 | P95 < 1000ms |

### 🟡 中等负载端点 (列表分页)

| 端点 | 测试建议 |
|------|----------|
| `GET /employees` | 1000+ 员工时 P95 < 300ms |
| `GET /customers` | 10000+ 客户时 P95 < 300ms |
| `GET /projects` | 带作用域过滤性能 |
| `GET /inventory` | 带分类树过滤性能 |
| `GET /sales/opps` | 商机列表 + 漏斗统计 |
| `GET /audit-logs` | 大量日志分页性能 |

### 🟡 批量操作性能

| 端点 | 测试建议 |
|------|----------|
| `POST /inventory/batch-delete` | 100 条批量删除 < 5s |
| `POST /inventory/batch-update` | 100 条批量更新 < 5s |
| `POST /employees/import` | 500 行 CSV < 10s |
| `POST /schedules/` (batch-save) | 批量排班 < 3s |

---

## 🧪 五、测试策略建议

### 1. 分层测试金字塔

```
         /  E2E (5%)  \          ← 关键业务流程端到端
        / Integration (25%) \    ← API 契约 + 状态机
       /    Unit (70%)        \  ← 模型/服务/中间件
```

### 2. 优先级排序 — 推荐执行顺序

#### 第一阶段: 核心安全 (1-2 周)
```
1. 认证/授权测试 — 验证所有 auth:sanctum 端点拒绝未认证请求
2. 权限矩阵测试 — 验证 permission middleware 在所有端点生效
3. IDOR 测试 — 验证 owns middleware 防止越权
4. 公开端点安全 — /health, /portal, /portal/repair
5. admin/wipe-data 权限验证
```

#### 第二阶段: 核心业务 (2-3 周)
```
1. 员工 CRUD + 部门/岗位
2. 客户 CRUD + 联系人 + 跟进
3. 项目 CRUD + 阶段流转
4. 财务 CRUD + 审批流
5. 采购全流程 (需求→计划→合同→付款→发货)
```

#### 第三阶段: 状态机测试 (1-2 周)
```
1. 销售漏斗: 线索→商机→报价→成交/丢单
2. 维修中心: 工单→分配→开始→解决→关闭
3. 返修管理: 创建→发货→维修→回寄→关闭
4. 审批流程: 提交→审批→通过/拒绝/转发
5. 采购计划: 草稿→提交→审批→执行
```

#### 第四阶段: 边界 & 性能 (1 周)
```
1. 大数据量分页性能
2. 聚合查询性能
3. 批量操作性能
4. 限流验证
5. 并发安全 (乐观锁/悲观锁)
```

### 3. 测试工具建议

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Pest** (Laravel 推荐) | Feature/Unit 测试 | P0 |
| **Postman/Newman** | API 集成测试 + CI | P1 |
| **k6 / Artillery** | 性能测试 | P2 |
| **OWASP ZAP** | 安全扫描 | P2 |

### 4. 测试数据工厂

建议为每个模型创建 Factory:
- `UserFactory` (含 admin/manager/finance/user 角色)
- `CustomerFactory` (含联系人、发票信息)
- `ProjectFactory` (含各阶段数据)
- `SalesLeadFactory` / `SalesOppFactory` / `SalesQuoteFactory`
- `PurchaseRequirementFactory` / `PurchasePlanFactory`
- `RepairOrderFactory` / `WorkOrderFactory`

### 5. 每个端点的标准测试矩阵

每个 API 端点至少需要以下测试:

```
✅ 200 — 正常请求成功
✅ 201 — 创建资源成功
✅ 401 — 未认证拒绝
✅ 403 — 无权限拒绝
✅ 404 — 资源不存在
✅ 422 — 验证失败 (缺少必填字段/格式错误)
✅ IDOR — 越权访问他人数据
✅ 分页 — 参数校验 (page/limit/sort)
✅ 过滤 — 搜索参数校验
```

---

## 📈 六、测试覆盖目标

| 阶段 | 目标覆盖率 | 用例数估算 | 时间 |
|------|------------|------------|------|
| 当前 | ~3.7% | 102 | — |
| 第一阶段 | 20% | ~350 | 2 周 |
| 第二阶段 | 50% | ~900 | 5 周 |
| 第三阶段 | 75% | ~1400 | 8 周 |
| 第四阶段 | 90%+ | ~1800 | 10 周 |

---

## ⚠️ 七、关键风险总结

| # | 风险 | 影响 | 建议 |
|---|------|------|------|
| 1 | **96.3% 路由无测试** | 回归风险极高 | 立即开始安全测试 |
| 2 | **财务模块无测试** | 金额错误/越权 | P0 优先覆盖 |
| 3 | **审批流程无测试** | 流程绕过 | 状态机测试必须 |
| 4 | **文件上传无测试** | 恶意文件注入 | 验证文件类型/大小/内容 |
| 5 | **`admin/wipe-data` 无测试** | 数据毁灭 | 首个安全测试目标 |
| 6 | **portal 公开端点无限流** | 暴力枚举 | 添加 throttle middleware |
| 7 | **采购全流程无端到端测试** | 业务流程断裂 | 集成测试覆盖 |
| 8 | **无 CI/CD 测试集成** | 手动测试遗漏 | 接入 GitHub Actions |

---

## 📝 八、快速启动: 建议立即添加的测试

### 1. 安全冒烟测试 (20 个用例, 覆盖所有端点类型)

```php
// tests/Feature/SecuritySmokeTest.php
// 验证所有 auth:sanctum 端点拒绝未认证请求
// 验证 permission middleware 在关键端点生效
// 验证 admin/wipe-data 仅 admin 可调用
// 验证 file upload 拒绝非法文件类型
```

### 2. 核心 CRUD 测试 (50 个用例)

```php
// tests/Feature/EmployeeApiTest.php
// tests/Feature/CustomerApiTest.php
// tests/Feature/ProjectApiTest.php
// tests/Feature/FinanceApiTest.php
// tests/Feature/PurchaseApiTest.php
```

### 3. 状态机测试 (30 个用例)

```php
// tests/Feature/SalesPipelineTest.php
// tests/Feature/RepairWorkflowTest.php
// tests/Feature/ApprovalWorkflowTest.php
```

---

*报告生成: API Tester Agent | 2026-06-26*
