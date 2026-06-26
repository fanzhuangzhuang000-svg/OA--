# MEMORY.md - 安防运维OA项目

> 核心决策 + 踩坑。日常进展看 `memory/YYYY-MM-DD.md`。
> **当前版本**: V0.5.8.9 (2026-06-25 19:50) — **客户开票信息 (新表 customer_invoice_infos + 4 REST + 多条 CRUD) + 联系人 (同版早段)**
> **Git tags**: v0.5.8 → ... → V0.5.8.8 (资金对账 + 6 真 BUG + 152 清理) → V0.5.8.9 (客户联系人 + 开票信息)
> **E2E**: e2e_v0583_full_flow 60/60 + UI round2 19/19 + 入职 wizard 3 步 0 错 + e2e_v0588_fund_business 45/45 + 108 路由 click_through 全过 + _verify_add_contact 6 步 0 错 + _verify_invoice_info 11 步 0 错
> **账号统一**: 117 + 152 双机 `admin / admin123` (admin1 已改名)
> **🚦 部署主从策略 (2026-06-25 15:35 拍板)**: 后续测试 **以 117 为准**，152 未经授权不许推送更新。
>   - 117 = 主测试机（首选部署目标，E2E 验证默认走 117）
>   - 152 = 展示机（oa.afjsw.cn 域名）— 只接收用户明确授权的部署
>   - deploy_152.py / deploy_117.py 默认 117，152 需显式 `--target=152` 或 `?授权=是` 才推
> **下一里程碑**: V0.5.9 商机/报价/合同深度联动 / 慢查询优化 / seed 随机密码 / C 新业务
> **下一里程碑**: B2 生产准备 (HTTPS+备份+域名) / 授权系统 / C 新业务 / E 收工

## 项目管理 vs 施工管理 业务边界 (C 方案 2026-06-24 拍板)
- **项目管理** `/project/*` 管「钱/合同/质保」: list/board/calendar/gantt + **warranty/* 8 个**
- **施工管理** `/construction/*` 管「事/现场/工序」: team/commencement/log/rectification + work-process + external-work + **process/* 4 个**
- 业务闭环: 商机 → 合同(项目) → 开工单(施工) → 工序(施工) → 验收(施工) → 质保(项目) → 回款
- 项目详情页有"施工进度"tab 用 `?project_id=xxx` query 跨页跳到工序实例/验收记录

## B 数据权限 (V0.4.6)
- **3 件套**: `HasDataScope` (trait) / `DataScope` (GlobalScope) / `AuthScope` (角色判定 + subquery)
- **角色** (username 前缀, users.type 全部 'staff'):
  - admin* → admin (全量)
  - fin_* → finance (全量)
  - sales_*/tech_mgr/proj_mgr/sales_mgr → manager (自己创建 + 自己参与)
  - 其他 → user (自己创建 + 自己参与)
- **9 Model 注册 scope** (traited): Project, PurchaseOrder, ConstructionLog, CustomerReceivable, Rectification, Warranty, WarrantyServiceOrder, WarrantyDeposit, Receivable, Payable
- **关键坑**: `receivables` ≠ `customer_receivables` (不同表, FinanceController 用的 Receivable)
- **关键坑**: warranty 表 scope 要用 EXISTS + 外层表名 `%s.project_id` 占位 (不能用 `projects.id` alias)
> **117 新服务器**: 192.168.3.117 (Ubuntu 26.04 + PHP 8.5.4 + PG 18.4) — 172 已关停
> **重大决策**: 版本号从 V0.4.1 起启用 V0.x 大版本（V0.4.x = 项目实操全链路，V1.0 = 正式发布）
> **预算超支规则**: 90% 软提示 + 100% 硬阻断（V0.4.1 大哥拍板）

## 项目
- 路径 `D:\work\website\OA` ｜ 大纲 `安防运维OA系统设计大纲V2.html`
- 后端 `pc-api/` Laravel 13 (PHP 8.3) + **PostgreSQL 15** + Sanctum
- 前端 `pc-web/` Vue3 + Element Plus + TS + Vite + Pinia
- 进度 v0.3.16: 15 模块 / 37 表 / 101 Vue 页面 / 43 Controller, ~87%
  - v0.3.12 → v0.3.13: 销售模块拆（Opps/Leads/Quotes）→ 7 dialog + 3 types
  - v0.3.13 → v0.3.14: process/employee + dashboard/customer/gantt/inventory 4 大文件拆 + 业务补齐 + 数据权限 + 152 灰度
  - 累计组件化: **47 子组件 + 9 共享 types + 1 composable**
  - **v0.3.14 三波组件化**：project 10 + sales 7 + process 4 + employee 3 + dashboard 8 + customer 6 + gantt 4 + inventory 4 + sales 增强 4

