"""Check what's failing on the /api/dashboard/screen endpoint."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=20)
print(f"[OK] Connected")

# 1. Hit the screen endpoint and see what comes back
print("\n[1/3] Testing GET /api/dashboard/screen...")
cmds = [
    'curl -s -H "Accept: application/json" -H "Authorization: Bearer 6|eAkQwOc6E8BtsHQYpD4gyZjbup4wr3KGO656HfBHbed08f16" http://127.0.0.1/api/dashboard/screen 2>&1 | head -c 2000',
    'echo ""',
    'echo "--- Latest log entries ---"',
    'sudo grep -E "production.ERROR|local.ERROR" /var/www/oa-api/storage/logs/laravel.log 2>&1 | tail -2',
]
for cmd in cmds:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip(): print(f"OUT: {out[:3000]}")
    if err.strip(): print(f"ERR: {err[:2000]}")

client.close()
