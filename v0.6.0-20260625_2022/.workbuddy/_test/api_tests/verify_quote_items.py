"""块四验证: 产品库 dialog + items 增删改 + 折扣/税率/有效期"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0: raise SystemExit(f'login fail: {j.get("message")}')
    return j['data']['token']

def sql(cmd):
    return subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True).stdout

admin_token = login('admin', 'admin123')
h = {'Authorization': f'Bearer {admin_token}'}

# 1. 拿一条 draft 报价单
print('=' * 60)
print('块四 验证')
print('=' * 60)

r = requests.get(f'{BASE}/sales/quotes?status=draft&per_page=5', headers=h, timeout=10)
quotes = r.json().get('data', {}).get('data', [])
if not quotes:
    # 找任意 opp 建一个
    r = requests.get(f'{BASE}/sales/opps?per_page=1', headers=h, timeout=10)
    opps = r.json().get('data', {}).get('data', [])
    if not opps:
        print('没 opp'); exit(1)
    opp = opps[0]
    r = requests.post(f'{BASE}/sales/opps/{opp["id"]}/quotations', headers=h, json={
        'discount_rate': 0, 'tax_rate': 13,
    }, timeout=10)
    print('建新报价单:', r.json())
    if r.status_code == 200:
        qid = r.json()['data']['id']
    else:
        print('建报价单失败'); exit(1)
else:
    qid = quotes[0]['id']
print(f'测试 quote_id={qid}')

# 2. 拿销售产品库
print('\n[1] GET /sales/products')
r = requests.get(f'{BASE}/sales/products?per_page=3', headers=h, timeout=10)
products = r.json().get('data', {}).get('data', [])
print(f'  拿到 {len(products)} 个产品')
if not products:
    print('没产品, 跳过 dialog 测试'); exit(1)
p1 = products[0]
print(f'  首个: id={p1["id"]} name={p1["name"]} price={p1.get("sale_price")}')

# 3. POST items 验证 product_id 关联
print('\n[2] POST /quotes/{id}/items 加 product_id')
r = requests.post(f'{BASE}/sales/quotes/{qid}/items', headers=h, json={
    'items': [
        {'product_id': p1['id'], 'code': p1.get('code'), 'name': p1['name'],
         'specification': p1.get('spec', ''), 'unit': p1.get('unit', '件'),
         'quantity': 2, 'unit_price': float(p1.get('sale_price', 100))},
        {'product_id': products[1]['id'] if len(products) > 1 else p1['id'],
         'code': p1.get('code', 'X'), 'name': '非标品定制',
         'specification': '自定义', 'unit': '个', 'quantity': 1, 'unit_price': 500.00},
    ],
    'discount_rate': 5,
    'tax_rate': 13,
    'valid_until': '2026-12-31',
}, timeout=10)
print(f'  HTTP {r.status_code} code={r.json().get("code")}')
if r.status_code == 200:
    q = r.json()['data']
    print(f'  total_amount={q.get("total_amount")} discount_rate={q.get("discount_rate")} tax_rate={q.get("tax_rate")} valid_until={q.get("valid_until")}')
    print(f'  items 数量={len(q.get("items", []))}')
    for it in q.get('items', []):
        print(f'    - {it.get("name")} (product_id={it.get("product_id")} code={it.get("code")})')

# 4. 唯一性检查 (重复 product_id)
print('\n[3] 重复 product_id 应 422')
r = requests.post(f'{BASE}/sales/quotes/{qid}/items', headers=h, json={
    'items': [
        {'product_id': p1['id'], 'name': '重复', 'quantity': 1, 'unit_price': 100},
        {'product_id': p1['id'], 'name': '重复2', 'quantity': 1, 'unit_price': 100},
    ],
}, timeout=10)
print(f'  HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:60]}')
assert r.status_code == 422, f'期望 422 实际 {r.status_code}'

# 5. 折扣 35% 超出 30% 上限
print('\n[4] discount_rate 35% 应 422')
r = requests.post(f'{BASE}/sales/quotes/{qid}/items', headers=h, json={
    'items': [{'name': 't', 'quantity': 1, 'unit_price': 100}],
    'discount_rate': 35,
}, timeout=10)
print(f'  HTTP {r.status_code} code={r.json().get("code")}')
assert r.status_code == 422, f'期望 422 实际 {r.status_code}'

# 6. tax_rate 非法值
print('\n[5] tax_rate=10 应 422')
r = requests.post(f'{BASE}/sales/quotes/{qid}/items', headers=h, json={
    'items': [{'name': 't', 'quantity': 1, 'unit_price': 100}],
    'tax_rate': 10,
}, timeout=10)
print(f'  HTTP {r.status_code} code={r.json().get("code")}')
assert r.status_code == 422, f'期望 422 实际 {r.status_code}'

# 7. 已 submitted 状态不可改
print('\n[6] 改 draft → submitted 后, 再改应 409')
# 改状态
r = requests.put(f'{BASE}/sales/quotes/{qid}/status', headers=h, json={'status': 'submitted'}, timeout=10)
print(f'  draft→submitted: HTTP {r.status_code} code={r.json().get("code")}')
# 再试着改 items
r = requests.post(f'{BASE}/sales/quotes/{qid}/items', headers=h, json={
    'items': [{'name': 't', 'quantity': 1, 'unit_price': 100}],
}, timeout=10)
print(f'  submitted 状态改 items: HTTP {r.status_code} code={r.json().get("code")} msg={r.json().get("message","")[:50]}')

# 8. 定时任务命令测试
print('\n[7] 手动跑 oa:expire-quotations 定时任务')
si_out = subprocess.run(['sudo', 'php', '/var/www/oa-api/artisan', 'oa:expire-quotations'], capture_output=True, text=True)
print(f'  {si_out.stdout.strip()}')
print(f'  ERR: {si_out.stderr[:200]}')

# 9. 看 schedule:list
print('\n[8] php artisan schedule:list')
si_out = subprocess.run(['sudo', 'php', '/var/www/oa-api/artisan', 'schedule:list'], capture_output=True, text=True)
print(si_out.stdout[:500])
print('ERR:', si_out.stderr[:200])

print('\n=== 块四核心验证完成 ===')
