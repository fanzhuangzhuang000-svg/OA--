# OA-综合管理平台

> 安防运维 OA 综合管理系统 — PC Web 端 + Laravel API 端

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue3 + Element Plus + TypeScript + Vite + Pinia |
| **后端** | Laravel 13 (PHP 8.3) + PostgreSQL 15 + Sanctum Token |
| **桌面端** | Electron（规划中） |
| **移动端** | Flutter（规划中） |
| **小程序** | 微信小程序（规划中） |

## 项目进度

- **当前版本**: v0.6.0
- **完成度**: ~80%
- **模块数**: 15 个业务模块
- **数据表**: 35+ 张业务表
- **前端页面**: 101+ 个 Vue 页面
- **后端控制器**: 42+ 个 Controller

## 仓库结构

```
OA-综合管理平台/
├── pc-api/                          # Laravel 13 后端 API
│   ├── app/                         # 应用代码
│   │   ├── Http/Controllers/        # 控制器
│   │   ├── Models/                  # 数据模型
│   │   └── Services/                # 业务服务
│   ├── config/                      # 配置文件
│   ├── database/                    # 数据库迁移和种子
│   ├── routes/                      # 路由定义
│   └── tests/                       # 测试用例
│
├── pc-web/                          # Vue3 + Element Plus 前端
│   ├── src/
│   │   ├── api/                     # API 接口
│   │   ├── components/              # 公共组件
│   │   ├── router/                  # 路由配置
│   │   ├── stores/                  # Pinia 状态管理
│   │   └── views/                   # 页面视图
│   ├── public/                      # 静态资源
│   └── vite.config.ts               # Vite 配置
│
├── pc-desktop/                      # Electron 桌面端（规划中）
├── deploy/                          # 部署脚本
├── docs/                            # 项目文档
│   ├── PRD/                         # 产品需求文档
│   └── *.md                         # 部署指南
│
├── .gitignore                       # Git 忽略规则
├── MANIFEST.md                      # 项目清单
├── README.md                        # 本文件
└── 安防运维OA系统设计大纲V2.html     # 系统设计大纲
```

## 快速开始

### 前端开发

```bash
cd pc-web
npm install
npm run dev              # 启动开发服务器 → http://localhost:3000
```

### 后端开发

```bash
cd pc-api
composer install
cp .env.example .env     # 配置数据库连接
php artisan key:generate
php artisan migrate --seed
php artisan serve        # 启动开发服务器 → http://localhost:8000
```

### 构建生产版本

```bash
# 前端构建
cd pc-web
npm run build

# 后端优化
cd pc-api
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

## 部署

### 部署脚本

```bash
python deploy/deploy.py web          # 仅前端
python deploy/deploy.py api          # 仅后端
python deploy/deploy.py full         # 全栈部署
python deploy/deploy.py status       # 查看服务器状态
python deploy/deploy.py health       # 健康检查
```

### 部署目标

| 服务 | 说明 | 端口 |
|------|------|------|
| Nginx | 前端静态文件 + API 反向代理 | 80/443 |
| Laravel API | PHP-FPM 进程 | 80 (经 Nginx) |
| PostgreSQL 15 | 数据库 | 5432 |

## 核心模块

| 模块 | 说明 |
|------|------|
| 📊 仪表盘 | 系统概览、数据统计 |
| 👥 客户管理 | 客户信息、联系人、跟进记录 |
| 📁 项目管理 | 项目创建、任务分配、进度跟踪 |
| 🔧 维修服务 | 工单管理、维修记录、配件管理 |
| 📦 库存管理 | 物资出入库、库存盘点 |
| 💰 财务管理 | 应收应付、费用报销 |
| 🚗 车辆管理 | 车辆调度、保险、保养 |
| 📋 采购管理 | 采购申请、合同、物流 |
| 🏢 人事管理 | 员工信息、组织架构、考勤 |
| 📝 流程审批 | 自定义流程、审批记录 |
| 📚 知识库 | 文档管理、知识分享 |
| ⚙️ 系统设置 | 权限管理、角色配置 |

## 关键路径

```
后端控制器:  pc-api/app/Http/Controllers/Api/
数据模型:    pc-api/app/Models/
路由定义:    pc-api/routes/api.php
数据库迁移:  pc-api/database/migrations/
前端 API:    pc-web/src/api/
前端页面:    pc-web/src/views/
```

## UI 配色

| 用途 | 颜色 | 预览 |
|------|------|------|
| 主色 | `#0C447C` | 🔵 |
| 辅色 | `#1D9E75` | 🟢 |
| 警告 | `#BA7517` | 🟡 |
| 危险 | `#A32D2D` | 🔴 |
| 信息 | `#534AB7` | 🟣 |

## 文档

- 📄 [系统设计大纲](安防运维OA系统设计大纲V2.html)
- 📄 [部署指南](docs/production-deployment-guide.md)
- 📄 [产品需求文档](docs/PRD/)

## 许可证

私有项目，未经授权禁止使用。

---

**最后更新**: 2026-06-26
**版本**: v0.6.0
