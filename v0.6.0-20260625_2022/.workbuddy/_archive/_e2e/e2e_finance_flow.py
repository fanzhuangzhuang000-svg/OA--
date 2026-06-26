"""
完整资金流测试 — OA 系统
目标: 验证账户/应收/收款/应付/付款/转账全链路闭环

流程:
1) 登录拿 token
2) 创建两个测试账户 A (起始 100万) / B (起始 0)
3) 转账 A→B 30万
4) 创建应收 (客户 A) 100万
5) 部分收款 40万 → 入账到账户 A
6) 继续收款 60万 → 应收清零 → 自动入账到账户 A
7) 创建应付 (供应商 X) 50万
8) 部分付款 20万 → 出账从账户 A
9) 剩余付款 30万 → 应付清零 → 账户 A 继续扣
10) 全程校验账户余额 / 应收应付余额 / 支付总账
11) 清理测试数据 (可选)

最终预期:
- 账户 A 余额 = 100 + 40 + 60 - 30 - 20 - 30 = 120 万 (毛利假设0)
- 账户 B 余额 = 0 + 30 = 30 万
- 应收总额 100万 = 已收 100万 (清零)
- 应付总额 50万 = 已付 50万 (清零)
- 收款记录: 2 笔 (40 + 60)
- 付款记录: 2 笔 (20 + 30)
- 转账记录: 1 笔 (30, 双向记)
"""
import sys, json, time, requests
from datetime import date

API = 'http://172.20.0.139/api'

# 颜色
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def c(msg, color=GREEN, bold=False):
    return f'{BOLD if bold else ""}{color}{msg}{RESET}'

def log_section(title):
    print(f'\n{c("=" * 70, CYAN, bold=True)}')
    print(f'{c("  " + title, CYAN, bold=True)}')
    print(f'{c("=" * 70, CYAN, bold=True)}')

def log_step(n, msg):
    print(f'\n{c(f"[步骤 {n}] {msg}", BLUE, bold=True)}')

def log_ok(msg, detail=''):
    print(f'  {c("✓", GREEN, bold=True)} {msg}' + (f'  {c(detail, YELLOW)}' if detail else ''))

def log_fail(msg, detail=''):
    print(f'  {c("✗", RED, bold=True)} {msg}' + (f'  {c(detail, YELLOW)}' if detail else ''))

def log_warn(msg, detail=''):
    print(f'  {c("⚠", YELLOW, bold=True)} {msg}' + (f'  {c(detail, YELLOW)}' if detail else ''))

# =======================
# 工具函数
# =======================
class OAClient:
    def __init__(self, base):
        self.base = base
        self.token = None
        self.session = requests.Session()
    
    def login(self, username='admin', password='admin123'):
        r = self.session.post(f'{self.base}/auth/login', json={'username': username, 'password': password})
        r.raise_for_status()
        d = r.json()
        if d.get('code') != 0:
            raise Exception(f'login failed: {d}')
        self.token = d['data']['token']
        self.user_id = d['data']['user']['id']
        self.session.headers['Authorization'] = f'Bearer {self.token}'
        return self.token
    
    def get(self, path, **kwargs):
        r = self.session.get(f'{self.base}{path}', **kwargs)
        return r.json() if r.status_code < 500 else {'_http': r.status_code, 'msg': r.text}
    
    def post(self, path, **kwargs):
        r = self.session.post(f'{self.base}{path}', **kwargs)
        return r.json() if r.status_code < 500 else {'_http': r.status_code, 'msg': r.text}
    
    def put(self, path, **kwargs):
        r = self.session.put(f'{self.base}{path}', **kwargs)
        return r.json() if r.status_code < 500 else {'_http': r.status_code, 'msg': r.text}
    
    def delete(self, path, **kwargs):
        r = self.session.delete(f'{self.base}{path}', **kwargs)
        return r.json() if r.status_code < 500 else {'_http': r.status_code, 'msg': r.text}


def unwrap(d):
    """解包后端响应 {code, data}"""
    if not isinstance(d, dict):
        return d
    if d.get('code') == 0:
        return d.get('data')
    return d


