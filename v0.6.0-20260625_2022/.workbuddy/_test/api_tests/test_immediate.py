#!/usr/bin/env python3
"""立即测 endpoints[50:100]"""
import requests
import re
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

r = requests.post('http://172.20.0.139/api/auth/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
token = r.json()['data']['token']
print(f'fresh token: {token[:30]}')

# 立即测 endpoints[50:100]
codes = []
for m, u in endpoints[50:100]:
    if '{' in u:
        u2 = re.sub(r'\{[^}]+\}', '1', u)
    else:
        u2 = u
    r = requests.request(m, f'http://172.20.0.139{u2}', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
    codes.append((m, u2, r.status_code))
c = Counter(c[2] for c in codes)
print(f'\nendpoints[50:100] 立即测: {c}')
