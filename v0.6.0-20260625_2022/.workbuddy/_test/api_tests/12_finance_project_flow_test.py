#!/usr/bin/env python3
"""
Session B 阶段 3：资金和项目流转测试
测试目标：
1. 资金流转：创建应收款 → 创建收款 → 关闭应收款
2. 项目流转：创建项目 → 更新阶段 → 创建施工日志 → 查看跟踪
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://172.20.0.139/api"
TOKEN = None

def login():
    """登录获取 token"""
    print("🔑 登录获取 token...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123",
    }, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            global TOKEN
            TOKEN = data["data"]["token"]
            print(f"  ✅ 登录成功 (token 前 20 字符: {TOKEN[:20]}...)")
            return True
    
    print(f"  ❌ 登录失败: {resp.status_code} {resp.text[:200]}")
    return False

def auth_request(method, path, **kwargs):
    """带认证的请求"""
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {TOKEN}"
    headers["Accept"] = "application/json"
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)

def test_finance_flow():
    """测试资金流转"""
    print("\n💰 测试资金流转...")
    print("-" * 40)
    
    # 1. 创建应收款
    print("  1️⃣ 创建应收款...")
    receivable = {
        "customer_id": 1,
        "project_id": None,
        "amount": 100000,
        "received_amount": 0,
        "status": "pending",
        "received_date": None,
        "note": f"测试应收款 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    }
    
    resp = auth_request("POST", "/finance/receivables", json=receivable)
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        receivable_id = data["data"]["id"]
        print(f"    ✅ 应收款创建成功 (ID: {receivable_id})")
    else:
        print(f"    ❌ 创建失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
        return
    
    # 2. 创建第一笔收款
    print("  2️⃣ 创建第一笔收款 (50000)...")
    payment = {
        "amount": 50000,
        "payment_date": datetime.now().strftime("%Y-%m-%d"),
        "payment_method": "bank_transfer",
        "note": "测试收款 - 第一笔",
    }
    
    resp = auth_request("POST", f"/finance/receivables/{receivable_id}/payments", json=payment)
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 第一笔收款创建成功")
    else:
        print(f"    ❌ 创建失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 3. 创建第二笔收款（凑满）
    print("  3️⃣ 创建第二笔收款 (50000)...")
    payment["amount"] = 50000
    payment["note"] = "测试收款 - 第二笔"
    
    resp = auth_request("POST", f"/finance/receivables/{receivable_id}/payments", json=payment)
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 第二笔收款创建成功")
    else:
        print(f"    ❌ 创建失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 4. 关闭应收款
    print("  4️⃣ 关闭应收款...")
    resp = auth_request("POST", f"/finance/receivables/{receivable_id}/close")
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 应收款关闭成功")
    else:
        print(f"    ❌ 关闭失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 5. 验证应收款状态
    print("  5️⃣ 验证应收款状态...")
    resp = auth_request("GET", f"/finance/receivables/{receivable_id}")
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        status = data["data"].get("status", "")
        received_amount = data["data"].get("received_amount", 0)
        print(f"    ✅ 状态: {status}, 已收金额: {received_amount}")
        
        if status == "closed" and received_amount == 100000:
            print(f"    ✅ 资金流转测试通过！")
        else:
            print(f"    ⚠️ 状态或金额不正确")
    else:
        print(f"    ❌ 查询失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    print("  ✅ 资金流转测试完成\n")

def test_project_flow():
    """测试项目流转"""
    print("\n🏗️ 测试项目流转...")
    print("-" * 40)
    
    # 1. 创建项目
    print("  1️⃣ 创建项目...")
    project = {
        "name": f"测试项目 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "customer_id": 1,
        "type": "implementation",
        "status": "pending",
        "stage": "initiation",
        "progress": 0,
        "member_ids": [1],
    }
    
    resp = auth_request("POST", "/projects", json=project)
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        project_id = data["data"]["id"]
        print(f"    ✅ 项目创建成功 (ID: {project_id})")
    else:
        print(f"    ❌ 创建失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
        return
    
    # 2. 更新项目阶段（initiation → inquiry）
    print("  2️⃣ 更新项目阶段 (initiation → inquiry)...")
    resp = auth_request("PUT", f"/projects/{project_id}/stage", json={"stage": "inquiry"})
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 阶段更新成功")
    else:
        print(f"    ❌ 更新失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 3. 继续更新阶段（inquiry → contract）
    print("  3️⃣ 继续更新阶段 (inquiry → contract)...")
    resp = auth_request("PUT", f"/projects/{project_id}/stage", json={"stage": "contract"})
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 阶段更新成功")
    else:
        print(f"    ❌ 更新失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 4. 创建施工日志
    print("  4️⃣ 创建施工日志...")
    log = {
        "content": f"测试施工日志 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "log_date": datetime.now().strftime("%Y-%m-%d"),
        "progress": 30,
    }
    
    resp = auth_request("POST", f"/projects/{project_id}/construction-logs", json=log)
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        print(f"    ✅ 施工日志创建成功")
    else:
        print(f"    ❌ 创建失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    # 5. 查看项目跟踪
    print("  5️⃣ 查看项目跟踪...")
    resp = auth_request("GET", f"/projects/{project_id}/tracking")
    data = resp.json()
    
    if resp.status_code == 200 and data.get("code") == 0:
        current_stage = data["data"].get("current_stage", "unknown")
        print(f"    ✅ 项目跟踪数据获取成功")
        print(f"    当前阶段: {current_stage}")
    else:
        print(f"    ❌ 获取失败: {resp.status_code} {json.dumps(data, ensure_ascii=False)}")
    
    print("  ✅ 项目流转测试完成\n")

def main():
    print("🚀 Session B 阶段 3：资金和项目流转测试")
    print("=" * 50)
    print()
    
    # 登录
    if not login():
        print("❌ 登录失败，测试终止")
        return
    
    # 测试资金流转
    try:
        test_finance_flow()
    except Exception as e:
        print(f"❌ 资金流转测试异常: {e}")
    
    # 测试项目流转
    try:
        test_project_flow()
    except Exception as e:
        print(f"❌ 项目流转测试异常: {e}")
    
    print("✅ 所有测试完成")

if __name__ == "__main__":
    main()
