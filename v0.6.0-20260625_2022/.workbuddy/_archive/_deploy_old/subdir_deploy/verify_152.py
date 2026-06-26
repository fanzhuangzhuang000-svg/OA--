#!/usr/bin/env python
"""深度诊断152服务器API返回000的问题"""
import paramiko
import time

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
print("[OK] SSH连接成功\n")

# 完整诊断
checks = [
    ('PHP-FPM状态', 'sudo systemctl status php8.3-fpm --no-pager -l | head -20'),
    ('Nginx状态', 'sudo systemctl status nginx --no-pager -l | head -10'),
    ('Nginx配置', 'sudo cat /etc/nginx/sites-enabled/oa-api 2>/dev/null || sudo cat /etc/nginx/conf.d/oa-api.conf 2>/dev/null'),
    ('3001端口监听', 'sudo ss -tlnp | grep -E "(3001|3000|php-fpm)"'),
    ('oa-api目录', 'sudo ls -la /var/www/oa-api/ | head -20'),
    ('storage权限', 'sudo ls -la /var/www/oa-api/storage/logs/'),
    ('本地curl', 'curl -v http://localhost:3001/ 2>&1 | head -20'),
    ('PHP-FPM错误日志', 'sudo tail -30 /var/log/php8.3-fpm.log 2>&1'),
    ('Laravel错误日志', 'sudo tail -30 /var/www/oa-api/storage/logs/laravel.log 2>&1'),
]

for name, cmd in checks:
    print(f"=== {name} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(out if out.strip() else err)
    print()

ssh.close()
