#!/usr/bin/env python3
"""v3.9.0 — 新服务器一键部署 OA 系统
服务器: 152.136.115.121, ubuntu / Aa782997781., sudo 免密
目标: nginx + php8.3-fpm + PostgreSQL + oa-api + oa-web
"""
import paramiko, time, sys, os

HOST = '152.136.115.121'
USER = 'ubuntu'
PWD = 'Aa782997781.'
SUDO = "echo 'Aa782997781.' | sudo -S"  # 免密 sudo 也能用, 保险
# 实际上 sudo 是 NOPASSWD, 直接 sudo 即可
SUDO_DIRECT = 'sudo'

def ssh_exec(ssh, cmd, timeout=300, show=True):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    out = so.read().decode('utf-8', 'replace')
    err = se.read().decode('utf-8', 'replace')
    if show and (out.strip() or err.strip()):
        # 只显示有意义的输出
        for line in (out + err).strip().split('\n')[-8:]:
            if line.strip():
                print(f'    {line}')
    return out, err

def run_step(ssh, name, cmd, **kw):
    print(f'\n=== {name} ===')
    print(f'  $ {cmd[:100]}{"..." if len(cmd)>100 else ""}')
    out, err = ssh_exec(ssh, cmd, **kw)
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'[connect] {HOST} ...')
    ssh.connect(HOST, 22, USER, PWD, timeout=15)
    print('✅ connected')

    # 1. 装包
    run_step(ssh, '1.1 apt update', f'{SUDO_DIRECT} apt-get update -y -q', timeout=120)
    run_step(ssh, '1.2 apt install -y',
        f'{SUDO_DIRECT} DEBIAN_FRONTEND=noninteractive apt-get install -y -q '
        f'postgresql postgresql-contrib php8.3-fpm php8.3-cli php8.3-pgsql php8.3-mbstring '
        f'php8.3-xml php8.3-zip php8.3-curl php8.3-bcmath php8.3-intl '
        f'composer nginx unzip git rsync curl',
        timeout=600)
    # 2. 起服务
    run_step(ssh, '2.1 enable+start nginx', f'{SUDO_DIRECT} systemctl enable --now nginx')
    run_step(ssh, '2.2 enable+start php-fpm', f'{SUDO_DIRECT} systemctl enable --now php8.3-fpm')
    run_step(ssh, '2.3 enable+start postgresql', f'{SUDO_DIRECT} systemctl enable --now postgresql')

    # 3. 验证
    run_step(ssh, '3.1 versions',
        'php -v | head -1; psql --version; nginx -v 2>&1; composer --version 2>&1 | head -1')

    # 4. 监听端口
    run_step(ssh, '4.1 listening ports', f'{SUDO_DIRECT} ss -tln 2>&1 | grep -E \':(80|5432|9000)\'')

    ssh.close()
    print('\n✅ 阶段1完成')

if __name__ == '__main__':
    main()
