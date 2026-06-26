#!/usr/bin/env python3
"""检查 model_has_roles 的实际 model_type"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c \"SELECT DISTINCT model_type FROM model_has_roles;\"" )[1].read().decode())
print("---")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c \"SELECT * FROM model_has_roles ORDER BY model_id;\"" )[1].read().decode())
ssh.close()
