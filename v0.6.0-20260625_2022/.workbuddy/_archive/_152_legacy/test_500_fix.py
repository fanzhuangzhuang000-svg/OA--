"""Test the fixes by hitting the API directly."""
import time
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=20)

# Clear log first
c2 = client.get_transport().open_session()
c2.exec_command('sudo bash -c "echo > /var/www/oa-api/storage/logs/laravel.log"')
time.sleep(1)

# Login
cmd = 'curl -s -X POST -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print('Login:', out[:300])
import re
m = re.search(r'"token":"([^"]+)"', out)
token = m.group(1) if m else ''

# Test endpoints
for ep in ['/api/expenses', '/api/notifications', '/api/expenses?page=1&per_page=15']:
    cmd = f'curl -s -H "Authorization: Bearer {token}" http://127.0.0.1{ep} 2>&1'
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(f'  {ep}: {stdout.read().decode("utf-8", errors="replace")[:300]}')

# Log
cmd = 'sudo head -3 /var/www/oa-api/storage/logs/laravel.log 2>&1 | head -c 2000'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print('Log:', stdout.read().decode('utf-8', errors='replace'))

client.close()
