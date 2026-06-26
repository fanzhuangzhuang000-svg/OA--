# 安防运维OA系统 — 监控与告警指南

> 版本: v1.1 | 更新: 2026-06-26 | 维护: SRE 团队

---

## 目录

1. [架构概览](#1-架构概览)
2. [健康检查端点](#2-健康检查端点)
3. [系统监控面板](#3-系统监控面板)
4. [告警配置](#4-告警配置)
5. [错误追踪](#5-错误追踪)
6. [Prometheus + Grafana](#6-prometheus--grafana)
7. [日志管理](#7-日志管理)
8. [运维 Runbook](#8-运维-runbook)
9. [故障排查清单](#9-故障排查清单)

---

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      监控架构                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Uptime   │    │Prometheus│    │  Sentry  │              │
│  │ Robot    │    │          │    │          │              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  ┌─────────────────────────────────────────┐               │
│  │           Laravel API (pc-api)          │               │
│  │                                         │               │
│  │  /api/health          ← 存活探针       │               │
│  │  /api/health/ready    ← 就绪探针       │               │
│  │  /api/health/live     ← K8s liveness   │               │
│  │  /api/health/metrics  ← Prometheus格式  │               │
│  │  /api/admin/monitor/* ← 系统监控面板    │               │
│  └─────────┬──────────┬──────────┬────────┘               │
│            │          │          │                          │
│            ▼          ▼          ▼                          │
│       ┌────────┐ ┌────────┐ ┌────────┐                    │
│       │PostgreSQL│ │ Redis  │ │ Disk   │                    │
│       └────────┘ └────────┘ └────────┘                    │
│                                                             │
│  ┌─────────────────────────────────────────┐               │
│  │         AlertService (告警通知)          │               │
│  │  飞书 │ 钉钉 │ 企业微信 │ 邮件          │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 健康检查端点

### 2.1 公开端点（无需认证）

| 端点 | 用途 | 响应 |
|------|------|------|
| `GET /api/health` | 综合健康检查 | JSON，包含所有子系统状态 |
| `GET /api/health/ready` | K8s readinessProbe | `{"status":"ready"}` |
| `GET /api/health/live` | K8s livenessProbe | `{"status":"alive"}` |

#### 综合健康检查示例响应

```json
{
    "code": 0,
    "message": "healthy",
    "data": {
        "status": "healthy",
        "timestamp": "2026-06-26T10:00:00+08:00",
        "duration": "45.23ms",
        "checks": {
            "app": {
                "status": "ok",
                "name": "安防运维OA",
                "environment": "production",
                "php_version": "8.3.7",
                "laravel": "11.15.0"
            },
            "database": {
                "status": "ok",
                "driver": "pgsql",
                "latency": "2.15ms"
            },
            "cache": {
                "status": "ok",
                "driver": "redis",
                "latency": "0.89ms"
            },
            "redis": {
                "status": "ok",
                "latency": "0.45ms"
            },
            "storage": {
                "status": "ok",
                "latency": "0.12ms"
            },
            "disk": {
                "status": "ok",
                "total": "100 GB",
                "free": "65.2 GB",
                "used_percent": 34.8
            },
            "queue": {
                "status": "ok",
                "driver": "redis"
            }
        }
    }
}
```

#### 降级状态 (HTTP 503)

当任何关键子系统（database, cache, redis, storage, disk=critical）故障时，返回 503:
```json
{
    "code": 1001,
    "message": "degraded",
    "data": { ... }
}
```

### 2.2 认证端点

| 端点 | 用途 | Content-Type |
|------|------|--------------|
| `GET /api/health/metrics` | Prometheus 指标抓取 | `text/plain` |

#### Prometheus 指标示例

```
# HELP oa_app_info Application information
# TYPE oa_app_info gauge
oa_app_info{version="11.15.0",php="8.3.7",env="production"} 1
# HELP oa_db_connections Current database connections
# TYPE oa_db_connections gauge
oa_db_connections 12
# HELP oa_db_cache_hit_rate Database cache hit rate percent
# TYPE oa_db_cache_hit_rate gauge
oa_db_cache_hit_rate 99.85
# HELP oa_disk_usage_percent Root disk usage percent
# TYPE oa_disk_usage_percent gauge
oa_disk_usage_percent 34.8
# HELP oa_load_average System load average
# TYPE oa_load_average gauge
oa_load_average{window="1m"} 0.52
oa_load_average{window="5m"} 0.48
oa_load_average{window="15m"} 0.45
```

---

## 3. 系统监控面板

### 端点列表（需 admin 权限）

| 端点 | 说明 |
|------|------|
| `GET /api/admin/monitor/metrics` | 总览（一次获取所有指标） |
| `GET /api/admin/monitor/disk` | 磁盘详情 |
| `GET /api/admin/monitor/db` | 数据库连接/缓存/慢查询 |
| `GET /api/admin/monitor/services` | PHP-FPM/OPcache/Redis 状态 |
| `GET /api/admin/monitor/errors` | 24h 错误趋势 |
| `GET /api/admin/monitor/backups` | 最近备份文件 |

### 关键指标说明

| 指标 | 正常范围 | 告警阈值 | 说明 |
|------|----------|----------|------|
| 磁盘使用率 | < 85% | ≥ 85% warn, ≥ 95% critical | 根分区 |
| DB 连接数 | < 80 | ≥ 80 warn, ≥ 150 critical | pg_stat_activity |
| 慢查询数 | 0 | ≥ 3 warn, ≥ 10 critical | 执行 > 1s 的活跃查询 |
| 缓存命中率 | > 95% | < 90% warn, < 80% critical | pg_stat_database |
| 等待锁数 | 0 | ≥ 5 warn, ≥ 20 critical | pg_locks NOT granted |
| 24h 错误数 | < 50 | ≥ 50 warn, ≥ 200 critical | laravel.log ERROR |
| 备份年龄 | < 3 天 | ≥ 3 天 warn, ≥ 7 天 critical | 最新备份文件 |
| 系统负载 | < 4.0 | ≥ 4.0 warn, ≥ 8.0 critical | 1 分钟平均 |

---

## 4. 告警配置

### 4.1 环境变量

在 `.env` 中配置告警渠道:

```bash
# ===== 告警通知渠道 =====

# 飞书机器人
ALERT_FEISHU_ENABLED=true
ALERT_FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# 钉钉机器人
ALERT_DINGTALK_ENABLED=true
ALERT_DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
ALERT_DINGTALK_SECRET=SECxxx

# 企业微信机器人
ALERT_WECHAT_WORK_ENABLED=true
ALERT_WECHAT_WORK_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

# 邮件告警
ALERT_MAIL_ENABLED=true
ALERT_MAIL_TO=sre-team@company.com
```

### 4.2 告警命令

```bash
# 手动执行监控检查
php artisan monitor:check

# 试运行（仅输出不发送告警）
php artisan monitor:check --dry-run
```

### 4.3 定时任务配置

在服务器 crontab 中添加:

```cron
# 每 5 分钟执行监控检查
*/5 * * * * cd /path/to/oa/pc-api && php artisan monitor:check >> /dev/null 2>&1

# 每天凌晨清理过期日志
0 2 * * * cd /path/to/oa/pc-api && php artisan log:clear --days=30 >> /dev/null 2>&1
```

### 4.4 告警冷却机制

同一类型告警在 **30 分钟** 内不会重复发送，避免告警风暴。

冷却键示例:
- `alert_disk_90` — 磁盘 90-95% 区间
- `alert_db_conn_80` — 数据库连接 80-100 区间
- `alert_slow_q_3` — 慢查询 3-6 条区间

---

## 5. 错误追踪

### 5.1 本地错误追踪（已启用）

项目内置 `ErrorReporter` 服务，所有未处理异常自动记录到 `storage/logs/laravel.log`。

配置建议:

```bash
# .env — 使用 daily channel 自动按天切分
LOG_CHANNEL=daily
LOG_LEVEL=error

# 或使用 stack channel 同时输出到多个目标
LOG_CHANNEL=stack
```

### 5.2 Sentry 集成（推荐生产环境）

#### 安装

```bash
composer require sentry/sentry-laravel
```

#### 配置

```bash
# .env
SENTRY_ENABLED=true
SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_TRACES_SAMPLE_RATE=0.2
SENTRY_ENVIRONMENT=production
```

#### 发布配置文件

```bash
php artisan vendor:publish --provider="Sentry\Laravel\ServiceProvider"
```

#### 在 bootstrap/app.php 中注册

```php
// 在 withExceptions 中添加
$exceptions->report(function (\Throwable $e) {
    if (app()->environment('production')) {
        \Sentry\Laravel\Integration::captureUnhandledException($e);
    }
});
```

### 5.3 飞书/钉钉即时通知

对于生产环境 500 错误，建议配置 Sentry Webhook 到飞书/钉钉:

1. Sentry → Settings → Integrations → Internal Integrations → Webhooks
2. 配置 Webhook URL 指向飞书/钉钉机器人
3. 选择触发事件: `issue.created`, `issue.resolved`

---

## 6. Prometheus + Grafana

### 6.1 Prometheus 配置

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'oa-api'
    scrape_interval: 30s
    metrics_path: '/api/health/metrics'
    basic_auth:
      username: 'monitor'
      password: 'xxx'
    static_configs:
      - targets: ['oa-api.company.com']
        labels:
          service: 'oa-api'
          environment: 'production'
```

### 6.2 Grafana Dashboard

推荐导入以下 Dashboard 模板:

- **Laravel API 监控**: Dashboard ID `12345`
- **PostgreSQL 监控**: Dashboard ID `9628`
- **Node Exporter**: Dashboard ID `1860`

### 6.3 Alertmanager 告警规则

```yaml
# alertmanager.yml
groups:
  - name: oa-api-alerts
    rules:
      - alert: OAApiHighErrorRate
        expr: rate(oa_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "OA系统错误率过高"
          description: "5分钟内错误率超过 10%"

      - alert: OAApiHighDBConnections
        expr: oa_db_connections > 100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "OA系统数据库连接数过高"
          description: "当前连接数: {{ $value }}"

      - alert: OAApiDiskUsageHigh
        expr: oa_disk_usage_percent > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "OA系统磁盘使用率过高"
          description: "当前使用率: {{ $value }}%"
```

---

## 7. 日志管理

### 7.1 日志通道配置

```bash
# .env — 推荐生产环境配置
LOG_CHANNEL=daily
LOG_LEVEL=warning
LOG_DEPRECATIONS_CHANNEL=null
```

### 7.2 日志格式

项目使用 JSON Lines 格式记录结构化日志:

```json
{"ts":"2026-06-26T10:00:00+08:00","level":"error","msg":"APP_ERROR ...","exception":"RuntimeException","file":"/app/...","line":42,"trace_top":[...],"url":"/api/projects","ip":"10.0.0.1"}
```

### 7.3 日志分析命令

```bash
# 查看最近 1 小时的错误
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" storage/logs/laravel.log | grep ERROR

# 统计错误类型分布
grep ERROR storage/logs/laravel.log | grep -oP '"exception":"[^"]+' | sort | uniq -c | sort -rn

# 使用 jq 解析 JSON 日志
cat storage/logs/laravel.log | jq 'select(.level == "error")'

# 查看慢请求（> 2s）
grep APP_ERROR storage/logs/laravel.log | jq 'select(.response_time > 2000)'
```

### 7.4 日志轮转

```bash
# /etc/logrotate.d/oa-api
/path/to/oa/storage/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
}
```

---

## 8. 运维 Runbook

### 8.1 磁盘空间不足

**告警**: `disk_usage_percent >= 85%`

**排查步骤**:
```bash
# 1. 查看磁盘使用
df -h

# 2. 查找大文件
du -sh /var/www/oa/storage/logs/*
du -sh /var/www/oa/storage/app/backups/*

# 3. 清理旧日志
find /var/www/oa/storage/logs -name "*.log" -mtime +30 -delete

# 4. 清理旧备份（保留最近 7 天）
find /var/www/oa/storage/app/backups -name "*.sql.gz" -mtime +7 -delete

# 5. 清理 Laravel 缓存
cd /var/www/oa/pc-api && php artisan cache:clear
```

### 8.2 数据库连接数过高

**告警**: `db_connections >= 80`

**排查步骤**:
```sql
-- 1. 查看当前连接
SELECT pid, usename, application_name, client_addr, state, query_start, left(query, 80)
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY query_start;

-- 2. 查看空闲连接
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle' AND datname = current_database();

-- 3. 终止空闲超过 5 分钟的连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND now() - state_change > INTERVAL '5 minutes' AND datname = current_database();

-- 4. 查看锁等待
SELECT * FROM pg_locks WHERE NOT granted;
```

### 8.3 慢查询

**告警**: `slow_queries >= 3`

**排查步骤**:
```sql
-- 1. 查看当前慢查询
SELECT pid, now() - query_start AS duration, left(query, 200) AS query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > INTERVAL '1 second'
ORDER BY duration DESC;

-- 2. 终止超时查询（> 30s）
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > INTERVAL '30 seconds';

-- 3. 检查表膨胀
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;
```

### 8.4 缓存命中率低

**告警**: `cache_hit_rate < 90%`

**排查步骤**:
```bash
# 1. 检查 Redis 内存
redis-cli info memory

# 2. 检查 Redis 命中率
redis-cli info stats | grep -E "keyspace_hits|keyspace_misses"

# 3. 清理 Laravel 缓存重建
php artisan cache:clear
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

---

## 9. 故障排查清单

### 9.1 应用无响应

- [ ] 检查 Nginx 状态: `systemctl status nginx`
- [ ] 检查 PHP-FPM 状态: `systemctl status php8.3-fpm`
- [ ] 检查 PHP-FPM 进程: `ps aux | grep php-fpm`
- [ ] 检查端口监听: `ss -tlnp | grep :9000`
- [ ] 检查错误日志: `tail -50 /var/log/nginx/error.log`
- [ ] 检查 Laravel 日志: `tail -50 storage/logs/laravel.log`

### 9.2 数据库连接失败

- [ ] 检查 PostgreSQL 状态: `systemctl status postgresql`
- [ ] 检查连接数: `psql -c "SELECT count(*) FROM pg_stat_activity;"`
- [ ] 检查最大连接数: `psql -c "SHOW max_connections;"`
- [ ] 检查 pg_hba.conf 配置
- [ ] 检查网络连通性: `telnet db-host 5432`

### 9.3 502 Bad Gateway

- [ ] PHP-FPM 进程是否存活
- [ ] Nginx upstream 配置是否正确
- [ ] PHP-FPM socket 文件权限
- [ ] 检查 `php-fpm.conf` 中的 `listen` 配置

### 9.4 队列积压

- [ ] 检查队列 Worker: `supervisorctl status`
- [ ] 查看积压数量: `php artisan queue:failed`
- [ ] 重启 Worker: `php artisan queue:restart`
- [ ] 检查失败任务: `php artisan queue:failed`

---

## 附录

### A. 监控配置文件

| 文件 | 说明 |
|------|------|
| `config/monitoring.php` | 告警阈值、渠道、采集配置 |
| `app/Services/AlertService.php` | 多渠道告警通知服务 |
| `app/Services/ErrorReporter.php` | 结构化错误上报 |
| `app/Http/Controllers/Api/HealthCheckController.php` | 健康检查端点 |
| `app/Http/Controllers/Api/SystemMonitorController.php` | 系统监控面板 |
| `app/Console/Commands/MonitorCheckCommand.php` | 定时监控检查命令 |

### B. 相关文档

- [部署指南](production-deployment-guide.md)
- [生产部署报告](v1.0.0-prod-deployment-report.md)

### C. 联系方式

- SRE 团队: sre@company.com
- 飞书群: [安防运维-SRE告警群]
- 值班电话: 见内部通讯录
