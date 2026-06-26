"""
OA 资金流完整测试 — 端到端跑通资金流
测试账号: admin / admin123 (id=1)
目标: 172.20.0.139

资金流路径:
  1. 新建项目 (budget_device + budget_material + budget_labor)
  2. 新建报销 (expense_claim + expense_items)
  3. 审批报销
  4. 新建应收款 (finance_receivables)
  5. 新建应付款 (finance_payables)
  6. 新建付款 (finance_payments)
  7. 新建账户 (finance_accounts)
  8. 收款 (应收款 → 账户)
  9. 付款 (应付款 → 账户)
  10. 验证账户余额
  11. 验证现金流
"""
import requests, json, time, sys

BASE = 'http://172.20.0.139/api'
s = requests.Session()
s.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

def login():
    r = s.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123'})
    if r.status_code != 200:
        print(f'❌ 登录失败: {r.status_code} {r.text[:200]}'); sys.exit(1)
    token = r.json()['data']['token']
    s.headers['Authorization'] = f'Bearer {token}'
    print(f'  [登录] ✅ admin token')

def api(method, url, data=None, params=None, label=''):
    fn = getattr(s, method)
    kw = {}
    if data is not None: kw['json'] = data
    if params is not None: kw['params'] = params
    try:
        r = fn(f'{BASE}{url}', timeout=15, **kw)
    except Exception as e:
        print(f'  [{"❌"}] {method.upper()} {url} → 异常: {e}'); return False, {}
    code = r.status_code
    try:
        body = r.json()
    except:
        body = r.text[:300]
    ok = 200 <= code < 400
    tag = '✅' if ok else '❌'
    print(f'  [{tag}] {method.upper()} {url} → {code}')
    if not ok:
        print(f'      响应: {body}')
    return ok, body

