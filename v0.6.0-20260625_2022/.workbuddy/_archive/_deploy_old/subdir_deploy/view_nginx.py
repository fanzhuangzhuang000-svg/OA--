#!/usr/bin/env python
"""查看完整nginx oa配置"""
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

cmds = [
    ('完整oa配置', 'sudo cat /etc/nginx/sites-available/oa'),
    ('nginx主配置server段', 'sudo cat /etc/nginx/nginx.conf'),
    ('从80端口直接访问', 'curl -v http://localhost:80/ 2>&1 | head -30'),
    ('从80端口访问API', 'curl -s -o /dev/null -w "HTTP %{http_code}\\n" http://localhost:80/api/health'),
]

for name, cmd in cmds:
    print(f"\n=== {name} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print(out if out.strip() else err)

ssh.close()
