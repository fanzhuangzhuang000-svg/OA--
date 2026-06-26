#!/usr/bin/env python3
"""触发 /inventory/ 和 /vehicles 的 500 错误并读取 laravel.log"""
import requests, json, sys

BASE = "http://127.0.0.1/api"
s = requests.Session()

# 1. 登录
r = s.post(f"{BASE}/auth/login", json={"username": "nbcy", "password": "admin123"})
token = r.json().get("data", {}).get("token", "")
if not token:
    print("❌ 登录失败"); sys.exit(1)
h = {"Authorization": f"Bearer {token}"}
print(f"✅ 登录成功，token 前20字: {token[:20]}...")

# 2. 触发 POST /inventory/
print("\n🚀 触发 POST /inventory/ ...")
payload = {
    "category_id": 1,
    "name": "测试物资",
    "unit": "个",
    "quantity": 10,
    "specs": "规格测试",
}
r2 = s.post(f"{BASE}/inventory/", json=payload, headers=h)
print(f"  HTTP {r2.status_code}")
print(f"  响应: {r2.text[:500]}")

# 3. 触发 POST /vehicles
print("\n🚀 触发 POST /vehicles ...")
payload2 = {
    "plate_no": "京A00001",
    "brand": "Toyota",
    "model": "Camry",
    "year": 2023,
    "color": "black",
    "vin": "VIN123",
    "engine_no": "ENG123",
    "purchase_date": "2023-01-01",
    "purchase_price": 250000,
    "status": "active",
    "mileage": 0,
}
r3 = s.post(f"{BASE}/vehicles", json=payload2, headers=h)
print(f"  HTTP {r3.status_code}")
print(f"  响应: {r3.text[:500]}")

print("\n✅ 触发完成，请查看 laravel.log")
