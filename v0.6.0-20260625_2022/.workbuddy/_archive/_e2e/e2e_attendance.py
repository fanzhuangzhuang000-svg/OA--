#!/usr/bin/env python3
"""v0.3.7.3 考勤管理 E2E — 11 项
   1) overview      GET  /attendance/overview
   2) clock-in      POST /attendance/clock-in
   3) clock-out     POST /attendance/clock-out
   4) records       GET  /attendance/records
   5) leave create  POST /attendance/leave
   6) leave approve POST /attendance/leave/{id}/approve (approved)
   7) leave revoke  DELETE /attendance/leave/{id} 业务规则：已批准应被拒
   8) overtime      POST /attendance/overtime
   9) overtime appr POST /attendance/overtime/{id}/approve
  10) overtime rev  DELETE /attendance/overtime/{id} 业务规则：已批准应被拒
  11) report        GET  /attendance/report
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
        tmp = upload_payload(sftp, 'att', body)
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

    # 1) overview
    print("\n[1] GET /attendance/overview")
    out = curl(ssh, 'GET', f'{BASE}/attendance/overview', auth)
    r = json.loads(out)
    d = r.get('data', {})
    print(f"   totalUsers={d.get('totalUsers')} present={d.get('present')} late={d.get('late')} absent={d.get('absent')}")
    results.append(record('overview: 考勤总览', ok(r) and 'totalUsers' in d))

    # 2) clock-in
    print("\n[2] POST /attendance/clock-in")
    out = curl(ssh, 'POST', f'{BASE}/attendance/clock-in', auth, {
        'location': '公司1号楼-1F',
        'remark': 'e2e 上班打卡',
    })
    r = json.loads(out)
    clock_in = r.get('data', {}).get('clock_in') or r.get('clock_in')
    print(f"   clock_in={clock_in}")
    results.append(record('clock_in: 上班打卡', ok(r) and clock_in is not None))

    # 3) clock-out
    print("\n[3] POST /attendance/clock-out")
    out = curl(ssh, 'POST', f'{BASE}/attendance/clock-out', auth, {
        'location': '公司1号楼-1F',
    })
    r = json.loads(out)
    clock_out = r.get('data', {}).get('clock_out') or r.get('clock_out')
    work_hours = r.get('data', {}).get('work_hours') or r.get('work_hours')
    print(f"   clock_out={clock_out} work_hours={work_hours}")
    results.append(record('clock_out: 下班打卡', ok(r) and clock_out is not None))

    # 4) records
    print("\n[4] GET /attendance/records")
    out = curl(ssh, 'GET', f'{BASE}/attendance/records', auth)
    r = json.loads(out)
    rec_list = r.get('data', {}).get('data', r.get('data', []))
    if isinstance(rec_list, dict): rec_list = rec_list.get('data', [])
    print(f"   返回 {len(rec_list) if isinstance(rec_list, list) else 'N/A'} 条打卡记录")
    results.append(record('records: 打卡记录列表', ok(r)))

    # 5) leave create
    print("\n[5] POST /attendance/leave 请假申请")
    out = curl(ssh, 'POST', f'{BASE}/attendance/leave', auth, {
        'type': 'annual',
        'start_date': '2026-07-01',
        'end_date': '2026-07-03',
        'days': 3,
        'reason': 'e2e 请假测试',
    })
    r = json.loads(out)
    lid = r.get('data', {}).get('id')
    print(f"   created id={lid} status={r.get('data', {}).get('status')}")
    results.append(record('leave_create: 请假创建', ok(r) and lid is not None))

    # 6) leave approve
    print("\n[6] POST /attendance/leave/{id}/approve approved")
    out = curl(ssh, 'POST', f'{BASE}/attendance/leave/{lid}/approve', auth, {'action': 'approved'})
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('leave_approve: 请假通过', ok(r)))

    # 7) leave revoke (业务规则: 已批准应被拒)
    print("\n[7] DELETE /attendance/leave/{id} (业务规则: 已approved应被拒)")
    out = curl(ssh, 'DELETE', f'{BASE}/attendance/leave/{lid}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('leave_revoke_reject: 业务规则拒绝', not ok(r) and r.get('code') == 1001))

    # 7b) 新建 pending 请假然后撤销
    print("\n[7b] 新建 pending 请假 + 撤销")
    out = curl(ssh, 'POST', f'{BASE}/attendance/leave', auth, {
        'type': 'sick',
        'start_date': '2026-08-01',
        'end_date': '2026-08-01',
        'days': 1,
        'reason': 'e2e 待撤销',
    })
    r = json.loads(out)
    lid2 = r.get('data', {}).get('id')
    out = curl(ssh, 'DELETE', f'{BASE}/attendance/leave/{lid2}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('leave_revoke: 撤销pending请假', ok(r)))

    # 8) overtime create
    print("\n[8] POST /attendance/overtime 加班申请")
    out = curl(ssh, 'POST', f'{BASE}/attendance/overtime', auth, {
        'overtime_date': '2026-09-15',
        'start_time': '18:00',
        'end_time': '22:00',
        'hours': 4,
        'reason': 'e2e 加班测试',
        'compensation_type': 'time_off',
    })
    r = json.loads(out)
    oid = r.get('data', {}).get('id')
    print(f"   created id={oid} status={r.get('data', {}).get('status')}")
    results.append(record('overtime_create: 加班创建', ok(r) and oid is not None))

    # 9) overtime approve
    print("\n[9] POST /attendance/overtime/{id}/approve approved")
    out = curl(ssh, 'POST', f'{BASE}/attendance/overtime/{oid}/approve', auth, {'action': 'approved'})
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('overtime_approve: 加班通过', ok(r)))

    # 10) overtime revoke (业务规则)
    print("\n[10] DELETE /attendance/overtime/{id} (业务规则: 已approved应被拒)")
    out = curl(ssh, 'DELETE', f'{BASE}/attendance/overtime/{oid}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('overtime_revoke_reject: 业务规则拒绝', not ok(r) and r.get('code') == 1001))

    # 10b) 新建 pending 加班 + 撤销
    print("\n[10b] 新建 pending 加班 + 撤销")
    out = curl(ssh, 'POST', f'{BASE}/attendance/overtime', auth, {
        'overtime_date': '2026-09-20',
        'start_time': '19:00',
        'end_time': '21:00',
        'hours': 2,
        'reason': 'e2e 待撤销',
        'compensation_type': 'overtime_pay',
    })
    r = json.loads(out)
    oid2 = r.get('data', {}).get('id')
    out = curl(ssh, 'DELETE', f'{BASE}/attendance/overtime/{oid2}', auth)
    r = json.loads(out)
    print(f"   code={r.get('code')} msg={r.get('message')}")
    results.append(record('overtime_revoke: 撤销pending加班', ok(r)))

    # 11) report
    print("\n[11] GET /attendance/report?month=2026-06")
    out = curl(ssh, 'GET', f'{BASE}/attendance/report?month=2026-06', auth)
    r = json.loads(out)
    rep_list = r.get('data', [])
    if isinstance(rep_list, dict): rep_list = rep_list.get('data', [])
    print(f"   返回 {len(rep_list) if isinstance(rep_list, list) else 'N/A'} 条员工考勤汇总")
    results.append(record('report: 月度考勤报表', ok(r)))

    passed = sum(results)
    total = len(results)
    print(f"\n{'='*50}\nE2E 考勤管理: {passed}/{total} 通过\n{'='*50}")
    ssh.close()
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
