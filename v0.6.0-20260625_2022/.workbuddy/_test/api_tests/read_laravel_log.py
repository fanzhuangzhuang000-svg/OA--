#!/usr/bin/env python3
"""读取 172 服务器上的 laravel.log，找出最近的 500 错误"""
import paramiko
import io

SSH_HOST = "172.20.0.139"
SSH_USER = "nbcy"
SSH_PASS = "admin123"
SSH_PORT = 22

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    return client

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def main():
    print("🔗 连接 172.20.0.139 ...")
    client = ssh_connect()
    print("✅ 已连接")

    # 先触发一次 500，确保错误写入日志
    print("\n🚀 触发 PUT /projects/214/stage (确保错误写入日志)...")
    trigger_script = """
import requests, json
s = requests.Session()
r = s.post('http://127.0.0.1/api/auth/login', json={'username':'nbcy','password':'admin123'})
token = r.json().get('data',{}).get('token','')
h = {'Authorization':f'Bearer {token}'}
r2 = s.put(f'http://127.0.0.1/api/projects/214/stage', json={'stage':'accepted'}, headers=h)
print(f'HTTP {r2.status_code}')
print(r2.text[:500])
"""
    cmd = f"python3 -c \"{trigger_script.replace(chr(10), '; ')}\""
    # 用更简单的方式：写临时文件执行
    write_cmd = f"""cat > /tmp/trigger_500.py << 'PYEOF'
import requests, json
s = requests.Session()
r = s.post('http://127.0.0.1/api/auth/login', json={'username':'nbcy','password':'admin123'})
token = r.json().get('data',{}).get('token','')
h = {'Authorization': f'Bearer {token}'}
r2 = s.put('http://127.0.0.1/api/projects/214/stage', json={'stage':'accepted'}, headers=h)
print(f'HTTP {r2.status_code}')
print(r2.text[:500])
PYEOF
python3 /tmp/trigger_500.py"""
    out, err = run_cmd(client, write_cmd)
    print(f"  输出: {out[:300]}")
    if err: print(f"  stderr: {err[:200]}")

    # 触发 vehicles 500
    print("\n🚀 触发 POST /vehicles (确保错误写入日志)...")
    trigger_vehicles = """cat > /tmp/trigger_vehicles.py << 'PYEOF'
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
print(r2.text[:500])
PYEOF
python3 /tmp/trigger_vehicles.py"""
    out, err = run_cmd(client, trigger_vehicles)
    print(f"  输出: {out[:300]}")
    if err: print(f"  stderr: {err[:200]}")

    # 读取 laravel.log 最后 300 行
    print("\n📖 读取 laravel.log 最后 300 行...")
    log_cmd = "tail -300 /var/www/oa-api/storage/logs/laravel.log"
    out, err = run_cmd(client, log_cmd, timeout=15)
    
    if not out.strip():
        print("  ⚠️ 日志为空，尝试读取整个文件...")
        out, err = run_cmd(client, "cat /var/www/oa-api/storage/logs/laravel.log", timeout=15)
    
    # 找出包含 "ERROR" 或 "Stack trace" 或 ".php" 的行
    lines = out.split('\n')
    print(f"  日志共 {len(lines)} 行")
    
    # 提取最近的错误块（从最后一个 "[YYYY-MM-DD" 开始）
    error_blocks = []
    current_block = []
    in_error = False
    
    for line in lines:
        if line.startswith('[') and '] ' in line:
            if current_block:
                error_blocks.append('\n'.join(current_block))
                current_block = []
            current_block.append(line)
        elif line.strip():
            current_block.append(line)
    
    if current_block:
        error_blocks.append('\n'.join(current_block))
    
    # 找包含 "stage" 或 "Vehicle" 或 "ErrorException" 的块
    print("\n🔍 筛选相关错误...")
    relevant = [b for b in error_blocks if any(kw in b for kw in 
                  ['stage', 'Vehicle', 'ErrorException', 'TypeError', 
                   'NotFound', 'updateStage', 'store', 'SQLSTATE',
                   'Illuminate\\\\'])]
    
    if relevant:
        for i, block in enumerate(relevant[-5:]):  # 最后 5 个相关错误
            print(f"\n--- 错误块 #{i+1} ---")
            print(block[:1500])
            print("..." if len(block) > 1500 else "")
    else:
        print("  ⚠️ 未找到相关错误，输出最后 3 个错误块:")
        for block in error_blocks[-3:]:
            print(block[:1000])
            print("..." if len(block) > 1000 else "")
    
    # 也直接搜索 "local.ERROR"
    print("\n\n🔍 直接搜索 local.ERROR ...")
    grep_cmd = "grep -n 'local.ERROR' /var/www/oa-api/storage/logs/laravel.log | tail -20"
    out, err = run_cmd(client, grep_cmd, timeout=10)
    print(out[:2000] if out else "  (无 local.ERROR 行)")
    
    client.close()
    print("\n✅ 完成")

if __name__ == "__main__":
    main()
