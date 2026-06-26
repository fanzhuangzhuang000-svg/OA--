"""Fix the MySQL-specific TIMESTAMPDIFF and EXTRACT(HOUR ...) for PostgreSQL."""
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

# 1. Read local file
print("\n[1/4] Reading local DashboardController.php...")
with open(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php', 'r', encoding='utf-8') as f:
    content = f.read()

# 2. Replace MySQL-specific syntax with PG
# TIMESTAMPDIFF(HOUR, x, y) → EXTRACT(EPOCH FROM (y - x)) / 3600
# TIMESTAMPDIFF(MINUTE, x, y) → EXTRACT(EPOCH FROM (y - x)) / 60
old_new_pairs = [
    ("TIMESTAMPDIFF(HOUR, assigned_at, completed_at) <= sla_hours",
     "EXTRACT(EPOCH FROM (completed_at - assigned_at)) / 3600 <= sla_hours"),
    ("AVG(TIMESTAMPDIFF(MINUTE, assigned_at, started_at))",
     "AVG(EXTRACT(EPOCH FROM (started_at - assigned_at)) / 60)"),
]

new_content = content
for old, new in old_new_pairs:
    if old in new_content:
        new_content = new_content.replace(old, new)
        print(f"  Replaced: {old[:50]}...")
    else:
        print(f"  NOT FOUND: {old[:50]}...")

# Save
with open(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("  Local file saved.")

# 3. Upload
print("\n[2/4] Uploading to server...")
# First, fix ownership of the directory
cmd = f'sudo chown -R ubuntu:ubuntu {REMOTE_API}/app/Http/Controllers/Api/ 2>&1 | head -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"  chown: {stdout.read().decode('utf-8', errors='replace')}")
time.sleep(1)

scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api\DashboardController.php',
        f'{REMOTE_API}/app/Http/Controllers/Api/DashboardController.php')
scp.close()
print("  Uploaded.")

# 4. Fix ownership
print("\n[3/4] Fixing ownership...")
cmd = f'sudo chown www-data:www-data {REMOTE_API}/app/Http/Controllers/Api/DashboardController.php'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
stdout.read()

# 5. Clear config cache and test
print("\n[4/4] Clearing config cache and testing...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
print(stdout.read().decode('utf-8', errors='replace'))
time.sleep(1)

# Test
cmd = 'curl -s -H "Accept: application/json" -H "Authorization: Bearer 6|eAkQwOc6E8BtsHQYpD4gyZjbup4wr3KGO656HfBHbed08f16" http://127.0.0.1/api/dashboard/screen 2>&1 | head -c 2500'
stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
out = stdout.read().decode('utf-8', errors='replace')
print(f"Screen response: {out}")

client.close()
print("\n[DONE]")
