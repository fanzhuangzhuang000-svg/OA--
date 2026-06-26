#!/usr/bin/env python3
"""
测试152服务器的线索和商机API端点（修正URL）
"""

import requests
import json

# API配置
BASE_URL = "http://152.136.115.121/api"
LOGIN_URL = f"{BASE_URL}/auth/login"

# 登录凭据
LOGIN_DATA = {
    "username": "admin",
    "password": "Admin@2026"
}

def test_api():
    # 1. 登录获取token
    print("🔐 1. 登录获取token...")
    try:
        response = requests.post(LOGIN_URL, json=LOGIN_DATA, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                token = data.get('data', {}).get('token')
                print(f"  ✅ 登录成功，token获取成功")
                return token
            else:
                print(f"  ❌ 登录失败: {data.get('message')}")
                return None
        else:
            print(f"  ❌ 登录失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ 登录错误: {e}")
        return None

def test_leads_api(token):
    # 2. 测试线索API（修正URL）
    print("\n📋 2. 测试线索API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 正确的URL: /api/sales/leads
    url = f"{BASE_URL}/sales/leads"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  URL: {url}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应code: {data.get('code')}")
            
            if data.get('code') == 0:
                leads_data = data.get('data', [])
                if isinstance(leads_data, dict):
                    leads_data = leads_data.get('data', [])
                
                print(f"  ✅ 线索API调用成功，返回 {len(leads_data)} 条数据")
                
                if len(leads_data) > 0:
                    print(f"  示例数据: {json.dumps(leads_data[0], ensure_ascii=False)[:200]}...")
                else:
                    print(f"  ⚠️  线索API返回空数据")
            else:
                print(f"  ❌ 线索API返回错误: {data.get('message')}")
        else:
            print(f"  ❌ 线索API调用失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:500]}")
    except Exception as e:
        print(f"  ❌ 线索API调用错误: {e}")

def test_opps_api(token):
    # 3. 测试商机API（修正URL）
    print("\n📈 3. 测试商机API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 正确的URL: /api/sales/opps
    url = f"{BASE_URL}/sales/opps"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  URL: {url}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应code: {data.get('code')}")
            
            if data.get('code') == 0:
                opps_data = data.get('data', [])
                if isinstance(opps_data, dict):
                    opps_data = opps_data.get('data', [])
                
                print(f"  ✅ 商机API调用成功，返回 {len(opps_data)} 条数据")
                
                if len(opps_data) > 0:
                    print(f"  示例数据: {json.dumps(opps_data[0], ensure_ascii=False)[:200]}...")
                else:
                    print(f"  ⚠️  商机API返回空数据")
            else:
                print(f"  ❌ 商机API返回错误: {data.get('message')}")
        else:
            print(f"  ❌ 商机API调用失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:500]}")
    except Exception as e:
        print(f"  ❌ 商机API调用错误: {e}")

def main():
    print("🚀 开始测试152服务器API端点（修正URL）...\n")
    print("=" * 60)
    
    # 登录
    token = test_api()
    
    if not token:
        print("\n❌ 无法获取token，测试终止")
        return
    
    # 测试线索API
    test_leads_api(token)
    
    # 测试商机API
    test_opps_api(token)
    
    print("\n" + "=" * 60)
    print("✅ API测试完成")
    print("\n💡 如果API返回数据但前端看板仍为空，可能是：")
    print("  1. 前端调用了错误的API端点")
    print("  2. 前端看板组件有bug")
    print("  3. 数据格式不符合前端期望")

if __name__ == "__main__":
    main()
