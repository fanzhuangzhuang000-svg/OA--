"""块六完整验证: oppsMarkWon 触发建结算 + 审核 + 发放"""
import requests, subprocess

BASE = 'http://127.0.0.1/api'

def login(u, p):
    r = requests.post(f'{BASE}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0: raise SystemExit(f'login fail: {j.get("message")}')
    return j['data']['token']

def sql(cmd):
    return subprocess.run(['sudo', 'PGPASSWORD=oapass', 'psql', '-U', 'oa_user', '-d', 'security_oa', '-c', cmd], capture_output=True, text=True)

admin_token = login('admin', 'admin123')
h = {'Authorization': f'Bearer {admin_token}'}

# 准备: 找一个有 referrer 的 lead，然后看它的 lead_id 关联的 opp
print('=' * 60)
print('块六 完整流程验证')
print('=' * 60)

# 看现状
print('\n[1] 当前 lead.referrer_id 状态')
out = sql("SELECT count(*) AS with_ref, (SELECT count(*) FROM leads) AS total FROM leads WHERE referrer_id IS NOT NULL;")
print(out.stdout)

# 找一个有 referrer 的 lead
out = sql("SELECT l.id, l.lead_no, l.customer_name, l.referrer_id, r.name as ref_name, r.commission_rate FROM leads l JOIN referrers r ON r.id = l.referrer_id WHERE l.referrer_id IS NOT NULL LIMIT 1;")
print('有 referrer 的 lead:', out.stdout)

# 找该 lead 对应的 opp (若没有，需要建一个)
out = sql("SELECT o.id, o.name, o.lead_id, o.stage, o.estimated_amount FROM opportunities o WHERE o.lead_id IN (SELECT id FROM leads WHERE referrer_id IS NOT NULL) LIMIT 1;")
print('对应 opp:', out.stdout)

# 如果没有 opp, 手动 SQL 建一个
import re
m = re.search(r'\d+', out.stdout.splitlines()[0].split('|')[1].strip()) if out.stdout else None
opp_id = None
if m:
    opp_id = int(m.group())

if not opp_id:
    print('\n没有对应 opp, 手动 SQL 建一个')
    out = sql("SELECT l.id, l.referrer_id, r.commission_rate FROM leads l JOIN referrers r ON r.id = l.referrer_id WHERE l.referrer_id IS NOT NULL LIMIT 1;")
    parts = [l for l in out.stdout.splitlines() if '|' in l and l.strip()[0].isdigit()][0].split('|')
    lead_id = int(parts[0].strip())
    print(f'用 lead_id={lead_id}')
    # 先看 opps 表 status 枚举
    out = sql("\\d opportunities | grep -i stage")
    print('opp.stage enum:', out.stdout)
    out = sql(f"INSERT INTO opportunities (opp_no, name, customer_id, lead_id, type, estimated_amount, stage, probability) VALUES ('OPP-TEST-{int(subprocess.check_output([\"date\",\"+%s\"]).decode())[-5:]}', '测试结算用商机', NULL, {lead_id}, 'comprehensive', 100000, 'requirement', 20) RETURNING id;")
    print('insert opp:', out.stdout)
    # 提取 id
    m2 = re.search(r'\b(\d+)\b', [l for l in out.stdout.splitlines() if '|' in l and l.strip()[0].isdigit()][0])
    if m2: opp_id = int(m2.group(1))

if not opp_id:
    print('没 opp, 结束')
    exit(1)

print(f'\n测试 opp_id={opp_id}')

# 先看当前是否已有 settlement
out = sql(f"SELECT * FROM referral_settlements WHERE opportunity_id = {opp_id};")
print(f'当前 settlement 数量: {len([l for l in out.stdout.splitlines() if l.strip() and l.strip()[0].isdigit()])}')

# 调用 oppsMarkWon (admin 模拟)
print(f'\n[2] oppsMarkWon contract=100000')
r = requests.post(f'{BASE}/sales/opps/{opp_id}/mark-won', headers=h, json={
    'contract_amount': 100000,
    'signed_at': '2026-06-23',
    'notes': '块六测试'
}, timeout=10)
print(f'HTTP {r.status_code} code={r.json().get("code")}')
if r.status_code != 200:
    print('msg:', r.json().get('message', '')[:100])
    exit(1)

# 验证是否自动建了 settlement
out = sql(f"SELECT id, amount, commission_rate, status FROM referral_settlements WHERE opportunity_id = {opp_id};")
print(f'settlement after mark-won:')
print(out.stdout)

# 解析 settlement id
m = re.search(r'\b(\d+)\b', out.stdout.splitlines()[2])
sid = int(m.group(1)) if m else None
print(f'settlement_id={sid}')

if sid:
    # 测试列表
    print('\n[3] 列表查询')
    r = requests.get(f'{BASE}/sales/referral-settlements', headers=h, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} count={r.json().get("data", {}).get("total", 0)}')

    # 测试 stats
    print('\n[4] 统计')
    r = requests.get(f'{BASE}/sales/referral-settlements/stats', headers=h, timeout=10)
    print(f'HTTP {r.status_code} data={r.json().get("data")}')

    # 测试审核
    print('\n[5] 财务审核')
    r = requests.post(f'{BASE}/sales/referral-settlements/{sid}/approve', headers=h, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} status={r.json().get("data", {}).get("status")}')

    # 测试发放
    print('\n[6] 财务发放')
    r = requests.post(f'{BASE}/sales/referral-settlements/{sid}/pay', headers=h, json={
        'payment_no': 'TEST-' + str(sid),
        'payment_voucher': 'disk/sales/referral/2026/06/test.pdf'
    }, timeout=10)
    print(f'HTTP {r.status_code} code={r.json().get("code")} status={r.json().get("data", {}).get("status")}')

    # 验证 referrer.total_commission 累加
    out = sql(f"SELECT id, name, total_commission FROM referrers WHERE id = (SELECT referrer_id FROM referral_settlements WHERE id = {sid});")
    print(f'\n[7] 推荐人 total_commission:')
    print(out.stdout)

print('\n=== 块六核心 7 项验证完成 ===')
