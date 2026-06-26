"""Check the actual 500 error from browser request."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=15)

# Get the latest log
cmds = [
    'sudo head -3 /var/www/oa-api/storage/logs/laravel.log 2>&1',
]

for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    out = stdout.read().decode('utf-8', errors='replace')
    print(f"OUT: {out[:4000]}")

client.close()
