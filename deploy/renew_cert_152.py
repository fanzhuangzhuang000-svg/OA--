#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 152 服务器部署 HTTPS - 续期专用(oa.afjsw.cn)"""
import os, sys
from deploy_credentials import get_ssh_credentials_152, connect_ssh, load_credentials

CERT_LOCAL_DIR = r'D:\work\website\OA\.workbuddy\cert_staging\oa.afjsw.cn_nginx'
CERT_REMOTE_DIR = '/etc/nginx/ssl/oa.afjsw.cn'

def run(ssh, cmd, check=True, sudo=False):
    if sudo and not cmd.startswith('sudo'):
        cmd = f'sudo {cmd}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors='ignore')
    err = stderr.read().decode(errors='ignore')
    if check and err.strip():
        print(f'[STDERR] {err.strip()[:200]}')
    return out

def main():
    creds = get_ssh_credentials_152()
    ssh = connect_ssh(creds)

    print('=== 1) 备份现有证书和配置 ===')
    run(ssh, 'sudo mkdir -p /etc/nginx/ssl/oa.afjsw.cn.bak.$(date +%Y%m%d_%H%M%S) || true')
    run(ssh, 'sudo cp -r /etc/nginx/ssl/afjsw.cn/* /etc/nginx/ssl/afjsw.cn.bak.$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true')
    run(ssh, 'sudo cp /etc/nginx/sites-available/oa /etc/nginx/sites-available/oa.bak.$(date +%Y%m%d_%H%M%S)')

    print('=== 2) 上传新证书到 /etc/nginx/ssl/oa.afjsw.cn/ ===')
    run(ssh, 'sudo mkdir -p /etc/nginx/ssl/oa.afjsw.cn')
    run(ssh, 'sudo chown ubuntu:ubuntu /etc/nginx/ssl/oa.afjsw.cn')
    sftp = ssh.open_sftp()
    for f in os.listdir(CERT_LOCAL_DIR):
        local = os.path.join(CERT_LOCAL_DIR, f)
        remote = f'{CERT_REMOTE_DIR}/{f}'
        print(f'  put {f} -> {remote}')
        sftp.put(local, remote)
    sftp.close()
    run(ssh, f'sudo chmod 600 {CERT_REMOTE_DIR}/oa.afjsw.cn.key')
    run(ssh, f'sudo chmod 644 {CERT_REMOTE_DIR}/oa.afjsw.cn_bundle.crt {CERT_REMOTE_DIR}/oa.afjsw.cn_bundle.pem')
    print(run(ssh, f'ls -la {CERT_REMOTE_DIR}/'))

    print('=== 3) 校验 key/crt modulus 一致 ===')
    key_mod = run(ssh, f'sudo openssl rsa -in {CERT_REMOTE_DIR}/oa.afjsw.cn.key -noout -modulus 2>&1 | head -c 100')
    crt_mod = run(ssh, f'sudo openssl x509 -in {CERT_REMOTE_DIR}/oa.afjsw.cn_bundle.crt -noout -modulus 2>&1 | head -c 100')
    print('  key mod:', key_mod)
    print('  crt mod:', crt_mod)
    if key_mod.split('=', 1)[1] != crt_mod.split('=', 1)[1]:
        print('!! key 与证书不匹配!中止')
        sys.exit(1)
    print('  ✅ key/crt 配对一致')

    print('=== 4) 写新 oa 配置(证书名换成 oa.afjsw.cn,server_name 也改) ===')
    oa_https = '''# HTTP -> HTTPS 重定向(只对 oa.afjsw.cn)
server {
    listen 80;
    server_name oa.afjsw.cn;
    return 301 https://$host$request_uri;
}

# HTTPS 主站点
server {
    listen 443 ssl http2;
    server_name oa.afjsw.cn;

    ssl_certificate     /etc/nginx/ssl/oa.afjsw.cn/oa.afjsw.cn_bundle.crt;
    ssl_certificate_key /etc/nginx/ssl/oa.afjsw.cn/oa.afjsw.cn.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    root /var/www/oa-web;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Expires "0" always;
    }

    # API + health
    location ~ ^/(api|up)(/.*)?$ {
        root /var/www/oa-api/public;
        try_files $uri /index.php =404;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_split_path_info ^(.+\\\\.php)(/.+)$;
        fastcgi_index index.php;
        include fastcgi.conf;
        fastcgi_param SCRIPT_FILENAME $document_root/index.php;
        fastcgi_param SCRIPT_NAME /index.php;
    }

    # 静态资源
    location ~* \\\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        try_files $uri $uri/ /index.html;
        expires 7d;
        access_log off;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
}
'''
    tmp = '/tmp/oa-https-new.conf'
    sftp = ssh.open_sftp()
    sftp.open(tmp, 'w').write(oa_https)
    sftp.close()
    run(ssh, f'sudo cp {tmp} /etc/nginx/sites-available/oa')
    run(ssh, 'sudo chown root:root /etc/nginx/sites-available/oa')
    run(ssh, f'sudo rm {tmp}')

    print('=== 5) nginx -t ===')
    out = run(ssh, 'sudo nginx -t 2>&1', check=False)
    print(out)
    if 'syntax is ok' not in out:
        print('!! nginx 配置测试失败,中止')
        sys.exit(1)

    print('=== 6) reload nginx ===')
    run(ssh, 'sudo systemctl reload nginx')

    print('=== 7) 验证 ===')
    print('--- http (期望 301) ---')
    print(run(ssh, 'curl -sI http://oa.afjsw.cn/ | head -5', check=False))
    print('--- https (期望 200) ---')
    print(run(ssh, 'curl -skI https://oa.afjsw.cn/ | head -5', check=False))
    print('--- 当前证书信息 ---')
    print(run(ssh, 'echo | openssl s_client -connect oa.afjsw.cn:443 -servername oa.afjsw.cn 2>/dev/null | openssl x509 -noout -subject -dates', check=False))
    print('--- API 仍 OK ---')
    print(run(ssh, 'curl -sk -X POST -H "Content-Type: application/json" -d "{\\"username\\":\\"admin\\",\\"password\\":\\"admin123\\"}" https://oa.afjsw.cn/api/auth/login | head -c 200', check=False))

    ssh.close()
    print('\n✅ 证书已更新到 oa.afjsw.cn')

if __name__ == '__main__':
    main()
