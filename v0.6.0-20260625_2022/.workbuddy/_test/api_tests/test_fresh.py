#!/usr/bin/env python3
"""直接测 /api/auth/me 用 fresh token"""
import requests
r = requests.post('http://172.20.0.139/api/auth/login', json={'username': 'admin', 'password': 'admin123'}, timeout=10)
token = r.json()['data']['token']
print(f'fresh token: {token[:30]}')
# 立即测
r1 = requests.get('http://172.20.0.139/api/auth/me', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
print(f'/api/auth/me: {r1.status_code} body: {r1.text[:80]}')
r2 = requests.get('http://172.20.0.139/api/customers', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
print(f'/api/customers: {r2.status_code} body: {r2.text[:80]}')
# 测 /api/dashboard/stats
r3 = requests.get('http://172.20.0.139/api/dashboard/stats', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, timeout=5)
print(f'/api/dashboard/stats: {r3.status_code} body: {r3.text[:80]}')