## 部署（🚦 117 当前默认，152 停用）
| 服务 | 账户 | 端口 |
|---|---|---|
| 192.168.3.117 测试 | `nbcy/admin123` | oa-api 8081 + oa-web 80 |
| ~~172.20.0.139~~ | 已关停 (2026-06-24) | - |
| ~~152.136.115.121~~ | 已停用 | - |

路径 `/var/www/oa-{api,web}`, PHP 8.5-fpm + nginx 1.28 + PG 18.4
链: `本地改 → vite build → sftp put /tmp → sudo cp → sudo chown → restart php-fpm`
**`reload` 不清 opcache，新代码必须 `restart`** (V0.4.4 验证)
**117 oa-api 8081** (default_server) 避免 IP:80 server_name 冲突
**nginx 必须 `fastcgi_pass unix:/run/php/php8.5-fpm.sock`** — proxy_pass unix 502

### 172 已关停（2026-06-24 09:30）
- 117 已全量接替 172 (DB + 代码 + 部署脚本)
- 172 备份在 `/var/www/oa-backup-final/` + `/tmp/oa-full-2026-06-24.sql.gz`
- 172 关机命令 `sudo shutdown -h now`（已执行，ping 失败确认）
- ~~`www.afjsw.cn`~~ → 已停用(续期证书只含 `oa.afjsw.cn`)
- 80 → 301 → https(仅 `oa.afjsw.cn`),IP 仍走 80
- 证书路径: `/etc/nginx/ssl/oa.afjsw.cn/` (key 600, crt 644)
- 旧证书备份: `/etc/nginx/ssl/afjsw.cn.bak.YYYYMMDD_HHMMSS/`
- 站点配置: `oa` 接域名(80+443), `oa-api` 仅接 IP 80
- 部署脚本: `deploy/deploy_https_152.py`(首次)/ `deploy/renew_cert_152.py`(续期)
- **v0.3.14 起**：用 `.workbuddy/deploy_152.py` 灰度推送（增量 + NOPASSWD sudo + 分步 rc 校验）

## 核心脚本（`.workbuddy/`）
- `deploy_to_172.py` — 172 全量（补 artisan/Provider + drop check + grant）⚠️ v0.3.15 必修：默认跑 composer install 或加 --no-clear
- `deploy_web.py` / `deploy_web_v2.py` — 前端 dist 推送
- `deploy_api.py` / `deploy_with_tar.py` — 后端推送
- `deploy_152.py` — **v0.3.14 新增** 152 灰度专用（增量推送 + sudo -n + rc 校验）
- `deploy_117.py` — **v0.4.2 新增** 117 全量（PHP 8.5 + PG 18 + Ubuntu 26.04，8 阶段）
- `upload_web_117.py` — **v0.4.2 新增** 117 前端 dist 推送
- `smoke_117_v2.py` — **v0.4.2 新增** 117 25 API 烟囱测试
- `backup_full.py` — 快照 → `backups/vX.Y.Z/`
- `oa-monitor-v2.sh` — 服务器监控（cron）

## 调度任务
- `oa:expire-quotations` — 每日 01:00 过期报价单（v0.3.11）
- `oa:remind-overdue-settlements` — **v0.3.14 新增** 每日 09:00 推荐人结算 7 天逾期提醒（24h 频控，level: warning/danger）
- `oa:sync-actual-costs` — **v0.4.1 新增** 每日 02:00 兜底同步项目实际成本
- `oa:seed-admin` / `oa:seed-roles` / `oa:seed-finance` — 账号 seed（v0.3.14 新增 finance / sales_manager 角色）

## 踩坑

### Laravel 11+ 部署时手写补（本地缺）
`artisan` / `public/index.php` / `app/Http/Controllers/Controller.php`
`app/Providers/{App,Auth,Event,Route}ServiceProvider.php` / `routes/console.php`
`composer install --no-dev --no-security-blocking`
业务表 ~57 个 check 约束需 drop

