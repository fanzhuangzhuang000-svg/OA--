#!/usr/bin/env python
"""查找nginx配置和PHP-FPM连接"""
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)
print("[OK] SSH连接成功\n")

checks = [
    ('查找nginx配置', 'sudo grep -r "oa-api\\|3001\\|3000\\|fastcgi_pass" /etc/nginx/ 2>/dev/null | head -30'),
    ('nginx主配置', 'sudo cat /etc/nginx/nginx.conf | grep -A2 "include"'),
    ('所有conf.d配置', 'sudo ls -la /etc/nginx/conf.d/ /etc/nginx/sites-enabled/ 2>/dev/null'),
    ('PHP-FPM监听', 'sudo cat /etc/php/8.3/fpm/pool.d/www.conf | grep -E "(listen|pm\\.)" | head -10'),
    ('oa-api .env APP_URL', 'sudo cat /var/www/oa-api/.env | grep -E "(APP_URL|DB_)"'),
    ('测试PHP-FPM socket', 'ls -la /run/php/ 2>&1 | head -10'),
    ('直接测试PHP-FPM', 'curl -s -o /dev/null -w "HTTP %{http_code}\\n" --unix-socket /run/php/php8.3-fpm.sock http://localhost/api/health 2>&1 || echo "FAILED"'),
    ('端口实际监听', 'sudo netstat -tlnp 2>/dev/null | head -20 || sudo ss -tlnp | head -20'),
    ('完整nginx sites', 'sudo find /etc/nginx -name "*.conf" -type f 2>/dev/null'),
    ('oa-web反向代理配置', 'sudo cat /etc/nginx/sites-available/oa-web 2>/dev/null | head -40'),
]

for name, cmd in checks:
    print(f"=== {name} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(out if out.strip() else err)
    print()

ssh.close()
