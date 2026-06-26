import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
sql = """SELECT id,name,guard_name FROM roles ORDER BY id;
SELECT COUNT(*) AS perm_count FROM permissions;
SELECT id,name,guard_name FROM permissions LIMIT 5;
"""
script = f"""#!/bin/bash
mysql -uoa_user -poa_password oa_db -e "{sql}" 2>&1 | grep -v Warning
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/check_data.sh', 'w') as f:
    f.write(script)
sftp.chmod('/tmp/check_data.sh', 0o755)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('bash /tmp/check_data.sh')
print(stdout.read().decode())
ssh.close()
