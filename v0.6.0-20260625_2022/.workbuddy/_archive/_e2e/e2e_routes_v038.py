#!/usr/bin/env python3
"""v0.3.8 全量路由 E2E 验证 - 覆盖 router 表里所有 path + alias + 动态 ID 父路径
不依赖 paramiko，用本地 Windows + curl 跑服务器（前提：服务器网可达）
"""
import subprocess
import sys
import time

HOST = '172.20.0.139'
BASE = f'http://{HOST}:3000'

# 完整路由清单（路由表 + alias + 动态 ID）
PATHS = [
    # 登录 + 首页
    '/login',
    '/',
    '/dashboard',
    # 考勤（5 个子页 + 父路径 + alias）
    '/attendance', '/attendance/overview', '/attendance/record',
    '/attendance/leave', '/attendance/overtime', '/attendance/report',
    # 员工
    '/employee', '/employee/list', '/employee/org', '/employee/skill',
    # 客户
    '/customer', '/customer/list', '/customer/map', '/customer/1',
    # 项目
    '/project', '/project/list', '/project/create', '/project/123', '/project/123/gantt',
    # 售后
    '/service', '/service/orders', '/service/create', '/service/45',
    '/service/contract', '/service/stats',
    # 报销
    '/expense', '/expense/list', '/expense/apply', '/expense/approval',
    # 车辆
    '/vehicle', '/vehicle/fleet', '/vehicle/apply', '/vehicle/dispatch',
    # 库存（6 个子页 + 父）
    '/inventory', '/inventory/stock', '/inventory/inout',
    '/inventory/inbound-order', '/inventory/outbound-order',
    '/inventory/material-request', '/inventory/material-return',
    # 财务
    '/finance', '/finance/overview', '/finance/receipt', '/finance/payment',
    '/finance/receivable', '/finance/payable',
    # P1/P2
    '/disk', '/knowledge', '/knowledge/list', '/screen',
    # 消息
    '/message', '/message/list',
    # 系统设置（7 个子页 + 父）
    '/settings', '/settings/profile', '/settings/password', '/settings/organization',
    '/settings/role', '/settings/approval', '/settings/log', '/settings/backup',
    # 404 期望
    '/totally-invalid-route-xyz',
]

def curl_code(url, timeout=10):
    """返回 HTTP 状态码"""
    try:
        r = subprocess.run(
            ['curl', '-sS', '-o', 'NUL', '-w', '%{http_code}', url],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except Exception as e:
        return f'ERR:{e}'

print(f'=== 路由 HTTP E2E 验证 (共 {len(PATHS)} 条) ===')
print(f'目标: {BASE}')
print()

ok, err, exp404_ok, exp404_fail = 0, 0, 0, 0
results = []
for p in PATHS:
    code = curl_code(BASE + p)
    is_expected_404 = 'totally-invalid' in p
    is_404 = code == '404'
    if is_expected_404:
        if is_404:
            exp404_ok += 1
            results.append(f'  ✅ {p:48s}  {code} (期望 404)')
        else:
            exp404_fail += 1
            err += 1
            results.append(f'  ❌ {p:48s}  {code} (期望 404)')
    else:
        if code == '200':
            ok += 1
            results.append(f'  ✅ {p:48s}  {code}')
        else:
            err += 1
            results.append(f'  ❌ {p:48s}  {code} (期望 200)')

for r in results:
    print(r)

print()
print(f'=== 业务路由通过: {ok}  失败: {err}  期望 404 通过: {exp404_ok}  期望 404 失败: {exp404_fail}  ===')
print(f'=== 总计: 通过 {ok+exp404_ok} / 失败 {err+exp404_fail}  ===')
sys.exit(0 if err + exp404_fail == 0 else 1)
