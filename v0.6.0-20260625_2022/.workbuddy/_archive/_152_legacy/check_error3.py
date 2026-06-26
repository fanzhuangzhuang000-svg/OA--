"""Get the latest error from the log and check cache table."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    'sudo head -10 /var/www/oa-api/storage/logs/laravel.log 2>&1',
    'echo "============"',
    # Check if cache table exists
    'cd /var/www/oa-api && sudo -u www-data psql -d security_oa -c "\\dt" 2>&1 | head -60',
    'echo "==========="',
    # List failed migrations
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | tail -30',
    # Try login again with explicit Accept: application/json
    'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -c 2000',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out[:3000]}")
    if err.strip():
        print(f"ERR: {err[:1500]}")

client.close()
