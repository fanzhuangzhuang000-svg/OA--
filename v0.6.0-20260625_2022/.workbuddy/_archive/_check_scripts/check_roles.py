import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', 22, 'nbcy', 'admin123')
sql = "DESCRIBE roles;"
script = f"""#!/bin/bash
mysql -uoa_user -poa_password oa_db -e "{sql}" 2>&1 | grep -v Warning
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/check_roles.sh', 'w') as f:
    f.write(script)
sftp.chmod('/tmp/check_roles.sh', 0o755)
sftp.close()
stdin, stdout, stderr = ssh.exec_command('bash /tmp/check_roles.sh')
print(stdout.read().decode())
ssh.close()
