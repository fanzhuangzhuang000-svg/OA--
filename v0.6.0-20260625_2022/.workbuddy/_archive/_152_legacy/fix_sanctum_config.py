"""Upload fixed config/sanctum.php and re-test login."""
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

# 1. Upload fixed config
print("\n[1/4] Uploading fixed config/sanctum.php...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\config\sanctum.php', f'{REMOTE_API}/config/sanctum.php')
scp.close()
print("     Uploaded.")

# 2. Fix ownership
print("\n[2/4] Fixing ownership...")
cmd = f'sudo chown www-data:www-data {REMOTE_API}/config/sanctum.php'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
stdout.read()
time.sleep(1)

# 3. Clear config cache
print("\n[3/4] Clearing config cache...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
print(stdout.read().decode('utf-8', errors='replace'))

# 4. Test with Origin header (browser-like)
print("\n[4/4] Testing login with Origin header...")
test_cmd = 'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Origin: http://152.136.115.121" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1'
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print(f"Response: {out[:1500]}")

client.close()
print("\n[DONE]")
