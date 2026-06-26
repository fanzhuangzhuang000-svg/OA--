import requests
import json

# 1. 登录
print("=== 1. 登录 ===")
r = requests.post('http://127.0.0.1/api/auth/login',
    json={'username':'admin','password':'admin123'})
print('HTTP', r.status_code)
try:
    d = r.json()
    print(json.dumps(d, ensure_ascii=False)[:300])
    token = d.get('data', {}).get('token', '')
    print("\nToken:", token[:50], "...")

    if token:
        # 2. 用 api_token 测试 /api/vehicles
        print("\n=== 2. GET /api/vehicles?api_token=... ===")
        r2 = requests.get(f'http://127.0.0.1/api/vehicles?api_token={token}')
        print('HTTP', r2.status_code)
        print(r2.text[:300])

        # 3. 测试 /api/employees
        print("\n=== 3. GET /api/employees?api_token=... ===")
        r3 = requests.get(f'http://127.0.0.1/api/employees?api_token={token}')
        print('HTTP', r3.status_code)
        print(r3.text[:300])

        # 4. 测试 /api/customers?type=customer
        print("\n=== 4. GET /api/customers?type=customer&api_token=... ===")
        r4 = requests.get(f'http://127.0.0.1/api/customers?type=customer&api_token={token}')
        print('HTTP', r4.status_code)
        print(r4.text[:300])

    else:
        print("未获取到 token，跳过认证接口测试")
except Exception as e:
    print('解析失败:', e)
    print(r.text[:300])
