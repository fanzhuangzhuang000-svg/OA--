"""V0.4.4 业务闭环走查 - 真实业务流：团队→开工单→日志→整改→发包"""
import json, paramiko, time

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'


def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=20)
    return ssh


def http(ssh, method, path, token=None, body=None):
    headers = ['-H "Accept: application/json"']
    if token:
        headers.append(f'-H "Authorization: Bearer {token}"')
    if body is not None:
        headers.append('-H "Content-Type: application/json"')
    h = ' '.join(headers)
    if body is not None:
        b = f"-d '{json.dumps(body, ensure_ascii=False)}'"
        cmd = f"""curl -s -X {method} 'http://127.0.0.1{path}' {h} {b}"""
    else:
        cmd = f"""curl -s -X {method} 'http://127.0.0.1{path}' {h}"""
    si, so, se = ssh.exec_command(cmd, timeout=30)
    out = so.read().decode('utf-8', 'replace').strip()
    try:
        return json.loads(out)
    except Exception:
        return {'raw': out}


def login(ssh, username, password):
    j = http(ssh, 'POST', '/api/auth/login', body={'username': username, 'password': password})
    return (j.get('data') or {}).get('token') or j.get('token')


def main():
    ssh = ssh_connect()
    tok = login(ssh, 'admin', 'admin123')
    print(f'=== 业务闭环走查 (V0.4.4) ===')
    print(f'token={"OK" if tok else "FAIL"}\n')

    # 1) 拿项目
    j = http(ssh, 'GET', '/api/projects?per_page=1', token=tok)
    items = (j.get('data') or {}).get('data') if isinstance(j.get('data'), dict) else (j.get('data') or [])
    pid = items[0]['id'] if items else 1
    print(f'[1] 项目 pid = {pid}')

    # 找 active supplier (V0.4.4 放宽: material/service/outsource 都行)
    # 直接取存在的 id (117 端 supplier id 从 6 开始)
    sup_id = 7  # 大华股份
    print(f'[1.5] supplier_id = {sup_id}')

    flow = {}

    import time as _t
    suffix = str(int(_t.time()))[-6:]

    # 2) 团队
    j = http(ssh, 'POST', '/api/construction/teams', tok, {
        'project_id': pid, 'team_name': f'V044F-{suffix}-施工一组',
        'team_type': 'internal', 'leader_name': '王工', 'leader_phone': '13800000001'
    })
    team_id = (j.get('data') or {}).get('id')
    print(f'[2] 团队 {team_id}' if team_id else f'[2] 团队 FAIL: {j.get("message", "")[:60]}')
    flow['team_id'] = team_id

    # 3) 加成员
    j = http(ssh, 'POST', f'/api/construction/teams/{team_id}/members', tok, {
        'members': [
            {'name': '张工', 'phone': '13800000010', 'role': 'foreman'},
            {'name': '李工', 'phone': '13800000011', 'role': 'worker'},
        ]
    })
    member_count = (j.get('data') or {}).get('count', 0)
    print(f'[3] 团队成员 {member_count}')

    # 4) 开工单
    j = http(ssh, 'POST', '/api/construction/commencement-orders', tok, {
        'project_id': pid, 'team_id': team_id,
        'planned_start_date': '2026-06-25', 'planned_end_date': '2026-07-25',
        'work_scope': 'V044验收-某科技园综合布线项目',
        'safety_requirements': '高空作业需持证',
    })
    order_id = (j.get('data') or {}).get('id')
    print(f'[4] 开工单 {order_id}' if order_id else f'[4] 开工单 FAIL: {j.get("message", "")[:80]}')
    flow['order_id'] = order_id

    # 5) 审批开工单
    j = http(ssh, 'POST', f'/api/construction/commencement-orders/{order_id}/approve', tok, {
        'approve_remark': 'V044F 流程验收测试-审批通过'
    })
    print(f'[5] 审批 {j.get("message", "")[:50]}')

    # 6) 开工
    j = http(ssh, 'POST', f'/api/construction/commencement-orders/{order_id}/start', tok, {
        'remark': 'V044F 流程-实际开工日 2026-06-25'
    })
    print(f'[6] 开工 {j.get("message", "")[:50]}')

    # 7) 创建工序 (3 个, 用唯一 timestamp 后缀)
    proc_ids = []
    for seq, name in [(1, '线管敷设'), (2, '线缆穿管'), (3, '设备安装调试')]:
        j = http(ssh, 'POST', '/api/construction/work-processes', tok, {
            'project_id': pid, 'name': f'V044F-{suffix}-{name}', 'sequence': seq,
            'description': f'流程-工序-{name}', 'estimated_hours': 80
        })
        pid_ = (j.get('data') or {}).get('id')
        proc_ids.append(pid_)
        print(f'[7.{seq}] 工序 {name} id={pid_}')

    # 8) 提交 5 天施工日志
    from datetime import date, timedelta
    for i in range(5):
        d = (date(2026, 6, 25) + timedelta(days=i)).isoformat()
        j = http(ssh, 'POST', '/api/construction/logs', tok, {
            'commencement_order_id': order_id,
            'project_id': pid,
            'team_id': team_id,
            'work_date': d,
            'weather': '晴',
            'content': f'流程-{d} 完成了 V044 验收测试第 {i+1} 天工作',
            'progress_percentage': (i+1) * 20,
            'work_hours': 8.0,
            'worker_count': 5,
        })
        log_id = (j.get('data') or {}).get('id')
        print(f'[8.{i+1}] 日志 {d} id={log_id}')

    # 9) 提交施工日志 (id=443)
    j = http(ssh, 'POST', f'/api/construction/logs/{443}/submit', tok, {})
    print(f'[9] 提交日志 {j.get("message", "")[:50]}')

    # 10) 创建一个整改单
    j = http(ssh, 'POST', '/api/construction/rectifications', tok, {
        'project_id': pid, 'source_type': 'audit',
        'title': 'V044-流程-高空作业未带安全帽',
        'description': '现场检查发现 1 名工人未佩戴安全帽,要求立即整改',
        'severity': 'high', 'deadline': '2026-06-27',
        'responsible_id': 76  # proj_mgr
    })
    rect_id = (j.get('data') or {}).get('id')
    print(f'[10] 整改单 {rect_id}' if rect_id else f'[10] 整改单 FAIL: {j.get("message", "")[:80]}')
    flow['rect_id'] = rect_id

    # 11) 完成整改
    j = http(ssh, 'POST', f'/api/construction/rectifications/{rect_id}/complete', tok, {
        'rectify_result': '已现场教育 + 配发安全帽'
    })
    print(f'[11] 完成整改 {j.get("message", "")[:50]}')

    # 12) 内部验收
    # V0.4.4 内部验收 action: PATCH 直接改字段 (因为 V0.4.4 service 占位)
    # 改走 update action
    j = http(ssh, 'GET', f'/api/construction/rectifications/{rect_id}', token=tok)
    print(f'[12] 整改详情 status={((j.get("data") or {}).get("status"))}')

    # 13) 发包
    j = http(ssh, 'POST', '/api/construction/external-works', tok, {
        'project_id': pid, 'title': 'V044-流程-高空作业专业分包',
        'work_scope': '高空作业 100 工时',
        'budget': 50000, 'deadline': '2026-07-10',
        'requirements': ['高空作业证', '5 年以上经验'],
    })
    work_id = (j.get('data') or {}).get('id')
    print(f'[13] 发包 {work_id}' if work_id else f'[13] 发包 FAIL: {j.get("message", "")[:80]}')
    flow['work_id'] = work_id

    # 14) 投标 (用上面拿到的 sup_id)
    j = http(ssh, 'POST', f'/api/construction/external-works/{work_id}/bids', tok, {
        'supplier_id': sup_id, 'bid_amount': 48000, 'bid_days': 15,
        'technical_proposal': 'V044 流程-高空作业专业分包报价',
        'construction_plan': '人员配置 8 人,工期 15 天',
    })
    bid_msg = j.get('message', '')[:60]
    bid_id = (j.get('data') or {}).get('id')
    print(f'[14] 投标 {bid_msg} id={bid_id}')

    # 14.5) 定标
    if bid_id:
        j = http(ssh, 'POST', f'/api/construction/external-works/{work_id}/award', tok, {
            'bid_id': bid_id
        })
        print(f'[14.5] 定标 {j.get("message", "")[:60]}')

    # 15) 完工
    j = http(ssh, 'POST', f'/api/construction/commencement-orders/{order_id}/complete', tok, {})
    print(f'[15] 完工 {j.get("message", "")[:50]}')

    # 16) 最终状态
    print(f'\n========== 最终状态 ==========')
    for label, path in [
        ('团队',     f'/api/construction/teams/{team_id}'),
        ('开工单',   f'/api/construction/commencement-orders/{order_id}'),
        ('整改单',   f'/api/construction/rectifications/{rect_id}'),
        ('发包',     f'/api/construction/external-works/{work_id}'),
    ]:
        j = http(ssh, 'GET', path, token=tok)
        d = j.get('data') or {}
        print(f'  {label:8s} id={d.get("id")} status={d.get("status")}')

    ssh.close()


if __name__ == '__main__':
    main()
