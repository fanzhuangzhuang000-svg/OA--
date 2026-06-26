#!/usr/bin/env python3
"""
V0.5.4 新端点 e2e
- admin1 login
- /api/field-masks 列表 (V0.5.2)
- /api/field-masks/endpoints 端点元数据 (V0.5.4)
- /api/field-masks CRUD
- /api/field-masks/flush-cache
- /api/audit/role-changes + summary (V0.5.4)
- /api/roles/expiring 7 天窗口
"""
import requests, json
from datetime import datetime, timedelta

API = 'http://192.168.3.117/api'

def login(u, p='admin123'):
    r = requests.post(f'{API}/auth/login', json={'username': u, 'password': p}, timeout=10)
    j = r.json()
    if j.get('code') != 0:
        return None
    return j['data']['token']

def get(t, path):
    return requests.get(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10)

def post(t, path, data):
    return requests.post(f'{API}{path}', json=data, headers={'Authorization': f'Bearer {t}', 'Content-Type': 'application/json'}, timeout=10)

def put(t, path, data):
    return requests.put(f'{API}{path}', json=data, headers={'Authorization': f'Bearer {t}', 'Content-Type': 'application/json'}, timeout=10)

def delete(t, path):
    return requests.delete(f'{API}{path}', headers={'Authorization': f'Bearer {t}'}, timeout=10)

def main():
    print('='*60)
    print('  V0.5.4 授权系统 UI 收口 e2e')
    print('='*60)
    fails = 0
    t = login('admin1')
    assert t, 'admin1 login failed'
    print(f'  ✓ admin1 token len={len(t)}')

    # 1) field-masks 列表
    print('\n[1] GET /api/field-masks')
    r = get(t, '/field-masks')
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ status={r.status_code} body={r.text[:200]}')
        fails += 1
    else:
        groups = r.json()['data']
        total = sum(len(g['items']) for g in groups)
        print(f'  ✓ {len(groups)} 端点 / {total} 规则')

    # 2) endpoints 端点
    print('\n[2] GET /api/field-masks/endpoints (V0.5.4 新)')
    r = get(t, '/field-masks/endpoints')
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ status={r.status_code} body={r.text[:200]}')
        fails += 1
    else:
        eps = r.json()['data']
        print(f'  ✓ {len(eps)} 端点元数据')

    # 3) CRUD — 新建
    print('\n[3] POST /api/field-masks')
    r = post(t, '/field-masks', {
        'endpoint': '/api/_test_v054',
        'field': 'test_field',
        'allowed_roles': 'admin',
        'description': 'e2e test',
        'enabled': True,
    })
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ create failed: {r.text[:200]}')
        fails += 1
        new_id = None
    else:
        new_id = r.json()['data']['id']
        print(f'  ✓ created id={new_id}')

    # 4) update
    if new_id:
        print(f'\n[4] PUT /api/field-masks/{new_id}')
        r = put(t, f'/field-masks/{new_id}', {
            'allowed_roles': 'admin,finance',
            'description': 'e2e updated',
        })
        if r.status_code != 200 or r.json().get('code') != 0:
            print(f'  ✗ update failed: {r.text[:200]}')
            fails += 1
        else:
            print('  ✓ updated')

    # 5) delete
    if new_id:
        print(f'\n[5] DELETE /api/field-masks/{new_id}')
        r = delete(t, f'/field-masks/{new_id}')
        if r.status_code != 200 or r.json().get('code') != 0:
            print(f'  ✗ delete failed: {r.text[:200]}')
            fails += 1
        else:
            print('  ✓ deleted')

    # 6) flush-cache
    print('\n[6] POST /api/field-masks/flush-cache')
    r = post(t, '/field-masks/flush-cache', {})
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ flush failed: {r.text[:200]}')
        fails += 1
    else:
        print('  ✓ flushed')

    # 7) audit role-changes (V0.5.4 新)
    print('\n[7] GET /api/audit/role-changes (V0.5.4 新)')
    r = get(t, '/audit/role-changes?days=7')
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ status={r.status_code} body={r.text[:200]}')
        fails += 1
    else:
        rows = r.json()['data']
        print(f'  ✓ {len(rows)} 条权限变更流水')

    # 8) audit role-changes summary
    print('\n[8] GET /api/audit/role-changes/summary')
    r = get(t, '/audit/role-changes/summary?days=7')
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ status={r.status_code} body={r.text[:200]}')
        fails += 1
    else:
        d = r.json()['data']
        print(f'  ✓ by_action={d["by_action"]} total={d["total"]}')

    # 9) 临时角色 + audit 应该能看到刚改的
    print('\n[9] 触发一次 role_changed 看 audit 实时记录')
    # 先给 eng_qian (id=82) 改一个角色
    # 找到 user 列表
    r = get(t, '/users?keyword=eng_qian&per_page=5')
    users = r.json()['data']['data']
    if users:
        eng_qian = users[0]
        r = put(t, f'/users/{eng_qian["id"]}/roles', {'roles': ['user', 'manager']})
        if r.status_code == 200 and r.json().get('code') == 0:
            print(f'  ✓ updated roles for {eng_qian["username"]}')
            # 再查 audit
            r = get(t, '/audit/role-changes?days=1&action=role_changed')
            rows = r.json()['data']
            found = any('eng_qian' in (x.get('description') or '') for x in rows)
            if found:
                print(f'  ✓ audit log contains eng_qian role change ({len(rows)} rows)')
            else:
                print(f'  ✗ audit log miss eng_qian ({len(rows)} rows)')
                fails += 1
            # 还原角色
            r = put(t, f'/users/{eng_qian["id"]}/roles', {'roles': ['user']})
        else:
            print(f'  ⚠ role update failed: {r.text[:200]}')
            fails += 1

    # 10) non-admin 访问 audit 应 403
    print('\n[10] eng_qian (user) 访问 audit 应 403')
    t2 = login('eng_qian')
    if t2:
        r = get(t2, '/audit/role-changes')
        if r.status_code == 403:
            print('  ✓ 403 forbidden')
        else:
            print(f'  ✗ 应 403, 实际 {r.status_code}')
            fails += 1
    else:
        print('  ⚠ eng_qian login failed')

    # 11) roles/expiring
    print('\n[11] GET /api/roles/expiring?within_days=7')
    r = get(t, '/roles/expiring?within_days=7')
    if r.status_code != 200 or r.json().get('code') != 0:
        print(f'  ✗ status={r.status_code} body={r.text[:200]}')
        fails += 1
    else:
        d = r.json()['data']
        print(f'  ✓ count={d["count"]}')

    print('\n' + '='*60)
    if fails == 0:
        print('  ✓ V0.5.4 e2e ALL PASS')
    else:
        print(f'  ✗ {fails} 失败')
        import sys; sys.exit(1)

if __name__ == '__main__':
    main()
