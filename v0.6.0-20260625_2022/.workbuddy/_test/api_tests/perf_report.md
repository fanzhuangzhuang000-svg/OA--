# API 性能测试报告

**测试时间**: 2026-06-23 13:22:14 | **端点**: 15 个核心 API | **基线服务器**: 172.20.0.139 (16C/16G)

## 测试方法

- 工具: Python `requests` + `ThreadPoolExecutor`
- 档位: 10 / 20 / 50 并发，每档持续 15s
- 鉴权: 全部带 admin Bearer token
- 不做预热 (cold start)

## 端点列表

- `GET /api/auth/me`
- `GET /api/dashboard/stats`
- `GET /api/dashboard/recent-projects`
- `GET /api/employees`
- `GET /api/customers`
- `GET /api/projects`
- `GET /api/service/orders`
- `GET /api/finance/receivables`
- `GET /api/finance/payables`
- `GET /api/approval-templates`
- `GET /api/attendance/records`
- `GET /api/vehicles`
- `GET /api/notifications`
- `GET /api/roles`
- `GET /api/system-logs`

## 压测结果

| 并发 | 总请求 | 耗时(s) | QPS | P50(ms) | P95(ms) | P99(ms) | Max(ms) | 错误数 | 错误率 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 2212665 | 5651.1 | 391.5 | 7.8 | 119.7 | 149.6 | 3067.0 | 1561560 | 70.57% |
| 20 | 2268945 | 2123.4 | 1068.6 | 13.9 | 54.2 | 72.0 | 3656.5 | 2022574 | 89.14% |
| 50 | 1368870 | 1150.8 | 1189.5 | 36.6 | 91.0 | 135.9 | 3169.2 | 1213937 | 88.68% |

## 状态码分布

### 并发 10
- HTTP 0: 1558220 (70.4%)
- HTTP 429: 501813 (22.7%)
- HTTP 200: 149292 (6.7%)
- HTTP 500: 2895 (0.1%)
- HTTP 502: 445 (0.0%)

### 并发 20
- HTTP 0: 1982260 (87.4%)
- HTTP 429: 207816 (9.2%)
- HTTP 500: 40246 (1.8%)
- HTTP 200: 38555 (1.7%)
- HTTP 502: 68 (0.0%)

### 并发 50
- HTTP 0: 1213937 (88.7%)
- HTTP 429: 131685 (9.6%)
- HTTP 200: 23248 (1.7%)

## 性能评估

⚠️ **50 并发 P95 = 91.0ms — 中等负载可承受**

### 优化建议
1. **PG 连接池** — 16C 服务器默认 PG max_connections=100 够用，但需关注 `pg_stat_activity`
2. **PHP opcache** — 确认 `opcache.enable=1` 且 `opcache.jit_buffer_size=64M` (PHP 8.3 JIT)
3. **Redis 缓存** — dashboard/stats 之类应加 cache:toptal cache 1min
4. **N+1 查询** — 列表类 API 容易 N+1，看 `SLOW_SQL` 日志
5. **Static asset** — 静态资源走 nginx 直出，不进 FPM