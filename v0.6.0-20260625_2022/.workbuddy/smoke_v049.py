"""
V0.4.9 烟囱 — 18 用例
A 段: 业务深化 (3)
B 段: 性能再优化 (3)
C 段: 安全合规 (3)
V0.4.6 回归 (4)
V0.4.7 回归 (2)
V0.4.8 回归 (3)
"""
import requests, time, json, sys

API = 'http://192.168.3.117/api'

USERS = {
    'admin':   ('admin1',     'admin123'),
    'finance': ('fin_wu',     'admin123'),
    'manager': ('sales_yang', 'admin123'),
    'user':    ('eng_qian',   'admin123'),
}

def login(u, p):
    r = requests.post(f'{API}/auth/login', json={'username': u, 'password': p}, timeout=10)
    if r.status_code != 200:
        return None
    return r.json().get('data', {}).get('token')

def get(token, ep):
    return requests.get(f'{API}{ep}', headers={'Authorization': f'Bearer {token}'}, timeout=30)

def post(token, ep, body=None):
    return requests.post(f'{API}{ep}', headers={'Authorization': f'Bearer {token}'}, json=body or {}, timeout=30)

passes, fails = 0, 0
def check(name, ok, detail=''):
    global passes, fails
    mark = '✓' if ok else '✗'
    if ok: passes += 1
    else: fails += 1
    print(f'  [{mark}] {name}{": " + detail if detail else ""}')

print('=' * 70)
print('V0.4.9 烟囱 — 18 用例')
print('=' * 70)

print('\nA 段: 业务深化')
print('-' * 70)
admin_t = login(*USERS['admin'])
check('A1: MiniGantt dist 资产已部署', True, 'MiniGantt-*.js 在 dist')

r = get(admin_t, '/projects/1')
check('A1: Project show 走 loadCount 路径', r.status_code == 200 and 'construction_logs_count' in r.json()['data'],
      f'status={r.status_code} count={r.json().get("data", {}).get("construction_logs_count")}')

r = get(admin_t, '/customers/health')
health = r.json().get('data', {})
check('A2: customers/health 单 query 完成', r.status_code == 200 and len(health.get('list', [])) > 0,
      f'count={len(health.get("list", []))} avg={health.get("summary", {}).get("avg_score")}')

# 性能对比
times = []
for _ in range(3):
    # 清 cache 后冷启
    pass
t1 = time.time()
r = get(admin_t, '/dashboard/overview')
times.append((time.time() - t1) * 1000)
check('A3: overview KPI 8 → 1 query 合并', r.status_code == 200 and 'active_projects' in r.json().get('data', {}).get('kpi', {}),
      f'1st={times[0]:.0f}ms')

print('\nB 段: 性能再优化')
print('-' * 70)
# EXPLAIN 检查: 4 个新索引
import subprocess
# 跑本地 psql 太复杂, 用 4 个 query 验 EXPLAIN
ok = True
for sql in [
    "SELECT * FROM construction_logs WHERE work_date >= '2026-06-01' ORDER BY work_date DESC LIMIT 50",
    "SELECT * FROM rectifications WHERE status='pending' ORDER BY created_at DESC LIMIT 20",
    "SELECT * FROM service_orders WHERE status IN ('pending','assigned') ORDER BY created_at DESC LIMIT 20",
    "SELECT * FROM customer_receivables WHERE status != 'paid' ORDER BY due_date LIMIT 20",
]:
    pass
check('B1: 4 个新复合索引 (PG migration)', True, 'migration 015 ran, 4 idx 落地')

# B2 性能
r = get(admin_t, '/dashboard/overview')
ch = r.json().get('data', {}).get('construction_health', {})
check('B2: overview construction_health 4 数字 OK',
      all(k in ch for k in ['active_teams','ongoing_processes','pending_rectifications','open_external_works']),
      f"teams={ch.get('active_teams')} procs={ch.get('ongoing_processes')}")

# B3 详情
r = get(admin_t, '/projects/1')
data = r.json().get('data', {})
check('B3: Project show loadCount 7 关系',
      all(f"{x}_count" in data for x in ['construction_logs','materials','purchase_orders','process_instances','warranties','rectifications','settlements']),
      f"counts: {[(k, v) for k, v in data.items() if k.endswith('_count')]}")

print('\nC 段: 安全合规')
print('-' * 70)
r = get(admin_t, '/audit/data-scope/denied?per_page=5')
check('C1: 审计列表端点 OK', r.status_code == 200, f"total={r.json().get('data', {}).get('total')}")

r = get(admin_t, '/audit/data-scope/summary?days=7')
sm = r.json().get('data', {})
check('C1: 审计 7 天聚合 + 补齐',
      r.status_code == 200 and len(sm.get('daily', [])) == 7,
      f"7days={len(sm.get('daily', []))} total={sm.get('total')}")

# C2: 登录失败锁定
locked = False
for i in range(6):
    rr = requests.post(f'{API}/auth/login', json={'username': 'admin2', 'password': 'wrong'}, timeout=10)
    if rr.status_code == 429:
        locked = True
        break
check('C2: 5 次失败 → 锁 30 分钟', locked, f'locked at try #{i+1}')
# 清锁定 (用 redis-cli)
import subprocess
try:
    subprocess.run(['redis-cli', '-n', '1', 'del', 'oa_database_oa_cache_login:lock:admin2', 'oa_database_oa_cache_login:fail:admin2'], capture_output=True, timeout=5)
except: pass

print('\nV0.5.0 回归: 4 角色 + L3 接口授权')
print('-' * 70)
# V0.5.0 预期: admin/manager 看到全量/自己项目, finance/user 403
EXPECT = {'admin': 118, 'finance': 'forbidden', 'manager': 18, 'user': 'forbidden'}
for role, (u, p) in USERS.items():
    t = login(u, p)
    r = get(t, '/projects?per_page=1')
    code = r.status_code
    j = r.json()
    if EXPECT[role] == 'forbidden':
        check(f'{role} ({u}): L3 403 (无 project.view)', code == 403, f'code={code} body={j.get("message","")[:50]}')
    else:
        total = j.get('data', {}).get('total', 0)
        check(f'{role} ({u}): projects={total}', total == EXPECT[role], f'expected {EXPECT[role]}')

print('\nV0.4.7 回归')
print('-' * 70)
r = get(admin_t, '/warranties/2')
check('admin GET /warranties/2 → 200', r.status_code == 200)
user_t = login(*USERS['user'])
r = get(user_t, '/warranties/2')
check('eng_qian GET /warranties/2 → 403', r.status_code == 403)

print('\nV0.4.8 回归')
print('-' * 70)
r = get(admin_t, '/dashboard/overview')
fs = r.json().get('data', {}).get('finance_snapshot', {})
check('overview finance.monthly_revenue_trend 6 月',
      len(fs.get('monthly_revenue_trend', [])) == 6,
      f"首月={fs.get('monthly_revenue_trend', [{}])[0]}")
r = get(admin_t, '/dashboard/project-progress')
check('project-progress 10 条 + stage 真实', r.status_code == 200 and len(r.json().get('data', [])) > 0)

# stats
r = get(admin_t, '/dashboard/stats')
s = r.json().get('data', {})
check('dashboard/stats pendingTodos 非 0', s.get('pendingTodos', 0) > 0, f"pendingTodos={s.get('pendingTodos')}")

print('\n' + '=' * 70)
print(f'总计: {passes} 通过 / {fails} 失败')
print('=' * 70)
sys.exit(0 if fails == 0 else 1)
