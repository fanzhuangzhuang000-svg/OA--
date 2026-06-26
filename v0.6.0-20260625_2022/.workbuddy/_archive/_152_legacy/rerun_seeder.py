"""Re-upload and run seeder."""
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
print("\n[1/3] Chown seeders...")
cmd = f'sudo chown -R ubuntu:ubuntu {REMOTE_API}/database/seeders/ 2>&1 | head -3'
client.exec_command(cmd, timeout=10)
time.sleep(1)

# 2. Upload
print("\n[2/3] Uploading...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(r'D:\work\website\OA\pc-api\database\seeders\ComprehensiveTestDataSeeder.php',
        f'{REMOTE_API}/database/seeders/ComprehensiveTestDataSeeder.php')
scp.close()

# Restore ownership
cmd = f'sudo chown -R www-data:www-data {REMOTE_API}/database/seeders/ 2>&1'
client.exec_command(cmd, timeout=10)
time.sleep(1)

# 3. Run
print("\n[3/3] Running seeder...")
cmd = f'cd {REMOTE_API} && sudo -u www-data php artisan db:seed --class=ComprehensiveTestDataSeeder --force 2>&1 | tail -150'
stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"STDOUT:\n{out}")
if err:
    print(f"\nSTDERR:\n{err[:5000]}")

client.close()
print("\n[DONE]")
