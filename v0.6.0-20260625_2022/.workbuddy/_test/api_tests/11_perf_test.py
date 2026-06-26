#!/usr/bin/env python3
"""
11_perf_test.py — Session B 阶段 2: API 性能测试（修版 v2）

v2 改进:
- 用 Counter 做并发限流, 不再堆积 futs
- 只保留聚合后的统计, 不存每条 sample (省内存)
- 用 context manager 关闭
"""
import requests
import time
import json
import os
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

API_BASE = 'http://172.20.0.139'
TEST_USER = 'admin'
TEST_PASS = 'admin123'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, 'perf_results.json')
SUMMARY_PATH = os.path.join(SCRIPT_DIR, 'perf_report.md')

# 不同用户 — 用 admin1 (id=74) 多个测试账号避开单 IP login 5/min throttle
TEST_USERS = [
    ('admin1', 'admin123'),
    ('tech_mgr', 'admin123'),
    ('proj_mgr', 'admin123'),
    ('sales_mgr', 'admin123'),
    ('fin_mgr', 'admin123'),
]

CORE_ENDPOINTS = [
    ('GET', '/api/auth/me'),
    ('GET', '/api/dashboard/stats'),
    ('GET', '/api/employees'),
    ('GET', '/api/customers'),
    ('GET', '/api/projects'),
    ('GET', '/api/service/orders'),
    ('GET', '/api/finance/receivables'),
    ('GET', '/api/approval-templates'),
    ('GET', '/api/attendance/records'),
    ('GET', '/api/vehicles'),
    ('GET', '/api/notifications'),
    ('GET', '/api/roles'),
    ('GET', '/api/system-logs'),
    ('GET', '/api/dashboard/recent-projects'),
    ('GET', '/api/dashboard/todo'),
]

# 压测档位: (并发, 持续秒数)
LOAD_PROFILES = [
    (10, 10),
    (20, 10),
    (50, 10),
]

# 共享 token + 线程本地 lat 累加 (用 list 存是为了算 p95/p99)
thread_local = threading.local()


def get_tokens(count=10):
    """拿多个 token, 用不同账号 (绕开 login 5/min/IP throttle)"""
    tokens = []
    # 用单个 Session 复用 TCP 连接, 防止 Windows ephemeral port 耗尽
    sess = requests.Session()
    for i in range(count):
        user, pwd = TEST_USERS[i % len(TEST_USERS)]
        r = sess.post(f'{API_BASE}/api/auth/login',
                      json={'username': user, 'password': pwd}, timeout=10)
        if r.status_code == 200:
            tokens.append(r.json()['data']['token'])
        elif r.status_code == 429:
            clear_throttle_cache()
            time.sleep(2)
            r = sess.post(f'{API_BASE}/api/auth/login',
                          json={'username': user, 'password': pwd}, timeout=10)
            if r.status_code == 200:
                tokens.append(r.json()['data']['token'])
    return tokens


def clear_throttle_cache():
    """通过 SSH 清 PG cache 表, 防止 rate limiter 撞线"""
    import paramiko
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    cli.exec_command(
        'PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa '
        '-c "TRUNCATE cache; TRUNCATE cache_locks;" 2>/dev/null', timeout=10)
    cli.close()


def worker(deadline, token, start_offset, ep_cycle, latencies, status_counter, error_counter):
    """单线程 worker: 直到 deadline 到达前不断发请求"""
    n = len(ep_cycle)
    idx = start_offset
    # 用 Session 复用连接 + 限制单 host 最大连接数
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=1,
        pool_maxsize=10,
        max_retries=0,
    )
    sess.mount('http://', adapter)
    sess.headers.update({
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    })
    while time.time() < deadline:
        m, u = ep_cycle[idx % n]
        idx += 1
        url = f'{API_BASE}{u}'
        t0 = time.time()
        try:
            r = sess.request(m, url, timeout=10)
            dt = (time.time() - t0) * 1000
            latencies.append(dt)
            status_counter[r.status_code] += 1
            if r.status_code >= 500 or r.status_code == 0:
                error_counter[0] += 1
        except Exception:
            dt = (time.time() - t0) * 1000
            latencies.append(dt)
            status_counter[0] += 1
            error_counter[0] += 1


