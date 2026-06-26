#!/usr/bin/env python3
"""触发 500 错误并读取 Laravel log"""
import requests, json, subprocess, time

BASE = "http://127.0.0.1/api"

# 1. 登录拿 token
print("=== 1. 登录 ===")
r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
d = r.json()
TOKEN = d["data"]["token"]
print(f"Token: {TOKEN[:30]}...")

headers = {"Authorization": f"Bearer {TOKEN}"}

# 2. 触发 PUT /projects/214/stage (500)
print("\n=== 2. 触发 PUT /projects/214/stage ===")
r = requests.put(f"{BASE}/projects/214/stage",
                     headers=headers,
                     json={"stage": "in_progress"})
print(f"HTTP {r.status_code}")
print(f"Response: {r.text[:300]}")

# 3. 读 laravel.log（用 subprocess 在 172 上直接读）
print("\n=== 3. 读 laravel.log（最近 50 行）===')
# 注意：这个脚本是在 172 上跑的，所以可以直接读文件
try:
    with open("/var/www/oa-api/storage/logs/laravel.log", "r") as f:
        lines = f.readlines()
        print("".join(lines[-50:]))
except Exception as e:
    print(f"读 log 失败: {e}")

# 4. 触发 POST /inventory/ (500)
print("\n=== 4. 触发 POST /inventory/ ===")
r = requests.post(f"{BASE}/inventory/",
                      headers=headers,
                      json={
                          "code": f"TEST{datetime.now():%Y%m%d%H%M%S}",
                          "name": "测试物资",
                          "category_id": 1,
                          "unit": "个",
                      })
print(f"HTTP {r.status_code}")
print(f"Response: {r.text[:300]}")

# 5. 再读 log
print("\n=== 5. 读 laravel.log（最近 50 行）===')
try:
    with open("/var/www/oa-api/storage/logs/laravel.log", "r") as f:
        lines = f.readlines()
        print("".join(lines[-50:]))
except Exception as e:
    print(f"读 log 失败: {e}")
