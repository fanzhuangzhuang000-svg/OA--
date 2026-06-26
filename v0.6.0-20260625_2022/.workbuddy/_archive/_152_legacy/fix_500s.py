"""Upload fixes for ExpenseController and OtherModels."""
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
print(f"[OK] Connected")

# 1. Chown
print("\n[1/4] Chown for upload...")
cmd = f'sudo chown -R ubuntu:ubuntu {REMOTE_API}/app/Models/ {REMOTE_API}/app/Http/Controllers/Api/ 2>&1 | head -3'
client.exec_command(cmd, timeout=10)
time.sleep(1)

# 2. Upload
print("\n[2/4] Uploading files...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\app\Models\OtherModels.php',
        f'{REMOTE_API}/app/Models/OtherModels.php')
scp.put(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\ExpenseController.php',
        f'{REMOTE_API}/app/Http/Controllers/Api/ExpenseController.php')
scp.close()

# 3. Restore ownership
print("\n[3/4] Restoring ownership...")
cmd = f'sudo chown -R www-data:www-data {REMOTE_API}/app/Models/ {REMOTE_API}/app/Http/Controllers/Api/ 2>&1 | head -3'
client.exec_command(cmd, timeout=10)
time.sleep(1)

# 4. Clear cache and dump autoload
print("\n[4/4] Clearing config and dump autoload...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3 && sudo -u www-data composer dump-autoload --no-dev 2>&1 | tail -5'
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
out = stdout.read().decode('utf-8', errors='replace')
print(f"  {out[:1500]}")

# Test
cmd = 'curl -s -X POST -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -c 200'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
import json
data = json.loads(out)
token = data.get('data', {}).get('token', '')

for ep in ['/api/expenses', '/api/notifications']:
    cmd = f'curl -s -H "Authorization: Bearer {token}" http://127.0.0.1{ep} 2>&1 | head -c 200'
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(f"  {ep}: {stdout.read().decode('utf-8', errors='replace')}")

client.close()
print("\n[DONE]")
