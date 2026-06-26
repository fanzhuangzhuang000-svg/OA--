#!/usr/bin/env python
"""完整测试152服务器所有API（使用正确端口80）"""
import requests
import json

BASE = "http://152.136.115.121"
# BASE = "http://172.20.0.139"  # 测试172

print("="*60)
print(f"测试目标: {BASE}")
print("="*60)

# 1. 登录
print("\n[1] 登录...")
r = requests.post(f"{BASE}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
}, timeout=10)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    token = data.get('data', {}).get('token') or data.get('token')
    print(f"  Token: {token[:30]}..." if token else "  NO TOKEN")
else:
    print(f"  Response: {r.text[:200]}")
    token = None

if not token:
    print("[FAIL] 登录失败，无法继续测试")
    exit(1)

headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

# 2. 测试所有关键API
apis = [
    ('Health', 'GET', '/api/health'),
    ('Finance Accounts', 'GET', '/api/finance/accounts'),
    ('Finance Receivables', 'GET', '/api/finance/receivables'),
    ('Finance Summary', 'GET', '/api/finance/summary'),
    ('Finance Payments', 'GET', '/api/finance/payments'),
    ('Departments', 'GET', '/api/employee/departments'),
    ('Positions', 'GET', '/api/employee/positions'),
    ('Employees', 'GET', '/api/employee/employees'),
    ('Customers', 'GET', '/api/customer/customers'),
    ('Projects', 'GET', '/api/project/projects'),
    ('Vehicles', 'GET', '/api/vehicle/vehicles'),
    ('Inventory', 'GET', '/api/inventory/items'),
    ('Finance Approvals', 'GET', '/api/approvals/finance'),
    ('Operation Approvals', 'GET', '/api/approvals/operation'),
    ('Project Approvals', 'GET', '/api/approvals/project'),
]

print("\n[2] 测试所有关键API:")
print(f"  {'API':<30} {'Status':<10} {'OK?':<5}")
print("  " + "-"*50)

for name, method, path in apis:
    try:
        r = requests.request(method, f"{BASE}{path}", headers=headers, timeout=10)
        ok = "✅" if r.status_code == 200 else f"❌ {r.status_code}"
        print(f"  {name:<30} {r.status_code:<10} {ok}")
        if r.status_code not in [200, 201]:
            print(f"    → {r.text[:150]}")
    except Exception as e:
        print(f"  {name:<30} {'ERROR':<10} ❌ {str(e)[:50]}")

print("\n[DONE]")
