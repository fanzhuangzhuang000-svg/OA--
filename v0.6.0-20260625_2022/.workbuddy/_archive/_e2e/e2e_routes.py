#!/usr/bin/env python3
"""v0.3.7.5 实际 HTTP 路由验证"""
import paramiko, time

HOST='172.20.0.139'; USER='nbcy'; PWD='admin123'
BASE='http://172.20.0.139:3000'

PATHS = [
    # 父路径（应该走 alias → redirect 到子页面）
    '/attendance', '/attendance/overview', '/attendance/record', '/attendance/leave', '/attendance/overtime', '/attendance/report',
    '/employee', '/employee/list', '/employee/org', '/employee/skill',
    '/customer', '/customer/list', '/customer/map', '/customer/1',
    '/project', '/project/list', '/project/create', '/project/123',
    '/project/123/gantt',
    '/service', '/service/orders', '/service/create', '/service/45', '/service/contract', '/service/stats',
    '/expense', '/expense/list', '/expense/apply', '/expense/approval',
    '/vehicle', '/vehicle/fleet', '/vehicle/apply', '/vehicle/dispatch',
    '/inventory', '/inventory/stock', '/inventory/inout', '/inventory/inbound-order',
    '/inventory/outbound-order', '/inventory/material-request', '/inventory/material-return',
    '/finance', '/finance/overview', '/finance/receipt', '/finance/payment',
    '/finance/receivable', '/finance/payable',
    '/disk', '/knowledge', '/knowledge/list', '/screen', '/message', '/message/list',
    '/settings', '/settings/profile', '/settings/password', '/settings/organization',
    '/settings/role', '/settings/approval', '/settings/log', '/settings/backup',
    # 真实存在的 404
    '/totally-invalid-route-xyz',
]

SSH = paramiko.SSHClient()
SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
SSH.connect(HOST, port=22, username=USER, password=PWD, timeout=10)

ok = 0
err = 0
results = []
for p in PATHS:
    cmd = f"curl -sS -o /dev/null -w '%{{http_code}}' {BASE}{p}"
    si, so, se = SSH.exec_command(cmd, timeout=15)
    code = so.read().decode('utf-8','replace').strip()
    is_expected_404 = 'totally-invalid' in p
    is_404 = code == '404'
    if is_expected_404:
        # 期望是 404
        if is_404:
            ok += 1
            results.append(f'  ✅ {p:50s}  {code} (期望 404)')
        else:
            err += 1
            results.append(f'  ❌ {p:50s}  {code} (期望 404)')
    else:
        # 期望是 200
        if code == '200':
            ok += 1
            results.append(f'  ✅ {p:50s}  {code}')
        else:
            err += 1
            results.append(f'  ❌ {p:50s}  {code} (期望 200)')

print(f'=== 路由 HTTP 验证 (共 {len(PATHS)} 条) ===')
for r in results:
    print(r)
print()
print(f'=== 通过: {ok} / {ok+err} ===')

SSH.close()