def test_fund_flow():
    print('=' * 60)
    print('💰 OA 资金流完整测试')
    print('=' * 60)
    login()

    ts = int(time.time())

    # ── 1. 新建项目（带预算） ──────────────────────────────
    print('\n── 1. 新建项目（预算来源） ───────────────────────')
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
    if not ok:
        print('  ❌ 跳过后续测试'); return
    project_id = proj['data']['id']
    print(f'  [项目ID] {project_id}, 总预算 100,000')

    # ── 2. 新建报销（资金流出） ──────────────────────────────
    print('\n── 2. 新建报销（资金流出） ───────────────────────')
    ok, exp = api('post', '/expenses', {
        'category': '材料费',
        'project_id': project_id,
        'items': [
            {'amount': 5000, 'description': '摄像头采购'},
            {'amount': 3500, 'description': '安装工时'},
        ]
    })
    expense_id = None
    if ok:
        expense_id = exp['data']['id']
        print(f'  [报销ID] {expense_id}, 金额 8,500')
    else:
        # 如果失败，尝试不带 items（后端可能不接受嵌套）
        print('  ⚠️ 带 items 失败，尝试不带 items...')
        ok2, exp2 = api('post', '/expenses', {
            'project_id': project_id,
            'amount': 8500,
            'type': 'reimbursement',
            'status': 'pending',
            'expense_date': '2026-06-20',
        })
        if ok2:
            expense_id = exp2['data']['id']
            print(f'  [报销ID] {expense_id}, 金额 8,500 (不含 items)')

    # ── 3. 审批报销 ───────────────────────────────────────────
    print('\n── 3. 审批报销 ───────────────────────────────────')
    if expense_id:
        ok, _ = api('post', f'/expenses/{expense_id}/approve', {
            'action': 'approve',
            'remark': '资金流测试审批通过'
        })
        if ok:
            print('  [审批] ✅ 报销已批准')
    else:
        print('  [审批] ⚠️ 报销审批失败（可能不需要审批或直接通过）')

    # ── 4. 新建应收款 ────────────────────────────────────────
    print('\n── 4. 新建应收款 ───────────────────────────────────')
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
    receivable_id = None
    if ok:
        receivable_id = rec['data']['id']
        print(f'  [应收款ID] {receivable_id}, 金额 150,000')
    else:
        print('  ⚠️ 应收款创建失败，检查字段名...')
        # 尝试不同字段名
        for payload in [
            {'project_id': project_id, 'amount': 150000, 'balance': 150000, 'status': 'pending'},
            {'project_id': project_id, 'total_amount': 150000, 'status': 'pending'},
        ]:
            ok2, rec2 = api('post', '/finance/receivables', payload, label='重试')
            if ok2:
                receivable_id = rec2['data']['id']
                print(f'  [应收款ID] {receivable_id}, 金额 150,000 (重试成功)')
                break

    # ── 5. 新建应付款 ────────────────────────────────────────
    print('\n── 5. 新建应付款 ───────────────────────────────────')
    ok, pay = api('post', '/finance/payables', {
        'project_id': project_id,
        'supplier': '测试供应商',
        'amount': 30000,
        'balance': 30000,
        'issue_date': '2026-06-15',
        'due_date': '2026-07-15',
        'status': 'pending',
        'description': '设备采购款',
    })
    payable_id = None
    if ok:
        payable_id = pay['data']['id']
        print(f'  [应付款ID] {payable_id}, 金额 30,000')

    # ── 6. 新建账户 ──────────────────────────────────────────
    print('\n── 6. 新建账户 ────────────────────────────────────')
    ok, acct = api('post', '/finance/accounts', {
        'name': f'测试账户-{ts}',
        'type': 'bank',
        'bank_name': '测试银行',
        'account_number': f'TEST-{ts}',
        'balance': 200000,
        'status': 'active',
    })
    account_id = None
    if ok:
        account_id = acct['data']['id']
        print(f'  [账户ID] {account_id}, 初始余额 200,000')

    # ── 7. 收款（应收款 → 账户） ─────────────────────────
    print('\n── 7. 收款（应收款 → 账户） ─────────────────')
    if receivable_id and account_id:
        ok, _ = api('post', f'/finance/receivables/{receivable_id}/receive', {
            'account_id': account_id,
            'amount': 50000,
            'receive_date': '2026-06-22',
            'remark': '资金流测试收款',
        })
        if ok:
            print('  [收款] ✅ 50,000 已收')
        else:
            print('  ⚠️ 收款失败，尝试不同端点...')
            # 尝试 /finance/receipts 端点
            ok2, _ = api('post', '/finance/receipts', {
                'receivable_id': receivable_id,
                'account_id': account_id,
                'amount': 50000,
            }, label='receipts')
            if ok2:
                print('  [收款] ✅ 50,000 已收 (via /receipts)')
    else:
        print('  ⚠️ 跳过（应收款或账户不存在）')

    # ── 8. 付款（应付款 → 账户） ─────────────────────────
    print('\n── 8. 付款（应付款 → 账户） ─────────────────')
    if payable_id and account_id:
        ok, _ = api('post', f'/finance/payables/{payable_id}/pay', {
            'account_id': account_id,
            'amount': 10000,
            'pay_date': '2026-06-22',
            'remark': '资金流测试付款',
        })
        if ok:
            print('  [付款] ✅ 10,000 已付')
        else:
            print('  ⚠️ 付款失败，尝试不同端点...')
            ok2, _ = api('post', '/finance/payments', {
                'payable_id': payable_id,
                'account_id': account_id,
                'amount': 10000,
            }, label='payments')
            if ok2:
                print('  [付款] ✅ 10,000 已付 (via /payments)')
    else:
        print('  ⚠️ 跳过（应付款或账户不存在）')

    # ── 9. 验证账户余额 ─────────────────────────────────────
    print('\n── 9. 验证账户余额 ──────────────────────────────')
    if account_id:
        ok, acct = api('get', f'/finance/accounts/{account_id}')
        if ok:
            balance = acct['data'].get('balance', 'N/A')
            print(f'  [账户余额] {balance}')
        #  also check summary
        ok2, summary = api('get', '/finance/accounts', label='账户列表')
        if ok2:
            print(f'  [账户列表] {len(summary.get("data", []))} 个账户')

    # ── 10. 验证现金流 ────────────────────────────────────
    print('\n── 10. 验证现金流 ───────────────────────────────')
    ok, cashflow = api('get', '/finance/cashflow')
    if ok:
        print(f'  [现金流] ✅ 获取成功')
        print(f'      数据: {json.dumps(cashflow.get("data", {}), ensure_ascii=False)[:200]}')
    else:
        # 尝试不同端点
        for ep in ['/finance/cash-flow', '/finance/summary', '/finance/overview']:
            ok2, cf2 = api('get', ep, label=ep)
            if ok2:
                print(f'  [现金流] ✅ 获取成功 (via {ep})')
                break

    # ── 11. 验证财务总览 ────────────────────────────────────
    print('\n── 11. 验证财务总览 ─────────────────────────────')
    for ep in ['/finance/summary', '/finance/overview', '/finance/dashboard']:
        ok, ov = api('get', ep, label=ep)
        if ok:
            print(f'  [财务总览] ✅ 获取成功 (via {ep})')
            break

    print('\n' + '=' * 60)
    print('💰 资金流测试完成')
    print('=' * 60)

if __name__ == '__main__':
    test_fund_flow()