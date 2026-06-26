"""
Upload ComprehensiveTestDataSeeder.php and run php artisan db:seed.
"""
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

# 1. Chown the seeders dir for upload
print("\n[1/5] Chown seeders dir...")
cmd = f'sudo chown -R ubuntu:ubuntu {REMOTE_API}/database/seeders/ 2>&1 | head -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"  {stdout.read().decode('utf-8', errors='replace')}")
time.sleep(1)

# 2. Upload
print("\n[2/5] Uploading ComprehensiveTestDataSeeder.php...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\database\seeders\ComprehensiveTestDataSeeder.php',
        f'{REMOTE_API}/database/seeders/ComprehensiveTestDataSeeder.php')
scp.close()
print("  Uploaded.")

# 3. Restore ownership
print("\n[3/5] Restoring www-data ownership...")
cmd = f'sudo chown -R www-data:www-data {REMOTE_API}/database/seeders/ 2>&1 | head -3'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
print(f"  {stdout.read().decode('utf-8', errors='replace')}")
time.sleep(1)

# 4. Clear config cache (autoload may need refresh)
print("\n[4/5] Clearing config cache and running autoload...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan config:clear 2>&1 | tail -3 && sudo -u www-data composer dump-autoload --no-dev 2>&1 | tail -5'
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
out = stdout.read().decode('utf-8', errors='replace')
print(f"  {out[:1500]}")

# 5. Run the seeder
print("\n[5/5] Running ComprehensiveTestDataSeeder...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan db:seed --class=ComprehensiveTestDataSeeder 2>&1 | tail -80'
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"STDOUT:\n{out}")
if err:
    print(f"\nSTDERR:\n{err[:3000]}")

client.close()
print("\n[DONE]")