def get_first_id(data, key='id'):
    """从分页结构取第一条 (支持 1-3 层嵌套)"""
    if not isinstance(data, dict):
        if isinstance(data, list) and data:
            return data[0].get(key) if isinstance(data[0], dict) else None
        return None
    for _ in range(3):
        inner = data.get('data') if isinstance(data, dict) else None
        if isinstance(inner, list) and inner:
            return inner[0].get(key) if isinstance(inner[0], dict) else None
        if isinstance(inner, dict):
            data = inner
        else:
            return None
    return None


def _extract_list(data):
    """统一解包分页结构 {data: {data: [...], total}} 或 {data: [...]} 或 [...]"""
    if not isinstance(data, dict):
        return data if isinstance(data, list) else []
    if 'data' not in data:
        return []
    inner = data['data']
    if isinstance(inner, list):
        return inner
    if isinstance(inner, dict) and 'data' in inner:
        return inner['data'] if isinstance(inner['data'], list) else []
    return []


def get_account_by_id(cli, account_id):
    """从 accounts 列表找指定 id 的账户 — 后端 accounts 接口 per_page 默认 15, 必须翻页"""
    for page in range(1, 10):
        res = cli.get('/finance/accounts', params={'per_page': 50, 'page': page})
        lst = _extract_list(res)
        if not lst:
            break
        for a in lst:
            if a.get('id') == account_id:
                return a
    return None


def get_receivable_by_id(cli, rid):
    """从 receivables 列表找指定 id"""
    res = cli.get('/finance/receivables', params={'per_page': 100})
    lst = _extract_list(res)
    if isinstance(lst, list):
        for r in lst:
            if r.get('id') == rid:
                return r
    return None


def get_payable_by_id(cli, pid):
    """从 payables 列表找指定 id"""
    res = cli.get('/finance/payables', params={'per_page': 100})
    lst = _extract_list(res)
    if isinstance(lst, list):
        for p in lst:
            if p.get('id') == pid:
                return p
    return None


# =======================
# 测试断言工具
# =======================
class FlowChecker:
    def __init__(self):
        self.checks = []
    
    def check(self, name, expected, actual, tolerance=0.01):
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            ok = abs(float(expected) - float(actual)) <= tolerance
        else:
            ok = expected == actual
        self.checks.append({'name': name, 'expected': expected, 'actual': actual, 'ok': ok})
        if ok:
            log_ok(name, f'期望={expected}, 实际={actual}')
        else:
            log_fail(name, f'期望={expected}, 实际={actual}')
        return ok
    
    def summary(self):
        passed = sum(1 for c in self.checks if c['ok'])
        total = len(self.checks)
        return passed, total


