"""Remove the server IP from SANCTUM_STATEFUL_DOMAINS so the browser request
uses bearer token auth (which the front-end already supports)."""
import time
import paramiko
from scp import SCPClient

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
REMOTE_API = '/var/www/oa-api'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=20)
print(f"[OK] Connected to {HOST}")

# 1. Download current .env
print("\n[1/4] Reading current .env...")
cmd = f'cat {REMOTE_API}/.env'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
env_content = stdout.read().decode('utf-8', errors='replace')
print(f"     Lines: {len(env_content.splitlines())}")

# 2. Update SANCTUM_STATEFUL_DOMAINS
print("\n[2/4] Updating SANCTUM_STATEFUL_DOMAINS...")
# Use sudo sed for in-place edit
cmd = f"sudo sed -i 's|SANCTUM_STATEFUL_DOMAINS=152.136.115.121,localhost|SANCTUM_STATEFUL_DOMAINS=localhost,localhost:3000|' {REMOTE_API}/.env"
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"     sed: {stdout.read().decode('utf-8', errors='replace')}")
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"     ERR: {err[:300]}")

# Verify
cmd = f'grep SANCTUM_STATEFUL_DOMAINS {REMOTE_API}/.env'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"     New value: {stdout.read().decode('utf-8', errors='replace').strip()}")

# 3. Fix ownership and clear cache
print("\n[3/4] Fixing ownership and clearing config cache...")
cmds = [
    f'sudo chown www-data:www-data {REMOTE_API}/.env',
    f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3',
]
for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
    print(stdout.read().decode('utf-8', errors='replace'))
    time.sleep(0.5)

# 4. Test
print("\n[4/4] Testing login with Origin header...")
test_cmd = 'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Origin: http://152.136.115.121" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1'
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print(f"Response: {out[:1500]}")

client.close()
print("\n[DONE]")
