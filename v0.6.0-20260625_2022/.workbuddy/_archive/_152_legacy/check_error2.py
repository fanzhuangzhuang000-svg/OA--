"""Get the actual error message and check nginx routing."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    # Get the error message and first part of the stack
    'sudo head -40 /var/www/oa-api/storage/logs/laravel.log 2>&1',
    'echo "============= nginx config ============="',
    'cat /etc/nginx/sites-enabled/oa 2>&1 | head -80',
    'echo "============= test direct from port 3001 ============="',
    'curl -sv -X POST -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' http://127.0.0.1:3001/api/auth/login 2>&1 | head -40',
    'echo "============= php-fpm status ============="',
    'systemctl status php8.3-fpm --no-pager 2>&1 | head -10',
    'echo "============= port 3001 listening? ============="',
    'ss -tlnp 2>&1 | grep -E "3001|3000|80 "',
    'echo "============= check API direct via 80 ============="',
    'curl -s http://127.0.0.1/api/up 2>&1 | head -c 500',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(f"OUT: {out[:3000]}")
    if err.strip():
        print(f"ERR: {err[:2000]}")

client.close()
