#!/usr/bin/env python3
"""
10_api_smoke.py — Session B 阶段 1: API 烟囱测试

跑全部 ~640 个 API 端点：
- 登录拿 token
- 每个端点请求一次（用纯 requests，不带 session 避免 cookie 干扰）
- 记录 status code + 响应时间 + body + 是否通过
- 失败的写报告

输出：
- _test/api_tests/smoke_results.json
- _test/api_tests/smoke_summary.md
"""
import requests
import re
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

API_BASE = 'http://172.20.0.139'  # paths already include /api
TEST_USER = 'admin'
TEST_PASS = 'admin123'

# 脚本绝对路径 — 写报告和结果都用绝对路径，跟 cwd 无关
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, 'smoke_results.json')
SUMMARY_PATH = os.path.join(SCRIPT_DIR, 'smoke_summary.md')


def load_routes():
    """从 172 实时拉 routes（最准）"""
    import paramiko
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)
    sin, sout, serr = cli.exec_command(
        'cd /var/www/oa-api && php artisan route:list 2>/dev/null',
        timeout=30,
    )
    raw = sout.read().decode('utf-8', 'replace')
    cli.close()
    endpoints = []
    for line in raw.splitlines():
        m = re.match(r'^\s*(\S+)\s+(/\S+|\S+)\s', line)
        if m and m.group(2).startswith('api/'):
            methods = m.group(1).split('|')
            for method in methods:
                endpoints.append((method.strip(), '/' + m.group(2)))
    return endpoints


# ⚠️ 排除会破坏主 token / 需要特殊 body / 会改 admin 资料的端点
SKIP_URLS = {
    '/api/auth/logout',
    '/api/auth/change-password',
    '/api/auth/profile',   # PUT 会改 admin name/phone/email
}

# 全局 throttle 节流（毫秒）— 防止 FPM 顶满
REQUEST_INTERVAL_MS = 30


def get_token():
    """登录拿 token"""
    r = requests.post(f'{API_BASE}/api/auth/login', json={
        'username': TEST_USER,
        'password': TEST_PASS
    }, timeout=10)
    r.raise_for_status()
    data = r.json()
    if 'data' in data and isinstance(data['data'], dict):
        return data['data'].get('token') or data['data'].get('access_token')
    return data.get('token') or data.get('access_token')


def test_endpoint(method, url, token):
    """测试一个端点 - 用纯 requests 不带 session 避免 cookie 干扰"""
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    if '{' in url:
        url = re.sub(r'\{[^}]+\}', '1', url)
    full = f'{API_BASE}{url}'
    t0 = time.time()
    try:
        r = requests.request(method, full, headers=headers, timeout=15)
        dt = (time.time() - t0) * 1000
        return {
            'method': method,
            'url': url,
            'status': r.status_code,
            'ms': round(dt, 1),
            'ok': r.status_code < 500,  # 4xx 业务层 OK（路由可达）
            'error': None,
            'body': r.text[:200],
        }
    except Exception as e:
        dt = (time.time() - t0) * 1000
        return {
            'method': method,
            'url': url,
            'status': 0,
            'ms': round(dt, 1),
            'ok': False,
            'error': str(e)[:200],
        }


def main():
    print("=== 1. 加载 API 端点 ===")
    endpoints = load_routes()
    print(f"  找到 {len(endpoints)} 个 (method, url) 组合")

    print(f"\n=== 2. 登录拿 token ===")
    try:
        token = get_token()
        print(f"  ✅ token: {token[:30]}...")
    except Exception as e:
        print(f"  ❌ 登录失败: {e}")
        return
    if not token:
        print("  ❌ 拿不到 token")
        return

    print(f"\n=== 3. 串行测试 {len(endpoints)} 个端点 ===")
    # 排除自杀/需特殊 body 的端点
    filtered = [(m, u) for m, u in endpoints if u not in SKIP_URLS]
    skipped = len(endpoints) - len(filtered)
    if skipped:
        print(f"  跳过 {skipped} 个端点 (logout/change-password)")
    results = []
    t0 = time.time()
    # 串行：1) FPM pm.max_children=20 也不抗 10 并发跑全 600+ 端点
    # 2) 简单 GET/POST 串行足够快 (~30-100ms × 600 = 20-60s)
    for i, (m, u) in enumerate(filtered, 1):
        r = test_endpoint(m, u, token)
        results.append(r)
        if i % 100 == 0:
            print(f"  进度 {i}/{len(filtered)}")
        time.sleep(REQUEST_INTERVAL_MS / 1000.0)
    total = time.time() - t0
    print(f"  ✅ 完成 {len(results)} 个, 耗时 {total:.1f}s")

    results.sort(key=lambda x: (x['status'] >= 400, -x['ms']))

    by_status = defaultdict(int)
    for r in results:
        by_status[r['status']] += 1
    print(f"\n=== 4. 状态码分布 ===")
    for s, c in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  HTTP {s}: {c}")
    passed = sum(1 for r in results if r['ok'])
    print(f"  通过: {passed}/{len(results)} ({passed*100//len(results)}%)")

    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    lines = ['# API 烟囱测试报告', '', f'**总端点**: {len(results)} | **通过**: {passed} | **耗时**: {total:.1f}s', '']
    lines.append('## 状态码分布')
    for s, c in sorted(by_status.items(), key=lambda x: -x[1]):
        lines.append(f'- HTTP {s}: {c}')
    lines.append('')
    lines.append('## 失败端点（HTTP >= 500）')
    fail_500 = [r for r in results if r['status'] >= 500]
    lines.append(f'共 {len(fail_500)} 个')
    lines.append('')
    for r in fail_500:
        lines.append(f"- `{r['method']} {r['url']}` → {r['status']} ({r['ms']}ms)")
        if r.get('body'):
            lines.append(f"  body: `{r['body'][:150]}`")
    lines.append('')
    lines.append('## 401/404/422 端点（业务层，路由可达）')
    for status in [401, 403, 404, 422, 429]:
        sr = [r for r in results if r['status'] == status]
        if sr:
            lines.append(f'\n### HTTP {status} ({len(sr)} 个)')
            for r in sr[:5]:
                lines.append(f"- `{r['method']} {r['url']}` → {r['status']} ({r['ms']}ms)")
                if r.get('body'):
                    lines.append(f"  body: `{r['body'][:100]}`")
            if len(sr) > 5:
                lines.append(f"- ...还有 {len(sr)-5} 个")
    lines.append('')
    lines.append('## 最慢的 20 个')
    for r in sorted(results, key=lambda x: -x['ms'])[:20]:
        lines.append(f"- `{r['method']} {r['url']}` → {r['status']} ({r['ms']}ms)")

    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n报告写入 {SUMMARY_PATH}")


if __name__ == '__main__':
    import traceback
    try:
        main()
    except Exception as e:
        # 兜底：写一份 crash 报告
        with open(SUMMARY_PATH, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## ⚠️ 脚本异常退出\n\n```\n{traceback.format_exc()}\n```\n")
        raise
