"""Fix the missing APP_KEY and verify the API works end-to-end."""
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

# 1. Generate APP_KEY
print("\n[1/4] Generating APP_KEY...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan key:generate --show 2>&1'
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(f"OUT: {out}")
if err:
    print(f"ERR: {err}")

# 2. Inject the key into .env
print("\n[2/4] Setting APP_KEY in .env...")
# First check current .env
cmd = f'cat {REMOTE_API}/.env | grep -E "APP_KEY|APP_URL" 2>&1'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"Current: {stdout.read().decode('utf-8', errors='replace').strip()}")

# 3. Use sed to replace the APP_KEY line
cmd = f"cd {REMOTE_API} && KEY=$(sudo -u www-data php artisan key:generate --show 2>/dev/null) && echo \"KEY: $KEY\" && sed -i 's|^APP_KEY=.*|APP_KEY='\"$KEY\"'|' .env && sudo chown www-data:www-data .env && echo 'Set:' && grep APP_KEY .env"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"OUT: {out}")
if err:
    print(f"ERR: {err[:500]}")

# 4. Clear config cache and test
print("\n[3/4] Clearing config cache and config:cache...")
cmds = [
    f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -5',
    f'cd {REMOTE_API} && sudo -u www-data php artisan cache:clear 2>&1 | tail -5',
]
for cmd in cmds:
    print(f">> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8', errors='replace'))
    time.sleep(0.5)

# 5. Test login via nginx (port 80)
print("\n[4/4] Testing API through nginx (port 80)...")
test_cmd = '''curl -s -X POST http://127.0.0.1/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>&1 | head -c 1500'''
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=20)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"Response: {out}")
if err:
    print(f"ERR: {err[:500]}")

# 6. Test /up
print("\n[+] Testing /up...")
up_cmd = 'curl -s -i http://127.0.0.1/up 2>&1 | head -c 500'
stdin, stdout, stderr = client.exec_command(up_cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
print("\n[DONE]")
