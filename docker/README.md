# Docker 开发环境

## 快速开始

```bash
# 1. 复制环境变量模板
cp .env.docker .env

# 2. 启动所有服务
docker compose up -d

# 3. 安装 PHP 依赖（首次启动时）
docker compose exec app composer install

# 4. 生成应用密钥
docker compose exec app php artisan key:generate

# 5. 运行数据库迁移和种子
docker compose exec app php artisan migrate --seed

# 6. 安装前端依赖并启动开发服务器
docker compose run --service-ports node npm run dev -- --host 0.0.0.0
```

## 服务说明

| 服务 | 说明 | 端口 | 访问地址 |
|------|------|------|----------|
| **nginx** | Web 服务器 | 80 | http://localhost |
| **app** | PHP-FPM (Laravel) | 9000 | - |
| **postgres** | PostgreSQL 15 | 5432 | - |
| **redis** | Redis 缓存 | 6379 | - |
| **node** | Vite 开发服务器 | 3000/5173 | http://localhost:3000 |

## 常用命令

```bash
# 查看所有服务状态
docker compose ps

# 查看日志
docker compose logs -f          # 所有服务
docker compose logs -f app      # 仅 PHP
docker compose logs -f nginx    # 仅 Nginx

# 进入 PHP 容器
docker compose exec app bash

# 进入 Node 容器
docker compose exec node sh

# 运行 Laravel 命令
docker compose exec app php artisan migrate
docker compose exec app php artisan tinker
docker compose exec app php artisan test

# 运行前端构建
docker compose run --rm node npm run build

# 停止所有服务
docker compose down

# 停止并删除数据卷（重置数据库）
docker compose down -v
```

## 目录结构

```
OA-综合管理平台/
├── docker-compose.yml      # Docker 编排配置
├── Dockerfile.php          # PHP 8.3 FPM 镜像
├── Dockerfile.node         # Node.js 构建镜像
├── .env.docker             # 环境变量模板
├── nginx/
│   └── default.conf        # Nginx 配置
├── pc-api/                 # Laravel API (挂载到 PHP 容器)
└── pc-web/                 # Vue3 前端 (挂载到 Node 容器)
```

## 开发流程

### 仅前端开发
```bash
docker compose up -d postgres redis app nginx
cd pc-web && npm install && npm run dev
```

### 仅后端开发
```bash
docker compose up -d postgres redis app nginx
# 前端访问: http://localhost (使用生产构建)
```

### 全栈开发
```bash
docker compose up -d
docker compose run --service-ports node npm run dev -- --host 0.0.0.0
# 前端: http://localhost:3000 (Vite HMR)
# API:  http://localhost/api
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_DATABASE` | 数据库名 | oa_security |
| `DB_USERNAME` | 数据库用户 | oa_user |
| `DB_PASSWORD` | 数据库密码 | oa_secret_2024 |
| `DB_PORT_EXTERNAL` | 宿主机数据库端口 | 5432 |
| `VITE_API_PROXY` | Vite API 代理目标 | http://nginx |

## 故障排除

### 数据库连接失败
```bash
# 检查 PostgreSQL 是否就绪
docker compose exec postgres pg_isready

# 查看数据库日志
docker compose logs postgres
```

### PHP 扩展缺失
```bash
# 查看已安装的扩展
docker compose exec app php -m

# 重新构建镜像
docker compose build --no-cache app
```

### 权限问题
```bash
# 修复 Laravel 存储目录权限
docker compose exec app chmod -R 775 storage bootstrap/cache
```
