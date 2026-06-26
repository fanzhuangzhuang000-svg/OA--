"""Fix backend Nginx config - use raw string write via SFTP to avoid escaping"""
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
        cmd = 'echo {} | sudo -S {}'.format(SUDO_PASS, cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

# Upload via SFTP with proper content
correct_config = (
    "server {\n"
    "    listen 3001;\n"
    "    server_name 172.20.0.139;\n"
    "    root /var/www/oa-api/public;\n"
    "    index index.php index.html;\n"
    '    add_header X-Frame-Options "SAMEORIGIN";\n'
    "    location / {\n"
    "        try_files \\$uri \\$uri/ /index.php\\?\\$query_string;\n"
    "    }\n"
    "    location ~ \\\\.php\\$ {\n"
    "        include snippets/fastcgi-php.conf;\n"
    "        fastcgi_pass unix:/run/php/php8.3-fpm.sock;\n"
    "    }\n"
    "    location ~ /\\\\.(?!well-known).* {\n"
    "        deny all;\n"
    "    }\n"
    "}\n"
)

print("Config to write:")
print(correct_config)
print()

# Actually let me just use a sed approach on the original file
# First restore the original file structure (it had \$uri literal)
# The issue is Python string escaping. Let me use base64 encoding instead.

import base64

nginx_config = b"""server {
    listen 3001;
    server_name 172.20.0.139;
    root /var/www/oa-api/public;
    index index.php index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    location ~ \\.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
    location ~ /\.(?!well-known).* {
        deny all;
    }
}
"""

encoded = base64.b64encode(nginx_config).decode()
print(f"[1] Base64 encoded config ({len(encoded)} chars)")

# Write via base64 decode on server
cmd = "echo {} | base64 -d | {} tee /etc/nginx/sites-available/oa-api > /dev/null".format(
    encoded,
    'echo admin123 | sudo -S '
)
# This is getting complex, let me use a simpler method
# Just write the base64 to a temp file, then decode it

sftp = ssh.open_sftp()
with sftp.open('/tmp/nginx_config_b64.txt', 'w') as f:
    f.write(encoded + '\n')
sftp.close()

run('base64 -d /tmp/nginx_config_b64.txt | sudo tee /etc/nginx/sites-available/oa-api > /dev/null')

# Verify
out, _ = run('cat /etc/nginx/sites-available/oa-api')
print("[2] Config on server:")
print(out)

# Test & reload
out, _ = run('nginx -t 2>&1')
print(f"\n[3] nginx -t: {out}")
run('systemctl reload nginx')
print("[4] Nginx reloaded")

ssh.close()

# Verify from outside
print("\n=== Verification ===")
try:
    r = requests.get('http://172.20.0.139:3001/', timeout=5)
    print(f"Backend :3001 -> {r.status_code}")
except Exception as e:
    print(f"Backend :3001 -> {e}")

try:
    r = requests.post('http://172.20.0.139:3000/api/auth/login',
                     json={'username':'admin','password':'admin123'}, timeout=5)
    print(f"Login via :3000 -> {r.status_code}")
    print(f"Response: {r.text[:150]}")
except Exception as e:
    print(f"Login via :3000 -> {e}")

print("\nDone! Backend: :3001, Frontend: :3000")
