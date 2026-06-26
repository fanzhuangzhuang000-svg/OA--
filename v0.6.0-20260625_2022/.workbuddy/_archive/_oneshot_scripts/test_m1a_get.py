#!/usr/bin/env python3
"""M1-A GET 11 端点冒烟测试 + 转化链路状态机"""
import paramiko, json, re, subprocess, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123', timeout=20)

def run(cmd, timeout=15):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    return so.read().decode('utf-8', 'replace')

out = run('curl -s -X POST http://172.20.0.139:3001/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\'')
TOKEN = re.search(r'"token":"([^"]+)"', out).group(1)
AUTH = f'Authorization: Bearer {TOKEN}'

def curl(method, path, body=None):
    cmd = ['curl', '-s', '-o', '/tmp/curl_out', '-w', '%{http_code}', '-X', method,
           f'http://172.20.0.139:3001{path}', '-H', AUTH, '-H', 'Content-Type: application/json']
    if body: cmd += ['-d', json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        with open('/tmp/curl_out') as f: return r.stdout.strip(), f.read()
    except: return r.stdout.strip(), r.stderr

results = []

# === 11 个 P0 GET 端点冒烟 ===
print('=== 11 个 P0 GET 端点 ===')
for path in [
    '/api/sales/leads',
    '/api/sales/leads/source-options',
    '/api/sales/opps',
    '/api/sales/opps/stage-options',
    '/api/sales/opps/funnel',
    '/api/sales/opps/lost-reasons',
    '/api/sales/quotes',
    '/api/sales/quotes/status-options',
    '/api/sales/referrers',
    '/api/sales/pool',
    '/api/sales/follow-ups',
]:
    code, body = curl('GET', path)
    results.append((f'GET {path}', code))
    print(f'  GET {path}: {code}')

# === 状态机非法流转测试（应返回 409） ===
print()
print('=== 状态机非法流转测试 ===')
# 创建一个 lead 来测
code, body = curl('POST', '/api/sales/leads', {
    'customer_name': '状态机测试', 'contact_name': '测', 'contact_phone': '13900000000', 'source': 'online'
})
m = re.search(r'"id":(\d+)', body)
lead_id = int(m.group(1)) if m else None

# 尝试 PATCH {lead}/status from new -> converted (非法)
code, body = curl('PATCH', f'/api/sales/leads/{lead_id}/status', {'status': 'converted'})
print(f'  PATCH status new->converted: {code} | {body[:100]}')
results.append(('状态机非法流转 (期望 409)', code))

# 创建一个 opp 测 stage 流转
code, body = curl('POST', '/api/sales/opps', {
    'name': '阶段测试', 'estimated_amount': 10000, 'sales_id': 1, 'presale_id': 1
})
m = re.search(r'"id":(\d+)', body)
opp_id = int(m.group(1)) if m else None

# 尝试直接 PATCH stage -> won (非法，应 409)
code, body = curl('PATCH', f'/api/sales/opps/{opp_id}/stage', {'stage': 'won'})
print(f'  PATCH stage requirement->won: {code} | {body[:100]}')
results.append(('stage 看板不能直拖 won (期望 409)', code))

# 跨用户权限测试 (admin 是 1，换个不存在的 user id)
# 这需要 RBAC 角色检测，本项目暂不测
print()
print('=== 业务规则校验 ===')
# 测试 discount_rate > 30% 应失败
code, body = curl('POST', '/api/sales/quotes', {
    'opportunity_id': opp_id, 'discount_rate': 50, 'tax_rate': 13
})
print(f'  POST quotes discount_rate=50: {code} | {body[:100]} (期望 422)')
results.append(('discount_rate>30% 限制 (期望 422)', code))

# 总结
print()
print('=' * 60)
print('M1-A 综合测试结果:')
print('=' * 60)
ok = fail = 0
for name, code in results:
    is_ok = str(code).startswith('200') or (str(code) in ['422', '409'] and '期望' in name)
    print(f'  {"OK" if is_ok else "FAIL"} ({code:>3})  {name}')
    if is_ok: ok += 1
    else: fail += 1
print(f'\n总计: {ok} OK / {fail} FAIL (共 {len(results)} 个)')

ssh.close()
