#!/usr/bin/env python3
"""查 users 密码 hash"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.3.117', port=22, username='nbcy', password='admin123', timeout=20)

cmd = """sudo -n -u postgres psql -d security_oa -c "SELECT id, username, substring(password, 1, 40) AS hash_prefix FROM users WHERE id IN (1, 74, 80, 81, 82, 86) ORDER BY id\""""
si, so, se = ssh.exec_command(cmd)
print(so.read().decode())
ssh.close()