### Laravel 11 + 6 个 PKSA 安全公告（2026 composer 默认 block）
**修法**：composer install 加 `--no-security-blocking`（2026 composer 2.10+ 改了语义，`--no-audit` 已不存在）

### .env 中文字符串 f-string 转义（v0.4.2 117 部署踩过）
**现象**：`APP_NAME="\u5b89\u9632\u8fd0\u7ef4OA"` dotenv 不识别
**修**：直接写 `APP_NAME=OA` 或用 base64 + sudo tee 写文件

### Nginx proxy_pass unix socket 502（v0.4.2 117 部署踩过）
**现象**：`proxy_pass http://unix:/run/php/php-fpm.sock` → "Connection reset by peer" 502
**修**：用 `fastcgi_pass unix:/run/php/php-fpm.sock` + `include snippets/fastcgi-php.conf`（fastcgi 协议不是 http）

### nginx 两个 server 同一 IP listen 80 冲突
**修**：oa-api 站点改 `listen 8081 default_server; server_name _;` + oa 站点 `/api/` 用 `proxy_pass http://127.0.0.1:8081`

### PHP 8.5 兼容性
- composer.json `"php": "^8.2"` 不含 8.5 → 改 `"php": ">=8.2"`（或 `"php": "^8.4"`）
- Laravel 11 在 8.5 上**实测可用**（v0.4.2 117 端 composer 装到 107 包全过）
- PSR-4 模型分散 CoreModels/ServiceModels/ProjectModels/OtherModels 老结构**有 warning 但不影响**

### 路由顺序（踩过 3 次）
`Route::get('{vehicle}', ...)` 通配**必须**放子路由 (`/insurances` `/maintenances` `/fuel-cards`) 之后，否则 PG 22P02 `invalid input syntax for type bigint`
`bootstrap/app.php` 已加 22P02 全局兜底 → 404 友好

### 表名自动复数化（踩过 2 次）
`VehicleInsurance` 默认找复数表 → 42P01。**显式 `protected $table = 'xxx'`**

### 烟囱测试假 401（v0.3.7.8 踩过）
**根因**：smoke 脚本用本地缓存的 `routes_raw.txt` 跑端点，但 172 路由已演进（`backups/{id}` → `backups/{filename}`、`auth/me` 新增别名等），导致 562 个 401 假象
**修**：`load_routes()` 改为实时 `php artisan route:list` 拉（用 paramiko 走 SSH）→ 假 401 全消失

### admin 密码 hash 不匹配（v0.3.7.8 踩过）
装库时 admin 密码 hash 跟 `admin123` 不对应 → `Hash::check` BAD → login 401
**修**：服务器上 `php -r` 或 tinker 重置：`$u = User::find(1); $u->password = Hash::make('admin123'); $u->save();`
**测**：`Hash::check('admin123', $u->fresh()->password) ? 'OK' : 'BAD'`

### PG 序列滞后导致 23505（v0.3.7.8 踩过）
session A 大量 INSERT 走的是非 Laravel 通道（直接 SQL），sequence 没跟上
**修**：跑 `fix_seq.sql`：DO 块遍历所有 `id` 字段表，`SELECT setval(seq_name, MAX(id), true)`

### service_orders.urgency 枚举冲突（v0.3.7.8 踩过）
DB 有 `low/high/normal`，enum `App\Enums\Urgency` 用 `normal/urgent/critical` → `ValueError: low is not a valid backing value`
**修**：`UPDATE service_orders SET urgency='urgent' WHERE urgency='low'; UPDATE ... SET 'critical' WHERE 'high';`

### 新表后手动 GRANT
```sql
GRANT ALL PRIVILEGES ON TABLE xxx TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE xxx_id_seq TO oa_user;
```

### Controller 必须注册到 `routes/api.php` 顶部 `use { }`
漏了: `Target class [XxxController] does not exist`

### 前端分页解包（防重犯）
后端 `{code, data: {current_page, data, total}}` → 拦截器解包后 `res = {current_page, data, total}`（**不是** array）
```js
const d = res; list.value = d.data || []; total.value = d.total || 0  // ✅
// const d = res.data || res  ❌ d 变 array, d.total undefined
// 拦截器已解包，res.code === 0 永远 false
```