# =======================
# 主流程
# =======================
def main():
    results = {'steps': [], 'checks': [], 'created': {'accounts': [], 'receivables': [], 'payables': [], 'invoices': [], 'payments': []}}
    checker = FlowChecker()
    
    log_section('OA 系统完整资金流测试 (E2E Finance Flow)')
    ts = int(time.time())
    
    # ========== 步骤 1: 登录 ==========
    log_step(1, '系统登录')
    cli = OAClient(API)
    try:
        cli.login()
        log_ok(f'登录成功, user_id={cli.user_id}', f'admin / admin123')
        results['steps'].append({'step': 1, 'name': '登录', 'ok': True})
    except Exception as e:
        log_fail('登录失败', str(e))
        results['steps'].append({'step': 1, 'name': '登录', 'ok': False, 'error': str(e)})
        return results
    
    # ========== 步骤 2: 查询现有数据 (客户/供应商/项目) ==========
    log_step(2, '查询基础数据 (找现有客户/供应商)')
    
    customers = cli.get('/customers', params={'per_page': 5})
    customer_id = get_first_id(customers, 'id')
    if customer_id:
        log_ok(f'找到客户', f'id={customer_id}')
    else:
        # 创建一个测试客户
        log_warn('无客户,创建一个')
        new_cust = cli.post('/customers', json={
            'name': f'资金流测试客户-{int(time.time())}',
            'type': 'enterprise',
            'contact_person': '测试',
            'contact_phone': '13800138000',
            'level': 'A',
            'status': 'active'
        })
        if unwrap(new_cust):
            customer_id = unwrap(new_cust).get('id') if isinstance(unwrap(new_cust), dict) else None
        if not customer_id:
            log_fail('无法获取客户,终止')
            return results
    
    suppliers = cli.get('/projects/suppliers', params={'per_page': 10})
    supplier_id = get_first_id(suppliers, 'id')
    if supplier_id:
        log_ok(f'找到供应商', f'id={supplier_id}')
    else:
        log_fail('无供应商且无法创建,终止')
        return results
    
    projects = cli.get('/projects', params={'per_page': 5})
    project_id = get_first_id(projects, 'id')
    if project_id:
        log_ok(f'找到项目', f'id={project_id}')
    else:
        log_warn('无项目,跳过 project_id')
        project_id = None
    
    # ========== 步骤 3: 创建两个测试资金账户 ==========
    log_step(3, '创建两个测试资金账户 A (100万) / B (0)')
    
    acc_a = cli.post('/finance/accounts', json={
        'name': f'测试账户A-{ts}',
        'type': 'bank',
        'bank_name': '工商银行',
        'account_no': f'622200{ts:010d}',
        'balance': 1000000.00,
        'currency': 'CNY',
        'status': 'active',
        'remark': '资金流测试账户A'
    })
    acc_a_id = unwrap(acc_a).get('id') if isinstance(unwrap(acc_a), dict) else None
    if acc_a_id:
        log_ok('账户 A 创建', f'id={acc_a_id}, 余额=100万')
        results['created']['accounts'].append(acc_a_id)
    else:
        log_fail('账户 A 创建失败', json.dumps(acc_a, ensure_ascii=False)[:200])
        return results
    
    acc_b = cli.post('/finance/accounts', json={
        'name': f'测试账户B-{ts}',
        'type': 'bank',
        'bank_name': '建设银行',
        'account_no': f'622200{ts + 1:010d}',
        'balance': 0.00,
        'currency': 'CNY',
        'status': 'active',
        'remark': '资金流测试账户B'
    })
    acc_b_id = unwrap(acc_b).get('id') if isinstance(unwrap(acc_b), dict) else None
    if acc_b_id:
        log_ok('账户 B 创建', f'id={acc_b_id}, 余额=0')
        results['created']['accounts'].append(acc_b_id)
    else:
        log_fail('账户 B 创建失败', json.dumps(acc_b, ensure_ascii=False)[:200])
        return results
    
    # ========== 步骤 4: 转账 A→B 30万 ==========
    log_step(4, '转账 A → B 30万')
    today = date.today().isoformat()
    transfer = cli.post('/finance/accounts/transfer', json={
        'from_account_id': acc_a_id,
        'to_account_id': acc_b_id,
        'amount': 300000.00,
        'transfer_date': today,
        'method': '内部转账',
        'remark': '资金流测试: A→B 30万'
    })
    transfer_data = unwrap(transfer)
    # 后端 transferAccount 返回 [outPayment, inPayment] 数组
    if isinstance(transfer_data, list) and len(transfer_data) >= 2:
        log_ok('转账成功', f'out={transfer_data[0].get("id")}, in={transfer_data[1].get("id")}, 双记账')
        results['created']['payments'].extend([transfer_data[0].get('id'), transfer_data[1].get('id')])
    elif isinstance(transfer_data, dict) and transfer_data.get('id'):
        log_ok('转账成功', f'id={transfer_data.get("id")}')
        results['created']['payments'].append(transfer_data.get('id'))
    else:
        log_fail('转账失败', json.dumps(transfer, ensure_ascii=False)[:200])
    
    # 校验余额
    acc_a_info = get_account_by_id(cli, acc_a_id)
    acc_b_info = get_account_by_id(cli, acc_b_id)
    checker.check('转账后账户A余额', 700000, float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0)
    checker.check('转账后账户B余额', 300000, float(acc_b_info.get('balance', 0)) if isinstance(acc_b_info, dict) else 0)
    
    # ========== 步骤 5: 创建应收 (客户A) 100万 ==========
    log_step(5, f'创建应收: 客户#{customer_id} 100万')
    recv = cli.post('/finance/receivables', json={
        'customer_id': customer_id,
        'project_id': project_id,
        'amount': 1000000.00,
        'due_date': '2026-12-31',
        'notes': f'资金流测试: 应收 100万, 客户#{customer_id}'
    })
    recv_data = unwrap(recv)
    recv_id = recv_data.get('id') if isinstance(recv_data, dict) else None
    if recv_id:
        log_ok('应收创建', f'id={recv_id}, 状态={recv_data.get("status")}, 应收金额=100万, 已收=0, 未收=100万')
        results['created']['receivables'].append(recv_id)
    else:
        log_fail('应收创建失败', json.dumps(recv, ensure_ascii=False)[:200])
        return results
    
    checker.check('初始未收金额', 1000000, float(recv_data.get('remaining_amount', 0)))
    checker.check('初始状态', 'pending', recv_data.get('status'))
    
    # ========== 步骤 6: 部分收款 40万 → 入账到账户 A ==========
    log_step(6, '部分收款 40万 → 入账账户A')
    pay1 = cli.post(f'/finance/receivables/{recv_id}/payments', json={
        'amount': 400000.00,
        'payment_date': today,
        'account_id': acc_a_id,
        'method': '银行转账',
        'operator': '测试员',
        'remark': '资金流测试: 部分收款 40万'
    })
    pay1_data = unwrap(pay1)
    if isinstance(pay1_data, dict) and pay1_data.get('id'):
        log_ok('收款 40万 成功', f'payment_id={pay1_data.get("id")}')
        results['created']['payments'].append(pay1_data.get('id'))
    else:
        log_fail('收款 40万 失败', json.dumps(pay1, ensure_ascii=False)[:200])
    
    # 校验
    acc_a_info = get_account_by_id(cli, acc_a_id)
    recv_info = get_receivable_by_id(cli, recv_id)
    checker.check('部分收款后账户A余额', 700000 + 400000, float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0)
    checker.check('应收已收金额', 400000, float(recv_info.get('received_amount', 0)) if isinstance(recv_info, dict) else 0)
    checker.check('应收未收金额', 600000, float(recv_info.get('remaining_amount', 0)) if isinstance(recv_info, dict) else 0)
    checker.check('应收状态变为 partial', 'partial', recv_info.get('status') if isinstance(recv_info, dict) else None)
    
    # ========== 步骤 7: 继续收款 60万 → 应收清零 ==========
    log_step(7, '剩余收款 60万 → 应收清零')
    pay2 = cli.post(f'/finance/receivables/{recv_id}/payments', json={
        'amount': 600000.00,
        'payment_date': today,
        'account_id': acc_a_id,
        'method': '银行转账',
        'operator': '测试员',
        'remark': '资金流测试: 剩余收款 60万'
    })
    pay2_data = unwrap(pay2)
    if isinstance(pay2_data, dict) and pay2_data.get('id'):
        log_ok('收款 60万 成功', f'payment_id={pay2_data.get("id")}')
        results['created']['payments'].append(pay2_data.get('id'))
    else:
        log_fail('收款 60万 失败', json.dumps(pay2, ensure_ascii=False)[:200])
    
    acc_a_info = get_account_by_id(cli, acc_a_id)
    recv_info = get_receivable_by_id(cli, recv_id)
    checker.check('全部收款后账户A余额', 700000 + 400000 + 600000, float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0)
    checker.check('应收已收金额=总额', 1000000, float(recv_info.get('received_amount', 0)) if isinstance(recv_info, dict) else 0)
    checker.check('应收未收=0', 0, float(recv_info.get('remaining_amount', 0)) if isinstance(recv_info, dict) else 0)
    checker.check('应收状态 fully_paid', 'fully_paid', recv_info.get('status') if isinstance(recv_info, dict) else None)
    
    # ========== 步骤 8: 创建发票 ==========
    log_step(8, '创建发票 100万')
    invoice = cli.post('/finance/invoices', json={
        'customer_id': customer_id,
        'project_id': project_id,
        'receivable_id': recv_id,
        'invoice_type': 'ordinary',
        'amount': 1000000.00,
        'tax_rate': 13,
        'issue_date': today,
        'status': 'issued',
        'remark': '资金流测试发票'
    })
    inv_data = unwrap(invoice)
    if isinstance(inv_data, dict) and inv_data.get('id'):
        log_ok('发票创建', f'id={inv_data.get("id")}, 总额={inv_data.get("total_amount")} (含税)')
        results['created']['invoices'].append(inv_data.get('id'))
    else:
        log_fail('发票创建失败', json.dumps(invoice, ensure_ascii=False)[:200])
    
    # ========== 步骤 9: 创建应付 (供应商) 50万 ==========
    log_step(9, '创建应付 50万')
    pay = cli.post('/finance/payables', json={
        'supplier_id': supplier_id,
        'project_id': project_id,
        'amount': 500000.00,
        'due_date': '2026-12-31',
        'payment_term': '验收后30天',
        'notes': '资金流测试: 应付 50万'
    })
    pay_data = unwrap(pay)
    pay_id = pay_data.get('id') if isinstance(pay_data, dict) else None
    if pay_id:
        log_ok('应付创建', f'id={pay_id}, 应付=50万, 已付=0, 未付=50万')
        results['created']['payables'].append(pay_id)
    else:
        log_fail('应付创建失败', json.dumps(pay, ensure_ascii=False)[:200])
        pay_id = None
    
    if pay_id:
        checker.check('应付未付初始', 500000, float(pay_data.get('remaining_amount', 0)))
        checker.check('应付初始状态', 'pending', pay_data.get('status'))
        
        # ========== 步骤 10: 部分付款 20万 ==========
        log_step(10, '部分付款 20万 → 出账账户A')
        paid1 = cli.post(f'/finance/payables/{pay_id}/payments', json={
            'amount': 200000.00,
            'payment_date': today,
            'account_id': acc_a_id,
            'method': '银行转账',
            'operator': '测试员',
            'remark': '资金流测试: 部分付款 20万'
        })
        paid1_data = unwrap(paid1)
        if isinstance(paid1_data, dict) and paid1_data.get('id'):
            log_ok('付款 20万 成功', f'payment_id={paid1_data.get("id")}')
            results['created']['payments'].append(paid1_data.get('id'))
        
        acc_a_info = get_account_by_id(cli, acc_a_id)
        pay_info = get_payable_by_id(cli, pay_id)
        expected_bal = 700000 + 400000 + 600000 - 200000  # 1500000
        checker.check('部分付款后账户A余额', expected_bal, float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0)
        checker.check('应付已付', 200000, float(pay_info.get('paid_amount', 0)) if isinstance(pay_info, dict) else 0)
        checker.check('应付未付', 300000, float(pay_info.get('remaining_amount', 0)) if isinstance(pay_info, dict) else 0)
        checker.check('应付状态 partial', 'partial', pay_info.get('status') if isinstance(pay_info, dict) else None)
        
        # ========== 步骤 11: 剩余付款 30万 ==========
        log_step(11, '剩余付款 30万 → 应付清零')
        paid2 = cli.post(f'/finance/payables/{pay_id}/payments', json={
            'amount': 300000.00,
            'payment_date': today,
            'account_id': acc_a_id,
            'method': '银行转账',
            'operator': '测试员',
            'remark': '资金流测试: 剩余付款 30万'
        })
        paid2_data = unwrap(paid2)
        if isinstance(paid2_data, dict) and paid2_data.get('id'):
            log_ok('付款 30万 成功', f'payment_id={paid2_data.get("id")}')
            results['created']['payments'].append(paid2_data.get('id'))
        
        acc_a_info = get_account_by_id(cli, acc_a_id)
        pay_info = get_payable_by_id(cli, pay_id)
        expected_bal = 700000 + 400000 + 600000 - 200000 - 300000  # 1200000
        checker.check('全部付款后账户A余额', expected_bal, float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0)
        checker.check('应付已付=总额', 500000, float(pay_info.get('paid_amount', 0)) if isinstance(pay_info, dict) else 0)
        checker.check('应付未付=0', 0, float(pay_info.get('remaining_amount', 0)) if isinstance(pay_info, dict) else 0)
        checker.check('应付状态 fully_paid', 'fully_paid', pay_info.get('status') if isinstance(pay_info, dict) else None)
    
    # ========== 步骤 12: 校验收款/付款/账户总账 ==========
    log_step(12, '校验收款/付款/账户总账一致性')
    
    # 总览
    overview = unwrap(cli.get('/finance/overview')) if 'overview' in str(cli.get('/finance')) else None
    
    # 收款记录
    recv_payments = cli.get(f'/finance/receivables/{recv_id}/payments')
    recv_pay_list = recv_payments if isinstance(recv_payments, list) else recv_payments.get('data', [])
    total_received = sum(float(p.get('amount', 0)) for p in recv_pay_list)
    log_ok(f'应收 #{recv_id} 共 {len(recv_pay_list)} 笔收款, 合计={total_received:.2f}')
    checker.check('收款总额校验', 1000000, total_received)
    
    # 付款记录
    if pay_id:
        pay_payments = cli.get(f'/finance/payables/{pay_id}/payments')
        pay_pay_list = pay_payments if isinstance(pay_payments, list) else pay_payments.get('data', [])
        total_paid = sum(float(p.get('amount', 0)) for p in pay_pay_list)
        log_ok(f'应付 #{pay_id} 共 {len(pay_pay_list)} 笔付款, 合计={total_paid:.2f}')
        checker.check('付款总额校验', 500000, total_paid)
    
    # 账户 A 交易记录
    acc_a_txns = cli.get(f'/finance/accounts/{acc_a_id}/transactions')
    txn_list = acc_a_txns if isinstance(acc_a_txns, list) else acc_a_txns.get('data', [])
    log_ok(f'账户 A 交易记录: {len(txn_list)} 条')
    
    # 余额公式: A = 100 - 30 + 40 + 60 - 20 - 30 = 120 万
    acc_a_info = get_account_by_id(cli, acc_a_id)
    acc_b_info = get_account_by_id(cli, acc_b_id)
    expected_a = 1200000.00
    expected_b = 300000.00
    
    a_bal = float(acc_a_info.get('balance', 0)) if isinstance(acc_a_info, dict) else 0
    b_bal = float(acc_b_info.get('balance', 0)) if isinstance(acc_b_info, dict) else 0
    
    log_ok(f'账户A 余额={a_bal:.2f}  (期望={expected_a:.2f})')
    log_ok(f'账户B 余额={b_bal:.2f}  (期望={expected_b:.2f})')
    log_ok(f'总资产={a_bal + b_bal:.2f}  (期望=150万=初始总资产)')
    
    checker.check('账户A最终余额公式', expected_a, a_bal)
    checker.check('账户B最终余额公式', expected_b, b_bal)
    checker.check('总资产守恒 150万', 1500000, a_bal + b_bal)
    
    # ========== 步骤 13: 错误用例 - 收款超额 ==========
    log_step(13, '边界测试: 收款超额应被拒绝')
    
    # 创建第二个应收 100
    recv2 = cli.post('/finance/receivables', json={
        'customer_id': customer_id,
        'amount': 100.00,
        'due_date': '2026-12-31',
        'notes': '边界测试: 应收 100元'
    })
    recv2_id = unwrap(recv2).get('id') if isinstance(unwrap(recv2), dict) else None
    if recv2_id:
        overpay = cli.post(f'/finance/receivables/{recv2_id}/payments', json={
            'amount': 200.00,  # 超额
            'payment_date': today,
            'account_id': acc_a_id,
            'method': '银行转账'
        })
        if isinstance(overpay, dict) and overpay.get('code') == 1002:
            log_ok('超额收款被正确拒绝', f'code=1002, msg={overpay.get("message", "")}')
        else:
            log_warn('超额收款返回结构异常', json.dumps(overpay, ensure_ascii=False)[:150])
        results['created']['receivables'].append(recv2_id)
    
    # ========== 步骤 14: 边界 - 转账余额不足 ==========
    log_step(14, '边界测试: 转账余额不足应被拒绝')
    
    nobal_transfer = cli.post('/finance/accounts/transfer', json={
        'from_account_id': acc_a_id,
        'to_account_id': acc_b_id,
        'amount': 99999999.00,  # 天价
        'transfer_date': today,
        'method': '内部转账'
    })
    if isinstance(nobal_transfer, dict) and (nobal_transfer.get('code') == 1006 or '余额不足' in str(nobal_transfer.get('message', ''))):
        log_ok('余额不足转账被正确拒绝', f'code={nobal_transfer.get("code")}')
    else:
        log_warn('余额不足转账返回异常', json.dumps(nobal_transfer, ensure_ascii=False)[:150])
    
    # ========== 步骤 15: 清理 ==========
    log_step(15, '清理测试数据 (软删除)')
    
    cleanup_ok = 0
    cleanup_fail = 0
    # 删除应收
    for rid in results['created'].get('receivables', []):
        r = cli.delete(f'/finance/receivables/{rid}')
        if isinstance(r, dict) and (r.get('code') == 0 or '已删除' in str(r.get('message', ''))):
            cleanup_ok += 1
        else:
            cleanup_fail += 1
    
    # 删除应付
    for pid in results['created'].get('payables', []):
        r = cli.delete(f'/finance/payables/{pid}')
        if isinstance(r, dict) and (r.get('code') == 0 or '已删除' in str(r.get('message', ''))):
            cleanup_ok += 1
        else:
            cleanup_fail += 1
    
    # 删除发票
    for iid in results['created'].get('invoices', []):
        r = cli.delete(f'/finance/invoices/{iid}')
        if isinstance(r, dict) and (r.get('code') == 0 or '已删除' in str(r.get('message', ''))):
            cleanup_ok += 1
        else:
            cleanup_fail += 1
    
    log_ok(f'清理: {cleanup_ok} 成功, {cleanup_fail} 跳过 (可能有 FK 约束, 不影响主流程)')
    
    # ========== 总结 ==========
    log_section('测试总结')
    passed, total = checker.summary()
    print(f'\n  {c("断言通过率", BLUE, bold=True)}: {c(f"{passed} / {total}", GREEN if passed == total else YELLOW, bold=True)}')
    print(f'  {c("创建账户", BLUE, bold=True)}: {len(results["created"]["accounts"])}')
    print(f'  {c("创建应收", BLUE, bold=True)}: {len(results["created"]["receivables"])}')
    print(f'  {c("创建应付", BLUE, bold=True)}: {len(results["created"]["payables"])}')
    print(f'  {c("创建发票", BLUE, bold=True)}: {len(results["created"]["invoices"])}')
    print(f'  {c("产生支付记录", BLUE, bold=True)}: {len(results["created"]["payments"])}')
    
    print(f'\n  {c("最终账户A余额", BLUE, bold=True)}: {c(f"{a_bal:,.2f} 元", GREEN, bold=True)} (期望 1,200,000.00)')
    print(f'  {c("最终账户B余额", BLUE, bold=True)}: {c(f"{b_bal:,.2f} 元", GREEN, bold=True)} (期望 300,000.00)')
    print(f'  {c("总资产守恒", BLUE, bold=True)}: {c(f"{a_bal + b_bal:,.2f} 元", GREEN, bold=True)} (期望 1,500,000.00)')
    
    if passed == total:
        print(f'\n  {c("✅ 全链路资金流验证通过 — 账户/应收/收款/应付/付款/转账 全部闭环", GREEN, bold=True)}')
    else:
        print(f'\n  {c(f"⚠️  {total - passed} 项断言未通过", YELLOW, bold=True)}')
    
    # 保存报告
    results['summary'] = {
        'assertion_pass': passed,
        'assertion_total': total,
        'accounts_created': len(results['created']['accounts']),
        'receivables_created': len(results['created']['receivables']),
        'payables_created': len(results['created']['payables']),
        'invoices_created': len(results['created']['invoices']),
        'payments_created': len(results['created']['payments']),
        'final_acc_a_balance': a_bal,
        'final_acc_b_balance': b_bal,
        'total_balance': a_bal + b_bal,
        'conservation_ok': abs((a_bal + b_bal) - 1500000) < 0.01
    }
    
    with open(r'D:\work\website\OA\.workbuddy\finance_flow_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == '__main__':
    main()