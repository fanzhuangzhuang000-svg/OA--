#!/usr/bin/env python
"""检查152服务器状态"""
import paramiko
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=10)
    print("[OK] SSH连接成功\n")

    commands = [
        ('PHP-FPM', 'sudo systemctl is-active php8.3-fpm'),
        ('Nginx', 'sudo systemctl is-active nginx'),
        ('Concerns目录', 'sudo ls -la /var/www/oa-api/app/Http/Controllers/Api/Concerns/ 2>&1'),
        ('API health', 'curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:3001/api/health'),
        ('finance测试', 'curl -s http://localhost:3001/api/finance/accounts -H "Accept: application/json" | head -c 500'),
    ]

    for name, cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        print(f"=== {name} ===")
        print(out if out else err)
        print()

    ssh.close()
except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)
