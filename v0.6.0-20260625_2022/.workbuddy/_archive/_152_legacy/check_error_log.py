"""Check Laravel log for the actual server error after enum fix."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# 1. Get latest log lines
cmds = [
    'sudo tail -30 /var/www/oa-api/storage/logs/laravel.log 2>&1',
    # 2. Check /up response directly
    'curl -s -H "Accept: application/json" http://127.0.0.1:3001/up 2>&1 | head -c 500',
    'echo "---"',
    'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1:3001/api/auth/login 2>&1 | head -c 2000',
    'echo "---"',
    # 3. Test artisan tinker-like enum load
    'cd /var/www/oa-api && sudo -u www-data php artisan tinker --execute="echo \\"loaded\\"; var_dump(\\App\\Models\\User::first());" 2>&1 | head -c 1000',
    # 4. Check what file /up serves
    'cat /var/www/oa-api/routes/web.php 2>&1 | head -30',
    'ls /var/www/oa-api/public/ 2>&1',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out[:2500]}")
    if err.strip():
        print(f"ERR: {err[:1500]}")

client.close()
