#!/usr/bin/env python3
"""v0.3.7.3 E2E: 消息中心 + 公司网盘 (A 阶段)"""
import paramiko, json, sys, os, tempfile

HOST='172.20.0.139'; USER='nbcy'; PWD='admin123'
BASE='http://127.0.0.1:3000/api'
SSH = None; SFTP = None

def ssh_cmd(cmd, timeout=30):
    so,se = SSH.exec_command(f'sudo -u www-data bash -c "cd /var/www/oa-api && {cmd}"', timeout=timeout)
    return so.read().decode('utf-8','replace'), se.read().decode('utf-8','replace')

def curl(method, url, body=None, token=None, timeout=15, debug=False):
    cmd = f"curl -sS -X {method} '{url}' -H 'Accept: application/json'"
    if token:
        cmd += f" -H 'Authorization: Bearer {token}'"
    if body:
        tf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(body, tf); tf.close()
        SFTP.put(tf.name, f'/tmp/{os.path.basename(tf.name)}')
        os.unlink(tf.name)
        cmd += f" --data-binary @/tmp/{os.path.basename(tf.name)}"
    cmd += " -H 'Content-Type: application/json'"
    si, so, se = SSH.exec_command(cmd, timeout=timeout)
    raw = so.read().decode('utf-8','replace')
    if debug:
        print(f'  [DEBUG] {method} {url}')
        print(f'  [DEBUG] raw: {raw[:300]}')
    try: return json.loads(raw)
    except: return {'_raw': raw[:200]}

passcount = 0; failcount = 0; steps = []
def step(desc, cond, detail=''):
    global passcount, failcount
    if cond:
        passcount += 1
        steps.append(f'  ✅ {desc}')
    else:
        failcount += 1
        steps.append(f'  ❌ {desc}: {detail}')

try:
    print('=== E2E 消息+网盘 开始 ===')
    SSH = paramiko.SSHClient()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    SFTP = SSH.open_sftp()

    # 登录
    r = curl('POST', f'{BASE}/auth/login', {'username':'admin','password':'admin123'})
    step('登录', r.get('code')==0 or r.get('data',{}).get('token'), f"code={r.get('code')}")
    TOKEN = r.get('data',{}).get('token','')
    H = TOKEN

    # ── 消息中心 ──
    print('\n--- 消息中心 ---')
    r = curl('GET', f'{BASE}/notifications', token=H)
    step('消息列表', r.get('code')==0, f"code={r.get('code')}")
    # 健壮解析：处理各种响应格式
    d = r.get('data', {})
    msgs = []
    if isinstance(d, list):
        msgs = d
    elif isinstance(d, dict):
        # 分页格式: d['data'] = [...] 或 d['items'] = [...]
        for k in ('data', 'items'):
            v = d.get(k, None)
            if isinstance(v, list):
                msgs = v
                break
    step(f'消息列表条数={len(msgs)}', True)

    r2 = curl('GET', f'{BASE}/notifications/unread-count', token=H)
    step('未读计数', r2.get('code')==0, f"code={r2.get('code')}")
    uc = (r2.get('data',{}).get('count',0)) if r2.get('code')==0 else 0
    step(f'未读数={uc}', True)

    r3 = curl('POST', f'{BASE}/notifications/mark-all-read', token=H)
    step('全部标为已读', r3.get('code')==0, f"code={r3.get('code')}")

    r4 = curl('GET', f'{BASE}/notifications/unread-count', token=H)
    uc2 = (r4.get('data',{}).get('count',0)) if r4.get('code')==0 else 0
    step(f'全部已读后未读数={uc2}', uc2==0, f"uc2={uc2}")

    # ── 公司网盘 ──
    print('\n--- 公司网盘 ---')
    r5 = curl('GET', f'{BASE}/disk/folders', token=H)
    step('文件夹列表', r5.get('code')==0, f"code={r5.get('code')}")
    folders = r5.get('data',[]) if r5.get('code')==0 else []
    step(f'根目录文件夹数={len(folders)}', True)

    # 新建文件夹
    r6 = curl('POST', f'{BASE}/disk/folders', {'name':'E2E测试文件夹'}, H)
    step('新建文件夹', r6.get('code')==0, f"code={r6.get('code')}")
    folder_id = (r6.get('data',{}).get('id')) if r6.get('code')==0 else None
    step(f'新文件夹id={folder_id}', folder_id is not None, f"folder_id={folder_id}")

    # 列出新文件夹里的内容（应该为空）
    if folder_id:
        r7 = curl('GET', f'{BASE}/disk/files?folder_id={folder_id}', token=H)
        step('新文件夹文件列表', r7.get('code')==0, f"code={r7.get('code')}")

    # 删除测试文件夹
    if folder_id:
        r8 = curl('DELETE', f'{BASE}/disk/folders/{folder_id}', token=H)
        step('删除测试文件夹', r8.get('code')==0, f"code={r8.get('code')}")

    # 根目录文件夹数恢复
    r9 = curl('GET', f'{BASE}/disk/folders', token=H)
    folders2 = r9.get('data',[]) if r9.get('code')==0 else []
    step(f'删除后根目录文件夹数={len(folders2)}', len(folders2)<=len(folders), f"before={len(folders)},after={len(folders2)}")

    print('\n'.join(steps))
    print(f'\n=== 结果: {passcount}/{passcount+failcount} 通过 ===')

finally:
    if SFTP: SFTP.close()
    if SSH: SSH.close()
