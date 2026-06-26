"""V0.4.4 多角色端到端走查脚本 - 4 角色 × 6 模块 × 14 动作"""
import json, time, paramiko

HOST = '192.168.3.117'
USER = 'nbcy'
PWD = 'admin123'

# 4 角色测试账号 (117 端实际用户名)
ACCOUNTS = {
    'admin':    ('admin',     'admin123',  1,  '超级管理员'),
    'manager':  ('proj_mgr',  '123456',    2,  '项目经理'),
    'user':     ('eng_zhao',  '123456',    4,  '普通员工(工程师)'),
    'finance':  ('fin_zhou',  '123456',    3,  '财务人员'),
    'tech':     ('tech_mgr',  '123456',    2,  '技术经理'),
    'sales':    ('sales_chen','123456',    2,  '销售经理'),
}


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
    j = http(ssh, 'POST', '/api/auth/login',
             body={'username': username, 'password': password})
    token = (j.get('data') or {}).get('token') or j.get('token')
    if not token:
        raise RuntimeError(f'login fail: {j.get("message", j)[:100]}')
    return token


def get_pid(ssh, token):
    j = http(ssh, 'GET', '/api/projects?per_page=1', token=token)
    items = (j.get('data') or {}).get('data') if isinstance(j.get('data'), dict) else (j.get('data') or [])
    return items[0]['id'] if items else 1


def main():
    ssh = ssh_connect()
    pid = None
    # 先用 admin 取 pid
    admin_tok = login(ssh, 'admin', 'admin123')
    pid = get_pid(ssh, admin_tok)
    print(f'=== test pid = {pid} ===\n')

    results = {}

    for role_key, (uname, upwd, role_id, role_label) in ACCOUNTS.items():
        print(f'\n========== 角色: {role_label} ({uname}) ==========')
        try:
            tok = login(ssh, uname, upwd)
        except Exception as e:
            print(f'  login fail: {e}')
            results[role_key] = {'login': 'fail', 'reason': str(e)}
            continue
        results[role_key] = {'login': 'ok'}

        # 6 模块
        for label, method, path, body in [
            # GET 列表
            ('GET 团队',      'GET',  '/api/construction/teams',                    None),
            ('GET 开工单',    'GET',  '/api/construction/commencement-orders',      None),
            ('GET 施工日志',  'GET',  '/api/construction/logs',                      None),
            ('GET 工序字典',  'GET',  '/api/construction/work-processes',            None),
            ('GET 整改',      'GET',  '/api/construction/rectifications',            None),
            ('GET 发包',      'GET',  '/api/construction/external-works',            None),
            # POST 创建 (用唯一带角色后缀名字)
            ('POST 团队',     'POST', '/api/construction/teams',                     {'project_id': pid, 'team_name': f'V044-{role_key}-团队', 'team_type': 'internal', 'leader_name': f'L-{role_key}', 'leader_phone': '13800138000'}),
            ('POST 工序',     'POST', '/api/construction/work-processes',            {'name': f'V044-{role_key}-工序', 'sequence': 1, 'status': 'active'}),
            # 详情
            ('GET 团队详情',  'GET',  '/api/construction/teams/1',                   None),
        ]:
            j = http(ssh, method, path, token=tok, body=body)
            code = j.get('code', '?')
            if code == 0:
                if method == 'GET' and 'data' in j:
                    data = j['data']
                    if isinstance(data, dict) and 'data' in data:
                        cnt = len(data.get('data', []))
                    elif isinstance(data, dict):
                        cnt = 'detail'
                    else:
                        cnt = len(data) if data else 0
                else:
                    cnt = 'created'
                print(f'  ✓ {label:14s} code={code} cnt={cnt}')
                results[role_key][label] = 'OK'
            else:
                msg = (j.get('message') or '')[:60]
                print(f'  ✗ {label:14s} code={code} msg={msg}')
                results[role_key][label] = f'FAIL:{msg}'

    # 总结
    print('\n\n========== 多角色走查总结 ==========')
    print(f"{'角色':15s} {'登录':4s} | " + ' | '.join(f'{k:12s}' for k in [
        'GET团队', 'GET开工单', 'GET日志', 'GET工序', 'GET整改', 'GET发包',
        'POST团队', 'POST工序', 'GET详情']))
    for r, res in results.items():
        login_s = '✓' if res.get('login') == 'ok' else '✗'
        line = f"{r:15s} {login_s:4s} | "
        for k in ['GET 团队', 'GET 开工单', 'GET 施工日志', 'GET 工序字典', 'GET 整改', 'GET 发包',
                  'POST 团队', 'POST 工序', 'GET 团队详情']:
            v = res.get(k, '-')
            sym = '✓' if v == 'OK' else '✗'
            line += f'{sym:12s} | '
        print(line)

    # 写文件
    import os
    os.makedirs(os.path.dirname('/d/work/website/OA/.workbuddy/memory/'), exist_ok=True)
    with open('/d/work/website/OA/.workbuddy/memory/v044_role_e2e.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ssh.close()
    print('\n结果已存: memory/v044_role_e2e.json')


if __name__ == '__main__':
    main()
