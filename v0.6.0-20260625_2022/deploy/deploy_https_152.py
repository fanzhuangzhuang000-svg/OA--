#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 152 服务器部署 HTTPS"""
import paramiko, os, sys

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'

CERT_LOCAL_DIR = r'D:\work\website\OA\.workbuddy\cert_staging\www.afjsw.cn_nginx'
CERT_REMOTE_DIR = '/etc/nginx/ssl/afjsw.cn'

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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PWD, timeout=15)

    print('=== 1) 备份现有配置 ===')
    run(ssh, 'sudo cp /etc/nginx/sites-available/oa /etc/nginx/sites-available/oa.bak.https-pre')
    run(ssh, 'sudo cp /etc/nginx/sites-available/oa-api /etc/nginx/sites-available/oa-api.bak.https-pre')
    print(run(ssh, 'ls -la /etc/nginx/sites-available/'))

    print('=== 2) 上传证书到 /etc/nginx/ssl/afjsw.cn/ ===')
    # 临时目录给 ubuntu 用户写
    run(ssh, 'sudo mkdir -p /etc/nginx/ssl/afjsw.cn && sudo chown ubuntu:ubuntu /etc/nginx/ssl/afjsw.cn')
    sftp = ssh.open_sftp()
    for f in os.listdir(CERT_LOCAL_DIR):
        local = os.path.join(CERT_LOCAL_DIR, f)
        remote = f'/etc/nginx/ssl/afjsw.cn/{f}'
        print(f'  put {f} -> {remote}')
        sftp.put(local, remote)
    sftp.close()
    # 收紧权限
    run(ssh, 'sudo chmod 600 /etc/nginx/ssl/afjsw.cn/www.afjsw.cn.key')
    run(ssh, 'sudo chmod 644 /etc/nginx/ssl/afjsw.cn/www.afjsw.cn_bundle.crt /etc/nginx/ssl/afjsw.cn/www.afjsw.cn_bundle.pem')
    print(run(ssh, 'ls -la /etc/nginx/ssl/afjsw.cn/'))

    print('=== 3) 校验证书可读 ===')
    print(run(ssh, 'sudo openssl x509 -in /etc/nginx/ssl/afjsw.cn/www.afjsw.cn_bundle.crt -noout -subject -dates'))

    print('=== 4) 写新的 oa 配置(同时承载 http 重定向 + https) ===')
    oa_https = '''# HTTP -> HTTPS 重定向(只对域名)
server {
    listen 80;
    server_name www.afjsw.cn afjsw.cn;
    return 301 https://$host$request_uri;
}

# HTTPS 主站点
server {
    listen 443 ssl http2;
    server_name www.afjsw.cn afjsw.cn;

    ssl_certificate     /etc/nginx/ssl/afjsw.cn/www.afjsw.cn_bundle.crt;
    ssl_certificate_key /etc/nginx/ssl/afjsw.cn/www.afjsw.cn.key;

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
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_index index.php;
        include fastcgi.conf;
        fastcgi_param SCRIPT_FILENAME $document_root/index.php;
        fastcgi_param SCRIPT_NAME /index.php;
    }

    # 静态资源
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        try_files $uri $uri/ /index.html;
        expires 7d;
        access_log off;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
}
'''
    # 临时文件
    tmp = '/tmp/oa-https.conf'
    sftp = ssh.open_sftp()
    with sftp.open(tmp, 'w') as f:
        f.write(oa_https)
    sftp.close()
    run(ssh, f'sudo cp {tmp} /etc/nginx/sites-available/oa && sudo chown root:root /etc/nginx/sites-available/oa && sudo rm {tmp}')
    print('  oa 配置已写入')

    print('=== 5) 修改 oa-api(让 IP 访问也走 oa,避免重复 server 块告警) ===')
    print('  保留现有 oa-api(IP 用 80)不变,以避开 conflicting server name 告警')

    print('=== 6) nginx -t 测试 ===')
    out = run(ssh, 'sudo nginx -t 2>&1', check=False)
    print(out)
    if 'syntax is ok' not in out:
        print('!! nginx 配置测试失败,中止 reload')
        sys.exit(1)

    print('=== 7) reload nginx ===')
    run(ssh, 'sudo systemctl reload nginx')
    print(run(ssh, 'sudo systemctl status nginx --no-pager | head -5'))

    print('=== 8) 验证 HTTPS ===')
    print('--- http (预期 301) ---')
    print(run(ssh, 'curl -sI http://www.afjsw.cn/ | head -5', check=False))
    print('--- https (预期 200) ---')
    print(run(ssh, 'curl -skI https://www.afjsw.cn/ | head -10', check=False))
    print('--- https + /api (预期 200/302) ---')
    print(run(ssh, 'curl -skI https://www.afjsw.cn/api | head -8', check=False))

    ssh.close()
    print('\\nALL DONE')

if __name__ == '__main__':
    main()
