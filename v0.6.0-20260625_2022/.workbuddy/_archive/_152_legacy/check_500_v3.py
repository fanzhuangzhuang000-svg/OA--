"""Investigate why the new error isn't being logged."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    'ls -la /var/www/oa-api/storage/logs/ 2>&1',
    'echo "---"',
    'sudo tail -50 /var/www/oa-api/storage/logs/laravel.log 2>&1',
    'echo "---"',
    # Try curl with browser-like headers
    'curl -sv -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Origin: http://152.136.115.121" -H "Referer: http://152.136.115.121/login" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -40',
    'echo "---"',
    # Curl with /api prefix
    'curl -sv -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -30',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=20)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out[:3000]}")
    if err.strip():
        print(f"ERR: {err[:1500]}")

client.close()
