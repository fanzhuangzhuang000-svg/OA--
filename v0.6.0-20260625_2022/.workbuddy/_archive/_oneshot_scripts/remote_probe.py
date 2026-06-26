import paramiko, time
host='172.20.0.139'; user='nbcy'; pwd='admin123'
ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()); ssh.connect(host, username=user, password=pwd, timeout=30)
cmds = [
  "sudo ls -la /var/www/oa-web | head -3",
  "sudo find /var/www/oa-web/assets -maxdepth 1 -type f | head -3",
  "curl -s -o /dev/null -w 'HTTP:%{http_code}\\n' http://127.0.0.1/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'",
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=30)
    out=stdout.read().decode(errors='ignore'); err=stderr.read().decode(errors='ignore')
    print('CMD:', cmd)
    print(out if out else err)
    print('---')
ssh.close()
