"""处理剩余问题：attendance 缺 calendar/makeup-cards 路由 + 知识库报错 + 一键清理不生效"""
import paramiko
import urllib.request
import urllib.error
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

def run(cmd, t=10):
    si, so, se = ssh.exec_command(cmd, timeout=t)
    out = so.read().decode('utf-8', 'replace')
    return out

# 1. 找 AttendanceController 里有没有 calendar / makeupCards 方法
print('=== AttendanceController 全部方法 ===')
out = run('grep -n "public function" /var/www/oa-api/app/Http/Controllers/Api/AttendanceController.php')
print(out)

# 2. 找 wipeData
print()
print('=== SystemSettingsController::wipeData ===')
out = run('sed -n "/function wipeData/,/^    }/p" /var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php | head -80')
print(out)

# 3. 看 wipeData POST 数据格式
print()
print('=== wipeData validation ===')
out = run('grep -B 2 -A 8 "validation.required" /var/www/oa-api/app/Http/Controllers/Api/SystemSettingsController.php | head -20')
print(out)

ssh.close()
