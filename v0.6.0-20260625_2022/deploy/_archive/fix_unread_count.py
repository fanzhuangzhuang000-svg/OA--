#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix unreadCount method signature"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=30)
    return stdout.read().decode('utf-8', errors='replace').strip()

run('chown nbcy:nbcy /var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')

sftp = ssh.open_sftp()
content = sftp.open('/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php').read().decode('utf-8')

# Fix: add Request $request parameter to unreadCount
content = content.replace(
    "public function unreadCount(): JsonResponse",
    "public function unreadCount(Request $request): JsonResponse"
)

sftp.open('/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php', 'w').write(content)
sftp.close()

run('chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')
run('php /var/www/oa-api/artisan config:clear')
run('php /var/www/oa-api/artisan cache:clear')
print("Fixed unreadCount")

ssh.close()
