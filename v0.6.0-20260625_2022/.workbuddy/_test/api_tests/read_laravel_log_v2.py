#!/usr/bin/env python3
"""
读取 172 服务器 laravel.log 定位 500 错误根因
复用 deploy_to_172.py 的 ssh_connect()
"""
import sys, os
sys.path.insert(0, r'D:\work\website\OA\.workbuddy')

# 复用 deploy_to_172.py 的连接函数
import importlib.util
spec = importlib.util.spec_from_file_location("deploy", r"D:\work\website\OA\.workbuddy\deploy_to_172.py")
deploy_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy_mod)
ssh_connect = deploy_mod.ssh_connect

def run(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def main():
    print("🔗 连接 172.20.0.139 ...")
    ssh = ssh_connect()
    print("✅ 已连接")

    # 先触发 500 错误，确保写入日志
    print("\n🚀 触发 PUT /projects/214/stage (500) ...")
    trigger = r"""cat > /tmp/trigger_500.py << 'PYEOF'
import requests, json
s = requests.Session()
r = s.post('http://127.0.0.1/api/auth/login', json={'username':'nbcy','password':'admin123'})
token = r.json().get('data',{}).get('token','')
h = {'Authorization': f'Bearer {token}'}
r2 = s.put('http://127.0.0.1/api/projects/214/stage', json={'stage':'accepted'}, headers=h)
print(f'HTTP {r2.status_code}')
print(r2.text[:800])
PYEOF
python3 /tmp/trigger_500.py"""
    out, err = run(ssh, trigger, timeout=30)
    print(f"  输出: {out[:400]}")
    if err: print(f"  stderr: {err[:200]}")

    # 触发 vehicles 500
    print("\n🚀 触发 POST /vehicles (500) ...")
    trigger2 = r"""cat > /tmp/trigger_vehicles.py << 'PYEOF'
import requests, json
s = requests.Session()
r = s.post('http://127.0.0.1/api/auth/login', json={'username':'nbcy','password':'admin123'})
token = r.json().get('data',{}).get('token','')
h = {'Authorization': f'Bearer {token}'}
data = {
    'plate_no': '京A12345',
    'type': 'sedan',
    'brand': 'Toyota',
    'model': 'Camry',
    'year': 2023,
    'color': 'black',
    'vin': 'VIN123456789',
    'engine_no': 'ENG123',
    'purchase_date': '2023-01-01',
    'purchase_price': 250000,
    'status': 'active',
    'mileage': 0
}
r2 = s.post('http://127.0.0.1/api/vehicles', json=data, headers=h)
print(f'HTTP {r2.status_code}')
print(r2.text[:800])
PYEOF
python3 /tmp/trigger_vehicles.py"""
    out, err = run(ssh, trigger2, timeout=30)
    print(f"  输出: {out[:400]}")
    if err: print(f"  stderr: {err[:200]}")

    # 读取 laravel.log 最后 200 行
    print("\n📖 读取 laravel.log 最后 200 行 ...")
    out, err = run(ssh, "tail -200 /var/www/oa-api/storage/logs/laravel.log", timeout=15)
    
    if not out.strip():
        print("  ⚠️  tail 无输出，尝试 sudo ...")
        out, err = run(ssh, "sudo tail -200 /var/www/oa-api/storage/logs/laravel.log", timeout=15)
    
    lines = out.split('\n')
    print(f"  日志共 {len(lines)} 行")
    
    # 找错误块
    print("\n🔍 提取错误堆栈 ...")
    error_content = out
    
    # 搜索关键字
    keywords = ['stage', 'Vehicle', 'updateStage', 'ErrorException', 'TypeError', 
                'SQLSTATE', 'Illuminate\\', 'Stack trace', 'Exception']
    
    found = False
    for kw in keywords:
        if kw in error_content:
            idx = error_content.rfind(kw)  # 最后一个匹配
            start = max(0, error_content.rfind('\n[', 0, idx))
            snippet = error_content[start:start+3000] if start >= 0 else error_content[idx:idx+3000]
            print(f"\n--- 关键字 '{kw}' 附近 ---")
            print(snippet)
            found = True
    
    if not found:
        print("  ⚠️  未找到关键字，输出最后 100 行:")
        print('\n'.join(lines[-100:]))
    
    # 直接 grep ERROR
    print("\n\n🔍 grep local.ERROR ...")
    out2, _ = run(ssh, "grep -n 'local.ERROR' /var/www/oa-api/storage/logs/laravel.log | tail -10", timeout=10)
    print(out2 if out2 else "  (无 ERROR 行)")

    ssh.close()
    print("\n✅ 完成")

if __name__ == "__main__":
    main()
