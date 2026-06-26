#!/usr/bin/env python3
"""
V0.5.3 临时角色 e2e 测试
- admin1 登录
- 给 fin_wu 授一个 7 天后的临时 manager
- 查 fin_wu 的 active roles — 应包含 manager
- 撤销
- 查 fin_wu 的 active roles — 不应包含 manager
- 授一个过期时间在过去的 — 应 422
- 查 expiring 端点
"""
import requests, time, json
from datetime import datetime, timedelta

API = 'http://192.168.3.117/api'

def login(username, pwd='admin123'):
    r = requests.post(f'{API}/auth/login', json={'username': username, 'password': pwd}, timeout=10)
    j = r.json()
    assert j.get('code') == 0, f'login {username} 失败: {j}'
    return j['data']['token']

def get(t, path):
    r = requests.get(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10)
    return r.status_code, r.json()

def post(t, path, data):
    r = requests.post(f'{API}{path}', json=data, headers={'Authorization': f'Bearer {t}', 'Content-Type': 'application/json'}, timeout=10)
    return r.status_code, r.json()

def delete(t, path):
    r = requests.delete(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10)
    return r.status_code, r.json()

def main():
    print('='*60)
    print('  V0.5.3 临时角色 e2e')
    print('='*60)
    fails = 0

    # 0) login
    print('\n[0] admin1 login')
    t = login('admin1')
    print(f'  ✓ token len={len(t)}')

    # 1) 找一个纯 user 角色用户 (id 固定: eng_qian=82)
    print('\n[1] 找 eng_qian (纯 user)')
    code, j = get(t, '/users?keyword=eng_qian&per_page=5')
    assert code == 200 and j.get('code') == 0, f'找 eng_qian 失败: {j}'
    users = j['data']['data']
    assert len(users) > 0, 'eng_qian 不存在'
    target = users[0]
    user_id = target['id']
    print(f'  ✓ target id={user_id}, username={target["username"]}')

    # 2) 清理一下
    print('\n[2] 清理之前可能残留的临时角色')
    code, j = get(t, f'/users/{user_id}/roles')
    assignments = j.get('data', {}).get('assignments', [])
    for a in assignments:
        if a.get('status') == 'temporary':
            delete(t, f"/users/{user_id}/roles/{a['name']}")
            print(f"  - 删 {a['name']}")

    # 3) 授一个 7 天后的临时 manager
    print('\n[3] 授临时 manager (7 天后过期)')
    expires = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    code, j = post(t, f'/users/{user_id}/roles/temporary', {
        'assignments': [{'role': 'manager', 'expires_at': expires, 'reason': 'e2e test 7d'}]
    })
    assert code == 200 and j.get('code') == 0, f'授临时角色失败: {j}'
    added = j['data']['added']
    assert added >= 1, f'应至少 added 1, 实际 {added}'
    print(f'  ✓ added={added}')

    # 4) 查 active roles — 应包含 manager
    print('\n[4] 查 fin_wu active roles')
    code, j = get(t, f'/users/{user_id}/roles/active')
    assert code == 200 and j.get('code') == 0, f'查 active 失败: {j}'
    role_names = [r['name'] for r in j['data']['roles']]
    print(f'  roles = {role_names}')
    if 'manager' not in role_names:
        print('  ✗ manager 不在 active roles 中')
        fails += 1
    else:
        print('  ✓ manager 在 active roles 中')

    # 5) 撤销
    print('\n[5] 撤销 manager')
    code, j = delete(t, f'/users/{user_id}/roles/manager')
    assert code == 200 and j.get('code') == 0, f'撤销失败: {j}'
    print(f'  ✓ 已撤销')

    # 6) 再查 active — 不应包含 manager
    print('\n[6] 再查 active roles')
    code, j = get(t, f'/users/{user_id}/roles/active')
    role_names = [r['name'] for r in j['data']['roles']]
    print(f'  roles = {role_names}')
    if 'manager' in role_names:
        print('  ✗ 撤销后 manager 仍在 active 中')
        fails += 1
    else:
        print('  ✓ 撤销后 manager 不在 active 中')

    # 7) 过去时间应被 422
    print('\n[7] 过去时间应 422')
    code, j = post(t, f'/users/{user_id}/roles/temporary', {
        'assignments': [{'role': 'manager', 'expires_at': '2020-01-01 00:00:00', 'reason': '过去时间'}]
    })
    if code != 422:
        print(f'  ✗ 应 422, 实际 {code}')
        fails += 1
    else:
        print(f'  ✓ 422 拒绝: {j.get("message", "")[:50]}')

    # 8) expiring 端点
    print('\n[8] expiring 端点')
    code, j = get(t, '/roles/expiring?within_days=7')
    assert code == 200 and j.get('code') == 0
    print(f'  ✓ count={j["data"]["count"]}')

    # 9) 非 admin 应 403
    print('\n[9] eng_qian (manager) 尝试授临时角色应 403')
    t2 = login('eng_qian')
    code, j = post(t2, f'/users/{user_id}/roles/temporary', {
        'assignments': [{'role': 'admin', 'expires_at': expires}]
    })
    if code != 403:
        print(f'  ✗ 应 403, 实际 {code}')
        fails += 1
    else:
        print('  ✓ 403 forbidden')

    # 10) myPermissions 端点
    print('\n[10] /users/{id}/roles/active 给当前用户自己')
    code, j = get(t, f'/users/{user_id}/roles/active')
    assert code == 200
    assert 'permissions' in j['data']
    assert isinstance(j['data']['permissions'], list)
    print(f'  ✓ permissions count = {len(j["data"]["permissions"])}')

    print('\n' + '='*60)
    if fails == 0:
        print('  ✓ V0.5.3 e2e ALL PASS (10/10)')
    else:
        print(f'  ✗ {fails} 失败')
        import sys; sys.exit(1)

if __name__ == '__main__':
    main()
