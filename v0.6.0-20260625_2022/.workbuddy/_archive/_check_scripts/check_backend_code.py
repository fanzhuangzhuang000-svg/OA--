#!/usr/bin/env python3
"""
检查152服务器的后端代码状态
"""

import paramiko

HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("🔍 检查152服务器后端代码状态...\n")

# 1. 检查routes/api.php是否有leads路由
print("📋 1. 检查routes/api.php中的leads路由...")
cmd1 = "sudo -u www-data grep -n 'leads' /var/www/oa-api/routes/api.php 2>/dev/null | head -10"
stdin, stdout, stderr = ssh.exec_command(cmd1, timeout=30)
result1 = stdout.read().decode('utf-8', errors='ignore')
if result1.strip():
    print(result1)
else:
    print("  ❌ 没有找到leads路由\n")

# 2. 检查SalesController是否存在
print("📁 2. 检查SalesController...")
cmd2 = "sudo -u www-data ls -la /var/www/oa-api/app/Http/Controllers/Api/ | grep -i sales"
stdin, stdout, stderr = ssh.exec_command(cmd2, timeout=30)
result2 = stdout.read().decode('utf-8', errors='ignore')
if result2.strip():
    print(result2)
else:
    print("  ❌ 没有找到SalesController\n")

# 3. 检查routes/api.php文件行数
print("📊 3. 检查routes/api.php文件大小...")
cmd3 = "sudo -u www-data wc -l /var/www/oa-api/routes/api.php 2>/dev/null || echo 'FILE_NOT_FOUND'"
stdin, stdout, stderr = ssh.exec_command(cmd3, timeout=30)
result3 = stdout.read().decode('utf-8', errors='ignore')
print(f"  文件行数: {result3.strip()}\n")

# 4. 检查api.php是否包含opportunities路由
print("📈 4. 检查opportunities路由...")
cmd4 = "sudo -u www-data grep -n 'opportunities' /var/www/oa-api/routes/api.php 2>/dev/null | head -10"
stdin, stdout, stderr = ssh.exec_command(cmd4, timeout=30)
result4 = stdout.read().decode('utf-8', errors='ignore')
if result4.strip():
    print(result4)
else:
    print("  ❌ 没有找到opportunities路由\n")

print("=" * 60)
print("✅ 检查完成")

ssh.close()
