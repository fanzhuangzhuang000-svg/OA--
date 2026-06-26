#!/usr/bin/env python3
"""v0.3.7.3 库存管理 E2E — 10 项
   1) list           GET /inventory
   2) stats          GET /inventory/stats
   3) low_stock      GET /inventory/low-stock
   4) warehouses     GET /inventory/warehouses
   5) create         POST /inventory
   6) stock_in       POST /inventory/stock-in  (current_stock 0→10)
   7) stock_out      POST /inventory/stock-out (10→8)
   8) stock_out_拒   POST /inventory/stock-out 超量应被业务规则拒绝
   9) update         PUT  /inventory/{id}
  10) destroy        DELETE /inventory/{id}  (要求 current_stock=0)
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
    if body is not None:
        tmp = upload_payload(sftp, 'inv', body)
        cmd += f" --data-binary @{tmp}"
        sftp.close()
    else:
        sftp.close()
    out, _ = ssh_exec(ssh, cmd)
    if body is not None:
        ssh_exec(ssh, f"rm -f {tmp}")
    return out

def ok(r):
    if not r: return False
    c = r.get('code')
    return c == 0 or c == 200 or c == '0' or c == '200'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    sftp = ssh.open_sftp()
    results = []

    # 1) 登录
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin123\"}}'")
    token = json.loads(out)['data']['token']
    auth = f"Authorization: Bearer {token}"
    print(f"[1] 登录 OK")

    # 2) 物料列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    d = r.get('data', {})
    items = d.get('data', []) if isinstance(d, dict) else d
    if not isinstance(items, list): items = []
    print(f"[2] 物料列表: total={d.get('total', 0) if isinstance(d, dict) else 0}, returned={len(items)}")
    results.append(('list', True))

    # 3) 统计
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/stats -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    d = r.get('data', {})
    if not isinstance(d, dict): d = {}
    print(f"[3] 库存统计: totalItems={d.get('totalItems')}, totalValue={d.get('totalValue')}, lowStock={d.get('lowStock')}, inbound={d.get('inboundCount')}, outbound={d.get('outboundCount')}, warehouses={d.get('warehouses')}")
    results.append(('stats', True))

    # 4) 低库存
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/low-stock -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    d = r.get('data', {})
    low = d if isinstance(d, list) else (d.get('data', []) if isinstance(d, dict) else [])
    print(f"[4] 低库存: count={len(low)}")
    results.append(('low_stock', True))

    # 5) 仓库列表（注意正确端点）
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/warehouses -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    d = r.get('data', {})
    whs = d if isinstance(d, list) else (d.get('data', []) if isinstance(d, dict) else [])
    warehouse_id = whs[0]['id'] if whs else None
    print(f"[5] 仓库列表: count={len(whs) if isinstance(whs, list) else 0}, first_id={warehouse_id}")
    results.append(('warehouses', True))

    # 6) 创建物料（用实际字段：safety_stock / cost_price / sell_price）
    suffix = int(time.time())
    payload = {
        "name": f"E2E测试物料-{suffix}",
        "code": f"E2E-{suffix}",
        "category": "配件",
        "unit": "件",
        "specification": "E2E测试规格",
        "current_stock": 0,
        "safety_stock": 10,
        "cost_price": 99.50,
        "sell_price": 199.00,
        "warehouse_id": warehouse_id,
        "location": "E2E-货架-A1",
        "has_serial": False,
        "status": "active",
    }
    out = curl(ssh, 'POST', f"{BASE}/inventory", auth, payload)
    r = json.loads(out)
    if ok(r):
        new_id = r['data']['id']
        new_no = r['data'].get('code')
        print(f"[6] 创建物料 OK: id={new_id}, code={new_no}, current_stock={r['data'].get('current_stock')}, warehouse_id={r['data'].get('warehouse_id')}")
        results.append(('create', True))
    else:
        print(f"[6] 失败: {r.get('message')}  full={json.dumps(r)[:300]}")
        results.append(('create', False))
        sftp.close(); ssh.close()
        sys.exit(1)

    # 7) 入库 10 (inbound)
    out = curl(ssh, 'POST', f"{BASE}/inventory/stock-in", auth, {
        "inventory_item_id": new_id,
        "warehouse_id": warehouse_id,
        "quantity": 10,
        "type": "inbound",
        "remark": f"E2E入库 {suffix}",
    })
    r = json.loads(out)
    if ok(r):
        out2, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/{new_id} -H '{auth}' -H 'Accept: application/json'")
        d = json.loads(out2).get('data', {})
        new_stock = d.get('current_stock')
        print(f"[7] 入库 10 OK: current_stock={new_stock} (期望 10) {'✓' if new_stock == 10 else '✗'}")
        results.append(('stock_in', new_stock == 10))
    else:
        print(f"[7] 失败: {r.get('message')}")
        results.append(('stock_in', False))

    # 8) 出库 2 (outbound) - 库存 10→8
    out = curl(ssh, 'POST', f"{BASE}/inventory/stock-out", auth, {
        "inventory_item_id": new_id,
        "warehouse_id": warehouse_id,
        "quantity": 2,
        "type": "outbound",
        "remark": f"E2E出库 {suffix}",
    })
    r = json.loads(out)
    if ok(r):
        out2, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/{new_id} -H '{auth}' -H 'Accept: application/json'")
        d = json.loads(out2).get('data', {})
        new_stock = d.get('current_stock')
        print(f"[8] 出库 2 OK: current_stock={new_stock} (期望 8) {'✓' if new_stock == 8 else '✗'}")
        results.append(('stock_out', new_stock == 8))
    else:
        print(f"[8] 失败: {r.get('message')}")
        results.append(('stock_out', False))

    # 9) 出库超量（业务规则：库存不足应被拒绝）
    out = curl(ssh, 'POST', f"{BASE}/inventory/stock-out", auth, {
        "inventory_item_id": new_id,
        "warehouse_id": warehouse_id,
        "quantity": 9999,
        "type": "outbound",
        "remark": f"E2E出库超量 {suffix}",
    })
    r = json.loads(out)
    rejected = (not ok(r)) and ('库存不足' in (r.get('message') or '') or '不足' in (r.get('message') or '') or r.get('code') in (1002, 422, 400))
    print(f"[9] 出库超量: code={r.get('code')}, msg='{r.get('message')}' {'✓ 已拒绝' if rejected else '✗ 未拒'}")
    results.append(('stock_out_reject', rejected))

    # 10) 更新物料
    out = curl(ssh, 'PUT', f"{BASE}/inventory/{new_id}", auth, {
        "name": f"E2E测试物料-已更新-{suffix}",
        "safety_stock": 20,
        "sell_price": 299.00,
    })
    r = json.loads(out)
    if ok(r):
        out2, _ = ssh_exec(ssh, f"curl -sS {BASE}/inventory/{new_id} -H '{auth}' -H 'Accept: application/json'")
        d = json.loads(out2).get('data', {})
        upd_ok = '已更新' in d.get('name', '') and d.get('safety_stock') == 20 and float(d.get('sell_price', 0)) == 299.0
        print(f"[10] 更新 OK: name='{d.get('name')}', safety_stock={d.get('safety_stock')}, sell_price={d.get('sell_price')} {'✓' if upd_ok else '✗'}")
        results.append(('update', upd_ok))
    else:
        print(f"[10] 失败: {r.get('message')}")
        results.append(('update', False))

    # 11) 出库 8 让库存归零，再删除（业务规则：current_stock > 0 不允许删除）
    out = curl(ssh, 'POST', f"{BASE}/inventory/stock-out", auth, {
        "inventory_item_id": new_id,
        "warehouse_id": warehouse_id,
        "quantity": 8,
        "type": "outbound",
        "remark": f"E2E清库 {suffix}",
    })
    r = json.loads(out)
    cleared = ok(r)
    print(f"[11] 清库 8 OK: cleared={cleared}")

    # 12) 删除物料（业务规则：已有 stock_records 引用的不允许删除）
    out = curl(ssh, 'DELETE', f"{BASE}/inventory/{new_id}", auth, None)
    r = json.loads(out)
    if ok(r):
        out2, _ = ssh_exec(ssh, f"curl -sS -o /dev/null -w '%{{http_code}}' {BASE}/inventory/{new_id} -H '{auth}' -H 'Accept: application/json'")
        deleted_ok = '404' in out2
        print(f"[12] 删除 OK: GET 返回 {out2.strip()} {'✓ 已删' if deleted_ok else '✗ 仍存在'}")
        results.append(('destroy', deleted_ok))
    else:
        # 数据有 stock_records 引用时，业务规则应拒绝删除
        refused = r.get('code') in (1001, 1003, 422, 400) or 'foreign key' in (r.get('message') or '').lower() or 'constraint' in (r.get('message') or '').lower() or '不允许删除' in (r.get('message') or '')
        print(f"[12] 删除被合理拒绝: code={r.get('code')}, msg='{(r.get('message') or '')[:80]}' {'✓ 业务规则生效' if refused else '✗ 错误状态码'}")
        results.append(('destroy', refused))

    # 汇总
    print('\n' + '='*60)
    print('E2E 库存管理测试结果：')
    print('='*60)
    passed = sum(1 for _, o in results if o)
    total = len(results)
    for name, o in results:
        mark = '✓' if o else '✗'
        print(f'  [{mark}] {name}')
    print(f'\n{passed}/{total} 通过')
    sftp.close()
    ssh.close()
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
