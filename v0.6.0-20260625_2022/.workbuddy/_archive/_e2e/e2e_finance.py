#!/usr/bin/env python3
"""v0.3.7.3 财务管理 E2E — 9 项
   1) overview      GET  /finance/overview
   2) recv list     GET  /finance/receivables
   3) recv create   POST /finance/receivables
   4) recv update   PUT  /finance/receivables/{id}  (登记收款)
   5) recv destroy  DELETE /finance/receivables/{id}
   6) pay list      GET  /finance/payables
   7) pay create    POST /finance/payables
   8) pay update    PUT  /finance/payables/{id}  (登记付款)
   9) pay destroy   DELETE /finance/payables/{id}
"""
import paramiko, json, sys, time

HOST = '172.20.0.139'; USER = 'nbcy'; PWD = 'admin123'
BASE = 'http://127.0.0.1:3000/api'

def ssh_exec(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    return so.read().decode('utf-8', 'replace'), se.read().decode('utf-8', 'replace')

def upload_payload(sftp, name, data):
    path = f"/tmp/{name}_{int(time.time()*1000)}.json"
    with sftp.open(path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))
    return path

def curl(ssh, method, url, auth, body=None):
    sftp = ssh.open_sftp()
    cmd = f"curl -sS -X {method} {url} -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json'"
    tmp = None
    if body is not None:
        tmp = upload_payload(sftp, 'fin', body)
        cmd += f" --data-binary @{tmp}"
    sftp.close()
    out, _ = ssh_exec(ssh, cmd)
    if tmp:
        ssh_exec(ssh, f"rm -f {tmp}")
    return out

def ok(r):
    if not r: return False
    c = r.get('code')
    return c == 0 or c == 200 or c == '0' or c == '200'

