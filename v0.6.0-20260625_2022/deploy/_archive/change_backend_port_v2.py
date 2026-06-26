"""Fix: update the correct backend config file (oa-api, not oa-api.conf)"""
import paramiko, requests

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
SUDO_PASS = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, sudo=False):
    if sudo:
        cmd = f'echo {SUDO_PASS} | sudo -S {cmd}'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

# 1. Update backend: listen 80 -> 3001
backend_conf = """server {
    listen 3001;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }
    location ~ \\.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
    location ~ /\\.(?!well-known).* {
        deny all;
    }
}"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/oa-api', 'w') as f:
    f.write(backend_conf)
sftp.close()

run('cp /tmp/oa-api /etc/nginx/sites-available/oa-api', sudo=True)
print("[1] Backend config updated to port 3001")

# 2. Verify frontend proxy points to 3001
out, _ = run('cat /etc/nginx/sites-available/oa-web.conf', sudo=True)
if 'proxy_pass http://127.0.0.1:3001;' in out:
    print("[2] Frontend proxy already points to :3001")
else:
    out = out.replace('proxy_pass http://127.0.0.1:80;', 'proxy_pass http://127.0.0.1:3001;')
    with ssh.open_sftp() as sftp:
        with sftp.open('/tmp/oa-web.conf', 'w') as f:
            f.write(out)
    run('cp /tmp/oa-web.conf /etc/nginx/sites-available/oa-web.conf', sudo=True)
    print("[2] Frontend proxy updated to :3001")

# 3. Remove the empty oa-api.conf we accidentally created
run('rm -f /etc/nginx/sites-available/oa-api.conf /etc/nginx/sites-enabled/oa-api.conf', sudo=True)

# 4. Test & reload
out, _ = run('nginx -t 2>&1', sudo=True)
print(f"[3] nginx -t: {out}")
run('systemctl reload nginx', sudo=True)
print("[4] Nginx reloaded")

ssh.close()

# 5. Verify
print("\n=== Verification ===")
try:
    r = requests.get(f'http://{HOST}:3000/', timeout=5)
    print(f"Frontend :3000 -> {r.status_code}")
except Exception as e:
    print(f"Frontend :3000 -> {e}")

try:
    r = requests.post(f'http://{HOST}:3000/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=5)
    print(f"Login via :3000 -> {r.status_code} {r.text[:120]}")
except Exception as e:
    print(f"Login via :3000 -> {e}")

try:
    r = requests.get(f'http://{HOST}:3001/', timeout=5)
    print(f"Backend  :3001 -> {r.status_code}")
except Exception as e:
    print(f"Backend  :3001 -> {e}")

print("\nDone! Backend: :3001, Frontend: :3000")
