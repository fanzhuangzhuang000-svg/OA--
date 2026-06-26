# Release Notes — v0.3.11 (2026-06-23) ✅ 完结

> **里程碑**: 销售前链路 P0 安全 + 推荐人结算完整闭环 + 报价单产品库 + 附件安全
> **部署**: 172 默认推送 ✅ / 152 手动待发布
> **类型**: 6 块 P1 业务逻辑全量交付

## 🎯 核心成果（4 块 P0 安全 + 2 块产品功能）

### ✅ 块一 销售核心流转（跨用户鉴权 + owner 隔离）
1. **跨用户 403 鉴权中间件** — `CheckResourceOwnership` 挂在 25+ 路由
2. **6 个列表 owner 隔离** — leadsIndex / oppsIndex / quotesIndex / referrersIndex / poolIndex / followUpsIndex 全部加 `$query->where('owner_id', $user->id)`
3. **admin/manager 角色旁路** — `hasRole('admin')` / `hasRole('manager')` 走特殊逻辑
4. **referrers 表补 owner_id 字段** — ALTER TABLE + UPDATE 补齐
5. **验证**: `verify_403_v4.py` 4/4 模块全过；`verify_owner_isolation.py` 8/8 通过

### ✅ 块二 看板校验（v0.3.10 已实现，v0.3.11 验证）
- LeadsBoard 7→5 状态机归一
- oppsMarkWon 事务回滚（建 ProjectPool + ReferralSettlement 原子性）

### ✅ 块三 战败复活 + 转施工事务
1. **oppsRevive 端点** — `POST /sales/opps/{id}/revive`（sales_manager / admin 角色）
2. **前端 Opps.vue** — lost 阶段显示"战败复活"按钮，隐藏"编辑/报价"
3. **oppsMarkWon 事务** — DB::transaction 包裹，失败回滚建 ProjectPool + 自动建 settlement

### ✅ 块四 报价单产品库（前端大幅重写 + 后端补全）
1. **migration `add_product_id_to_quotation_items`** — 加 product_id / code 字段
2. **Model `QuotationItem` fillable 扩展** — product_id / discount_rate / tax_rate
3. **`quotesStoreItems` 端点补全**:
   - product_id 验证 + 重复检测 422
   - discount_rate 上限 30% 422
   - tax_rate 枚举验证 422
   - submitted 状态不可改 409
4. **报价单过期定时任务** — `oa:expire-quotations` 命令 + Laravel 11 schedule（每日 01:00）
5. **`bootstrap/app.php` 调度注册** — `->withSchedule()` + 引用 console
6. **前端 `Quotes.vue` 大重写**（234 → 657 行）:
   - 产品库选择 dialog（搜索 + 分类过滤 + 多选 + 重复检测）
   - items 行编辑（增删改 + watch 重算 total）
   - 折扣/税率/有效期表单
   - 7 天过期提醒
   - submitted 状态只读
7. **验证**: `verify_quote_items.py` 6/6 通过

### ✅ 块五 跟进附件安全（11 项缺口全补）
1. **后端** — `followUpsUploadAttachment / DownloadAttachment / DeleteAttachment` 三端点 + 中间件
2. **`salesfollowupattachment` 中间件** — 走 follow_up_id 关联校验跨用户 403
3. **PHP 上传配置** — `99-upload.ini` (upload_max_filesize=64M, post_max_size=64M, memory_limit=256M)
4. **NGINX 配置** — `client_max_body_size 64M`
5. **附件安全验证** — 8/8 通过:
   - 上传 txt / 下载 / 跨用户 403（下载/删除）
   - .exe 拒 422 / 11MB 单文件拒 422 / 50MB 总额拒
   - Content-Disposition 头正确

### ✅ 块六 推荐人居间费结算（11 项从 0 到 1 跑通）
1. **migration `referral_settlements`** — 完整字段：opportunity_id/referrer_id/amount/commission_rate/contract_amount/status/approved_by/approved_at/paid_by/paid_at/payment_voucher/payment_no
2. **唯一约束 (opportunity_id, referrer_id)** — 同一商机不重复
3. **Model `ReferralSettlement`** — 6 个关系
4. **oppsMarkWon 触发自动建 pending 结算** — 事务内 firstOrCreate
5. **5 个 Controller 端点**（全部跑通）:
   - GET 列表（分页+过滤+权限隔离）
   - GET stats（pending/approved/paid 计数+金额）
   - GET 详情
   - POST approve（pending→approved）
   - POST pay（approved→paid，**自动累加 referrer.total_commission**）
