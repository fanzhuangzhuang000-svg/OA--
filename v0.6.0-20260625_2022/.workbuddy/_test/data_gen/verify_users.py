#!/usr/bin/env python3
"""验证用户和角色"""
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

print("=== users 总数 ===")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -t -A -c \"SELECT count(*) FROM users;\"" )[1].read().decode())

print("=== model_has_roles 总数 ===")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -t -A -c \"SELECT count(*) FROM model_has_roles;\"" )[1].read().decode())

print("=== 角色分布（不过滤 model_type）===")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c \"SELECT r.name, count(*) FROM model_has_roles mhr JOIN roles r ON r.id=mhr.role_id GROUP BY r.name ORDER BY r.name;\"" )[1].read().decode())

print("=== 所有 model_type ===")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c \"SELECT model_type, count(*) FROM model_has_roles GROUP BY model_type;\"" )[1].read().decode())

ssh.close()
