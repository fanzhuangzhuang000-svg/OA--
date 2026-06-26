"""Check session config and find the actual exception."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# Get the FULL error message - the head -3 was only getting top of log
cmds = [
    'sudo grep -E "production.ERROR|local.ERROR" /var/www/oa-api/storage/logs/laravel.log 2>&1 | tail -3',
    'echo "---"',
    'sudo cat /var/www/oa-api/config/session.php 2>&1 | grep -E "driver|connection|table" | head -10',
    'echo "---"',
    'sudo cat /var/www/oa-api/.env 2>&1 | grep -E "SESSION|CACHE|DB_"',
    'echo "---"',
    # Check if SESSION_DRIVER=file or database
    'sudo grep -A 3 "session" /var/www/oa-api/.env',
    'echo "---"',
    # Check the session storage dir
    'ls -la /var/www/oa-api/storage/framework/sessions/ 2>&1 | head -5',
    'echo "---"',
    # Try APP_DEBUG=true and replicate
    'cd /var/www/oa-api && sudo -u www-data sed -i "s/^APP_DEBUG=.*/APP_DEBUG=true/" .env && sudo -u www-data php artisan config:clear 2>&1 | tail -3',
    'echo "--- request with Origin ---"',
    'curl -s -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Origin: http://152.136.115.121" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1/api/auth/login 2>&1 | head -c 3000',
    'echo ""',
    'echo "--- reading log ---"',
    'sudo head -3 /var/www/oa-api/storage/logs/laravel.log 2>&1 | head -c 4000',
    # Revert
    'cd /var/www/oa-api && sudo -u www-data sed -i "s/^APP_DEBUG=.*/APP_DEBUG=false/" .env && sudo -u www-data php artisan config:clear 2>&1 | tail -3',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out[:4000]}")
    if err.strip():
        print(f"ERR: {err[:2000]}")

client.close()
