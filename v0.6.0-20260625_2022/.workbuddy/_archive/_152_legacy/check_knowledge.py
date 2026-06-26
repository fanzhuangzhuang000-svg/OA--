"""Check if knowledge_articles table exists on server."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

cmds = [
    'PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c "\\dt" 2>&1 | grep -i knowledge',
    'echo "---"',
    'PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c "SELECT * FROM migrations WHERE migration LIKE \\"%knowledge%" 2>&1"',
    'echo "---"',
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | grep -i knowledge',
    'echo "---"',
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate --force 2>&1 | tail -20',
]
for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip(): print(f"OUT: {out[:2000]}")
    if err.strip(): print(f"ERR: {err[:1000]}")

client.close()
