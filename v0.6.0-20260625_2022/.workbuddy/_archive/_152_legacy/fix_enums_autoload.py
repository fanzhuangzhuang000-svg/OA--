"""
Fix the InvalidCastException issue by:
1. Uploading updated composer.json with app/Enums/index.php in autoload.files
2. Running composer dump-autoload to regenerate the autoloader
3. Verifying the Enums class is now discoverable
4. Testing the login API
"""
import os
import time
import paramiko
from scp import SCPClient

# Server config
HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
REMOTE_API = '/var/www/oa-api'

LOCAL_COMPOSER = r'D:\work\website\OA\pc-api\composer.json'

# Connect
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=20)
print(f"[OK] Connected to {HOST}")

# 1. Upload composer.json
print("\n[1/5] Uploading composer.json...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)
scp.put(LOCAL_COMPOSER, f'{REMOTE_API}/composer.json')
scp.close()
print(f"     Uploaded: {LOCAL_COMPOSER} -> {REMOTE_API}/composer.json")

# 2. Fix ownership
print("\n[2/5] Fixing ownership of composer.json...")
client.exec_command(f'sudo chown www-data:www-data {REMOTE_API}/composer.json', timeout=10)
time.sleep(1)

# 3. Dump autoload (this is the key step)
print("\n[3/5] Running composer dump-autoload...")
cmd_dump = f'cd {REMOTE_API} && sudo -u www-data composer dump-autoload --no-dev --optimize 2>&1'
stdin, stdout, stderr = client.exec_command(cmd_dump, timeout=120)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"     STDOUT: {out[:1500]}")
if err.strip():
    print(f"     STDERR: {err[:1000]}")

# 4. Verify Enum class can be loaded now
print("\n[4/5] Verifying App\\Enums\\UserStatus can be autoloaded...")
verify_cmd = (
    f'sudo -u www-data php -r "require \\"{REMOTE_API}/vendor/autoload.php\\"; '
    f'var_dump(class_exists(\'App\\\\Enums\\\\UserStatus\')); '
    f'var_dump(class_exists(\'App\\\\Enums\\\\Gender\')); '
    f'var_dump(class_exists(\'App\\\\Enums\\\\ProjectStage\')); '
    f'var_dump(class_exists(\'App\\\\Enums\\\\ServiceOrderStatus\')); '
    f'var_dump(class_exists(\'App\\\\Enums\\\\Urgency\'));" 2>&1'
)
stdin, stdout, stderr = client.exec_command(verify_cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"     Result: {out.strip()}")
if err.strip():
    print(f"     STDERR: {err[:500]}")

# 5. Test the login API
print("\n[5/5] Testing POST /api/auth/login...")
test_cmd = f'''curl -s -X POST http://127.0.0.1:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{{"username":"admin","password":"admin123"}}' 2>&1 | head -c 1500'''
stdin, stdout, stderr = client.exec_command(test_cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"     Response: {out[:1500]}")
if err.strip():
    print(f"     STDERR: {err[:500]}")

client.close()
print("\n[DONE] Autoload fix script complete.")
