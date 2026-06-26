"""Change backend API from port 80 to 3001, update frontend proxy accordingly."""
import paramiko

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

# 1. Read current backend Nginx config
print("=== Current backend config ===")
out, _ = run('cat /etc/nginx/sites-available/oa-api.conf', sudo=True)
print(out)

# 2. Change backend to listen on 3001
print("\n=== Updating backend to port 3001 ===")
backend_conf = out.replace('listen 80;', 'listen 3001;')

sftp = ssh.open_sftp()
with sftp.open('/tmp/oa-api.conf', 'w') as f:
    f.write(backend_conf)
sftp.close()

run('cp /tmp/oa-api.conf /etc/nginx/sites-available/oa-api.conf', sudo=True)
print("Backend now listens on 3001")

# 3. Update frontend proxy to point to 3001
print("\n=== Updating frontend proxy to backend:3001 ===")
out2, _ = run('cat /etc/nginx/sites-available/oa-web.conf', sudo=True)
print("Old frontend config:")
print(out2)

frontend_conf = out2.replace('proxy_pass http://127.0.0.1:80;', 'proxy_pass http://127.0.0.1:3001;')

sftp = ssh.open_sftp()
with sftp.open('/tmp/oa-web.conf', 'w') as f:
    f.write(frontend_conf)
sftp.close()

run('cp /tmp/oa-web.conf /etc/nginx/sites-available/oa-web.conf', sudo=True)
print("Frontend proxy now points to 3001")

# 4. Test & reload
out, _ = run('nginx -t 2>&1', sudo=True)
print(f"\nnginx -t: {out}")

run('systemctl reload nginx', sudo=True)
print("Nginx reloaded")

# 5. Verify
import requests
try:
    r1 = requests.get('http://172.20.0.139:3000/', timeout=5)
    print(f"\nFrontend :3000 → {r1.status_code}")
except Exception as e:
    print(f"\nFrontend :3000 → {e}")

try:
    r2 = requests.get('http://172.20.0.139:3001/', timeout=5)
    print(f"Backend  :3001 → {r2.status_code}")
except Exception as e:
    print(f"Backend  :3001 → {e}")

try:
    r3 = requests.post('http://172.20.0.139:3000/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=5)
    print(f"Login via :3000 proxy → {r3.status_code}")
    print(f"Response: {r3.text[:150]}")
except Exception as e:
    print(f"Login via :3000 proxy → {e}")

ssh.close()
print("\nDone! Backend: :3001, Frontend: :3000")
