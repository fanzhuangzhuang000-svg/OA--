#!/usr/bin/env python3
"""v0.3.7.3 报销管理 E2E — 7 项
   1) list           GET /expenses
   2) stats          GET /expenses/stats
   3) projects       GET /expenses/projects
   4) create         POST /expenses  (含 items 数组)
   5) show           GET /expenses/{id}
   6) approve        POST /expenses/{id}/approve  (action=approved)
   7) pay            POST /expenses/{id}/pay      (paid_amount)
   8) cancel         POST /expenses/{id}/cancel   (回到 cancelled)
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
    """用文件传 payload 避免 shell escape"""
    sftp = ssh.open_sftp()
    tmp = upload_payload(sftp, 'exp', body)
    sftp.close()
    out, _ = ssh_exec(ssh, f"curl -sS {url} -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data-binary @{tmp}")
    ssh_exec(ssh, f"rm -f {tmp}")
    return out

def curl_put_json(ssh, url, auth, body):
    sftp = ssh.open_sftp()
    tmp = upload_payload(sftp, 'exp', body)
    sftp.close()
    out, _ = ssh_exec(ssh, f"curl -sS {url} -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json' -X PUT --data-binary @{tmp}")
    ssh_exec(ssh, f"rm -f {tmp}")
    return out

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    results = []
    sftp = ssh.open_sftp()

    # 1) 登录
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin123\"}}'")
    login = json.loads(out)
    token = login['data']['token']
    auth = f"Authorization: Bearer {token}"
    print(f"[1] 登录 OK: token={token[:30]}...")

    # 2) 列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/expenses -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        d = r.get('data', {})
        total = d.get('total', 0) if isinstance(d, dict) else 0
        items = d.get('data', []) if isinstance(d, dict) else d
        print(f"[2] 报销列表: total={total}, returned={len(items) if isinstance(items, list) else 'n/a'}")
        results.append(('list', True))
    except Exception as e:
        print(f"[2] 解析失败: {e}, raw={out[:200]}")
        results.append(('list', False))

    # 3) stats
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/expenses/stats -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        d = r.get('data', {})
        print(f"[3] 统计: total={d.get('total')}, pending={d.get('pending')}, approved={d.get('approved')}, paid={d.get('paid')}, totalAmount={d.get('totalAmount')}")
        ok = 'total' in d
        results.append(('stats', ok))
    except Exception as e:
        print(f"[3] 失败: {e}, raw={out[:200]}")
        results.append(('stats', False))

    # 4) projects (下拉)
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/expenses/projects -H '{auth}' -H 'Accept: application/json'")
    try:
        r = json.loads(out)
        projects = r.get('data', [])
        print(f"[4] 项目下拉: count={len(projects)}")
        if projects:
            print(f"    第1个: {projects[0].get('name')}")
        project_id = projects[0]['id'] if projects else None
        results.append(('projects', True))
    except Exception as e:
        print(f"[4] 失败: {e}, raw={out[:200]}")
        project_id = None
        results.append(('projects', False))

    # 5) 新建报销 — 含 items 数组
    create_payload = {
        "category": "travel",
        "description": f"E2E测试-{int(time.time())} 报销事由：客户现场差旅",
        "project_id": project_id,
        "items": [
            {"item_date": "2026-06-10", "description": "高铁票（深圳-北京）", "amount": 580.50, "category": "travel"},
            {"item_date": "2026-06-10", "description": "住宿2晚",            "amount": 1200.00, "category": "travel"},
            {"item_date": "2026-06-11", "description": "市内打车",            "amount": 219.50, "category": "travel"},
        ],
    }
    out = curl_post_json(ssh, f"{BASE}/expenses", auth, create_payload)
    new_id = None
    try:
        r = json.loads(out)
        if r.get('code') == 0:
            d = r['data']
            new_id = d['id']
            print(f"[5] 新建报销 OK: id={new_id}, claim_no={d.get('claim_no')}, total={d.get('total_amount')}")
            # 验证 total 自动计算
            expected_total = 580.50 + 1200.00 + 219.50
            actual_total = float(d.get('total_amount', 0))
            if abs(actual_total - expected_total) < 0.01:
                print(f"    ✓ 金额自动计算正确: {actual_total}")
            else:
                print(f"    ✗ 金额计算异常: 期望 {expected_total}, 实际 {actual_total}")
            results.append(('create', True))
        else:
            print(f"[5] 失败: {r.get('message')}")
            results.append(('create', False))
    except Exception as e:
        print(f"[5] 解析失败: {e}, raw={out[:300]}")
        results.append(('create', False))

    # 6) show 详情
    if new_id:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/expenses/{new_id} -H '{auth}' -H 'Accept: application/json'")
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                d = r['data']
                items = d.get('items', [])
                print(f"[6] 详情 OK: status={d.get('status')}, status_label={d.get('status_label')}, items={len(items)}")
                results.append(('show', True))
            else:
                print(f"[6] 失败: {r.get('message')}")
                results.append(('show', False))
        except Exception as e:
            print(f"[6] 异常: {e}")
            results.append(('show', False))

    # 7) 审批通过
    if new_id:
        out = curl_post_json(ssh, f"{BASE}/expenses/{new_id}/approve", auth, {"action": "approved", "comment": "E2E测试通过"})
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[7] 审批 OK: {r.get('message')}")
                results.append(('approve', True))
            else:
                print(f"[7] 失败: {r.get('message')}")
                results.append(('approve', False))
        except Exception as e:
            print(f"[7] 异常: {e}")
            results.append(('approve', False))

    # 8) 标记付款
    if new_id:
        out = curl_post_json(ssh, f"{BASE}/expenses/{new_id}/pay", auth, {"paid_amount": 2000.00})
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[8] 付款 OK: {r.get('message')}")
                results.append(('pay', True))
            else:
                print(f"[8] 失败: {r.get('message')}")
                results.append(('pay', False))
        except Exception as e:
            print(f"[8] 异常: {e}")
            results.append(('pay', False))

    # 9) 验证已付款状态 + 验证「已付款单据不能撤销」业务规则
    if new_id:
        # 9a) 撤销应被拒绝 (status=paid)
        out = curl_post_json(ssh, f"{BASE}/expenses/{new_id}/cancel", auth, {})
        try:
            r = json.loads(out)
            msg = r.get('message', '')
            # 期望返回 1002 错误
            if r.get('code') in (1001, 1002) or '已审批' in msg or '已支付' in msg or '已付款' in msg:
                print(f"[9a] 撤销已付款单据被拒 ✓ ({msg})")
                results.append(('cancel_paid_blocked', True))
            else:
                print(f"[9a] 期望拒绝，实际: {r}")
                results.append(('cancel_paid_blocked', False))
        except Exception as e:
            print(f"[9a] 异常: {e}")
            results.append(('cancel_paid_blocked', False))

        # 9b) 验证最终状态
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/expenses/{new_id} -H '{auth}' -H 'Accept: application/json'")
        try:
            r = json.loads(out)
            d = r.get('data', {})
            ok = d.get('status') == 'paid' and float(d.get('paid_amount', 0)) > 0
            print(f"[9b] 最终状态: status={d.get('status')}, paid_amount={d.get('paid_amount')}, paid_at={d.get('paid_at')}")
            print(f"    {'✓' if ok else '✗'} 完整流程正确")
            results.append(('final_state', ok))
        except Exception as e:
            print(f"[9b] 异常: {e}")
            results.append(('final_state', False))

    # 总结
    print('\n' + '='*60)
    print('E2E 报销管理测试结果：')
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
