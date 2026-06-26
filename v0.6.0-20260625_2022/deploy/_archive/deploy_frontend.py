"""
Deploy frontend (pc-web dist/) to 172.20.0.139:3000
- Build Vue project locally
- Upload dist/ to server
- Configure Nginx to serve static files on port 3000
- Proxy /api requests to Laravel backend (port 80)
"""

import paramiko
import os
import subprocess
import sys

HOST = '172.20.0.139'
USER = 'nbcy'
PASS = 'admin123'
SUDO_PASS = 'admin123'
LOCAL_DIST = r'D:\work\website\OA\pc-web\dist'
REMOTE_WEB = '/var/www/oa-web'

def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    return ssh

def run_cmd(ssh, cmd, use_sudo=False, timeout=30):
    if use_sudo:
        cmd = f'echo {SUDO_PASS} | sudo -S {cmd}'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

def main():
    # Step 1: Check dist exists
    if not os.path.isdir(LOCAL_DIST):
        print(f"[ERROR] dist directory not found: {LOCAL_DIST}")
        print("Please run: cd pc-web && npm run build")
        sys.exit(1)

    files = []
    for root, dirs, filenames in os.walk(LOCAL_DIST):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, LOCAL_DIST)
            files.append((full, rel))
    print(f"[1] Found {len(files)} files in dist/")

    # Step 2: Connect SSH
    ssh = ssh_connect()
    print("[2] SSH connected")

    # Step 3: Create remote directory
    print("[3] Creating remote directory...")
    run_cmd(ssh, f'mkdir -p {REMOTE_WEB}', use_sudo=True)
    run_cmd(ssh, f'chown -R {USER}:{USER} {REMOTE_WEB}', use_sudo=True)

    # Step 4: Upload files via SFTP
    print("[4] Uploading files...")
    sftp = ssh.open_sftp()
    uploaded = 0
    for local_path, rel_path in files:
        remote_path = os.path.join(REMOTE_WEB, rel_path).replace('\\', '/')
        remote_dir = os.path.dirname(remote_path)
        # Create remote directories as needed
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            parts = remote_dir.split('/')
            for i in range(2, len(parts) + 1):
                d = '/'.join(parts[:i])
                try:
                    sftp.stat(d)
                except FileNotFoundError:
                    sftp.mkdir(d)
        sftp.put(local_path, remote_path)
        uploaded += 1
        if uploaded % 20 == 0:
            print(f"  uploaded {uploaded}/{len(files)}...")
    sftp.close()
    print(f"  uploaded {uploaded}/{len(files)} files complete")

    # Step 5: Set permissions
    print("[5] Setting permissions...")
    run_cmd(ssh, f'chown -R www-data:www-data {REMOTE_WEB}', use_sudo=True)
    run_cmd(ssh, f'chmod -R 755 {REMOTE_WEB}', use_sudo=True)

    # Step 6: Configure Nginx
    print("[6] Configuring Nginx for port 3000...")
    nginx_conf = """server {
    listen 3000;
    server_name 172.20.0.139;

    root /var/www/oa-web;
    index index.html;

    # SPA fallback - all routes to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to Laravel backend
    location /api {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}"""

    # Write nginx config
    sftp = ssh.open_sftp()
    with sftp.open('/tmp/oa-web.conf', 'w') as f:
        f.write(nginx_conf)
    sftp.close()

    run_cmd(ssh, 'cp /tmp/oa-web.conf /etc/nginx/sites-available/oa-web.conf', use_sudo=True)
    run_cmd(ssh, 'ln -sf /etc/nginx/sites-available/oa-web.conf /etc/nginx/sites-enabled/oa-web.conf', use_sudo=True)

    # Step 7: Test and reload Nginx
    print("[7] Testing Nginx config...")
    out, err = run_cmd(ssh, 'nginx -t 2>&1', use_sudo=True)
    print(f"  nginx -t: {out} {err}")

    run_cmd(ssh, 'systemctl reload nginx', use_sudo=True)
    print("  Nginx reloaded")

    # Step 8: Verify
    print("[8] Verifying...")
    out, err = run_cmd(ssh, f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:3000/')
    print(f"  Frontend HTTP status: {out}")

    out, err = run_cmd(ssh, f'curl -s -o /dev/null -w "%{{http_code}}" http://127.0.0.1:3000/api/auth/login')
    print(f"  API proxy HTTP status: {out}")

    # List files
    out, err = run_cmd(ssh, f'ls -la {REMOTE_WEB}/')
    print(f"  Remote files: {out}")

    ssh.close()
    print(f"\n Done! Frontend deployed to http://{HOST}:3000")

if __name__ == '__main__':
    main()
