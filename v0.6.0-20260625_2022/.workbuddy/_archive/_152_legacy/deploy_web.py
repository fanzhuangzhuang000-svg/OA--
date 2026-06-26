"""
Upload the pc-web dist/ to /var/www/oa-web/ on the server.
Then verify the full welcome page flow.
"""
import time
import os
import paramiko
from scp import SCPClient

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PWD, timeout=30)
print(f"[OK] Connected to {HOST}")

# 1. Create /var/www/oa-web directory (need sudo)
print("\n[1/4] Cleaning and recreating /var/www/oa-web directory...")
cmd = f'sudo rm -rf {REMOTE_WEB} && sudo mkdir -p {REMOTE_WEB} && sudo chown ubuntu:ubuntu {REMOTE_WEB} && ls -la {REMOTE_WEB}'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print(f"OUT: {out}")
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"ERR: {err[:300]}")
time.sleep(1)

# 2. Upload dist contents recursively
print("\n[2/4] Uploading dist/ to /var/www/oa-web/ ...")
scp = SCPClient(client.get_transport(), progress=lambda x, y, z: None)

# Upload each file in dist
for item in os.listdir(LOCAL_DIST):
    local_path = os.path.join(LOCAL_DIST, item)
    remote_path = f'{REMOTE_WEB}/{item}'
    if os.path.isdir(local_path):
        print(f"  Uploading dir: {item}/")
        scp.put(local_path, remote_path, recursive=True)
    else:
        print(f"  Uploading file: {item}")
        scp.put(local_path, remote_path)
scp.close()
print("  Upload complete")

# 3. Fix ownership to www-data
print("\n[3/4] Fixing ownership to www-data...")
cmd = f'sudo chown -R www-data:www-data {REMOTE_WEB} && ls -la {REMOTE_WEB} | head -10'
stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
print(f"OUT:\n{out}")
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"ERR: {err[:300]}")

# 4. Verify by hitting root
print("\n[4/4] Verifying via HTTP...")
cmds = [
    'curl -sI http://127.0.0.1/ 2>&1 | head -10',
    'curl -s http://127.0.0.1/ 2>&1 | head -c 500',
    'echo ""',
    'echo "--- API login ---"',
    'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -c 800',
]
for cmd in cmds:
    print(f">> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(stdout.read().decode('utf-8', errors='replace'))
    time.sleep(0.5)

client.close()
print("\n[DONE]")
