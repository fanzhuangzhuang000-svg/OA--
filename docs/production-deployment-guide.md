# OA 安防运维系统 — 生产环境部署文档

> **版本**: v1.0.0  
> **日期**: 2026-06-22  
> **适用服务器**: 172.20.0.139 (测试/演示环境), 152.136.115.121 (生产环境)  
> **作者**: Senior Developer (高级开发工程师)

---

## 📋 目录

1. [服务器信息](#1-服务器信息)
2. [生产环境准备清单](#2-生产环境准备清单)
3. [安全配置](#3-安全配置)
4. [Nginx 配置](#4-nginx-配置)
5. [数据库配置](#5-数据库配置)
6. [部署流程](#6-部署流程)
7. [备份策略](#7-备份策略)
8. [监控与告警](#8-监控与告警)
9. [故障排查](#9-故障排查)
10. [上线检查清单](#10-上线检查清单)

---

## 1. 服务器信息

### 1.1 服务器列表

| 用途 | IP 地址 | SSH 凭据 | 部署路径 | 说明 |
|------|---------|---------|---------|------|
| **测试平台** | 172.20.0.139 | 见 `.env.deploy` | `/var/www/oa-api` | 默认推送目标 |
| **展示平台** | 152.136.115.121 | 见 `.env.deploy` | `/var/www/oa-api` | 手动确认后推送 |

> ⚠️ **重要**: SSH 凭据已从代码中移除，请使用 `deploy/.env.deploy` 配置文件或环境变量。

### 1.2 服务架构

```
[客户端] 
    ↓ HTTP/HTTPS (80/443)
[Nginx] (反向代理)
    ↓ FastCGI
[PHP 8.3-FPM] (Unix Socket: /run/php/php8.3-fpm.sock)
    ↓ PDO
[PostgreSQL 15] (端口 5432)
```

### 1.3 目录结构

```
/var/www/oa-api/                  # Laravel API 后端
├── app/
├── bootstrap/
├── database/
│   └── migrations/              # 数据库迁移文件
├── public/
│   └── index.php                # HTTP 入口
├── storage/
│   └── logs/
│       └── laravel.log          # 应用日志（调试必看）
├── .env                         # 环境配置（不入库）
└── artisan                      # Laravel 命令行工具

/var/www/oa-web/                  # Vue 3 前端（build 后 dist/）
├── index.html
├── assets/
└── .htaccess                    # SPA fallback 规则
```

---

## 2. 生产环境准备清单

### 2.1 关键安全项（上线前必须完成）

| # | 检查项 | 当前状态 | 操作命令 |
|---|---------|---------|---------|
| 1 | `APP_ENV=production` | ✅ 已完成 | `grep APP_ENV /var/www/oa-api/.env` |
| 2 | `APP_DEBUG=false` | ✅ 已完成 | `grep APP_DEBUG /var/www/oa-api/.env` |
| 3 | **修改 admin 默认密码** | ❌ 未完成 | 见 [3.1 修改默认密码](#31-修改默认密码) |
| 4 | **生成 JWT_SECRET** | ❌ 未完成 | 见 [3.2 配置 JWT](#32-配置-jwt-secret) |
| 5 | **配置 HTTPS** | ❌ 未完成 | 见 [4.2 HTTPS 配置](#42-https-配置) |
| 6 | **配置 Nginx 80/443** | ❌ 未完成 | 见 [4.1 生产级 Nginx 配置](#41-生产级-nginx-配置) |
| 7 | **配置数据库自动备份** | ❌ 未完成 | 见 [7.1 数据库备份](#71-数据库备份) |
| 8 | 配置日志切割 | ❌ 未完成 | 见 [7.2 日志切割](#72-日志切割) |

### 2.2 性能优化项

| # | 检查项 | 当前状态 | 建议值 |
|---|---------|---------|---------|
| 1 | `opcache.memory_consumption` | 128MB | → 256MB |
| 2 | `opcache.validate_timestamps` | 未设置 | → `0`（生产环境） |
| 3 | `PM.max_children` | 未优化 | → `50`（根据内存调整） |
| 4 | Nginx gzip 压缩 | 未开启 | → 开启 |

---

## 3. 安全配置

### 3.1 修改默认密码

> ⚠️ **高危**：当前 `admin` 密码仍是 `admin123`，任何人都能登录！

#### 方案 A：通过 API 修改（推荐）

```bash
# 1. 先登录获取 token
TOKEN=$(curl -s -X POST http://172.20.0.139:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 2. 修改密码
curl -X POST http://172.20.0.139:3001/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"admin123","new_password":"新强密码(至少12位)"}'
```

#### 方案 B：直接修改数据库（紧急）

```bash
sudo -u postgres psql -d security_oa -c "
UPDATE users 
SET password = crypt('新强密码', gen_salt('bf', 10)) 
WHERE username='admin';
"
```

#### 方案 C：通过部署脚本批量修改

```python
# 见 deploy_change_password.py（如需我帮你写）
```

---

### 3.2 配置 JWT Secret

```bash
# 登录服务器
ssh nbcy@172.20.0.139

# 生成 JWT secret（会自动写入 .env）
cd /var/www/oa-api
sudo -u www-data php artisan jwt:secret --force

# 验证
grep JWT_SECRET /var/www/oa-api/.env
# 应输出：JWT_SECRET=base64:xxxxx（长字符串）
```

> 📌 如果 `jwt:secret` 命令不存在，手动生成：
> ```bash
> openssl rand -base64 32  # 复制输出，手动写入 .env 的 JWT_SECRET
> ```

---

### 3.3 配置 CORS（跨域访问）

如果前端和 API 不同域，需配置 CORS：

```php
// 文件：/var/www/oa-api/config/cors.php
return [
    'paths' => ['api/*', 'sanctum/csrf-cookie'],
    'allowed_methods' => ['*'],
    'allowed_origins' => [
        'https://your-domain.com',      // 生产域名
        'http://localhost:5173',       // 开发环境（可保留）
    ],
    'allowed_headers' => ['*'],
    'exposed_headers' => [],
    'max_age' => 0,
    'supports_credentials' => true,
];
```

---

### 3.4 配置 API 限流（防恶意请求）

```php
// 文件：/var/www/oa-api/routes/api.php
// 在所有路由前加限流中间件

Route::middleware(['throttle:60,1'])->group(function () {
    // 所有 API 路由写在这里
    Route::post('/auth/login', [AuthController::class, 'login']);
    // ...
});
```

> 说明：`60,1` = 每 1 分钟最多 60 次请求（单 IP）。

---

## 4. Nginx 配置

### 4.1 生产级 Nginx 配置

创建 `/etc/nginx/sites-available/oa-api`（替换当前的 3001 端口配置）：

```nginx
# HTTP 强制跳转 HTTPS
server {
    listen 80;
    server_name your-domain.com;  # 改成你的域名或 IP
    return 301 https://$server_name$request_uri;
}

# HTTPS 主配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书路径（用 certbot 会自动生成）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 根目录（Laravel public/）
    root /var/www/oa-api/public;
    index index.php index.html;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # SPA fallback（如果前端和 API 同域）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 路由（Laravel）
    location /api {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP 处理
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # 禁止访问敏感文件
    location ~ /\.(?!well-known).* {
        deny all;
    }

    # 静态资源缓存（1 周）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

#### 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/oa-api /etc/nginx/sites-enabled/oa-api
sudo rm /etc/nginx/sites-enabled/default  # 删除默认配置
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

---

### 4.2 HTTPS 配置

#### 方案 A：有域名（推荐）

```bash
# 安装 certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 申请证书（会自动修改 Nginx 配置）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo systemctl enable certbot.timer
```

#### 方案 B：只有 IP（临时方案）

用自签名证书过渡：

```bash
# 生成自签名证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/oa-api.key \
  -out /etc/ssl/certs/oa-api.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=OA/CN=172.20.0.139"

# 在 Nginx 配置中指定证书路径
ssl_certificate /etc/ssl/certs/oa-api.crt;
ssl_certificate_key /etc/ssl/private/oa-api.key;
```

---

## 5. 数据库配置

### 5.1 PostgreSQL 性能优化

编辑 `/etc/postgresql/15/main/postgresql.conf`：

```ini
# 内存配置（根据服务器内存调整）
shared_buffers = 256MB          # 建议：总内存的 25%
effective_cache_size = 1GB       # 建议：总内存的 75%
maintenance_work_mem = 128MB     # 建议：64-256MB
work_mem = 16MB                 # 建议：4-32MB

# 日志配置（便于排查慢查询）
log_min_duration_statement = 1000  # 记录超过 1 秒的查询
log_checkpoints = on
log_connections = on
log_disconnections = on
```

重启生效：

```bash
sudo systemctl restart postgresql
```

---

### 5.2 数据库索引检查

对高频查询字段加索引（避免全表扫描）：

```sql
-- 1. 审批记录按状态查询
CREATE INDEX idx_approval_records_status ON approval_records(status);

-- 2. 报销按申请人查询
CREATE INDEX idx_expenses_applicant ON expenses(applicant_id);

-- 3. 项目按状态查询
CREATE INDEX idx_projects_status ON projects(status);

-- 4. 应收款按状态查询
CREATE INDEX idx_receivables_status ON receivables(status);

-- 5. 应付款按状态查询
CREATE INDEX idx_payables_status ON payables(status);

-- 查看现有索引
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';
```

---

### 5.3 找出慢查询（pg_stat_statements）

```sql
-- 启用 pg_stat_statements 扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查看最慢的 10 条查询
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 6. 部署流程

### 6.1 自动部署脚本

> 📌 当前项目已有部署脚本：`.workbuddy/deploy_api.py` 和 `.workbuddy/deploy_web.py`。

#### 标准部署流程

```bash
# 1. 本地构建前端
cd D:/work/website/OA/pc-web
npm run build  # 输出到 dist/

# 2. 部署后端（API）
python D:/work/website/OA/.workbuddy/deploy_api.py

# 3. 部署前端（Web）
python D:/work/website/OA/.workbuddy/deploy_web.py

# 4. 清理缓存 + 重启 PHP-FPM（重要！）
ssh nbcy@172.20.0.139 "
    cd /var/www/oa-api && sudo -u www-data php artisan route:clear
    sudo systemctl restart php8.3-fpm
"
```

---

### 6.2 部署后验证

```bash
# 1. 检查 API 是否可达
curl -s http://172.20.0.139/api/health || echo "API 不可达"

# 2. 检查登录是否正常
curl -s -X POST http://172.20.0.139/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"新密码"}' \
  | python3 -m json.tool

# 3. 检查前端是否加载
curl -s http://172.20.0.139/ | head -20
```

---

### 6.3 回滚方案

```bash
# 如果部署后出问题，快速回滚到上一个版本

# 1. 查看 Git 上一个 commit
git log --oneline -5

# 2. 回滚代码
git reset --hard HEAD~1

# 3. 重新部署
python D:/work/website/OA/.workbuddy/deploy_api.py
```

> 💡 **建议**：部署前先用 `git tag -a v1.0.0 -m "生产版本"` 打标签，方便回滚。

---

## 7. 备份策略

### 7.1 数据库备份

#### 每日自动备份（crontab）

```bash
# 登录服务器
ssh nbcy@172.20.0.139

# 创建备份目录
sudo mkdir -p /var/backups/oa-db
sudo chown postgres:postgres /var/backups/oa-db

# 编辑 crontab
sudo crontab -e -u postgres

# 添加以下行（每天凌晨 2 点备份）
0 2 * * * pg_dump security_oa | gzip > /var/backups/oa-db/oa-db-$(date +\%Y\%m\%d).sql.gz

# 每天凌晨 3 点删除 7 天前的备份
0 3 * * * find /var/backups/oa-db/ -name "*.sql.gz" -mtime +7 -delete
```

#### 手动备份命令

```bash
# 立即备份
sudo -u postgres pg_dump security_oa | gzip > /var/backups/oa-db/oa-db-manual-$(date +%Y%m%d).sql.gz

# 恢复备份（紧急）
gunzip -c /var/backups/oa-db/oa-db-20260622.sql.gz | sudo -u postgres psql security_oa
```

---

### 7.2 日志切割

防止 `/var/www/oa-api/storage/logs/laravel.log` 占满磁盘：

```bash
# 创建 logrotate 配置
sudo tee /etc/logrotate.d/oa-api << 'EOF'
/var/www/oa-api/storage/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload php8.3-fpm > /dev/null 2>&1 || true
    endscript
}
EOF

# 测试配置
sudo logrotate -d /etc/logrotate.d/oa-api
```

---

### 7.3 代码备份

```bash
# 每次部署前，自动打标签并备份到 Git
git tag -a "deploy-$(date +%Y%m%d-%H%M)" -m "生产部署"
git push origin --tags
```

---

## 8. 监控与告警

### 8.1 服务器资源监控

#### 安装 netdata（开源，开箱即用）

```bash
# 一键安装
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# 访问监控面板
http://172.20.0.139:19999
```

#### 关键指标告警阈值

| 指标 | 告警阈值 | 说明 |
|------|---------|------|
| CPU 使用率 | > 80% 持续 5 分钟 | 可能代码有死循环或 SQL 慢查询 |
| 内存使用率 | > 90% | 可能内存泄漏 |
| 磁盘使用率 | > 85% | 清理日志或备份文件 |
| PostgreSQL 连接数 | > 80% max_connections | 连接池配置不当 |
| API 响应时间 | > 2 秒 | 数据库慢查询或服务器负载高 |

---

### 8.2 API 可用性监控

#### 方案 A：Uptime Kuma（开源，推荐）

```bash
# 用 Docker 安装
docker run -d --name uptime-kuma -p 3001:3001 -v uptime-kuma:/app/data --restart=always louislam/uptime-kuma:1

# 访问
http://172.20.0.139:3001
```

监控项配置：
- `https://your-domain.com/api/health` — API 健康检查
- `https://your-domain.com/` — 前端可用性

#### 方案 B：简单 Shell 脚本（轻量）

```bash
# 创建监控脚本
sudo tee /usr/local/bin/oa-health-check.sh << 'EOF'
#!/bin/bash
API_URL="http://127.0.0.1:3001/api/health"
if ! curl -s --connect-timeout 5 $API_URL | grep -q '"code":0'; then
    echo "$(date): API 不可用！" | mail -s "OA API 告警" admin@your-domain.com
    # 或者调用企业微信/钉钉机器人
fi
EOF

chmod +x /usr/local/bin/oa-health-check.sh

# 每 5 分钟检查一次
sudo crontab -e
# 添加：
*/5 * * * * /usr/local/bin/oa-health-check.sh
```

---

### 8.3 错误日志监控

#### 用 Sentry（商业，功能强）

```bash
# 安装 Sentry SDK
cd /var/www/oa-api
sudo -u www-data composer require sentry/sentry-laravel

# 配置 DSN（在 .env 中）
SENTRY_LARAVEL_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

#### 或用 Flare（Laravel 专用，推荐）

```bash
# 注册：https://flareapp.io
# 安装 SDK
cd /var/www/oa-api
sudo -u www-data composer require beyondcode/flare-client

# 配置 API Key（在 .env 中）
FLARE_KEY=your-api-key
FLARE_ENV=production
```

---

## 9. 故障排查

### 9.1 常见问题速查

#### API 返回 500

```bash
# 1. 查看 Laravel 日志
ssh nbcy@172.20.0.139 "tail -50 /var/www/oa-api/storage/logs/laravel.log"

# 2. 检查 .env 配置
ssh nbcy@172.20.0.139 "cat /var/www/oa-api/.env | grep -v PASSWORD"

# 3. 检查数据库是否可达
ssh nbcy@172.20.0.139 "sudo -u postgres psql -d security_oa -c 'SELECT 1;'"
```

#### 部署后代码不生效

```bash
# 原因：opcache 缓存了旧代码
# 解决：重启 PHP-FPM
ssh nbcy@172.20.0.139 "sudo systemctl restart php8.3-fpm"

# 验证：查看 PHP-FPM 状态
ssh nbcy@172.20.0.139 "systemctl status php8.3-fpm"
```

#### 数据库迁移失败

```bash
# 查看迁移状态
cd /var/www/oa-api
sudo -u www-data php artisan migrate:status

# 如果某张表已存在但迁移未记录，手动插入记录
sudo -u postgres psql -d security_oa -c "
INSERT INTO migrations (migration, batch) 
SELECT 'migration_file_name', MAX(batch)+1 
FROM migrations 
ON CONFLICT DO NOTHING;
"
```

#### 前端白屏（404）

```bash
# 原因：Nginx 未配置 SPA fallback
# 解决：在 Nginx 配置中加
location / {
    try_files $uri $uri/ /index.html;
}
```

---

### 9.2 日志文件位置

| 日志 | 路径 | 说明 |
|------|------|------|
| Laravel 应用日志 | `/var/www/oa-api/storage/logs/laravel.log` | 应用错误、异常 |
| Nginx 访问日志 | `/var/log/nginx/access.log` | API 请求记录 |
| Nginx 错误日志 | `/var/log/nginx/error.log` | Nginx 配置错误 |
| PHP-FPM 日志 | `/var/log/php8.3-fpm.log` | PHP 错误 |
| PostgreSQL 日志 | `/var/log/postgresql/postgresql-15-main.log` | 数据库错误 |

---

## 10. 上线检查清单

### 10.1 上线前（必须完成）

- [ ] `APP_ENV=production` ✅
- [ ] `APP_DEBUG=false` ✅
- [ ] **修改 admin 默认密码** ❌
- [ ] **生成 JWT_SECRET** ❌
- [ ] **配置 HTTPS** ❌
- [ ] **配置 Nginx 80/443** ❌
- [ ] **配置数据库自动备份** ❌
- [ ] 配置日志切割
- [ ] 配置 API 限流
- [ ] 跑通资金流完整测试（10/10 通过）✅

---

### 10.2 上线当天

- [ ] 通知用户维护时间窗口
- [ ] 备份当前数据库（最后一次全量备份）
- [ ] 部署新代码
- [ ] 运行数据库迁移（如果有）
- [ ] 清理缓存 + 重启 PHP-FPM
- [ ] 验证登录功能
- [ ] 验证核心功能（项目/报销/应收应付）
- [ ] 通知用户上线完成

---

### 10.3 上线后 24 小时

- [ ] 监控服务器资源（CPU/内存/磁盘）
- [ ] 查看 Laravel 日志是否有异常
- [ ] 验证数据库备份是否正常
- [ ] 收集用户反馈
- [ ] 准备热修复流程（如有紧急 bug）

---

## 📞 应急联系人

| 角色 | 姓名 | 联系方式 | 职责 |
|------|------|---------|------|
| 系统管理员 | - | - | 服务器维护、备份恢复 |
| 开发负责人 | Senior Developer | - | 代码修复、紧急部署 |
| 数据库管理员 | - | - | 数据库优化、慢查询分析 |

---

## 📝 版本历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|---------|
| v1.0.0 | 2026-06-22 | Senior Developer | 初始版本 |

---

**文档结束**

> 💡 本文档会随着系统迭代持续更新。如有问题，请联系开发团队。
