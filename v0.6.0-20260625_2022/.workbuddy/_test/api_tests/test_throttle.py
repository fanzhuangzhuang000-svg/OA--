#!/usr/bin/env python3
"""
测试 throttle 触发机制，找出 26 401 真实原因
"""
import requests
import re
import time
from collections import Counter

# 读 routes
with open(r'D:/work/website/OA/.workbuddy/_test/api_tests/routes_raw.txt', encoding='utf-8') as f:
    raw = f.read()
endpoints = []
for line in raw.splitlines():
    m = re.match(r'^\s*(\S+)\s+(/\S+|\S+)\s', line)
    if m and m.group(2).startswith('api/'):
        methods = m.group(1).split('|')
        for method in methods:
            endpoints.append((method.strip(), '/' + m.group(2)))

# login
r = requests.post('http://172.20.0.139/api/auth/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
token = r.json()['data']['token']
print(f'fresh token: {token[:30]}')

# sleep 65s 让 throttle 计数清零
print('sleep 65s...')
time.sleep(65)

# 跑 50 端点
codes = []
for m, u in endpoints[50:100]:
    if '{' in u:
        u2 = re.sub(r'\{[^}]+\}', '1', u)
    else:
        u2 = u
    r = requests.request(m, f'http://172.20.0.139{u2}', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
    codes.append((m, u2, r.status_code))
    # 记每个 401 的 body
    if r.status_code == 401:
        codes[-1] = codes[-1] + (r.text[:80],)

# 统计
c = Counter(c[2] for c in codes)
print(f'50-99 端点 (sleep 65s 后): {c}')

# 401 详情
r401 = [c for c in codes if c[2] == 401]
print(f'\n401 端点 ({len(r401)} 个):')
for m, u, s, body in r401[:10]:
    print(f'  {m:7s} {u}: {body[:60]}')
