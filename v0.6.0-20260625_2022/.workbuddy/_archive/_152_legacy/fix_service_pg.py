"""Upload fixed ServiceController and re-scan for MySQL-isms."""
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

# 1. Chown the Controllers/Api dir for upload
print("\n[1/4] Fixing perms for upload...")
cmd = f'sudo chown -R ubuntu:ubuntu {REMOTE_API}/app/Http/Controllers/Api/ 2>&1 | head -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"  chown: {stdout.read().decode('utf-8', errors='replace')}")
time.sleep(1)

# 2. Upload
print("\n[2/4] Uploading ServiceController.php...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\ServiceController.php',
        f'{REMOTE_API}/app/Http/Controllers/Api/ServiceController.php')
scp.close()
print("  Uploaded.")

# 3. Chown back to www-data
print("\n[3/4] Restoring www-data ownership...")
cmd = f'sudo chown -R www-data:www-data {REMOTE_API}/app/Http/Controllers/Api/ && ls -la {REMOTE_API}/app/Http/Controllers/Api/ServiceController.php'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(stdout.read().decode('utf-8', errors='replace'))

# 4. Final scan
print("\n[4/4] Final scan for MySQL-isms in deployed code...")
cmd = f'grep -rn "TIMESTAMPDIFF\|DATE_FORMAT\|DATEDIFF\|IFNULL" {REMOTE_API}/app/ --include="*.php" 2>&1 | head -20'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

# Test service metrics endpoint
print("\n[+] Testing /api/service/metrics...")
cmd = 'curl -s -H "Accept: application/json" -H "Authorization: Bearer 9|EePpV6ssgpSqZSGpfH2UkuL7ZAV1DPc4I3NSspA852097c65" http://127.0.0.1/api/service/metrics 2>&1 | head -c 500'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
print("\n[DONE]")
