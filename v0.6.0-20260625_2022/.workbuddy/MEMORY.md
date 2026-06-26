# MEMORY.md - 安防运维OA项目 (2026-06-24)

> 核心决策 + 踩坑。日常进展看 `memory/YYYY-MM-DD.md` 和 `memory/2026-06-24-v057-*.md`。

## 当前版本
**V0.5.7 块4 完工 (2026-06-24 20:00) — 维修成本归集 (4维度 + dashboard widget + 财务报表)**
**累计**: 101 临时角色用例 / 烟囱 19/19 / e2e 286+58 (含块4 新) / 全绿

## V0.5.7 块4 关键点
- **RepairCostStat 服务** — 5 方法 (overview/byMonth/byProject/byCustomer/byMethod), 状态过滤 completed/closed/shipped_back
- **5 端点** `/api/repair-cost/*` (要 token)
- **Dashboard 扩展** maintenance-stats 加 5 cost 字段 (this_month_total / warranty / paid / total_contract / cost_ratio_pct)
- **财务报表** `/finance/repair-cost` (4 Tab: 月度/项目/客户/方式)
- **关键 schema 坑**: `projects` 表没 `contract_amount` 也没 `code`, 用 `budget_*` 字段合计 + `project_no`

## V0.5.7 块3 关键点
- **PortalRepairController** 公开端点 (无需 token), `code + phone_suffix` 双因子
- 公开页 `/portal/repair` 移动友好 (渐变背景 + 卡片)
- 客户名脱敏 "张**", 内部字段 (total_cost 等) 不暴露
- throttle 10/min 防暴力枚举

## 117 服务器
- `192.168.3.117` (Ubuntu 26.04 + PHP 8.5-fpm + PG 18.4 + nginx 1.28)
- oa-api 8081 (default_server) + oa-web 80
- 路径 `/var/www/oa-{api,web}`
- 部署链: `本地改 → vite build → sftp put /tmp → sudo cp → sudo chown www-data → restart php-fpm`
- **新坑 (V0.5.7 块4)**: `scp + sudo cp` 在 117 上首次不可靠 (md5 不一致), 必须强制 `sudo cp /tmp/X /var/www/...` + `md5sum` 校验
- **`reload` 不清 opcache**, 新代码必须 `restart`
- nginx 必须 `fastcgi_pass unix:/run/php/php8.5-fpm.sock`

## 核心踩坑
- **`projects` 表字段**: `id/project_no/name/customer_id/type/stage/status/.../budget_device/budget_material/budget_labor/budget_outsource/budget_other/...` — **没有 `code`, 没有 `contract_amount`**
- **`repair-orders` POST 自动改 code**: `nextCode()` 强制覆盖外部 code, e2e 必须用响应里的 code
- **throttle 累计**: 跨测试会触发 429, 跨测试间 sleep 65s 或用唯一参数
- **Customer 列名**: `customers` 表用 `name` + `contact_phone` (无 `phone` 无 `contact_phone` 历史)
- **scp + sudo cp 不可靠**: 必须 `md5sum` 校验, 不一致就 `sudo -n cp` 强制覆盖

## 项目
- 路径 `D:\work\website\OA` ｜ 大纲 `安防运维OA系统设计大纲V2.html`
- 后端 `pc-api/` Laravel 13 (PHP 8.3) + **PostgreSQL 15** + Sanctum
- 前端 `pc-web/` Vue3 + Element Plus + TS + Vite + Pinia
- 进度 v0.5.7 块4: 15 模块 + 1 新财务子模块 / 101+ Vue 页面 / 50+ Controller

## V0.5.7 6 块计划
- [x] 块1: 工单/项目/工序 互锁 (14 e2e)
- [x] 块2: 全过程照片 7 步 (15 e2e)
- [x] 块3: 客户端公开查询 (37 e2e)
- [x] 块4: 维修成本归集 (58 e2e) ✓
- [ ] 块5: Dashboard 多维度 (估 0.5)
- [ ] 块6: PWA 初步 (估 0.5)
