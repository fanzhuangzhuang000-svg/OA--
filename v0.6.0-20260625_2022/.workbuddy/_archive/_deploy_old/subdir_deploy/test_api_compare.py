#!/usr/bin/env python
"""对比172和152服务器"""
import requests

def test_server(name, base):
    print(f"\n{'='*60}")
    print(f"测试: {name} ({base})")
    print('='*60)

    try:
        r = requests.post(f"{base}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        }, timeout=5)
        if r.status_code != 200:
            print(f"[FAIL] 登录失败: {r.status_code}")
            return
        token = r.json().get('data', {}).get('token') or r.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[OK] 登录成功")
    except Exception as e:
        print(f"[FAIL] 无法连接: {e}")
        return

    # 测试各种路径格式
    paths = [
        # 员工
        ('Departments /api/departments', '/api/departments'),
        ('Departments /api/employee/departments', '/api/employee/departments'),
        ('Departments /api/org/departments', '/api/org/departments'),
        ('Employees /api/employees', '/api/employees'),
        ('Employees /api/employee/employees', '/api/employee/employees'),
        # 客户
        ('Customers /api/customers', '/api/customers'),
        ('Customers /api/customer/customers', '/api/customer/customers'),
        # 项目
        ('Projects /api/projects', '/api/projects'),
        ('Projects /api/project/projects', '/api/project/projects'),
        # 车辆
        ('Vehicles /api/vehicles', '/api/vehicles'),
        ('Vehicles /api/vehicle/vehicles', '/api/vehicle/vehicles'),
        # 库存
        ('Inventory /api/inventory/items', '/api/inventory/items'),
        ('Inventory /api/inventory', '/api/inventory'),
    ]

    for name, path in paths:
        try:
            r = requests.get(f"{base}{path}", headers=headers, timeout=5)
            print(f"  {name:<55} → {r.status_code}")
        except Exception as e:
            print(f"  {name:<55} → ERR: {str(e)[:30]}")

test_server("172服务器", "http://172.20.0.139")
test_server("152服务器", "http://152.136.115.121")
