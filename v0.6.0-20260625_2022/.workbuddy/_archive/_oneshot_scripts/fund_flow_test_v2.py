"""
OA 资金流完整测试 v2 — 对齐真实后端端点
测试账号: admin / admin123
目标: 172.20.0.139
"""
import requests, json, time, sys

BASE = 'http://172.20.0.139/api'
s = requests.Session()
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

def login():
    r = s.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
    if r.status_code != 200:
        print(f'❌ 登录失败: {r.status_code}'); sys.exit(1)
    s.headers['Authorization'] = f'Bearer {r.json()["data"]["token"]}'
    print('  [登录] ✅')

def api(method, url, data=None, params=None):
    fn = getattr(s, method)
    kw = {}
    if data is not None: kw['json'] = data
    if params is not None: kw['params'] = params
    try:
        r = fn(f'{BASE}{url}', timeout=15, **kw)
    except Exception as e:
        print(f'  [❌] {method.upper()} {url} → {e}'); return False, {}
    code = r.status_code
    try: body = r.json()
    except: body = r.text[:300]
    ok = 200 <= code < 400
    tag = '✅' if ok else '❌'
    print(f'  [{tag}] {method.upper()} {url} → {code}')
    if not ok: print(f'      响应: {body}')
    return ok, body

# ── 主测试 ─────────────────────────────────────────────
login()
ts = int(time.time())
results = []

def log(step, ok, msg=''):
    results.append((step, ok, msg))
    tag = '✅' if ok else '❌'
    print(f'  {tag} {step}{" → "+msg if msg else ""}')

print('=' * 60)
print('💰 OA 资金流完整测试 v2')
print('=' * 60)

# ── 1. 新建项目 ──────────────────────────────────────
print('\n── 1. 新建项目 ───────────────────────────────')
ok, proj = api('post', '/projects', {
    'project_no': f'FLOW-{ts}',
    'name': '资金流测试项目',
    'customer_id': 1,
    'manager_id': 1,
    'status': 'in_progress',
    'start_date': '2026-06-01',
    'end_date': '2026-12-31',
    'budget_device': 50000,
    'budget_material': 30000,
    'budget_labor': 20000,
})
project_id = None
if ok:
    project_id = proj['data']['id']
    log('新建项目', True, f'ID={project_id}')
else:
    log('新建项目', False)

# ── 2. 新建报销 ──────────────────────────────────────
print('\n── 2. 新建报销 ───────────────────────────────')
expense_id = None
if project_id:
    ok, exp = api('post', '/expenses', {
        'category': '材料费',
        'project_id': project_id,
        'items': [
            {'amount': 5000, 'description': '摄像头采购'},
            {'amount': 3500, 'description': '安装工时'},
        ],
    })
    if ok:
        expense_id = exp['data']['id']
        log('新建报销', True, f'ID={expense_id} 8500')
    else:
        log('新建报销', False)
else:
    log('新建报销', False, '跳过（无项目）')

# ── 3. 审批报销 ──────────────────────────────────────
print('\n── 3. 审批报销 ───────────────────────────────')
if expense_id:
    ok, _ = api('post', f'/expenses/{expense_id}/approve', {'action': 'approved'})
    log('审批报销', ok)
else:
    log('审批报销', False, '跳过')

# ── 4. 新建应收款 ───────────────────────────────────
print('\n── 4. 新建应收款 ───────────────────────────────')
receivable_id = None
ok, rec = api('post', '/finance/receivables', {
    'project_id': project_id,
    'customer_id': 1,
    'amount': 150000,
    'balance': 150000,
    'issue_date': '2026-06-01',
    'due_date': '2026-07-01',
    'status': 'pending',
    'description': '项目进度款-第一阶段',
})
if ok:
    receivable_id = rec['data']['id']
    log('新建应收款', True, f'ID={receivable_id} 150000')
else:
    log('新建应收款', False)

# ── 5. 新建应付款 ───────────────────────────────────
print('\n── 5. 新建应付款 ───────────────────────────────')
payable_id = None
    ok, pay = api('post', '/finance/payables', {
        'project_id': project_id,
        'amount': 30000,
        'due_date': '2026-07-15',
        'notes': '设备采购款',
    })
if ok:
    payable_id = pay['data']['id']
    log('新建应付款', True, f'ID={payable_id} 30000')
else:
    log('新建应付款', False)

# ── 6. 新建账户 ─────────────────────────────────────
print('\n── 6. 新建账户 ───────────────────────────────')
account_id = None
ok, acct = api('post', '/finance/accounts', {
    'name': f'测试账户-{ts}',
    'type': 'bank',
    'bank_name': '测试银行',
    'account_number': f'TEST-{ts}',
    'balance': 200000,
    'status': 'active',
})
if ok:
    account_id = acct['data']['id']
    log('新建账户', True, f'ID={account_id} 余额200000')
else:
    log('新建账户', False)

# ── 7. 收款（应收款 → 账户） ─────────────────────
print('\n── 7. 收款（应收款 → 账户） ─────────────────')
if receivable_id and account_id:
    ok, _ = api('post', f'/finance/receivables/{receivable_id}/payments', {
        'account_id': account_id,
        'amount': 50000,
        'payment_date': '2026-06-22',
        'remark': '资金流测试收款',
    })
    log('收款', ok, '50000' if ok else '')
else:
    log('收款', False, '跳过')

# ── 8. 付款（应付款 → 账户） ─────────────────────
print('\n── 8. 付款（应付款 → 账户） ─────────────────')
if payable_id and account_id:
    ok, _ = api('post', f'/finance/payables/{payable_id}/payments', {
        'account_id': account_id,
        'amount': 10000,
        'payment_date': '2026-06-22',
        'remark': '资金流测试付款',
    })
    log('付款', ok, '10000' if ok else '')
else:
    log('付款', False, '跳过')

# ── 9. 验证账户余额 ──────────────────────────────────
print('\n── 9. 验证账户余额 ─────────────────────────────')
if account_id:
    ok, tx = api('get', f'/finance/accounts/{account_id}/transactions')
    if ok:
        log('账户流水', True, f'{len(tx.get("data", []))} 笔')
    else:
        # 尝试账户详情
        ok2, acct = api('get', f'/finance/accounts/{account_id}')
        if ok2:
            bal = acct['data'].get('balance', 'N/A')
            log('账户余额', True, f'{bal}')
        else:
            log('账户余额', False)
else:
    log('账户流水', False, '跳过')

# ── 10. 财务总览 ──────────────────────────────────
print('\n── 10. 财务总览 ──────────────────────────────')
for ep in ['/finance/overview', '/finance/summary']:
    ok, ov = api('get', ep)
    if ok:
        log(f'财务总览 ({ep})', True)
        break
else:
    log('财务总览', False)

# ── 汇总 ────────────────────────────────────────────────
print('\n' + '=' * 60)
print('📊 测试结果汇总')
print('=' * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
for step, ok, msg in results:
    tag = '  ✅' if ok else '  ❌'
    print(f'{tag} {step}{" → "+msg if msg else ""}')
print(f'\n合计: {passed}/{len(results)} 通过 ({passed*100//len(results)}%)')
print('=' * 60)