6. **前端 `Settlements.vue`** — 4 统计卡 + 表格 + 审核/发放 + 详情
7. **验证**: `verify_settlement_v2.py` 8/8 通过（100000×4.20%=4200.00 精确计算）

## 📊 6 块推进总账

| 块 | 状态 | 验证 | 工时 |
|---|---|---|---|
| 块一 跨用户鉴权 | ✅ | 4/4 + 8/8 | ~6h |
| 块二 看板校验 | ✅ | v0.3.10 已通过 | - |
| 块三 战败复活 | ✅ | 1/1 | ~2h |
| 块四 报价单产品库 | ✅ | 6/6 | ~8h |
| 块五 附件安全 | ✅ | 8/8 | ~6h |
| 块六 推荐人结算 | ✅ | 8/8 | ~6h |
| **合计** | **6/6** | **35/35** | **~28h** |

## 🛠️ 关键文件

### 后端新增
- `app/Http/Middleware/CheckResourceOwnership.php` — 跨用户 403 中间件
- `app/Models/ProjectModels.php` — ReferralSettlement Model（追加）
- `database/migrations/2026_06_23_150000_create_referral_settlements_table.php`
- `database/migrations/2026_06_23_160000_add_product_id_to_quotation_items.php`

### 后端修改
- `app/Http/Controllers/Api/SalesController.php` — +300 行（owns 中间件、oppsRevive、oppsMarkWon 事务、5 个 settlement 端点）
- `bootstrap/app.php` — owns alias + withSchedule 注册
- `routes/api.php` — 25+ `->middleware('owns:*')` + 5 settlement 路由 + console schedule
- `routes/console.php` — `oa:expire-quotations` 命令

### 前端新增
- `pc-web/src/views/sales/Settlements.vue` — 结算页面
- `pc-web/src/api/sales.ts` — 5 个 settlement API 追加

### 前端修改
- `pc-web/src/views/sales/Quotes.vue` — 大重写（234 → 657 行）
- `pc-web/src/views/sales/Opps.vue` — 加 Revive 按钮
- `pc-web/src/router/index.ts` — 加 Settlements 路由
- `pc-web/src/api/sales.ts` — 清 15 个死 alias，保留 28 个活 API
- `pc-web/src/api/user.ts` — 砍到只剩 login
- `pc-web/src/api/employee.ts` — 砍到只剩 getEmployeeList

## 🐛 踩坑集

1. **Spatie model_has_roles 反斜杠错位** — 历史上插入 `App\Models\User` 被转义成 `App\\Models\\User`，已用 `UPDATE ... SET model_type = 'App\Models\User'` 修复
2. **opcache 不会自动清** — 改 PHP 文件后必须 `sudo systemctl restart php8.3-fpm`
3. **route:list 不显示新路由** — 强制重 cp + 重启 php-fpm 才能生效
4. **shell 转义地狱** — 本地写 Python 脚本 → SFTP 上传 → 172 上 `python3 /tmp/xxx.py` 跑
5. **referrers 表缺 owner_id** — `ALTER TABLE referrers ADD COLUMN owner_id BIGINT; UPDATE referrers SET owner_id=1 WHERE owner_id IS NULL;`
6. **oppsRevive 找不到方法** — diff 确认 + 强制 cp + restart php-fpm
7. **oa:expire-quotations 未注册** — Laravel 11+ 需在 `bootstrap/app.php` 用 `->withSchedule()` 注册
8. **admin 角色绑定** — `INSERT INTO model_has_roles SELECT 1, 'App\\Models\\User', u.id FROM users u WHERE u.username = 'admin'`
9. **前端分页解包** — 拦截器解包后 res 直接是 `{current_page, data, total}`，不能再 `res.data || res` 解一层

## 💾 备份

`backups/v0.3.11-20260623_1640/` — 13MB 完整快照（pc-api 240 / pc-web 132 / pc-web-build 733）

## 🚀 后续 (v0.3.12+)

- v0.3.12: 销售/财务数据权限细化
- v0.3.13: 前端组件化（Detail.vue 1716 → 5 tab 子组件）← v0.3.12-rc 已开始
- v0.4: 第三方对接（钉钉/企业微信）
