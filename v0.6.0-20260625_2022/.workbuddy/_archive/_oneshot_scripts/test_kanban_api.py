#!/usr/bin/env python3
"""
测试152服务器的线索和商机API端点
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
            print(f"  响应: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ 登录错误: {e}")
        return None

def test_leads_api(token):
    # 2. 测试线索API
    print("\n📋 2. 测试线索API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试线索列表
    url = f"{BASE_URL}/leads"
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
    
    # 测试线索看板API（如果有）
    url = f"{BASE_URL}/leads/kanban"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n  测试线索看板API: {url}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ 线索看板API存在")
        elif response.status_code == 404:
            print(f"  ⚠️  线索看板API不存在 (404)")
        else:
            print(f"  ⚠️  线索看板API返回: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 线索看板API调用错误: {e}")

def test_opportunities_api(token):
    # 3. 测试商机API
    print("\n📈 3. 测试商机API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试商机列表
    url = f"{BASE_URL}/opportunities"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  URL: {url}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应code: {data.get('code')}")
            
            if data.get('code') == 0:
                opp_data = data.get('data', [])
                if isinstance(opp_data, dict):
                    opp_data = opp_data.get('data', [])
                
                print(f"  ✅ 商机API调用成功，返回 {len(opp_data)} 条数据")
                
                if len(opp_data) > 0:
                    print(f"  示例数据: {json.dumps(opp_data[0], ensure_ascii=False)[:200]}...")
                else:
                    print(f"  ⚠️  商机API返回空数据")
            else:
                print(f"  ❌ 商机API返回错误: {data.get('message')}")
        else:
            print(f"  ❌ 商机API调用失败: HTTP {response.status_code}")
            print(f"  响应: {response.text[:500]}")
    except Exception as e:
        print(f"  ❌ 商机API调用错误: {e}")
    
    # 测试商机看板API（如果有）
    url = f"{BASE_URL}/opportunities/kanban"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n  测试商机看板API: {url}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ 商机看板API存在")
        elif response.status_code == 404:
            print(f"  ⚠️  商机看板API不存在 (404)")
        else:
            print(f"  ⚠️  商机看板API返回: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ 商机看板API调用错误: {e}")

def main():
    print("🚀 开始测试152服务器API端点...\n")
    print("=" * 60)
    
    # 登录
    token = test_api()
    
    if not token:
        print("\n❌ 无法获取token，测试终止")
        return
    
    # 测试线索API
    test_leads_api(token)
    
    # 测试商机API
    test_opportunities_api(token)
    
    print("\n" + "=" * 60)
    print("✅ API测试完成")
    print("\n💡 如果API返回数据但前端看板仍为空，可能是：")
    print("  1. 前端看板组件有bug")
    print("  2. 前端没有调用正确的API端点")
    print("  3. 数据格式不符合前端期望")

if __name__ == "__main__":
    main()
