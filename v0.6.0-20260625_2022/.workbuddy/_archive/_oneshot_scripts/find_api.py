import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', port=22, username='nbcy', password='admin123')

for cmd in [
    'ss -tlnp | grep -E ":(80|8000|8080|9000|3000) "',
    'curl -sS http://127.0.0.1:8000/api/dashboard/stats -H "Accept: application/json" 2>&1 | head -c 400',
    'systemctl status php8.3-fpm --no-pager 2>&1 | head -15',
    'ls /etc/nginx/sites-enabled/ 2>/dev/null',
    'cat /etc/nginx/sites-enabled/oa-api* 2>/dev/null | head -30',
]:
    si,so,se = ssh.exec_command(cmd)
    print('---', cmd[:60], '---')
    print(so.read().decode() or se.read().decode())
ssh.close()
