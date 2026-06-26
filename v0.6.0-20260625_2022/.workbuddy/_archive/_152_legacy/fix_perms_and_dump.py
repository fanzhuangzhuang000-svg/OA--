"""
Fix composer permissions issue and re-run dump-autoload.
Also: re-verify Enums class loads after fix.
"""
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

# 1. Fix ownership of vendor/composer/ (composer needs write access)
print("\n[1/4] Fixing ownership of vendor/composer/...")
cmds = [
    f'sudo chown -R www-data:www-data {REMOTE_API}/vendor/composer/ {REMOTE_API}/vendor/composer/installed.json {REMOTE_API}/vendor/autoload.php 2>&1 | head -5',
    f'ls -la {REMOTE_API}/vendor/composer/autoload_files.php 2>&1',
]
for cmd in cmds:
    print(f"\n>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err.strip():
        print(f"ERR: {err[:500]}")
    time.sleep(0.5)

# 2. Run dump-autoload now that permissions are fixed
print("\n[2/4] Running composer dump-autoload...")
cmd_dump = f'cd {REMOTE_API} && sudo -u www-data composer dump-autoload --no-dev 2>&1 | tail -15'
stdin, stdout, stderr = client.exec_command(cmd_dump, timeout=120)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"OUT: {out}")
if err.strip():
    print(f"ERR: {err[:1000]}")

# 3. Verify autoload_files.php now contains the Enums file
print("\n[3/4] Checking autoload_files.php for index.php...")
cmd = f'grep "index.php" {REMOTE_API}/vendor/composer/autoload_files.php'
stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f"index.php references: {out if out else '(NONE)'}")

# 4. Verify the class is now loadable
print("\n[4/4] Verifying App\\Enums\\UserStatus can be autoloaded...")
verify_cmd = (
    f'sudo -u www-data php -r "require \\"{REMOTE_API}/vendor/autoload.php\\"; '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\UserStatus\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\Gender\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\ProjectStage\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\ServiceOrderStatus\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\Urgency\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\ApprovalStatus\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\CustomerCategory\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\LeaveType\')); '
    f'var_dump(enum_exists(\'App\\\\Enums\\\\ExpenseCategory\'));" 2>&1'
)
stdin, stdout, stderr = client.exec_command(verify_cmd, timeout=15)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(f"Result:\n{out}")
if err.strip():
    print(f"ERR: {err[:500]}")

client.close()
print("\n[DONE]")
