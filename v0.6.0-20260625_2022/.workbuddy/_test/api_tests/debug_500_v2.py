#!/usr/bin/env python3
"""临时开启 APP_DEBUG=true 并触发 500 错误，读取详细错误信息"""
import subprocess, requests, time, os

BASE = "http://127.0.0.1/api"
ENV = "/var/www/oa-api/.env"

def run(cmd, timeout=15):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.stderr.strip()

print("=== 1. 备份 .env ===")
run(f"cp {ENV} {ENV}.bak")

print("\n=== 2. 开启 APP_DEBUG=true ===")
out, err = run(f"sed -i 's/APP_DEBUG=.*/APP_DEBUG=true/' {ENV}")
print("  sed:", out or "(done)")
# 验证
out, _ = run(f"grep APP_DEBUG {ENV}")
print("  当前:", out)

print("\n=== 3. 登录拿 token ===")
r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "admin123"})
token = r.json()["data"]["token"]
print("  Token:", token[:30], "...")

headers = {"Authorization": f"Bearer {token}"}

print("\n=== 4. 触发 PUT /projects/214/stage (500) ===")
r = requests.put(f"{BASE}/projects/214/stage",
                     headers=headers,
                     json={"stage": "in_progress"})
print(f"  HTTP {r.status_code}")
print(f"  响应 (前 1000 字符):")
print(r.text[:1000])

print("\n=== 5. 触发 POST /inventory/ (500) ===")
r = requests.post(f"{BASE}/inventory/",
                     headers=headers,
                     json={"code": "TEST123", "name": "测试", "unit": "个"})
print(f"  HTTP {r.status_code}")
print(r.text[:500])

print("\n=== 6. 触发 POST /vehicles (500) ===")
r = requests.post(f"{BASE}/vehicles",
                     headers=headers,
                     json={"plate_no": "ERROR_TEST", "status": "active"})
print(f"  HTTP {r.status_code}")
print(r.text[:500])

print("\n=== 7. 恢复 APP_DEBUG=false ===")
run(f"sed -i 's/APP_DEBUG=.*/APP_DEBUG=false/' {ENV}")
out, _ = run(f"grep APP_DEBUG {ENV}")
print("  当前:", out)

print("\n=== 8. 清理：恢复 .env.bak ===")
run(f"mv {ENV}.bak {ENV}")
print("  done")
