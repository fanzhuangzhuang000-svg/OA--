#!/usr/bin/env python3
"""v0.3.7.3 E2E: 系统备份 (B 阶段)"""
import paramiko, json, sys, os, tempfile, time

HOST='172.20.0.139'; USER='nbcy'; PWD='admin123'
BASE='http://127.0.0.1:3000/api'
SSH = None; SFTP = None

def curl(method, url, body=None, token=None, timeout=60):
    cmd = f"curl -sS -X {method} '{url}' -H 'Accept: application/json'"
    if token: cmd += f" -H 'Authorization: Bearer {token}'"
    if body:
        tf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(body, tf); tf.close()
        SFTP.put(tf.name, f'/tmp/{os.path.basename(tf.name)}')
        os.unlink(tf.name)
        cmd += f" --data-binary @/tmp/{os.path.basename(tf.name)}"
    cmd += " -H 'Content-Type: application/json'"
    si, so, se = SSH.exec_command(cmd, timeout=timeout)
    raw = so.read().decode('utf-8','replace')
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
    print('=== E2E 系统备份 开始 ===')
    SSH = paramiko.SSHClient()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH.connect(HOST, port=22, username=USER, password=PWD, timeout=10)
    SFTP = SSH.open_sftp()

    # 登录
    r = curl('POST', f'{BASE}/auth/login', {'username':'admin','password':'admin123'})
    step('登录', r.get('code')==0, f"code={r.get('code')}")
    TOKEN = r.get('data',{}).get('token','')

    # 1. 列表
    r1 = curl('GET', f'{BASE}/backups', token=TOKEN)
    step('备份列表', r1.get('code')==0, f"code={r1.get('code')}")
    initial = r1.get('data',[]) if r1.get('code')==0 else []
    step(f'初始备份数={len(initial)}', True)

    # 2. 手动备份
    print('  [执行 mysqldump，可能需要 10-30 秒...]')
    r2 = curl('POST', f'{BASE}/backups', {'label':'e2e'}, TOKEN, timeout=120)
    step('手动备份', r2.get('code')==0, f"code={r2.get('code')}, msg={r2.get('message','')[:80]}")
    new_filename = (r2.get('data',{}).get('filename')) if r2.get('code')==0 else None
    step(f'新备份名={new_filename}', new_filename is not None)

    # 3. 列表更新
    r3 = curl('GET', f'{BASE}/backups', token=TOKEN)
    after = r3.get('data',[]) if r3.get('code')==0 else []
    step(f'备份后数量={len(after)}', len(after) == len(initial) + 1,
         f"before={len(initial)},after={len(after)}")

    # 4. 下载备份（用 curl 拉文件，验证非空）
    if new_filename:
        cmd_dl = (
            "curl -sS 'http://127.0.0.1:3000/api/backups/" + new_filename + "/download' "
            "-H 'Authorization: Bearer " + TOKEN + "' "
            "-o /tmp/test_download.sql.gz "
            "-w '%{http_code} %{size_download}'"
        )
        si, so, se = SSH.exec_command(cmd_dl, timeout=60)
        out = so.read().decode('utf-8','replace').strip()
        parts = out.split()
        status = parts[0] if parts else '?'
        try:
            size = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            size = -1
        step(f'下载响应 {status} 大小={size}B', status == '200' and size > 0,
             f"status={status} size={size} parts={parts}")

    # 5. 删除备份
    if new_filename:
        r5 = curl('DELETE', f'{BASE}/backups/{new_filename}', token=TOKEN)
        step('删除备份', r5.get('code')==0, f"code={r5.get('code')}")

    # 6. 删除后列表
    r6 = curl('GET', f'{BASE}/backups', token=TOKEN)
    final = r6.get('data',[]) if r6.get('code')==0 else []
    step(f'删除后数量={len(final)}', len(final) == len(initial),
         f"final={len(final)},initial={len(initial)}")

    print('\n'.join(steps))
    print(f'\n=== 结果: {passcount}/{passcount+failcount} 通过 ===')

finally:
    if SFTP: SFTP.close()
    if SSH: SSH.close()