### Vue 3 props / template ref 同名冲突 (V0.5.8.7 踩过)
**现象**: 子组件 `<el-form ref="form1Ref">` + 父级 `:form1-ref="formStep1Ref"` → el-form 注册被 prop 覆盖
**修法**:
- 子组件内模板 ref 用 elForm1Ref 命名 (不和 prop 重)
- 子组件内部 onNextClick 调 validate (拿得到本地 el-form ref)
- 父级 ref 想拿子组件 form, 必须 defineExpose
**扫雷**: `re.findall(r'\b([A-Za-z]\w*Ref)\s*[:?]', props_block)` ∩ `ref="xxx"` → clash

### SFTP 部署权限
`/var/www/*` 是 www-data，nbcy 无写权。流程: `/tmp/` → `sudo cp` → `sudo chown www-data`

### 线索 leads.status 7段脏数据 (v0.3.10 踩过)
**现象**: 看板拖动「跟进中→合格」报错 `状态机非法流转：contacted → qualified`
**根因**: 历史脏数据 + 后端只对 `{$new}` 归一，没对 `{$current}` 归一
**修**:
1. 后端 `SalesController::leadsUpdateStatus` 加 `boardMap[$lead->status] ?? $lead->status` 防御
2. SQL 清洗: `contacted→contacting, proposal/negotiating→qualified, won→converted, lost→discarded`
3. 重启 php-fpm 清 opcache (虽然 revalidate_freq=2)
**警惕**: `OppsBoard.vue` 7段列 vs DB 6段 同样可能踩

### v-model on prop 编译错误（v0.3.14 EmployeeDialog 踩过）
**现象**: Vue 3 不允许 `v-model` 直接绑 prop → TS 编译失败
**修**: 子组件内部维护副本（`localSkillIds`），对外只 emit 最终值

### notifications 表 title/content 必填（v0.3.14 B2 踩过）
**现象**: `$user->notify($notif)` 报 `null value in column "title"`
**根因**: 项目定制 schema 多了 title/content 顶级列（Laravel 默认只填 data JSON）
**修**: 不用 Notifiable trait 默认行为，改用 `DatabaseNotification::create([...])` 直接 Eloquent 写

### 152 deploy 深层目录静默失败（v0.3.14 B1 踩过）
**现象**: deploy 日志显示 `✓ app/Notifications/...` 但实际未上传
**根因**: `mkdir -p` + `&&` 链 + `echo=False` 吞掉 stderr
**修**: 分步执行 + rc 校验 + 显式 `sudo -n`

### 172 .env 权限事故（v0.3.16 P0 → 已修复）
**现象**: 172 API 全部 500，`Access denied for user 'forge'@'localhost' (using password: NO) (Connection: mysql)`
**根因**: deploy_to_172.py Step 4 写 .env 后只设 0600，www-data 读不到 → Laravel fallback `env('DB_CONNECTION', 'mysql')` → 默认 user `forge` 不存在
**修**: Step 4 末尾加 `chmod 644 + chown www-data:www-data`
**避**: 完整部署后**必须** `curl POST /api/auth/login` 验证 200

### 117 .env 覆盖事故（v0.4.10 P0 → 已修复）
**现象**: 117 API 500，`Target class [request] does not exist` + `could not find driver (Connection: mysql)`
**根因**: rsync `--exclude=.env` 因 zsh 引号实际未生效，117 上 V0.4.2 手写的 pgsql+redis .env 被覆盖成默认 mysql 模板
- 错误链：cache 表查 mysql → container request 服务找不到 → 容器 boot 失败
**修**:
1. 完整 .env 模板: APP_NAME=OA / DB_CONNECTION=pgsql / DB_DATABASE=security_oa / DB_USERNAME=oa_user / DB_PASSWORD=oa_pg_pwd_782997781 / CACHE_STORE=redis / REDIS_CLIENT=phpredis / REDIS_CACHE_DB=1
2. base64 编码上传（避免 shell 转义吞换行）
3. `rm -rf bootstrap/cache/* && chown www-data bootstrap/cache && php artisan package:discover`
4. `systemctl restart php8.5-fpm && nginx` 清 opcache
**避**:
- **deploy_117.py 必须** `cp .env .env.bak.$(date +%s)` 先备份
- rsync exclude 单独一行，不靠 `&&` 链
- 部署完 `curl /api/auth/login` 验 200 是底线

