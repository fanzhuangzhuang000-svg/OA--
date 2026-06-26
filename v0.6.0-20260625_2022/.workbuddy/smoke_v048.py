"""V0.4.8 烟囱 — 15 用例覆盖 A/B/C 三个段 + V0.4.6 回归

跑在 117 端 (requests 已有, 无 paramiko)
"""

import subprocess
import time
import sys
import requests

API = 'http://127.0.0.1:8081/api'

def run_local(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout + r.stderr

def login(username, password):
    r = requests.post(API + '/auth/login', json={'username': username, 'password': password}, timeout=10)
    if r.status_code != 200: return None
    return r.json()['data']['token']

def get_count(token, ep):
    h = {'Authorization': f'Bearer {token}'}
    r = requests.get(API + ep + '?per_page=1', headers=h, timeout=10)
    if r.status_code != 200: return None
    return r.json()['data'].get('total', 0)

def main():
    passed = 0
    failed = 0

    print('=' * 70)
    print('V0.4.8 烟囱 — 15 用例')
    print('=' * 70)

    # === A 段 ===
    print('A 段: 稳定性收口')
    print('-' * 70)

    # A1: phpunit 12 用例
    out = run_local('cd /var/www/oa-api && sudo -n -u www-data vendor/bin/phpunit 2>&1 | grep -E "OK|FAIL|Tests:" | head -3')
    if 'OK (12 tests' in out:
        print('  [1/15] A1: phpunit 12 用例 OK ✓'); passed += 1
    else:
        print('  [1/15] A1: phpunit 失败:'); print(out[:300]); failed += 1

    # A2: login 10 连测
    err = 0
    for i in range(10):
        r = requests.post(API + '/auth/login', json={'username':'admin1','password':'admin123'}, timeout=10)
        if r.status_code != 200: err += 1
    if err == 0:
        print('  [2/15] A2: login 10 连测全 200 (throttle 30/min) ✓'); passed += 1
    else:
        print(f'  [2/15] A2: 10 连测有 {err} 错 ✗'); failed += 1

    # A3: project-progress 真实数据
    token = login('admin1', 'admin123')
    r2 = requests.get(API + '/dashboard/project-progress', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    data = r2.json().get('data', [])
    has_stage = bool(data) and data[0].get('stage') is not None
    if has_stage and len(data) == 10:
        print(f'  [3/15] A3: project-progress 10 条 + stage 真实 ✓'); passed += 1
    else:
        print(f'  [3/15] A3: count={len(data)} stage={data[0].get("stage") if data else None} ✗'); failed += 1

    # === B 段 ===
    print('B 段: 性能优化')
    print('-' * 70)

    # B1: PG 索引已建
    sql = "SELECT indexname FROM pg_indexes WHERE indexname IN ('construction_logs_status_date_index','projects_status_created_at_index','rectifications_status_created_at_index')"
    out = run_local(f'sudo -n -u postgres psql -d security_oa -t -c "{sql}"')
    idx_count = len([l for l in out.split('\n') if l.strip()])
    if idx_count >= 3:
        print(f'  [4/15] B1: 新建 {idx_count} 个复合索引 ✓'); passed += 1
    else:
        print(f'  [4/15] B1: 索引缺失 ({idx_count}) ✗'); failed += 1

    # B2: withCount 生效
    r2 = requests.get(API + '/customers?per_page=5', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    data = r2.json()['data']['data']
    has_pc = data[0].get('project_count') is not None
    has_fc = data[0].get('follow_ups_count') is not None
    if has_pc and has_fc:
        print('  [5/15] B2: customers withCount 生效 (project_count + follow_ups_count) ✓'); passed += 1
    else:
        print(f'  [5/15] B2: project_count={has_pc} follow_ups_count={has_fc} ✗'); failed += 1

    # B3: redis cache 落 db 1
    r2 = requests.get(API + '/dashboard/stats', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    out = run_local("redis-cli -n 1 keys '*dashboard:stats*' 2>&1")
    if 'dashboard:stats:74' in out:
        print('  [6/15] B3: dashboard stats 落 redis (key=dashboard:stats:74) ✓'); passed += 1
    else:
        print(f'  [6/15] B3: redis key 缺失, out={out.strip()[:200]} ✗'); failed += 1

    # === C 段 ===
    print('C 段: 业务可视化')
    print('-' * 70)

    # C2: monthly_revenue_trend 6 个月
    r2 = requests.get(API + '/dashboard/overview', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    trend = r2.json()['data']['finance_snapshot'].get('monthly_revenue_trend')
    if trend and len(trend) == 6:
        first = trend[0]
        print(f'  [7/15] C2: monthly_revenue_trend 6 月齐全 (首月 {first["month"]}: ¥{first["revenue"]}万) ✓'); passed += 1
    else:
        print(f'  [7/15] C2: trend_len={len(trend) if trend else 0} ✗'); failed += 1

    # C1: 项目详情 gantt tab (前端 build 验证)
    out = run_local('ls /var/www/oa-web/assets/ | grep -iE "Overview|Gantt" | wc -l')
    if int(out.strip()) > 0:
        print(f'  [8/15] C1: dist 含 Overview/Gantt 资产 ({out.strip()} 个) ✓'); passed += 1
    else:
        print('  [8/15] C1: 缺 dist assets ✗'); failed += 1

    # C3: overview 全数据
    r2 = requests.get(API + '/dashboard/overview', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    data = r2.json()['data']
    has_all = (data.get('is_full_data') is True
               and bool(data.get('kpi'))
               and bool(data.get('finance_snapshot'))
               and bool(data.get('project_stage_distribution')))
    if has_all:
        print('  [9/15] C3: overview 8 图数据完整 (is_full + kpi + finance + project_stage) ✓'); passed += 1
    else:
        print(f'  [9/15] C3: data 不完整 ✗'); failed += 1

    # === 额外: V0.4.6 回归 4 角色 ===
    print('V0.4.6 回归: 4 角色')
    print('-' * 70)

    cases = [
        ('admin1', 118), ('fin_wu', 118), ('sales_yang', 18), ('eng_qian', 20)
    ]
    ok = True
    for i, (u, expected) in enumerate(cases, start=10):
        t = login(u, 'admin123')
        if not t: print(f'  [{i}/15] {u}: login 失败 ✗'); ok = False; failed += 1; continue
        c = get_count(t, '/projects')
        if c == expected:
            print(f'  [{i}/15] {u}: 看到 {c} 项目 (expected {expected}) ✓'); passed += 1
        else:
            print(f'  [{i}/15] {u}: 看到 {c} 项目 (expected {expected}) ✗'); ok = False; failed += 1

    # === 额外: V0.4.7 回归 5 用例 (admin 详情) ===
    print('V0.4.7 回归: 详情 + scope')
    print('-' * 70)
    # 已有 warranty id 2 (admin1 创建的)
    r2 = requests.get(API + '/warranties/2', headers={'Authorization': f'Bearer {token}'}, timeout=10)
    if r2.status_code == 200:
        print(f'  [14/15] admin GET /warranties/2 → 200 ✓'); passed += 1
    else:
        print(f'  [14/15] admin GET /warranties/2 → {r2.status_code} ✗'); failed += 1
    # eng_qian 看 warranty 2
    et = login('eng_qian', 'admin123')
    r2 = requests.get(API + '/warranties/2', headers={'Authorization': f'Bearer {et}'}, timeout=10)
    if r2.status_code == 403:
        print(f'  [15/15] eng_qian GET /warranties/2 → 403 ✓'); passed += 1
    else:
        print(f'  [15/15] eng_qian GET /warranties/2 → {r2.status_code} ✗'); failed += 1

    print('=' * 70)
    print(f'总计: {passed} 通过 / {failed} 失败')
    print('=' * 70)
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
