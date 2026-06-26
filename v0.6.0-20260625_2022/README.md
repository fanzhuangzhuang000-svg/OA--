# 安防运维OA系统

> PC Web 端 + Laravel API 端综合 OA 办公系统，配套设计大纲 V2.0。

## 技术栈

- **前端**: Vue3 + Element Plus + TypeScript + Vite + Pinia
- **后端**: Laravel 13 (PHP 8.3) + **PostgreSQL 15** + Sanctum Token
- **进度**: v0.3.10 — 15 模块 / 35 业务表 / 101 Vue 页面 / 42 Controller，总完成度 ~80%
- **最近更新**: 2026-06-23 — 拖拽看板状态机根治 / 全栈代码质量清理
- **Release Notes**: [`.workbuddy/memory/RELEASE_NOTES_v0.3.10.md`](.workbuddy/memory/RELEASE_NOTES_v0.3.10.md)

## 仓库结构

```
D:\work\website\OA\
├── pc-api/                       # Laravel 13 后端
├── pc-web/                       # Vue3 + Element Plus 前端
├── pc-desktop/                   # Electron 客户端（规划中）
├── mobile-app/                   # Flutter 移动端（规划中）
├── mp-miniapp/                   # 微信小程序（规划中）
├── deploy/                       # 统一部署入口
├── 安防运维OA系统设计大纲V2.html  # 系统设计大纲
├── README.md                     # 本文件
└── .workbuddy/                   # AI 工作区（不入 git）
    ├── memory/                   # 工作记忆 + 决策日志
    ├── deploy_*.py               # 推送 / 备份 / 监控脚本
    ├── backups/                  # 版本快照
    └── staging/                  # 运维手册 / 告警 / 灾备
```

## 快速开始

### 本地前端
```bash
cd pc-web
npm install
npm run dev      # http://localhost:3000
```

### 本地后端
```bash
cd pc-api
composer install
cp .env.example .env       # 改 DB 凭据
php artisan key:generate
php artisan migrate --seed
php artisan serve          # http://localhost:8000
```

### 一键部署到服务器
```bash
# 统一入口（推荐）
python deploy/deploy.py web          # 仅前端
python deploy/deploy.py api          # 仅后端
python deploy/deploy.py full         # 全栈
python deploy/deploy.py status       # 服务器状态
python deploy/deploy.py health       # 健康检查
python deploy/deploy.py backup v0.3.7.8

# 底层脚本（.workbuddy/）
python .workbuddy/deploy_to_172.py   # 172 全量（补 artisan/Provider）
python .workbuddy/deploy_web.py      # 前端 dist 推送
python .workbuddy/backup_full.py     # 全量快照
```

## 部署目标

| 服务 | 路径 | 端口 |
|---|---|---|
| Nginx (前端 + API 反代) | `/etc/nginx/sites-available/oa-web.conf` | 80 |
| Laravel API + PHP-FPM | `/var/www/oa-api` | 80（经 nginx）|
| PostgreSQL 15 | `oa_db` / `oa_user` | 5432 |

| 服务器 | 角色 | 账户 | 推送方式 |
|---|---|---|---|
| 172.20.0.139 | **测试** (默认推送) | `nbcy / admin123` | 自动 |
| 152.136.115.121 | **展示** (手动确认) | `ubuntu / Aa782997781.` | 手动 |

> **部署链**: `本地改 → vite build → sftp put /tmp → sudo cp → sudo chown www-data → restart php-fpm`
>
> ⚠️ `reload` 不清 opcache，新代码必须 `restart`。172 走密码认证。

## 关键路径速查

- **后端控制器**: `pc-api/app/Http/Controllers/Api/`
- **Model**: `pc-api/app/Models/{CoreModels,ProjectModels,ServiceModels,OtherModels,User}.php`
- **路由**: `pc-api/routes/api.php`
- **Migration**: `pc-api/database/migrations/`
- **前端 API**: `pc-web/src/api/{user,modules,dashboard}.ts`
- **前端页面**: `pc-web/src/views/{attendance,customer,project,service,vehicle,...}/`
- **运维手册**: `.workbuddy/staging/OPS-RUNBOOK.md`
- **监控脚本**: `oa-monitor-v2.sh`（服务器 cron）

## 文档

- **设计大纲**: `安防运维OA系统设计大纲V2.html`
- **核心记忆**: `.workbuddy/memory/MEMORY.md`（项目级决策 + 踩坑）
- **工作日志**: `.workbuddy/memory/2026-06-*.md`（daily log）
- **系统速查**: `.workbuddy/memory/SYSTEM_OVERVIEW.md`（路由/Controller/Model/前端 API 速查）
- **代码质量报告**: `.workbuddy/memory/CODE_SMELL_REPORT.md`（死代码/冗余/复制粘贴）
- **备份清单**: `.workbuddy/backups/v0.3.*/MANIFEST.md`

## UI 配色

| 用途 | 颜色 |
|---|---|
| 主色 | `#0C447C` |
| 辅色 | `#1D9E75` |
| 警告 | `#BA7517` |
| 危险 | `#A32D2D` |
| 信息 | `#534AB7` |
