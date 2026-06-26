import requests
import json

# 1. 登录
print("=== 1. 登录 ===")
r = requests.post('http://127.0.0.1/api/auth/login',
    json={'username':'admin','password':'admin123'})
print('HTTP', r.status_code)
d = r.json()
print(json.dumps(d, ensure_ascii=False)[:300])
token = d.get('data', {}).get('token', '')
print("Token:", token[:40], "...")

if token:
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试 /api/vehicles
    print("\n=== 2. GET /api/vehicles ===")
    r2 = requests.get('http://127.0.0.1/api/vehicles', headers=headers)
    print('HTTP', r2.status_code)
    print(r2.text[:200])
    
    # 3. 测试 /api/employees
    print("\n=== 3. GET /api/employees ===")
    r3 = requests.get('http://127.0.0.1/api/employees', headers=headers)
    print('HTTP', r3.status_code)
    print(r3.text[:200])
    
    # 4. 测试 /api/customers
    print("\n=== 4. GET /api/customers?type=customer ===")
    r4 = requests.get('http://127.0.0.1/api/customers?type=customer', headers=headers)
    print('HTTP', r4.status_code)
    print(r4.text[:200])
else:
    print("未获取到 token，跳过认证接口测试")
