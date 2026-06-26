#!/usr/bin/env python3
"""M1-A 端点 curl 验证"""
import paramiko, json, re, subprocess, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)

def run(cmd, timeout=15):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    return out

# Login
out = run('curl -s -X POST http://172.20.0.139:3001/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\'')
print('LOGIN:', out[:200])
m = re.search(r'"token":"([^"]+)"', out)
if not m:
    print('LOGIN FAILED')
    sys.exit(1)
TOKEN = m.group(1)
print(f'TOKEN len: {len(TOKEN)}')

AUTH = f'Authorization: Bearer {TOKEN}'

def curl(method, path, body=None, use_form=False, file_path=None):
    """Returns (http_code, response_body)"""
    cmd = ['curl', '-s', '-o', '/tmp/curl_out', '-w', '%{http_code}', '-X', method,
           f'http://172.20.0.139:3001{path}', '-H', AUTH]
    if use_form and file_path:
        cmd += ['-F', f'file=@{file_path}']
    else:
        cmd += ['-H', 'Content-Type: application/json']
        if body is not None:
            cmd += ['-d', json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    code = r.stdout.strip()
    try:
        with open('/tmp/curl_out', 'r', encoding='utf-8', errors='replace') as f:
            resp = f.read()
    except Exception:
        resp = r.stderr
    return code, resp[:500]

def run_remote(cmd):
    """Run a command on remote server, return output"""
    return run(cmd, timeout=15)

# Test data setup
run_remote('echo "test attachment content" > /tmp/test.txt')

# Also create a local test file for curl form upload
import tempfile, os
LOCAL_TEST_FILE = os.path.join(tempfile.gettempdir(), 'm1a_test.txt')
with open(LOCAL_TEST_FILE, 'w') as f:
    f.write('test attachment content')
print(f'Local test file: {LOCAL_TEST_FILE}')

results = []

# ========== 线索 5 ==========
print('\n=== 线索 5 端点 ===')

code, body = curl('POST', '/api/sales/leads', {
    'customer_name': '测试客户A', 'contact_name': '张三', 'contact_phone': '13800138000',
    'source': 'phone', 'requirement': '监控系统'
})
print(f'POST /sales/leads: HTTP {code}')
results.append(('POST /sales/leads', code))
m = re.search(r'"id":(\d+)', body)
lead_id = int(m.group(1)) if m else None
print(f'  lead_id={lead_id}, body={body[:200]}')

code, body = curl('PUT', f'/api/sales/leads/{lead_id}', {'requirement': '更新需求'})
print(f'PUT /sales/leads/{lead_id}: HTTP {code}')
results.append(('PUT /sales/leads/{lead}', code))

code, body = curl('PATCH', f'/api/sales/leads/{lead_id}/status', {'status': 'contacting'})
print(f'PATCH /sales/leads/{lead_id}/status: HTTP {code}')
results.append(('PATCH /sales/leads/{lead}/status', code))

code, body = curl('POST', f'/api/sales/leads/{lead_id}/convert-to-opp', {
    'name': '商机A', 'estimated_amount': 100000, 'sales_id': 1, 'presale_id': 1
})
print(f'POST /sales/leads/{lead_id}/convert-to-opp: HTTP {code}')
results.append(('POST /sales/leads/{lead}/convert-to-opp', code))
m = re.search(r'"id":(\d+)', body)
opp_id = int(m.group(1)) if m else None
print(f'  opp_id={opp_id}')

# DELETE 测试
code, body = curl('POST', '/api/sales/leads', {
    'customer_name': '待删线索', 'contact_name': '李四', 'contact_phone': '13700000000', 'source': 'online'
})
m = re.search(r'"id":(\d+)', body)
del_lead_id = int(m.group(1)) if m else None
if del_lead_id:
    code, body = curl('DELETE', f'/api/sales/leads/{del_lead_id}')
    print(f'DELETE /sales/leads/{del_lead_id}: HTTP {code}')
    results.append(('DELETE /sales/leads/{lead}', code))

# ========== 商机 6 ==========
print('\n=== 商机 6 端点 ===')

code, body = curl('POST', '/api/sales/opps', {
    'name': '测试商机B', 'estimated_amount': 50000, 'sales_id': 1, 'presale_id': 1
})
print(f'POST /sales/opps: HTTP {code}')
results.append(('POST /sales/opps', code))
m = re.search(r'"id":(\d+)', body)
opp2_id = int(m.group(1)) if m else None

code, body = curl('PUT', f'/api/sales/opps/{opp2_id}', {'estimated_amount': 80000})
print(f'PUT /sales/opps/{opp2_id}: HTTP {code}')
results.append(('PUT /sales/opps/{opp}', code))

code, body = curl('PATCH', f'/api/sales/opps/{opp2_id}/stage', {'stage': 'solution'})
print(f'PATCH /sales/opps/{opp2_id}/stage: HTTP {code}')
results.append(('PATCH /sales/opps/{opp}/stage', code))

code, body = curl('POST', f'/api/sales/opps/{opp2_id}/mark-lost', {'lost_reason': 'price_high'})
print(f'POST /sales/opps/{opp2_id}/mark-lost: HTTP {code}')
results.append(('POST /sales/opps/{opp}/mark-lost', code))

# 新建 mark-won 测试
code, body = curl('POST', '/api/sales/opps', {
    'name': '测试商机C-won', 'estimated_amount': 60000, 'sales_id': 1, 'presale_id': 1
})
m = re.search(r'"id":(\d+)', body)
opp3_id = int(m.group(1)) if m else None
code, body = curl('POST', f'/api/sales/opps/{opp3_id}/mark-won', {
    'contract_amount': 65000, 'signed_at': '2026-06-19'
})
print(f'POST /sales/opps/{opp3_id}/mark-won: HTTP {code}')
results.append(('POST /sales/opps/{opp}/mark-won', code))

# DELETE 测试 - 新建一个来删
code, body = curl('POST', '/api/sales/opps', {
    'name': '待删商机', 'estimated_amount': 10000, 'sales_id': 1, 'presale_id': 1
})
m = re.search(r'"id":(\d+)', body)
del_opp_id = int(m.group(1)) if m else None
if del_opp_id:
    code, body = curl('DELETE', f'/api/sales/opps/{del_opp_id}')
    print(f'DELETE /sales/opps/{del_opp_id}: HTTP {code}')
    results.append(('DELETE /sales/opps/{opp}', code))

# ========== 报价单 6 ==========
print('\n=== 报价单 6 端点 ===')

code, body = curl('POST', '/api/sales/quotes', {
    'opportunity_id': opp_id, 'discount_rate': 8, 'tax_rate': 13
})
print(f'POST /sales/quotes: HTTP {code}')
results.append(('POST /sales/quotes', code))
m = re.search(r'"id":(\d+)', body)
quote_id = int(m.group(1)) if m else None

code, body = curl('POST', f'/api/sales/quotes/{quote_id}/items', {
    'items': [
        {'name': '摄像头', 'quantity': 10, 'unit_price': 2000, 'unit': '台'},
        {'name': '线材', 'quantity': 5, 'unit_price': 1000, 'unit': '卷'}
    ]
})
print(f'POST /sales/quotes/{quote_id}/items: HTTP {code}')
results.append(('POST /sales/quotes/{quote}/items', code))

code, body = curl('PUT', f'/api/sales/quotes/{quote_id}', {'notes': '测试备注'})
print(f'PUT /sales/quotes/{quote_id}: HTTP {code}')
results.append(('PUT /sales/quotes/{quote}', code))

code, body = curl('PUT', f'/api/sales/quotes/{quote_id}/status', {'status': 'submitted'})
print(f'PUT /sales/quotes/{quote_id}/status: HTTP {code}')
results.append(('PUT /sales/quotes/{quote}/status', code))

code, body = curl('POST', f'/api/sales/quotes/{quote_id}/new-version')
print(f'POST /sales/quotes/{quote_id}/new-version: HTTP {code}')
results.append(('POST /sales/quotes/{quote}/new-version', code))

# DELETE 测试
code, body = curl('POST', '/api/sales/quotes', {
    'opportunity_id': opp_id, 'discount_rate': 0
})
m = re.search(r'"id":(\d+)', body)
qdel_id = int(m.group(1)) if m else None
if qdel_id:
    code, body = curl('DELETE', f'/api/sales/quotes/{qdel_id}')
    print(f'DELETE /sales/quotes/{qdel_id}: HTTP {code}')
    results.append(('DELETE /sales/quotes/{quote}', code))

# ========== 推荐人 3 ==========
print('\n=== 推荐人 3 端点 ===')

code, body = curl('POST', '/api/sales/referrers', {
    'name': '测试推荐人A', 'phone': '13900000000', 'commission_rate': 5
})
print(f'POST /sales/referrers: HTTP {code}')
results.append(('POST /sales/referrers', code))
m = re.search(r'"id":(\d+)', body)
ref_id = int(m.group(1)) if m else None

code, body = curl('PUT', f'/api/sales/referrers/{ref_id}', {'notes': '更新'})
print(f'PUT /sales/referrers/{ref_id}: HTTP {code}')
results.append(('PUT /sales/referrers/{referrer}', code))

code, body = curl('DELETE', f'/api/sales/referrers/{ref_id}')
print(f'DELETE /sales/referrers/{ref_id}: HTTP {code}')
results.append(('DELETE /sales/referrers/{referrer}', code))

# ========== 项目池 2 ==========
print('\n=== 项目池 2 端点 ===')

# 拿 mark-won 生成的 pool
out = run_remote(f'curl -s -X GET "http://172.20.0.139:3001/api/sales/pool" -H "{AUTH}" -H "Content-Type: application/json"')
m = re.search(r'"id":(\d+)', out)
pool_id = int(m.group(1)) if m else None
print(f'  pool_id={pool_id}')

if pool_id:
    code, body = curl('PUT', f'/api/sales/pool/{pool_id}', {'notes': '更新'})
    print(f'PUT /sales/pool/{pool_id}: HTTP {code}')
    results.append(('PUT /sales/pool/{pool}', code))

    code, body = curl('POST', f'/api/sales/pool/{pool_id}/convert-to-project', {
        'name': '施工项目A', 'manager_id': 1, 'start_date': '2026-06-20', 'budget': 65000
    })
    print(f'POST /sales/pool/{pool_id}/convert-to-project: HTTP {code}')
    results.append(('POST /sales/pool/{pool}/convert-to-project', code))
    print(f'  body: {body[:200]}')

# ========== 跟进 5 ==========
print('\n=== 跟进 5 端点 ===')

code, body = curl('POST', '/api/sales/follow-ups', {
    'target_type': 'opp', 'target_id': opp_id, 'content': '电话沟通了', 'result': '客户有兴趣'
})
print(f'POST /sales/follow-ups: HTTP {code}')
results.append(('POST /sales/follow-ups', code))
m = re.search(r'"id":(\d+)', body)
fu_id = int(m.group(1)) if m else None

if fu_id:
    code, body = curl('PUT', f'/api/sales/follow-ups/{fu_id}', {'result': '已发送资料'})
    print(f'PUT /sales/follow-ups/{fu_id}: HTTP {code}')
    results.append(('PUT /sales/follow-ups/{followUp}', code))

    # 附件上传
    code, body = curl('POST', f'/api/sales/follow-ups/{fu_id}/attachments', use_form=True, file_path=LOCAL_TEST_FILE)
    print(f'POST /sales/follow-ups/{fu_id}/attachments: HTTP {code}')
    results.append(('POST /sales/follow-ups/{followUp}/attachments', code))
    m = re.search(r'"id":(\d+)', body)
    att_id = int(m.group(1)) if m else None
    print(f'  body: {body[:200]}')

    if att_id:
        # 下载
        code, body = curl('GET', f'/api/sales/follow-ups/attachments/{att_id}/download')
        print(f'GET /sales/follow-ups/attachments/{att_id}/download: HTTP {code}')
        results.append(('GET /sales/follow-ups/attachments/{att}/download', code))

        # 删除附件
        code, body = curl('DELETE', f'/api/sales/follow-ups/attachments/{att_id}')
        print(f'DELETE /sales/follow-ups/attachments/{att_id}: HTTP {code}')
        results.append(('DELETE /sales/follow-ups/attachments/{att}', code))

    # 删除跟进
    code, body = curl('DELETE', f'/api/sales/follow-ups/{fu_id}')
    print(f'DELETE /sales/follow-ups/{fu_id}: HTTP {code}')
    results.append(('DELETE /sales/follow-ups/{followUp}', code))

# ========== 总结 ==========
print('\n' + '=' * 60)
print('M1-A 30 端点测试结果:')
print('=' * 60)
ok, fail = 0, 0
for name, code in results:
    is_ok = str(code) in ['200', '201', '204']
    print(f'  {"OK" if is_ok else "FAIL"} ({code:>3})  {name}')
    if is_ok: ok += 1
    else: fail += 1
print(f'\n总计: {ok} OK / {fail} FAIL (共 {len(results)} 个)')

ssh.close()