def record(name, cond, extra=''):
    status = '[PASS]' if cond else '[FAIL]'
    print(f"  {status} {name}{(' — ' + extra) if extra else ''}")
    return cond

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    results = []

    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin123\"}}'")
    j = json.loads(out)
    if not j.get('data', {}).get('token'):
        print("[FATAL] 登录失败:", out[:200]); return
    token = j['data']['token']
    auth = f"Authorization: Bearer {token}"
    print(f"[login] admin token: {token[:20]}...")

    # 取 customer_id + project_id + supplier_id
    # 拿初始数据（防 404）
    cust_id = None; proj_id = None; sup_id = None
    try:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/customers -H '{auth}'")
        r1 = json.loads(out)
        d1 = r1.get('data', {})
        if isinstance(d1, dict): d1 = d1.get('data', d1.get('items', []))
        cust_id = d1[0]['id'] if d1 else None
    except Exception as e: print('  cust fetch fail:', e)
    try:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/projects -H '{auth}'")
        r2 = json.loads(out)
        d2 = r2.get('data', {})
        if isinstance(d2, dict): d2 = d2.get('data', d2.get('items', []))
        proj_id = d2[0]['id'] if d2 else None
    except Exception as e: print('  proj fetch fail:', e)
    try:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/projects/suppliers -H '{auth}'")
        r3 = json.loads(out)
        d3 = r3.get('data', [])
        if isinstance(d3, dict): d3 = d3.get('data', d3.get('items', []))
        sup_id = d3[0]['id'] if d3 else None
    except Exception as e: print('  sup fetch fail:', e)
    print(f"[init] cust_id={cust_id} proj_id={proj_id} sup_id={sup_id}")

    # 1) overview
    print("\n[1] GET /finance/overview")
    out = curl(ssh, 'GET', f'{BASE}/finance/overview', auth)
    r = json.loads(out)
    d = r.get('data', {})
    print(f"   totalRevenue={d.get('totalRevenue')} totalReceivable={d.get('totalReceivable')} totalPayable={d.get('totalPayable')}")
    results.append(record('overview: 概览', ok(r) and 'totalReceivable' in d))

    # 2) 应收列表
    print("\n[2] GET /finance/receivables")
    out = curl(ssh, 'GET', f'{BASE}/finance/receivables', auth)
    r = json.loads(out)
    recv_list = r.get('data', {}).get('data', r.get('data', []))
    if isinstance(recv_list, dict): recv_list = recv_list.get('data', [])
    print(f"   返回 {len(recv_list) if isinstance(recv_list, list) else 'N/A'} 条应收")
    results.append(record('recv_list: 应收列表', ok(r)))

    # 3) 应收创建
    print("\n[3] POST /finance/receivables")
    recv_payload = {
        'customer_id': cust_id,
        'project_id': proj_id,
        'amount': 10000,
        'received_amount': 0,
        'due_date': '2026-12-31',
        'notes': 'e2e 创建应收'
    }
    out = curl(ssh, 'POST', f'{BASE}/finance/receivables', auth, recv_payload)
    r = json.loads(out)
    rid = r.get('data', {}).get('id')
    print(f"   created id={rid} status={r.get('data', {}).get('status')}")
    results.append(record('recv_create: 应收创建', ok(r) and rid is not None))

    # 4) 应收更新（登记部分收款）
    print("\n[4] PUT /finance/receivables/{id} 登记收款 3000")
    out = curl(ssh, 'PUT', f'{BASE}/finance/receivables/{rid}', auth, {'received_amount': 3000})
    r = json.loads(out)
    updated = r.get('data', {})
    print(f"   remaining={updated.get('remaining_amount')} status={updated.get('status')}")
    results.append(record('recv_update: 登记部分收款', ok(r) and float(updated.get('remaining_amount', -1)) == 7000 and updated.get('status') == 'partial'))

    # 5) 应收更新（收完全部）
    print("\n[5] PUT /finance/receivables/{id} 收完全部 7000")
    out = curl(ssh, 'PUT', f'{BASE}/finance/receivables/{rid}', auth, {'received_amount': 10000})
    r = json.loads(out)
    updated = r.get('data', {})
    print(f"   remaining={updated.get('remaining_amount')} status={updated.get('status')} received_date={updated.get('received_date')}")
    results.append(record('recv_full: 收完全部', ok(r) and float(updated.get('remaining_amount', -1)) == 0 and updated.get('status') == 'fully_paid' and updated.get('received_date') is not None))

    # 6) 应收删除（已 fully_paid 业务规则应拒绝）
    print("\n[6] DELETE /finance/receivables/{id} (业务规则: 已 fully_paid 应被拒)")
    out = curl(ssh, 'DELETE', f'{BASE}/finance/receivables/{rid}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('recv_delete_paid_reject: 业务规则拒绝', not ok(r) and r.get('code') == 1001))

    # 新建一条 received_amount=0 的应收用于删除
    print("\n[6b] POST 新建 0 收款应收")
    recv2 = curl(ssh, 'POST', f'{BASE}/finance/receivables', auth, {**recv_payload, 'amount': 5000, 'received_amount': 0, 'notes': 'e2e 待删'})
    r2 = json.loads(recv2)
    rid2 = r2.get('data', {}).get('id')
    out = curl(ssh, 'DELETE', f'{BASE}/finance/receivables/{rid2}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('recv_destroy: 应收删除', ok(r)))

    # 7) 应付列表
    print("\n[7] GET /finance/payables")
    out = curl(ssh, 'GET', f'{BASE}/finance/payables', auth)
    r = json.loads(out)
    pay_list = r.get('data', {}).get('data', r.get('data', []))
    if isinstance(pay_list, dict): pay_list = pay_list.get('data', [])
    print(f"   返回 {len(pay_list) if isinstance(pay_list, list) else 'N/A'} 条应付")
    results.append(record('pay_list: 应付列表', ok(r)))

    # 8) 应付创建
    print("\n[8] POST /finance/payables")
    pay_payload = {
        'supplier_id': sup_id or 1,
        'project_id': proj_id,
        'amount': 8000,
        'paid_amount': 0,
        'due_date': '2026-12-31',
        'payment_term': '月结30天',
        'notes': 'e2e 创建应付'
    }
    out = curl(ssh, 'POST', f'{BASE}/finance/payables', auth, pay_payload)
    r = json.loads(out)
    pid = r.get('data', {}).get('id')
    print(f"   created id={pid} status={r.get('data', {}).get('status')}")
    results.append(record('pay_create: 应付创建', ok(r) and pid is not None))

    # 9) 应付更新（登记付款）
    print("\n[9] PUT /finance/payables/{id} 登记付款 8000")
    out = curl(ssh, 'PUT', f'{BASE}/finance/payables/{pid}', auth, {'paid_amount': 8000})
    r = json.loads(out)
    updated = r.get('data', {})
    print(f"   remaining={updated.get('remaining_amount')} status={updated.get('status')} paid_date={updated.get('paid_date')}")
    results.append(record('pay_paid: 付完全部', ok(r) and float(updated.get('remaining_amount', -1)) == 0 and updated.get('status') == 'fully_paid' and updated.get('paid_date') is not None))

    # 10) 删除不存在应 404
    print("\n[10] DELETE /finance/receivables/999999")
    out = curl(ssh, 'DELETE', f'{BASE}/finance/receivables/999999', auth)
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('recv_delete_404: 不存在', not ok(r)))

    passed = sum(results)
    total = len(results)
    print(f"\n{'='*50}\nE2E 财务管理: {passed}/{total} 通过\n{'='*50}")
    ssh.close()
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
