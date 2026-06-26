#!/usr/bin/env python3
"""
全面测试所有 API 端点
"""
import paramiko
import requests
import json

SSH_HOST = "172.20.0.139"
SSH_PORT = 22
SSH_USER = "nbcy"
SSH_PASS = "admin123"
SUDO_PASS = "admin123"

BASE_URL = "http://172.20.0.139/api"

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    return client

def run_cmd(client, cmd, use_sudo=False, timeout=30):
    full_cmd = (f"echo {SUDO_PASS} | sudo -S {cmd}") if use_sudo else cmd
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace') + stderr.read().decode('utf-8', errors='replace')

print("=" * 70)
print("安防运维OA系统 - 后端 API 全面测试")
print("=" * 70)

# 1. 登录
print("\n[1] 登录...")
try:
    resp = requests.post(f"{BASE_URL}/auth/login",
                       json={"username": "admin", "password": "admin123"}, timeout=10)
    print(f"    状态: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"    ❌ 登录失败: {resp.text}")
        exit(1)
    
    data = resp.json()
    token = data['data']['token']
    user = data['data']['user']
    print(f"    ✅ 登录成功")
    print(f"    用户: {user['name']} ({user['username']})")
    print(f"    部门: {user.get('department', 'N/A')}")
    
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
except Exception as e:
    print(f"    ❌ 连接失败: {e}")
    exit(1)

# 2. 获取用户信息
print("\n[2] 获取用户信息...")
resp = requests.get(f"{BASE_URL}/auth/userinfo", headers=headers, timeout=10)
print(f"    状态: {resp.status_code}")
if resp.status_code == 200:
    info = resp.json()['data']['user']
    print(f"    ✅ 用户: {info['name']} ({info.get('gender', 'N/A')})")
else:
    print(f"    ❌ 失败: {resp.text[:200]}")

# 3. 测试各个 API 模块
api_tests = [
    ("仪表盘统计", "GET", "/dashboard/stats"),
    ("最近项目", "GET", "/dashboard/recent-projects"),
    ("最近工单", "GET", "/dashboard/recent-service-orders"),
    ("员工列表", "GET", "/employees"),
    ("部门列表", "GET", "/employees/departments"),
    ("客户列表", "GET", "/customers"),
    ("项目列表", "GET", "/projects"),
    ("售后服务单", "GET", "/service/orders"),
    ("报销列表", "GET", "/expenses"),
    ("我的报销", "GET", "/expenses/my"),
    ("车辆列表", "GET", "/vehicles"),
    ("车辆使用", "GET", "/vehicles/usage"),
    ("库存列表", "GET", "/inventory"),
    ("库存记录", "GET", "/inventory/stock-records"),
    ("仓库列表", "GET", "/inventory/warehouses"),
    ("财务概览", "GET", "/finance/overview"),
    ("应收款", "GET", "/finance/receivables"),
    ("应付款", "GET", "/finance/payables"),
    ("网盘文件夹", "GET", "/disk/folders"),
    ("网盘文件", "GET", "/disk/files"),
    ("知识库分类", "GET", "/knowledge/categories"),
    ("知识库文章", "GET", "/knowledge/articles"),
    ("消息列表", "GET", "/notifications"),
    ("未读消息数", "GET", "/notifications/unread-count"),
    ("系统日志", "GET", "/system-logs"),
    ("考勤概览", "GET", "/attendance/overview"),
    ("考勤记录", "GET", "/attendance/records"),
    ("请假列表", "GET", "/attendance/leave"),
    ("加班列表", "GET", "/attendance/overtime"),
    ("考勤报表", "GET", "/attendance/report"),
    ("岗位列表", "GET", "/employees/positions"),
    ("技能列表", "GET", "/employees/skills"),
    ("证书列表", "GET", "/employees/certificates"),
    ("供应商列表", "GET", "/projects/suppliers"),
    ("服务统计", "GET", "/service/stats"),
    ("维保合同", "GET", "/service/maintenance-contracts"),
]

success_count = 0
fail_count = 0
error_details = []

print(f"\n[3] 测试 {len(api_tests)} 个 API 端点...")
print("-" * 70)

for name, method, path in api_tests:
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json={}, timeout=10)
        
        status = resp.status_code
        if status == 200:
            success_count += 1
            # 尝试解析响应
            try:
                resp_data = resp.json()
                code = resp_data.get('code', 'N/A')
                print(f"    ✅ {name:20s} {path:40s} [{status}] code={code}")
            except:
                print(f"    ✅ {name:20s} {path:40s} [{status}]")
        else:
            fail_count += 1
            error_msg = resp.text[:100]
            print(f"    ❌ {name:20s} {path:40s} [{status}] {error_msg}")
            error_details.append((name, path, status, error_msg))
            
    except Exception as e:
        fail_count += 1
        print(f"    ❌ {name:20s} {path:40s} [ERR] {str(e)[:50]}")
        error_details.append((name, path, 'ERR', str(e)))

# 4. 总结
print("\n" + "=" * 70)
print(f"测试结果: {success_count} 成功 / {fail_count} 失败 / {len(api_tests)} 总计")
print("=" * 70)

if error_details:
    print(f"\n失败的端点详情:")
    for name, path, status, msg in error_details:
        print(f"  - {name} ({path}): [{status}] {msg}")

# 5. 登出测试
print("\n[4] 登出测试...")
resp = requests.post(f"{BASE_URL}/auth/logout", headers=headers, timeout=10)
print(f"    状态: {resp.status_code}")
if resp.status_code == 200:
    print(f"    ✅ 登出成功")
else:
    print(f"    ❌ 登出失败: {resp.text[:200]}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
print(f"\nAPI 地址: http://172.20.0.139/api")
print(f"默认账号: admin / admin123")
print(f"可用用户: admin, manager, user, zhaodc, chenjing")
print(f"所有用户密码: admin123")
