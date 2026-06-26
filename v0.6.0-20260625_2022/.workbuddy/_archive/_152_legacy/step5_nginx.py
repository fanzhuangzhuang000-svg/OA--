#!/usr/bin/env python3
"""v3.9.0 阶段5: 配 nginx + 上传 oa-web dist + 跑 fpm"""
import paramiko
import os
import posixpath

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = 'sudo'

NGINX_CONF = r'''server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name 152.136.115.121 _;

    root /var/www/oa-web;
    index index.html;

    # 前端 SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API → PHP-FPM
    location /api {
        try_files $uri /index.php$is_args$args;
    }
    location /up {
        try_files $uri /index.php$is_args$args;
    }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }

    # 静态资源 cache
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 7d;
        access_log off;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
'''

def ssh_exec(ssh, cmd, timeout=120, show_tail=10):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    if show_tail and (out or err):
        for line in (out+err).strip().split('\n')[-show_tail:]:
            if line.strip(): print(f'    {line}')
    return out, err

def sftp_mkdir_p(sftp, path):
    parts = path.strip('/').split('/')
    cur = ''
    for p in parts:
        cur = f'{cur}/{p}'
        try: sftp.stat(cur)
        except IOError:
            try: sftp.mkdir(cur)
            except IOError: pass

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    sftp = ssh.open_sftp()
    print('✅ connected')

    # 1. 上传 dist 到 /var/www/oa-web/
    print('\n=== 1. 上传 pc-web/dist → /var/www/oa-web/ ===')
    si, so, se = ssh.exec_command(f'{SUDO} mkdir -p /var/www/oa-web && {SUDO} chown -R ubuntu:ubuntu /var/www/oa-web 2>&1', timeout=10)
    print(so.read().decode('utf-8','replace').strip())
    LOCAL = r'D:\work\website\OA\pc-web\dist'
    REMOTE = '/var/www/oa-web'
    count = 0
    for root, dirs, files in os.walk(LOCAL):
        dirs[:] = [d for d in dirs if d not in ('.git',)]
        rel = os.path.relpath(root, LOCAL)
        remote_dir = REMOTE if rel == '.' else f'{REMOTE}/{rel.replace(chr(92), "/")}'
        sftp_mkdir_p(sftp, remote_dir)
        for fn in files:
            local = os.path.join(root, fn)
            remote = f'{remote_dir}/{fn}'
            sftp.put(local, remote)
            count += 1
    print(f'  上传 {count} 个文件')

    # 2. chown 给 www-data
    si, so, se = ssh.exec_command(f'{SUDO} chown -R www-data:www-data /var/www/oa-web 2>&1', timeout=10)
    print('  chown:', so.read().decode('utf-8','replace').strip())

    # 3. 写 nginx 配置
    print('\n=== 2. 写 nginx 配置 ===')
    si, so, se = ssh.exec_command(f'{SUDO} tee /etc/nginx/sites-available/oa > /dev/null << "NGINX_EOF"\n{NGINX_CONF}NGINX_EOF', timeout=10)
    # 上面的 tee in ssh 不靠谱, 用 sftp.put
    sftp_mkdir_p(sftp, '/tmp/nginx')
    with open(r'D:\work\website\OA\.workbuddy\newserver\oa-nginx.conf', 'w', encoding='utf-8') as f:
        f.write(NGINX_CONF)
    sftp.put(r'D:\work\website\OA\.workbuddy\newserver\oa-nginx.conf', '/tmp/nginx/oa-nginx.conf')
    si, so, se = ssh.exec_command(f'{SUDO} cp /tmp/nginx/oa-nginx.conf /etc/nginx/sites-available/oa && {SUDO} ln -sf /etc/nginx/sites-available/oa /etc/nginx/sites-enabled/oa && {SUDO} rm -f /etc/nginx/sites-enabled/default && echo OK', timeout=10)
    print(so.read().decode('utf-8','replace').strip()[:200])

    # 4. nginx config test
    print('\n=== 3. nginx config test ===')
    si, so, se = ssh.exec_command(f'{SUDO} nginx -t 2>&1', timeout=10)
    print(so.read().decode('utf-8','replace'))

    # 5. reload nginx
    print('\n=== 4. reload nginx ===')
    si, so, se = ssh.exec_command(f'{SUDO} systemctl reload nginx 2>&1', timeout=10)
    print(so.read().decode('utf-8','replace'))

    # 6. 启动 php-fpm (应该已经起来了)
    si, so, se = ssh.exec_command(f'{SUDO} systemctl status php8.3-fpm --no-pager 2>&1 | head -5', timeout=10)
    print('\n=== 5. php8.3-fpm 状态 ===')
    print(so.read().decode('utf-8','replace'))

    # 7. 验证 nginx
    print('\n=== 6. 验证 ===')
    si, so, se = ssh.exec_command("curl -sS -o /dev/null -w 'HTTP %{http_code}\\n' http://127.0.0.1/ 2>&1", timeout=10)
    print('首页:', so.read().decode('utf-8','replace').strip())
    si, so, se = ssh.exec_command("curl -sS -o /dev/null -w 'HTTP %{http_code}\\n' http://127.0.0.1/login 2>&1", timeout=10)
    print('login:', so.read().decode('utf-8','replace').strip())
    si, so, se = ssh.exec_command("curl -sS -w '\\nHTTP %{http_code}\\n' http://127.0.0.1/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}' 2>&1 | head -5", timeout=10)
    print('login API:', so.read().decode('utf-8','replace').strip()[:300])
    si, so, se = ssh.exec_command("curl -sS -w 'HTTP %{http_code}\\n' http://127.0.0.1/up 2>&1 | tail -3", timeout=10)
    print('health:', so.read().decode('utf-8','replace').strip())

    sftp.close()
    ssh.close()
    print('\n✅ 阶段5 完成')

if __name__ == '__main__':
    main()
