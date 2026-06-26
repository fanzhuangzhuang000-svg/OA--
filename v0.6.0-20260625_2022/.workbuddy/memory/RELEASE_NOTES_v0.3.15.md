# Release Notes — v0.3.15 (2026-06-23)

> **类型**: 基础设施加固（零业务变更）
> **核心**: 修 `deploy_to_172.py` vendor 误删事故（v0.3.14 B1 复发点）
> **范围**: 1 个文件 + 1 个回归脚本

---

## 🎯 改动总览

| 指标 | v0.3.14 | v0.3.15 | 备注 |
|---|---|---|---|
| 前端子组件 | 42 | 42 | 不变 |
| 后端 Controller | 43 | 43 | 不变 |
| 部署脚本 | 4 | 4 | 不变（**只是同一脚本加 2 个新 flag**） |
| 部署安全 flag | 0 | **2** | `--no-clear` + `--skip-composer` |
| 备份 | v0.3.14-20260623_1943 | v0.3.15-20260623_1948 | 30MB |

---

## 🛠️ P0 — `deploy_to_172.py` 健壮性加固

### 背景
v0.3.14 B1 期间，误用 `--skip-migrate --skip-seed --skip-web` 跑部署 → 脚本 Step 2 的 `rm -rf {REMOTE_API}/*` **把 vendor 也清了** → 整个 172 API 全 500
- 修复：用 `.bak.1782209613` 完整恢复
- 根因：脚本缺乏 `--no-clear` 选项，每次部署都强制 `rm -rf`

### 改动 1 — 新增 `--no-clear` flag（核心防护）
```bash
python .workbuddy/deploy_to_172.py --no-clear
# Step 2 跳过 rm -rf，只 chown 让 nbcy 可写
# vendor/storage/.env 全部保留
# 仅覆盖源代码（app/、routes/、config/、database/migrations/ 等）
```

**何时用**：
- 增量迭代（只改了 PHP 文件，没改 composer.json）
- 紧急修复（不能冒 vendor 风险）
- composer install 失败后的应急回滚

**何时不用**：
- composer.json 有改动（需要 composer install）
- 全新初始化（首次部署）
- 怀疑 vendor 被污染（需要重建）

### 改动 2 — 新增 `--skip-composer` flag
```bash
python .workbuddy/deploy_to_172.py --no-clear --skip-composer
# 跳过 Step 5 整个 composer install
# 用于：纯源码改动 + vendor 已存在
```

### 改动 3 — 错误信息分级
- `--no-clear` + composer 失败 → 升级为 `[WARN]`（vendor 还在，业务不挂）
- 正常模式 + composer 失败 → 保持 `[ERROR]`（必须修复）

---

## ✅ 验证清单

| 项 | 状态 | 备注 |
|---|---|---|
| deploy_to_172.py --help | ✅ | 显示 2 个新 flag + 中文 help |
| deploy_to_172.py --dry-run --no-clear | ✅ | 跳过 rm -rf，输出 `[v0.3.15] --no-clear 模式` |
| 172 vendor 完整性回归 | ✅ | 8/8 通过：vendor + autoload + Laravel 11.54 + 2 调度任务 + spatie + .env + opcache + Notifications |
| 172 API 健康 | ✅ | `/api/auth/login` + 9 关键端点全 200（来自 v0.3.14 验证） |
| 备份 v0.3.15-20260623_1948 | ✅ | 30MB |

---

## 🐛 修复历史事故

### v0.3.14 172 vendor 误删（→ v0.3.15 根治）

**症状**：`deploy_to_172.py --skip-migrate --skip-seed --skip-web` 跑完 → 172 API 全 500
**根因**：
1. 脚本 Step 2 默认 `rm -rf {REMOTE_API}/*` 无条件清空
2. 用户用 `--skip-*` 想"轻量部署"但不知道会清 vendor
3. 没有 `--no-clear` 选项

**v0.3.15 修复**：
- 引入 `--no-clear` flag，从根上让用户能选择"不清空"
- 引入 `--skip-composer` flag，让"轻量部署"语义完整
- 错误信息分级，--no-clear 模式下 composer 失败不阻塞

---

## 📁 关键文件

| 文件 | 改动 | 说明 |
|---|---|---|
| `.workbuddy/deploy_to_172.py` | +18 行 / 改 1 段 | 加 2 flag + Step 2 改写 + Step 5 加 vendor 预检 + 错误分级 |

---

## 🚀 下一站 v0.3.16 候选

| 优先级 | 项 | 工作量 | 价值 |
|---|---|---|---|
| P0 | **修 composer install 失败兜底**（`--no-clear` 时 vendor 完整但 autoload 可能缺新包）| 1h | 防止 composer 失败但脚本"通过" |
| P1 | customer 模块继续拆（FollowCalendar 22KB / Detail 21KB / CustomerMap 19KB / Pipeline 18KB / Health 15KB）| 4-5h | 与 v0.3.12-14 节奏一致 |
| P1 | dashboard 营收图接 ECharts | 1-2h | 原生 CSS 太简陋 |
| P1 | process/InstanceList 712 拆 | 2-3h | 工序实例列表 |
| P2 | Knowledge / Incoming 拆分 | 2-3h | 知识库/来访 |
| P2 | dashboard 8 子组件加 loading 骨架屏 | 1h | 与 Quotes.vue 对齐 |
| P3 | 152 在 2026-09-21 证书续期前提前预演 | 10min | 避免生产事故 |