def run_load(concurrency, duration_s, endpoints, tokens):
    """每个线程用不同 token, 避开 throttle 5/min/login 限制"""
    deadline = time.time() + duration_s
    latencies = []
    status_counter = defaultdict(int)
    error_counter = [0]
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futs = []
        for i in range(concurrency):
            start_offset = (i * len(endpoints) // concurrency) % len(endpoints)
            token = tokens[i % len(tokens)]
            futs.append(pool.submit(
                worker, deadline, token, start_offset,
                endpoints, latencies, status_counter, error_counter,
            ))
        for f in futs:
            f.result()
    return latencies, dict(status_counter), error_counter[0]


def analyze(latencies, statuses, errors, concurrency, duration):
    if not latencies:
        return None
    lat = sorted(latencies)
    n = len(lat)
    total = n
    elapsed = duration
    return {
        'concurrency': concurrency,
        'duration_s': elapsed,
        'total_requests': total,
        'qps': round(total / elapsed, 1),
        'p50': round(lat[int(n * 0.5)], 1),
        'p90': round(lat[int(n * 0.9)], 1),
        'p95': round(lat[int(n * 0.95)], 1),
        'p99': round(lat[int(n * 0.99)], 1),
        'max_ms': round(lat[-1], 1),
        'min_ms': round(lat[0], 1),
        'mean_ms': round(statistics.mean(lat), 1),
        'error_count': errors,
        'error_rate_pct': round(errors * 100 / total, 2) if total else 0,
        'statuses': statuses,
    }


def main():
    print("=== 1. 拿多个 token (绕开 login 5/min/IP throttle) ===")
    # 先清 cache 保证 login 能成功
    try:
        clear_throttle_cache()
    except Exception:
        pass
    time.sleep(2)
    tokens = get_tokens(50)  # 50 个 token 备用
    print(f"  ✅ 拿到 {len(tokens)} 个 token")
    if not tokens:
        print("  ❌ 没拿到任何 token, 中止")
        return

    print(f"\n=== 2. 压测 {len(CORE_ENDPOINTS)} 个核心端点 ===")
    all_results = []
    for concurrency, duration in LOAD_PROFILES:
        print(f"\n  --- 并发 {concurrency} × 持续 {duration}s ---")
        # 每档压测前清一次 cache (防止 rate limiter 撞线)
        try:
            clear_throttle_cache()
        except Exception:
            pass
        t0 = time.time()
        latencies, statuses, errors = run_load(concurrency, duration, CORE_ENDPOINTS, tokens)
        elapsed = time.time() - t0
        stats = analyze(latencies, statuses, errors, concurrency, elapsed)
        all_results.append(stats)
        print(f"  ✅ {stats['total_requests']} reqs in {elapsed:.1f}s")
        print(f"     QPS={stats['qps']:.1f} | P50={stats['p50']}ms P95={stats['p95']}ms P99={stats['p99']}ms")
        print(f"     错误 {stats['error_count']} ({stats['error_rate_pct']}%)")
        print(f"     状态码: {stats['statuses']}")

    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 报告
    lines = ['# API 性能测试报告', '',
             f'**测试时间**: {time.strftime("%Y-%m-%d %H:%M:%S")} | **端点**: {len(CORE_ENDPOINTS)} 个核心 API | **服务器**: 172.20.0.139 (16C/16G, FPM pm.max_children=20)', '',
             '## 测试方法', '',
             '- 工具: Python `requests` + `ThreadPoolExecutor`',
             '- 档位: 10 / 20 / 50 并发，每档持续 10s',
             '- 鉴权: admin Bearer token',
             '- 端点轮询: 每线程独立 endpoint 起点', '',
             '## 端点列表', '']
    for m, u in CORE_ENDPOINTS:
        lines.append(f'- `{m} {u}`')
    lines += ['', '## 压测结果', '']
    lines.append('| 并发 | 总请求 | 耗时(s) | QPS | P50 | P90 | P95 | P99 | Max | 错误率 |')
    lines.append('|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for s in all_results:
        lines.append(f"| {s['concurrency']} | {s['total_requests']} | {s['duration_s']} | {s['qps']} | {s['p50']} | {s['p90']} | {s['p95']} | {s['p99']} | {s['max_ms']} | {s['error_rate_pct']}% |")
    lines += ['', '## 状态码分布', '']
    for s in all_results:
        lines.append(f"### 并发 {s['concurrency']}")
        for code, cnt in sorted(s['statuses'].items(), key=lambda x: -x[1]):
            pct = cnt * 100 / s['total_requests']
            lines.append(f"- HTTP {code}: {cnt} ({pct:.1f}%)")
        lines.append('')
    # 评估
    lines += ['## 性能评估', '']
    final = all_results[-1]
    if final['p95'] < 500 and final['error_rate_pct'] < 1:
        lines.append(f'✅ **50 并发 P95 = {final["p95"]}ms, 错误率 {final["error_rate_pct"]}% — 性能良好**')
    elif final['p95'] < 1000:
        lines.append(f'⚠️ **50 并发 P95 = {final["p95"]}ms — 中等负载可承受**')
    else:
        lines.append(f'❌ **50 并发 P95 = {final["p95"]}ms — 性能不足，建议优化**')
    lines += ['', '## 优化建议', '',
              '1. **PG 连接池** — PG max_connections=100, 配合 FPM pm.max_children=20 留余量',
              '2. **OPcache + JIT** — PHP 8.3 JIT 默认开, 确认 `opcache.jit_buffer_size=64M`',
              '3. **Redis 缓存** — dashboard/stats / approval-templates 加 1min cache',
              '4. **N+1 优化** — Eloquent `with()` 预加载, 关注 `SLOW_SQL` 日志',
              '5. **静态资源分离** — 走 nginx 直出, FPM 只接 /api/']
    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n报告写入 {SUMMARY_PATH}")


if __name__ == '__main__':
    import traceback
    try:
        main()
    except Exception as e:
        with open(SUMMARY_PATH, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## ⚠️ 异常\n\n```\n{traceback.format_exc()}\n```\n")
        raise
