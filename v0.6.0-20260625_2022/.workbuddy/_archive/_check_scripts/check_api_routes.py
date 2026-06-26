#!/usr/bin/env python3
"""
检查152服务器的API路由和控制器
"""

import paramiko

HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("🔍 检查152服务器API路由和控制器...\n")

# 1. 检查routes/api.php中是否有leads和opportunities路由
print("📋 1. 检查routes/api.php中的线索和商机路由...")
cmd1 = "sudo -u www-data grep -n 'lead\|opportunity' /var/www/oa-api/routes/api.php 2>/dev/null || echo 'NOT_FOUND'"
stdin, stdout, stderr = ssh.exec_command(cmd1, timeout=30)
result1 = stdout.read().decode('utf-8', errors='ignore')
print(result1 if result1.strip() else "  ⚠️  没有找到leads或opportunities相关路由\n")

# 2. 检查是否有LeadController和OpportunityController
print("\n📁 2. 检查控制器文件...")
cmd2 = "sudo -u www-data ls -la /var/www/oa-api/app/Http/Controllers/Api/ | grep -i 'lead\|opportunity'"
stdin, stdout, stderr = ssh.exec_command(cmd2, timeout=30)
result2 = stdout.read().decode('utf-8', errors='ignore')
print(result2 if result2.strip() else "  ⚠️  没有找到LeadController或OpportunityController\n")

# 3. 检查前端调用的实际API端点
print("\n📡 3. 检查前端API调用...")
cmd3 = "sudo -u www-data grep -r 'api/leads\|api/opportunities' /var/www/oa-web/ 2>/dev/null | head -10"
stdin, stdout, stderr = ssh.exec_command(cmd3, timeout=30)
result3 = stdout.read().decode('utf-8', errors='ignore')
if result3.strip():
    print(result3[:500])
else:
    print("  ⚠️  前端可能没有部署，或者API路径不对\n")

# 4. 检查本地前端API文件
print("\n📡 4. 检查本地前端API文件...")
import os
if os.path.exists('D:/work/website/OA/pc-web/src/api'):
    cmd = "grep -r 'leads\|opportunities' 'D:/work/website/OA/pc-web/src/api/' 2>/dev/null | head -10"
    print(cmd)  # 这行只是示意，实际需要用Python文件读取

print("\n" + "=" * 60)
print("✅ 检查完成")

ssh.close()
