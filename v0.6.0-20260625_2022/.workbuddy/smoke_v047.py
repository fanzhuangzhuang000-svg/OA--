#!/usr/bin/env python3
"""V0.4.7 安全收口 - 5 用例烟囱
  1. admin GET /warranties/{任意 id} → 200
  2. 普通员工 GET /warranties/{非自己 id} → 403
  3. 普通员工 GET /dashboard/stats → 200 + isFull=false
  4. admin GET /dashboard/stats → 200 + isFull=true
  5. 普通员工 GET /warranties/{不存在 id} → 403
"""
import sys
import requests

API = 'http://127.0.0.1:8081/api'

USERS = {
    'admin':  ('admin1',     'admin123'),
    'finance':('fin_wu',     'admin123'),
    'user':   ('eng_qian',   'admin123'),
}

def login(u, p):
    r = requests.post(f'{API}/auth/login', json={'username': u, 'password': p}, timeout=15)
    return r.json().get('data', {}).get('token') if r.status_code == 200 else None

def get(token, url):
    h = {'Authorization': f'Bearer {token}'}
    return requests.get(f'{API}{url}', headers=h, timeout=15)

def assert_status(r, want, name):
    actual = r.status_code
    ok = actual == want
    print(f'  {"✓" if ok else "✗"} {name}: {actual} (want {want})')
    return ok

def main():
    fail = 0

    # 1. admin /warranties/{id} → 200 (找自己创建的, id=2 是 admin 创建的)
    admin_token = login(*USERS['admin'])
    if not admin_token:
        print('admin login FAIL'); return 1
    r = get(admin_token, '/warranties/2')
    if not assert_status(r, 200, 'admin GET /warranties/2'): fail += 1

    # 2. 普通员工 /warranties/{非自己 id} → 403
    user_token = login(*USERS['user'])
    if not user_token:
        print('user login FAIL'); return 1
    r = get(user_token, '/warranties/3')  # warranty id=3 应该是 admin 创建的
    if not assert_status(r, 403, 'user GET /warranties/3'): fail += 1

    # 3. 普通员工 /dashboard/stats → 200 + isFull=false
    r = get(user_token, '/dashboard/stats')
    if not assert_status(r, 200, 'user GET /dashboard/stats'): fail += 1
    else:
        d = r.json().get('data', {})
        ok = d.get('isFull') is False
        if not ok: fail += 1
        print(f'  {"✓" if ok else "✗"} user stats.isFull = {d.get("isFull")} (want False)')

    # 4. admin /dashboard/stats → 200 + isFull=true
    r = get(admin_token, '/dashboard/stats')
    if not assert_status(r, 200, 'admin GET /dashboard/stats'): fail += 1
    else:
        d = r.json().get('data', {})
        ok = d.get('isFull') is True
        if not ok: fail += 1
        print(f'  {"✓" if ok else "✗"} admin stats.isFull = {d.get("isFull")} (want True)')

    # 5. 普通员工 /warranties/{不存在 id=99999} → 403 (不泄漏存在性)
    r = get(user_token, '/warranties/99999')
    if not assert_status(r, 403, 'user GET /warranties/99999 (不存在)'): fail += 1
    else:
        msg = r.json().get('message', '')
        ok = '不存在或您没有访问权限' in msg
        if not ok: fail += 1
        print(f'  {"✓" if ok else "✗"} 友好提示: {msg}')

    print('-' * 50)
    print(f'{"✅ 全过" if fail == 0 else f"❌ {fail} 失败"}')
    return 0 if fail == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
