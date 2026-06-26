"""Enable APP_DEBUG and re-test to see actual error."""
import time
import paramiko

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
REMOTE_API = '/var/www/oa-api'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=20)
print(f"[OK] Connected to {HOST}")

# 1. Set APP_DEBUG=true temporarily
print("\n[1/5] Enabling APP_DEBUG=true temporarily...")
cmd = f"cd {REMOTE_API} && sudo -u www-data sed -i 's|^APP_DEBUG=.*|APP_DEBUG=true|' .env && grep APP_DEBUG .env"
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"OUT: {stdout.read().decode('utf-8', errors='replace').strip()}")
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"ERR: {err[:300]}")

# 2. Clear config cache
print("\n[2/5] Clearing config cache...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
print(stdout.read().decode('utf-8', errors='replace'))
time.sleep(1)

# 3. Truncate log to get fresh
print("\n[3/5] Truncating log file...")
cmd = f'sudo bash -c "echo \\"\\" > {REMOTE_API}/storage/logs/laravel.log"'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"OUT: {stdout.read().decode('utf-8', errors='replace')}")

# 4. Make a login request
print("\n[4/5] Testing login...")
test_cmd = '''curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"username":"admin","password":"admin123"}' http://127.0.0.1/api/auth/login 2>&1 | head -c 3000'''
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=20)
out = stdout.read().decode('utf-8', errors='replace')
print(f"Response:\n{out}")

# 5. Read log
print("\n[5/5] Reading fresh log...")
cmd = f'sudo head -20 {REMOTE_API}/storage/logs/laravel.log 2>&1'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
out = stdout.read().decode('utf-8', errors='replace')
print(f"Log:\n{out[:3000]}")

# 6. Revert APP_DEBUG
print("\n[+] Reverting APP_DEBUG to false...")
cmd = f"cd {REMOTE_API} && sudo -u www-data sed -i 's|^APP_DEBUG=.*|APP_DEBUG=false|' .env && grep APP_DEBUG .env"
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip())

client.close()
print("\n[DONE]")
