#!/usr/bin/env python3
"""v0.3.7.3 项目管理 E2E — 6 项
   1) list           GET /projects
   2) stages         GET /projects/stages
   3) create         POST /projects
   4) show           GET /projects/{id}
   5) update         PUT /projects/{id}
   6) destroy        DELETE /projects/{id}
"""
import paramiko, json, sys, time

HOST = '172.20.0.139'; USER = 'nbcy'; PWD = 'admin123'
BASE = 'http://127.0.0.1:3000/api'

def ssh_exec(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    return so.read().decode('utf-8','replace'), se.read().decode('utf-8','replace')

def upload_payload(sftp, name, data):
    path = f"/tmp/{name}_{int(time.time()*1000)}.json"
    with sftp.open(path, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))
    return path

def curl(ssh, method, url, auth, body=None):
    sftp = ssh.open_sftp()
    cmd = f"curl -sS -X {method} {url} -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json'"
    if body is not None:
        tmp = upload_payload(sftp, 'proj', body)
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

    # 2) 项目列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/projects -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    d = r.get('data', {})
    items = d.get('data', []) if isinstance(d, dict) else d
    print(f"[2] 项目列表: total={d.get('total',0) if isinstance(d,dict) else 0}, returned={len(items)}")
    results.append(('list', True))

    # 3) 阶段字典
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/projects/stages -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    stages = r.get('data', [])
    print(f"[3] 阶段字典: {len(stages)} 个阶段")
    results.append(('stages', True))

    # 4) 创建项目
    suffix = int(time.time())
    payload = {
        "name": f"E2E测试项目-{suffix}",
        "customer_id": 1,
        "type": "comprehensive",
        "description": f"E2E测试项目 {suffix}",
        "budget_device": 100000,
        "budget_material": 50000,
        "budget_labor": 80000,
        "budget_outsource": 20000,
        "budget_other": 10000,
        "manager_id": 1,
        "start_date": "2026-07-01",
        "end_date": "2026-12-31",
        "priority": "medium",
        "member_ids": [1, 2],
    }
    out = curl(ssh, 'POST', f"{BASE}/projects", auth, payload)
    r = json.loads(out)
    if ok(r):
        new_id = r['data']['id']
        print(f"[4] 创建项目 OK: id={new_id}, name={r['data']['name']}")
        results.append(('create', True))
    else:
        print(f"[4] 失败: {r.get('message')}")
        results.append(('create', False))
        sftp.close(); ssh.close()
        sys.exit(1)

    # 5) 查看项目
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/projects/{new_id} -H '{auth}' -H 'Accept: application/json'")
    r = json.loads(out)
    if ok(r):
        print(f"[5] 查看项目 OK: {r['data']['name']}")
        results.append(('show', True))
    else:
        print(f"[5] 失败: {r.get('message')}")
        results.append(('show', False))

    # 6) 更新项目
    out = curl(ssh, 'PUT', f"{BASE}/projects/{new_id}", auth, {"progress": 25})
    r = json.loads(out)
    if ok(r):
        print(f"[6] 更新 OK: progress={r['data'].get('progress')}")
        results.append(('update', True))
    else:
        print(f"[6] 失败: {r.get('message')}")
        results.append(('update', False))

    # 7) 删除项目（刚立项、无合同、无成员 - 业务允许删除）
    out = curl(ssh, 'DELETE', f"{BASE}/projects/{new_id}", auth, None)
    r = json.loads(out)
    if ok(r):
        # 验证已删
        out2, _ = ssh_exec(ssh, f"curl -sS -o /dev/null -w '%{{http_code}}' {BASE}/projects/{new_id} -H '{auth}' -H 'Accept: application/json'")
        deleted_ok = '404' in out2
        print(f"[7] 删除 OK: GET 返回 {out2.strip()} {'✓ 已删' if deleted_ok else '✗ 仍存在'}")
        results.append(('destroy', deleted_ok))
    else:
        print(f"[7] 失败: {r.get('message')}")
        results.append(('destroy', False))

    # 8) 业务规则：进入施工阶段的项目不能删
    out = curl(ssh, 'POST', f"{BASE}/projects", auth, {**payload, "name": f"E2E施工项目-{suffix}"})
    r = json.loads(out)
    if ok(r):
        construction_id = r['data']['id']
        out = curl(ssh, 'PUT', f"{BASE}/projects/{construction_id}/stage", auth, {"stage": "construction"})
        out2 = curl(ssh, 'DELETE', f"{BASE}/projects/{construction_id}", auth, None)
        r2 = json.loads(out2)
        refused = not ok(r2) and r2.get('code') in (1001, 1002, 422, 400)
        print(f"[8] 业务规则: code={r2.get('code')}, msg='{r2.get('message','')[:60]}' {'✓ 已拒' if refused else '✗ 未拒'}")
        results.append(('destroy_reject', refused))

    # 汇总
    print('\n' + '='*60)
    print('E2E 项目管理测试结果：')
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
