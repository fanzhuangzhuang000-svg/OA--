#!/usr/bin/env python3
"""修 model_has_roles - 重新插入用对的 model_type"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123')

# 用 raw 字符串 + 单反斜杠
sql = r"""
DELETE FROM model_has_roles WHERE model_type = 'App\Models\User' AND model_id >= 74;
INSERT INTO model_has_roles (role_id, model_type, model_id) VALUES
  (1, 'App\Models\User', 74),
  (2, 'App\Models\User', 75),
  (2, 'App\Models\User', 76),
  (2, 'App\Models\User', 77),
  (2, 'App\Models\User', 78),
  (3, 'App\Models\User', 79),
  (3, 'App\Models\User', 80),
  (4, 'App\Models\User', 81),
  (4, 'App\Models\User', 82),
  (4, 'App\Models\User', 83),
  (4, 'App\Models\User', 84),
  (4, 'App\Models\User', 85),
  (4, 'App\Models\User', 86),
  (4, 'App\Models\User', 87),
  (4, 'App\Models\User', 88),
  (1, 'App\Models\User', 89),
  (2, 'App\Models\User', 90),
  (2, 'App\Models\User', 91),
  (2, 'App\Models\User', 92),
  (2, 'App\Models\User', 93),
  (3, 'App\Models\User', 94),
  (3, 'App\Models\User', 95),
  (4, 'App\Models\User', 96),
  (4, 'App\Models\User', 97),
  (4, 'App\Models\User', 98),
  (4, 'App\Models\User', 99),
  (4, 'App\Models\User', 100),
  (4, 'App\Models\User', 101),
  (4, 'App\Models\User', 102),
  (4, 'App\Models\User', 103);
"""
with open('_test/data_gen/fix_roles.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

sftp = ssh.open_sftp()
sftp.put('_test/data_gen/fix_roles.sql', '/tmp/fix_roles.sql')
sftp.close()
print("sftp OK")
print(ssh.exec_command("PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -f /tmp/fix_roles.sql 2>&1")[1].read().decode())
print("---")
print(ssh.exec_command("""PGPASSWORD=oa_pg_pwd_782997781 psql -U oa_user -d security_oa -c "SELECT r.name, count(*) FROM model_has_roles mhr JOIN roles r ON r.id=mhr.role_id GROUP BY r.name ORDER BY r.name;""" )[1].read().decode())
ssh.close()
