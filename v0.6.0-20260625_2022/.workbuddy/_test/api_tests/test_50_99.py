#!/usr/bin/env python3
"""
诊断 endpoints[50:100] 26 401 的真实原因
"""
import requests
import re
import time
from collections import Counter

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

# 单独测 50-99 端点每个（间隔 1s 避免 throttle）
print('test 50 endpoints with 1s interval (no sleep first)...')
results = {}
for i, (m, u) in enumerate(endpoints[50:100]):
    if '{' in u:
        u2 = re.sub(r'\{[^}]+\}', '1', u)
    else:
        u2 = u
    r = requests.request(m, f'http://172.20.0.139{u2}', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
    results[(m, u2)] = r.status_code
    time.sleep(1.0)
c = Counter(results.values())
print(f'50 端点 (1s 间隔): {c}')

# 列 401
r401 = [(k[0], k[1], v) for k, v in results.items() if v == 401]
print(f'\n401 端点:')
for m, u, _ in r401:
    print(f'  {m:7s} {u}')
