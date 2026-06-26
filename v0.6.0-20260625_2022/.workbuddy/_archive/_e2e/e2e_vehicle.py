#!/usr/bin/env python3
"""v0.3.7.3 车辆管理 E2E — 7 项
   1) list        GET  /vehicles
   2) stats       GET  /vehicles/stats
   3) create      POST /vehicles
   4) show        GET  /vehicles/{id}
   5) update      PUT  /vehicles/{id}
   6) usage       POST /vehicles/usage  (创建用车申请)
   7) dispatch    POST /vehicles/usage/{id}/dispatch  action=approved
   8) update_usage PUT /vehicles/usage/{id}  (登记里程)
   9) destroy     DELETE /vehicles/{id}  (业务规则: 用车完结后允许删)
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
        tmp = upload_payload(sftp, 'veh', body)
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

def step(n, name, cond, extra=''):
    status = '[PASS]' if cond else '[FAIL]'
    print(f"  {status} {n}) {name}{(' — ' + extra) if extra else ''}")
    return cond

def record(name, cond, extra=''):
    status = '[PASS]' if cond else '[FAIL]'
    print(f"  {status} {name}{(' — ' + extra) if extra else ''}")
    return cond

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    results = []

    # 1) 登录
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin123\"}}'")
    j = json.loads(out)
    if not j.get('data', {}).get('token'):
        print("[FATAL] 登录失败:", out[:200])
        return
    token = j['data']['token']
    auth = f"Authorization: Bearer {token}"
    print(f"[login] admin token: {token[:20]}...")

    # 取一个部门 + 用户作为 department_id / responsible_user_id
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/departments -H '{auth}'")
    depts = json.loads(out).get('data', [])
    dept_id = depts[0]['id'] if depts else None
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees?page=1&pageSize=1 -H '{auth}'")
    emps = json.loads(out).get('data', {}).get('items') or json.loads(out).get('data') or []
    user_id = emps[0]['id'] if emps else None

    # 2) list
    print("\n[2] GET /vehicles")
    out = curl(ssh, 'GET', f'{BASE}/vehicles', auth)
    r = json.loads(out)
    initial = r.get('data', [])
    print(f"   返回 {len(initial)} 条车辆")
    results.append(record('list: 列表', ok(r) and isinstance(initial, list)))

    # 3) stats
    print("\n[3] GET /vehicles/stats")
    out = curl(ssh, 'GET', f'{BASE}/vehicles/stats', auth)
    r = json.loads(out)
    s = r.get('data', {})
    print(f"   total={s.get('total')} available={s.get('available')} pending={s.get('pending')}")
    results.append(record('stats: 统计', ok(r) and 'total' in s))

    # 4) create
    print("\n[4] POST /vehicles")
    plate = f"粤B-T{int(time.time())%100000:05d}"
    payload = {
        'plate_no': plate,
        'brand': '丰田',
        'model': '凯美瑞',
        'department_id': dept_id,
        'responsible_user_id': user_id,
        'status': 'available',
        'notes': 'e2e 创建'
    }
    out = curl(ssh, 'POST', f'{BASE}/vehicles', auth, payload)
    r = json.loads(out)
    vid = r.get('data', {}).get('id')
    print(f"   created id={vid} plate={plate}")
    results.append(record('create: 创建', ok(r) and vid is not None))

    # 5) show
    print("\n[5] GET /vehicles/{id}")
    out = curl(ssh, 'GET', f'{BASE}/vehicles/{vid}', auth)
    r = json.loads(out)
    v = r.get('data', {})
    print(f"   plate={v.get('plate_no')} brand={v.get('brand')}")
    results.append(record('show: 详情', ok(r) and v.get('plate_no') == plate))

    # 6) update
    print("\n[6] PUT /vehicles/{id}")
    out = curl(ssh, 'PUT', f'{BASE}/vehicles/{vid}', auth, {'brand': '本田', 'model': '雅阁', 'notes': 'e2e 更新'})
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('update: 更新', ok(r)))

    # 7) 用车申请
    print("\n[7] POST /vehicles/usage")
    usage_payload = {
        'usage_date': '2026-07-01',
        'start_time': '09:00',
        'end_time': '18:00',
        'destination': '客户现场',
        'purpose': '现场技术支持',
        'passengers': 3,
        'self_drive': False,
    }
    out = curl(ssh, 'POST', f'{BASE}/vehicles/usage', auth, usage_payload)
    r = json.loads(out)
    uid = r.get('data', {}).get('id')
    print(f"   usage id={uid} status={r.get('data', {}).get('status')}")
    results.append(record('usage_create: 用车申请', ok(r) and uid is not None))

    # 8) 派车 dispatch action=approved
    print("\n[8] POST /vehicles/usage/{id}/dispatch action=approved")
    out = curl(ssh, 'POST', f'{BASE}/vehicles/usage/{uid}/dispatch', auth, {'vehicle_id': vid, 'action': 'approved'})
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('dispatch_approved: 派车-批准', ok(r)))

    # 9) 派车 using（出发）
    print("\n[9] POST /vehicles/usage/{id}/dispatch action=using")
    out = curl(ssh, 'POST', f'{BASE}/vehicles/usage/{uid}/dispatch', auth, {'vehicle_id': vid, 'action': 'using'})
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('dispatch_using: 派车-出发', ok(r)))

    # 10) 登记里程（updateUsageRequest）
    print("\n[10] PUT /vehicles/usage/{id} 登记里程油耗")
    out = curl(ssh, 'PUT', f'{BASE}/vehicles/usage/{uid}', auth, {'start_mileage': 1000, 'end_mileage': 1080, 'actual_fuel': 6.5})
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('usage_update: 登记里程', ok(r)))

    # 11) 归还 dispatch returned
    print("\n[11] POST /vehicles/usage/{id}/dispatch action=returned")
    out = curl(ssh, 'POST', f'{BASE}/vehicles/usage/{uid}/dispatch', auth, {'action': 'returned'})
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('dispatch_returned: 派车-归还', ok(r)))

    # 12) 删除（无 pending/approved/using 申请，应允许）
    print("\n[12] DELETE /vehicles/{id}")
    out = curl(ssh, 'DELETE', f'{BASE}/vehicles/{vid}', auth)
    r = json.loads(out)
    print(f"   msg={r.get('message')}")
    results.append(record('destroy: 删除车辆', ok(r)))

    # 13) 删除不存在的应 404
    print("\n[13] DELETE /vehicles/999999")
    out = curl(ssh, 'DELETE', f'{BASE}/vehicles/999999', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('destroy_404: 删除不存在', not ok(r)))

    # ===== 汇总 =====
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*50}\nE2E 车辆管理: {passed}/{total} 通过\n{'='*50}")
    ssh.close()
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
