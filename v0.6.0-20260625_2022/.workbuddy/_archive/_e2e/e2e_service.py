#!/usr/bin/env python3
"""v0.3.7.3 服务工单 E2E — 6 项
   1) list           GET /service/orders
   2) stats          GET /service/stats
   3) maintenance    GET /service/maintenance-contracts
   4) create         POST /service/orders
   5) assign         POST /service/orders/{id}/assign
   6) start          POST /service/orders/{id}/start
   7) complete       POST /service/orders/{id}/complete
"""
import paramiko, json, sys, time

HOST='172.20.0.139'; USER='nbcy'; PWD='admin123'
BASE='http://127.0.0.1:3000/api'

def ssh_exec(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    return so.read().decode('utf-8', 'replace'), se.read().decode('utf-8', 'replace')

def upload_payload(sftp, name, data):
    path = f"/tmp/{name}_{int(time.time()*1000)}.json"
    with sftp.open(path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))
    return path

def curl_post_json(ssh, url, auth, body):
    sftp = ssh.open_sftp()
    tmp = upload_payload(sftp, 'svc', body)
    sftp.close()
    out, _ = ssh_exec(ssh, f"curl -sS {url} -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data-binary @{tmp}")
    ssh_exec(ssh, f"rm -f {tmp}")
    return out

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

    # 2) 拿一个 customer_id + user_id（维修人员）
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/customers -H '{auth}' -H 'Accept: application/json'")
    cust_data = json.loads(out).get('data', {})
    customers = cust_data.get('data', []) if isinstance(cust_data, dict) else cust_data
    customer_id = customers[0]['id'] if customers else None
    print(f"[2] 客户列表: total={cust_data.get('total') if isinstance(cust_data, dict) else 'n/a'}, first_id={customer_id}")

    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees -H '{auth}' -H 'Accept: application/json'")
    emp_data = json.loads(out).get('data', {})
    employees = emp_data.get('data', []) if isinstance(emp_data, dict) else emp_data
    technician_id = employees[0]['id'] if employees else None
    print(f"[3] 员工列表: total={emp_data.get('total') if isinstance(emp_data, dict) else 'n/a'}, first_id={technician_id}")

    # 4) 列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/service/orders -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        d = r.get('data', {})
        total = d.get('total', 0) if isinstance(d, dict) else 0
        items = d.get('data', []) if isinstance(d, dict) else d
        print(f"[4] 工单列表: total={total}, returned={len(items) if isinstance(items, list) else 'n/a'}")
        results.append(('list', True))
    except Exception as e:
        print(f"[4] 解析失败: {e}")
        results.append(('list', False))

    # 5) 统计
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/service/stats -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        d = r.get('data', {})
        print(f"[5] 服务统计: totalOrders={d.get('totalOrders')}, completed={d.get('completedOrders')}, slaRate={d.get('slaRate')}%, avgRating={d.get('avgRating')}")
        results.append(('stats', True))
    except Exception as e:
        print(f"[5] 失败: {e}")
        results.append(('stats', False))

    # 6) 维保合同
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/service/maintenance-contracts -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        d = r.get('data', {})
        items = d.get('data', []) if isinstance(d, dict) else d
        print(f"[6] 维保合同: total={d.get('total', 0) if isinstance(d, dict) else 0}, count={len(items) if isinstance(items, list) else 0}")
        results.append(('maintenance', True))
    except Exception as e:
        print(f"[6] 失败: {e}")
        results.append(('maintenance', False))

    # 7) 新建工单
    new_id = None
    new_no = None
    if customer_id:
        payload = {
            "customer_id": customer_id,
            "fault_description": f"E2E测试工单 {int(time.time())}：核心交换机电源模块异常告警",
            "urgency": "urgent",
            "service_type": "warranty",
            "sla_hours": 24,
            "fault_photos": [],
        }
        out = curl_post_json(ssh, f"{BASE}/service/orders", auth, payload)
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                new_id = r['data']['id']
                new_no = r['data'].get('order_no')
                print(f"[7] 新建工单 OK: id={new_id}, order_no={new_no}, status={r['data'].get('status')}")
                results.append(('create', True))
            else:
                print(f"[7] 失败: {r.get('message')}")
                results.append(('create', False))
        except Exception as e:
            print(f"[7] 解析失败: {e}")
            results.append(('create', False))

    # 8) 派单
    if new_id and technician_id:
        out = curl_post_json(ssh, f"{BASE}/service/orders/{new_id}/assign", auth, {"assigned_to": technician_id})
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[8] 派单 OK: {r.get('message')}")
                results.append(('assign', True))
            else:
                print(f"[8] 失败: {r.get('message')}")
                results.append(('assign', False))
        except Exception as e:
            print(f"[8] 解析失败: {e}")
            results.append(('assign', False))

    # 9) 开始维修
    if new_id:
        out = curl_post_json(ssh, f"{BASE}/service/orders/{new_id}/start", auth, {})
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[9] 开始维修 OK: {r.get('message')}")
                results.append(('start', True))
            else:
                print(f"[9] 失败: {r.get('message')}")
                results.append(('start', False))
        except Exception as e:
            print(f"[9] 解析失败: {e}")
            results.append(('start', False))

    # 10) 完成维修
    if new_id:
        out = curl_post_json(ssh, f"{BASE}/service/orders/{new_id}/complete", auth, {
            "repair_content": f"E2E测试维修完成 {int(time.time())}：更换电源模块，系统恢复正常",
            "photos": [],
            "parts": [{"name": "电源模块 PSU-500W", "quantity": 1, "unit_cost": 800}]
        })
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[10] 维修完成 OK: {r.get('message')}")
                results.append(('complete', True))
            else:
                print(f"[10] 失败: {r.get('message')}")
                results.append(('complete', False))
        except Exception as e:
            print(f"[10] 解析失败: {e}")
            results.append(('complete', False))

    # 11) 验证最终状态 + 日志链路
    if new_id:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/service/orders/{new_id} -H '{auth}' -H 'Accept: application/json'")
        try:
            r = json.loads(out)
            d = r.get('data', {})
            logs = d.get('logs', [])
            parts = d.get('parts', [])
            print(f"[11] 最终状态: status={d.get('status')}, logs={len(logs)} 条, parts={len(parts)} 个")
            # 期望 logs 至少 3 条：created/assigned/started/completed
            ok = d.get('status') == 'completed' and len(logs) >= 3 and len(parts) >= 1
            print(f"    {'✓' if ok else '✗'} 完整工单链路正确")
            results.append(('full_lifecycle', ok))
        except Exception as e:
            print(f"[11] 异常: {e}")
            results.append(('full_lifecycle', False))

    print('\n' + '='*60)
    print('E2E 服务工单测试结果：')
    print('='*60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        mark = '✓' if ok else '✗'
        print(f'  [{mark}] {name}')
    print(f'\n{passed}/{total} 通过')
    sftp.close()
    ssh.close()
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
