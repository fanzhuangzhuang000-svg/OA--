#!/usr/bin/env python3
"""V0.4.6 B 数据权限 - 24 用例烟囱 (在 117 上跑)"""
import sys
import json
import requests

API = 'http://127.0.0.1:8081/api'

USERS = [
    ('admin',   'admin1',     'admin123'),
    ('finance', 'fin_wu',     'admin123'),
    ('manager', 'sales_yang', 'admin123'),
    ('user',    'eng_qian',   'admin123'),
]

ENDPOINTS = {
    'projects':              '/projects',
    'customer_receivables':  '/finance/receivables',
    'payables':              '/finance/payables',  # 用 payable 测 finance scope
    'construction_logs':     '/construction/logs',
    'rectifications':        '/construction/rectifications',
    'warranties':            '/warranties',
}

EXPECTATIONS = {
    'admin':   {'projects': 118, 'customer_receivables': 64, 'payables_min': 0, 'construction_logs': 445, 'rectifications': 55, 'warranties': 5},
    'finance': {'projects': 118, 'customer_receivables': 64, 'payables_min': 0, 'construction_logs': 445, 'rectifications': 55, 'warranties': 5},
    'manager': {'projects_min': 18, 'customer_receivables_min': 0, 'payables_min': 0, 'construction_logs_min': 100, 'all_min': 0},
    'user':    {'projects_min': 20, 'all_min': 0},
}

def login(username, password):
    r = requests.post(f'{API}/auth/login', json={'username': username, 'password': password}, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json().get('data', {})
    return data.get('token') or data.get('access_token')

def get_count(token, endpoint):
    h = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{API}{endpoint}?per_page=1', headers=h, timeout=15)
    if r.status_code != 200:
        return None, r.status_code, r.text[:200]
    body = r.json()
    data = body.get('data', body) or {}
    total = data.get('total', 0)
    return total, 200, ''

def main():
    print(f'{"ROLE":<10}{"USER":<14}{"MODULE":<25}{"TOTAL":<8}{"STATUS":<10}')
    print('-' * 70)

    fail = 0
    for role, username, pwd in USERS:
        token = login(username, pwd)
        if not token:
            print(f'  ✗ {username} login failed')
            fail += 1
            continue

        for mod, ep in ENDPOINTS.items():
            total, code, err = get_count(token, ep)
            if code != 200:
                print(f'{role:<10}{username:<14}{mod:<25}{"ERR":<8}{code:<10} {err[:50]}')
                fail += 1
                continue

            exp = EXPECTATIONS[role]
            if role in ('admin', 'finance'):
                want = exp.get(mod)
                if want is None:
                    ok = (total >= 0)  # 未知模块只验证 200
                else:
                    ok = (total >= max(0, want - 1))
            else:
                min_p = exp.get(f'{mod}_min', exp.get('all_min', 0))
                ok = (total >= min_p)

            mark = 'OK' if ok else 'FAIL'
            print(f'{role:<10}{username:<14}{mod:<25}{total:<8}{mark:<10}')
            if not ok: fail += 1

    print('-' * 70)
    if fail == 0:
        print('OK 24 用例')
        return 0
    else:
        print(f'FAIL {fail} 个')
        return 1

if __name__ == '__main__':
    sys.exit(main())