### artisan test vs vendor/bin/phpunit（v0.4.10 117 跑测踩过）
**现象**: `php artisan test` 在 117 报 `Target class [request] does not exist`
**修**: 直接用 `vendor/bin/phpunit --testsuite=Unit` 跑，不走 Application Kernel boot
**原因**: artisan test 触发 Container 完整 boot，opcache 缓存 + manifest 损坏时会爆；phpunit 直接走 phpunit.xml bootstrap 更轻

### stock_records 迁移幂等性（v0.3.17 必修）
**现象**: v0.3.14 完整部署时 `2026_06_21_130000_add_party_fields_to_stock_records` 跑过，列已存在
**修**: migration 加 `if (!Schema::hasColumn('stock_records', 'party_type'))` 保护
**v0.3.17 必修**

### 172 storage/logs/laravel.log 权限（v0.3.16 排查踩过）
**现象**: 错误时 log 完全空白，浪费时间排查
**根因**: log 文件 nbcy:nbcy 600，www-data 写不进去
**修**: 完整部署后 `sudo chown -R www-data:www-data /var/www/oa-api/storage/logs/`

### Laravel 11+ 部署时手写补
**现象**: `deploy_to_172.py --skip-migrate --skip-seed --skip-web` 跑完 → 172 API 全 500
**根因**: 脚本默认 `rm -rf {REMOTE_API}/*` 但不跑 composer install = 全挂
**修**: 用 `oa-api.bak.1782209613` 完整恢复 + 单独重推 console.php
**v0.3.15 已修**: 引入 `--no-clear` (不清空 REMOTE_API) + `--skip-composer` 2 个新 flag，错误信息分级

### Model $fillable 漏字段 = 静默 23502（V0.4.4 必踩）
**现象**: Eloquent create() 没把字段写入 SQL，但 DB not null 约束报错
**根因**: 字段不在 `$fillable` 数组里 → Mass Assignment 静默丢弃
**修**: 每次新字段必加 `$fillable` + `$casts`
**例**: ProjectCommencementOrder 漏 `commencement_date` → 开工单 POST 全 23502

### Model 关系 hasMany 走错列 = 静默 42703（V0.4.4 必踩）
**现象**: 关联预加载报 `column X does not exist`
**根因**: V0.4.3 设计时假定的列实际不存在
**例**: `processes(): hasMany(WorkProcess, 'commencement_order_id')` 但 work_processes 表无此列
**修**: 改 hasManyThrough 或去掉关联预加载

### V0.4.3 错读 schema (V0.4.4 必踩)
- construction_teams 表**无** `remark` 字段
- project_commencement_orders `commencement_date`（不是 planned_start_date）
- construction_logs 表**无** `commencement_order_id` 字段（走 rectification_daily_required 中转）
- external_construction_works 表**无** `description/budget_amount`（用 work_scope/estimated_budget）
- rectification_daily_required 是 `is_required`（不是 is_rectification）
- rectification_daily_required 唯一键 `[project_id, work_date]`（不是 commencement_order_id）

### 117 composer install 必加 `--no-security-blocking`（V0.4.4 验证）
- Laravel 11 有 6 个 PKSA 公告，不加会卡住
- `--no-audit` 2026 已废弃（--no-clear 模式下 composer 失败不阻塞）

### element-plus icons 命名（v0.3.14 B3 踩过）
**现象**: `CirclePlus/CircleMinus` import 报不存在
**根因**: `@element-plus/icons-vue` 实际命名是 `Plus/Minus`
**修**: 用通用名 `Plus/Minus`

### created_at 为 null 导致 overdue_days=0（v0.3.14 B2 踩过）
**现象**: 注入 10 天前 settlement 但 overdue_days=0
**根因**: PG `referral_settlements.created_at` 默认 null + Carbon diffInDays 行为不一致
**修**: 显式 `->abs()` + `now()->diffInDays($ts, true)` + fallback

## 详见 `memory/2026-06-23.md` 的清理日志
路径速查 / 项目跟踪 / 颜色 / 进度等细节 → 历史 daily log
