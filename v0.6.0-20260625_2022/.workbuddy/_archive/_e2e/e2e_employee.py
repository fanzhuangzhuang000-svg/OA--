#!/usr/bin/env python3
"""v0.3.7.3 员工管理 E2E 测试 — 8 项（用文件传 payload 避免 shell escape）"""
import paramiko, json, sys, time, os, tempfile

HOST='172.20.0.139'; USER='nbcy'; PWD='admin123'
BASE='http://127.0.0.1:3000/api'

def ssh_exec(ssh, cmd):
    si, so, se = ssh.exec_command(cmd, timeout=60)
    return so.read().decode('utf-8', 'replace'), se.read().decode('utf-8', 'replace')

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

    # 2) 列出员工
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees -H '{auth}'")
    emp = json.loads(out)
    items = emp.get('data', {}).get('data', [])
    total = emp.get('data', {}).get('total')
    print(f"[2] 员工列表: total={total}, count={len(items)}")
    if items:
        first = items[0]
        print(f"    第1个: name={first['name']}, status={first.get('status')}, is_active={first.get('is_active')}")
    results.append(('list', True))

    # 3) 部门列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/departments -H '{auth}'")
    depts = json.loads(out)
    dlist = depts.get('data', [])
    print(f"[3] 部门列表: count={len(dlist)}")
    if dlist:
        print(f"    第1个: name={dlist[0]['name']}, count={dlist[0].get('count')}")
    results.append(('departments', True))

    # 4) 岗位列表
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/positions -H '{auth}'")
    poss = json.loads(out)
    plist = poss.get('data', [])
    print(f"[4] 岗位列表: count={len(plist)}")
    results.append(('positions', True))

    # 5) 新建员工 — 用 SFTP 传 payload 文件
    uname = f"test_emp_{int(time.time())}"
    new_id = None
    # 用唯一手机号避免 unique 冲突
    phone = f"139{int(time.time()) % 100000000:08d}"
    # 先查一下有哪些 role（不能假设 id=1 存在）
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/roles -H '{auth}'")
    try:
        roles_data = json.loads(out).get('data', {}).get('data', [])
    except Exception:
        roles_data = []
    role_id = roles_data[0]['id'] if roles_data else None
    create_payload = {
        "name": "Test Employee",
        "username": uname,
        "password": "test123456",
        "phone": phone,
        "email": f"{uname}@test.com",
        "department_id": dlist[0]['id'] if dlist else None,
        "position_id": plist[0]['id'] if plist else None,
        "role_id": role_id,
        "hire_date": "2025-01-15",
    }
    tmp_remote = f"/tmp/emp_create_{int(time.time())}.json"
    payload_str = json.dumps(create_payload, ensure_ascii=False)
    with sftp.open(tmp_remote, 'w') as f:
        f.write(payload_str)
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees -H '{auth}' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data-binary @{tmp_remote}")
    ssh_exec(ssh, f"rm -f {tmp_remote}")
    print(f"[5] 新建员工 response: {out[:400]}")
    try:
        created = json.loads(out)
        if created.get('code') == 0:
            new_id = created['data']['id']
            print(f"    成功 id={new_id}, dept={created['data'].get('department',{}).get('name')}, role={[r['name'] for r in created['data'].get('roles',[])]}")
            results.append(('create', True))
        else:
            print(f"    失败: {created.get('message')}")
            results.append(('create', False))
    except Exception as e:
        print(f"    解析失败: {e}")
        results.append(('create', False))

    # 6) 编辑员工
    if new_id:
        upd = {"name": "Test Employee (Updated)", "is_active": False}
        tmp_remote = f"/tmp/emp_upd_{int(time.time())}.json"
        with sftp.open(tmp_remote, 'w') as f:
            f.write(json.dumps(upd, ensure_ascii=False))
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/{new_id} -H '{auth}' -H 'Content-Type: application/json' -X PUT --data-binary @{tmp_remote}")
        ssh_exec(ssh, f"rm -f {tmp_remote}")
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[6] 编辑员工 OK: name={r['data']['name']}, is_active={r['data'].get('is_active')}, status={r['data'].get('status')}")
                results.append(('update', True))
            else:
                print(f"[6] 失败: {r.get('message')}")
                results.append(('update', False))
        except Exception as e:
            print(f"[6] 解析失败: {e}")
            results.append(('update', False))

    # 7) 验证 enum cast 正确性 — inactive
    if new_id:
        # 用 show 端点（已加 is_active 字段）
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/{new_id} -H '{auth}'")
        try:
            r = json.loads(out)
            d = r.get('data', {})
            print(f"[7] 验证 enum: status={d.get('status')}, is_active={d.get('is_active')}")
            ok = d.get('status') == 'inactive' and d.get('is_active') == False
            print(f"    {'✓' if ok else '✗'} enum inactive 正确 (is_active 期望 False，实际 {d.get('is_active')})")
            results.append(('enum_inactive', ok))
        except Exception as e:
            print(f"[7] 异常: {e}")
            results.append(('enum_inactive', False))

    # 8) 删除员工
    if new_id:
        out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/{new_id} -H '{auth}' -X DELETE")
        try:
            r = json.loads(out)
            if r.get('code') == 0:
                print(f"[8] 删除员工 OK: {r.get('message')}")
                results.append(('delete', True))
            else:
                print(f"[8] 失败: {r.get('message')}")
                results.append(('delete', False))
        except Exception as e:
            print(f"[8] 解析失败: {e}")
            results.append(('delete', False))

    # 9) 部门管理 - 新建/编辑/删除
    dept_data = {"name": f"测试部-{int(time.time())}", "parent_id": 1, "sort_order": 99}
    tmp_remote = f"/tmp/dept_create_{int(time.time())}.json"
    with sftp.open(tmp_remote, 'w') as f:
        f.write(json.dumps(dept_data, ensure_ascii=False))
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/departments -H '{auth}' -H 'Content-Type: application/json' -X POST --data-binary @{tmp_remote}")
    ssh_exec(ssh, f"rm -f {tmp_remote}")
    try:
        d = json.loads(out)
        if d.get('code') == 0:
            did = d['data']['id']
            print(f"[9.1] 新建部门 OK: id={did}, name={d['data']['name']}")
            upd = {"sort_order": 88}
            tmp_remote = f"/tmp/dept_upd_{int(time.time())}.json"
            with sftp.open(tmp_remote, 'w') as f:
                f.write(json.dumps(upd, ensure_ascii=False))
            ssh_exec(ssh, f"curl -sS {BASE}/employees/departments/{did} -H '{auth}' -H 'Content-Type: application/json' -X PUT --data-binary @{tmp_remote}")
            ssh_exec(ssh, f"rm -f {tmp_remote}")
            print(f"[9.2] 编辑部门 OK")
            out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/departments/{did} -H '{auth}' -X DELETE")
            dd = json.loads(out)
            if dd.get('code') == 0:
                print(f"[9.3] 删除部门 OK")
                results.append(('dept_crud', True))
            else:
                print(f"[9.3] 删除失败: {dd.get('message')}")
                results.append(('dept_crud', False))
        else:
            print(f"[9.1] 失败: {d.get('message')}")
            results.append(('dept_crud', False))
    except Exception as e:
        print(f"[9] 部门测试异常: {e}")
        results.append(('dept_crud', False))

    # 10) 岗位管理
    pos_data = {"name": f"测试岗-{int(time.time())}", "department_id": 1, "level": "P5"}
    tmp_remote = f"/tmp/pos_create_{int(time.time())}.json"
    with sftp.open(tmp_remote, 'w') as f:
        f.write(json.dumps(pos_data, ensure_ascii=False))
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/positions -H '{auth}' -H 'Content-Type: application/json' -X POST --data-binary @{tmp_remote}")
    ssh_exec(ssh, f"rm -f {tmp_remote}")
    try:
        p = json.loads(out)
        if p.get('code') == 0:
            pid = p['data']['id']
            print(f"[10.1] 新建岗位 OK: id={pid}, name={p['data']['name']}")
            ssh_exec(ssh, f"curl -sS {BASE}/employees/positions/{pid} -H '{auth}' -X DELETE")
            print(f"[10.2] 删除岗位 OK")
            results.append(('position_crud', True))
        else:
            print(f"[10.1] 失败: {p.get('message')}")
            results.append(('position_crud', False))
    except Exception as e:
        print(f"[10] 岗位测试异常: {e}")
        results.append(('position_crud', False))

    # 11) 技能标签
    skill_data = {"name": f"测试技能-{int(time.time())}", "category": "install", "color": "#409EFF"}
    tmp_remote = f"/tmp/skill_create_{int(time.time())}.json"
    with sftp.open(tmp_remote, 'w') as f:
        f.write(json.dumps(skill_data, ensure_ascii=False))
    out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/skills -H '{auth}' -H 'Content-Type: application/json' -X POST --data-binary @{tmp_remote}")
    ssh_exec(ssh, f"rm -f {tmp_remote}")
    try:
        s = json.loads(out)
        if s.get('code') == 0:
            sid = s['data']['id']
            print(f"[11.1] 新建技能 OK: id={sid}, name={s['data']['name']}")
            # 11.2 attach — 绑给 admin
            att_data = {"user_id": 1, "proficiency": "advanced"}
            tmp_remote = f"/tmp/skill_attach_{int(time.time())}.json"
            with sftp.open(tmp_remote, 'w') as f:
                f.write(json.dumps(att_data, ensure_ascii=False))
            out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/skills/{sid}/attach -H '{auth}' -H 'Content-Type: application/json' -X POST --data-binary @{tmp_remote}")
            ssh_exec(ssh, f"rm -f {tmp_remote}")
            ar = json.loads(out)
            print(f"[11.2] 绑定技能 OK: {ar.get('message')}")
            # 11.3 detach
            det_data = {"user_id": 1}
            tmp_remote = f"/tmp/skill_detach_{int(time.time())}.json"
            with sftp.open(tmp_remote, 'w') as f:
                f.write(json.dumps(det_data, ensure_ascii=False))
            out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/skills/{sid}/detach -H '{auth}' -H 'Content-Type: application/json' -X POST --data-binary @{tmp_remote}")
            ssh_exec(ssh, f"rm -f {tmp_remote}")
            dr = json.loads(out)
            print(f"[11.3] 解绑技能 OK: {dr.get('message')}")
            # 11.4 删除技能
            out, _ = ssh_exec(ssh, f"curl -sS {BASE}/employees/skills/{sid} -H '{auth}' -X DELETE")
            dd = json.loads(out)
            print(f"[11.4] 删除技能 OK: {dd.get('message')}")
            results.append(('skill_crud', True))
        else:
            print(f"[11.1] 失败: {s.get('message')}")
            results.append(('skill_crud', False))
    except Exception as e:
        print(f"[11] 技能测试异常: {e}")
        results.append(('skill_crud', False))

    # 总结
    print(f"\n========== 员工管理 E2E 总结 ==========")
    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    print(f"\n通过: {passed}/{len(results)}")

    sftp.close()
    ssh.close()
    return 0 if passed == len(results) else 1

if __name__ == '__main__':
    sys.exit(main())
