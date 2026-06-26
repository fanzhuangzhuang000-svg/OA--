# Release Notes — v0.3.16 (2026-06-23)

> **类型**: 组件化深推 + 部署脚本加固
> **核心**: FollowCalendar 拆分 + deploy_to_172.py .env 权限 bug 修复（生产事故）
> **范围**: 5 个新子组件 + 1 个部署脚本加固

---

## 🎯 改动总览

| 指标 | v0.3.15 | v0.3.16 | 备注 |
|---|---|---|---|
| 前端子组件 | 42 | **47** | +5 (FollowCalendar 拆分) |
| 部署脚本 | 4 | 4 | +0 (同一脚本加固) |
| 部署安全 flag | 2 | 2 | 不变 |
| 部署 bug 修复 | 0 | **1** | **.env 权限导致 172 500 事故** |
| 备份 | v0.3.15-20260623_1956 | v0.3.16-20260623_2020 | 30MB |

---

## 🎨 P1 — 客户模块组件化

### FollowCalendar.vue (675 → 240, **-64%**)
- 抽 5 个子组件 + 1 个 types：
  - `FollowKpiCards.vue` (134) — 4 张 KPI 卡（总跟进/已完成/计划中/逾期）
  - `FollowFilterBar.vue` (62) — 顶部筛选条（月份/跟进人/客户）
  - `FollowCalendarGrid.vue` (180) — 6x7 网格日历 + 任务条 + 月切换
  - `FollowUpcomingList.vue` (108) — 未来 7 天待办列表
  - `FollowDayDrawer.vue` (107) — 抽屉详情（点击某天/某条跟进）
- 父组件 `FollowCalendar.vue` (240) — orchestration + 工具函数
- 共享 `CalCell` interface 从 `FollowCalendarGrid.vue` export

### 关键设计点
1. **emit 驱动模式** — FilterBar/Grid/List/Drawer 全部用 `emit('update:xxx')` + 父级 `v-model:filterMonth`
2. **函数 prop 传递** — `formatTime/countdownLabel/eventColor` 等通过 prop 传入子组件，**不重复定义**
3. **pure CSS 日历** — 不引第三方 calendar 库，纯 grid + 状态 class 实现 6x7 网格
4. **响应式 grid** — 1200px 以下，cal-main + cal-side 切换为单列
5. **drawer 双向绑定** — `v-model:visible` 让父级用 ref 控制 + 子组件 emit 关闭

### ✅ 验证
- `vite build` 10.28s 通过
- 部署 172 + 验证 login + /api/follow-ups/calendar 全 200

---

## 🛠️ P0 — deploy_to_172.py .env 权限 bug 修复

### 背景
本次 v0.3.16 部署 → 172 API 全部 500。
排查链路：
1. ✅ vendor 完整 (autoload.php OK)
2. ✅ schedule:list 跑通
3. ❌ login 报 `Access denied for user 'forge'@'localhost' (using password: NO) (Connection: mysql)`

**根因**：`deploy_to_172.py` Step 4 写入 `.env` 后只设置 0600 权限（`sftp_put_text` 默认），没 `chmod 644` + `chown www-data:www-data`。
→ `www-data` (fpm worker) 读不到 `.env`
→ Laravel `env('DB_CONNECTION', 'mysql')` fallback 到默认 `mysql`
→ 默认 user `forge` 不存在 + 无密码 → 1045 Access denied

### 修复
在 `deploy_to_172.py` Step 4 末尾加：
```python
run(ssh, f'sudo chmod 644 {REMOTE_API}/.env && sudo chown www-data:www-data {REMOTE_API}/.env', label='chmod .env')
```

### 修复后验证
- `.env` 600 → 644, owner `www-data:www-data`
- `sudo systemctl restart php8.3-fpm`
- `POST /api/auth/login` → 200, token: `1234|ND3ybaqICnPeKlE2fwqC4hWov...`

### 影响
- 172 全恢复，业务可继续
- 152 不受影响（152 走 deploy_152.py 不一样流程）

---

## 🐛 排查过程中踩过的坑

### 1. log 权限
`storage/logs/laravel.log` 也是 nbcy:nbcy 600 → www-data 写不了 → 错误被吞
**修**：`sudo chown -R www-data:www-data /var/www/oa-api/storage/logs/`

### 2. duplicate column 假象
v0.3.14 完整部署时 `2026_06_21_130000_add_party_fields_to_stock_records` 跑过，列已存在
**修**：手工 `INSERT INTO migrations VALUES (..., batch=1000)` 跳过

### 3. CACHE_DRIVER=redis vs cache=database
.env 写 `CACHE_DRIVER=redis` 但 Laravel 12 改用 `CACHE_STORE`，**fallback 到 database 缓存**
+ DB 又走默认 mysql → 双重失败
**修**：.env 改回 `CACHE_DRIVER=file` + `SESSION_DRIVER=file` (保持 172 一致)

### 4. bootstrap/cache 缓存
- `config:clear` 清了，但 `cache:clear` 自己走 cache 又失败
**修**：直接删 `bootstrap/cache/*.php` 重建

---

## 📁 关键文件

| 文件 | 改动 | 说明 |
|---|---|---|
| `pc-web/src/views/customer/FollowCalendar.vue` | 重写 675 → 240 | 5 子组件 + orchestration |
| `pc-web/src/views/customer/components/FollowKpiCards.vue` | 新建 134 | KPI 4 卡 |
| `pc-web/src/views/customer/components/FollowFilterBar.vue` | 新建 62 | 筛选条 |
| `pc-web/src/views/customer/components/FollowCalendarGrid.vue` | 新建 180 | 6x7 网格 |
| `pc-web/src/views/customer/components/FollowUpcomingList.vue` | 新建 108 | 7 天待办 |
| `pc-web/src/views/customer/components/FollowDayDrawer.vue` | 新建 107 | 详情抽屉 |
| `.workbuddy/deploy_to_172.py` | +3 行 | Step 4 加 chmod 644 + chown www-data |

---

## ✅ 验证清单

| 项 | 状态 | 备注 |
|---|---|---|
| FollowCalendar 拆 5 子组件 | ✅ | -64% 行数 |
| vite build | ✅ | 10.28s |
| 172 deploy | ✅ | 242 files nginx reload |
| 172 login 恢复 | ✅ | 200 + token |
| /api/follow-ups/calendar | ✅ | 200 |
| /api/customers | ✅ | 200 |
| .env 权限 bug 修复 | ✅ | chmod 644 + chown www-data |
| 备份 v0.3.16-20260623_2020 | ✅ | 30MB |

---

## 🚀 下一站 v0.3.17 候选

| 优先级 | 项 | 工作量 | 价值 |
|---|---|---|---|
| P0 | **修 stock_records 迁移幂等性** (`Schema::hasColumn` 保护) | 30min | 防止下次全量部署再 500 |
| P1 | 客户模块继续拆：Detail 21KB / CustomerMap 19KB / Pipeline 18KB / Health 15KB | 5-6h | 与 v0.3.12-16 节奏一致 |
| P1 | process/InstanceList 712 拆 | 2-3h | 工序实例列表 |
| P1 | dashboard 营收图接 ECharts | 1-2h | 原生 CSS 太简陋 |
| P2 | Knowledge / Incoming 拆分 | 2-3h | 知识库/来访 |
| P2 | customer 模块子组件加 loading 骨架屏 | 1h | 与 Quotes.vue 对齐 |
| P3 | 152 在 2026-09-21 证书续期前提前预演 | 10min | 避免生产事故 |
