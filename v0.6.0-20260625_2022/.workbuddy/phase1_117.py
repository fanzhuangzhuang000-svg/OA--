#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
117 阶段一收尾：时区/chrony/apt upgrade/基础工具/ufw/fail2ban
全程 sudo 免密（已配），失败立即停。
"""
import sys, time, posixpath
import paramiko

HOST = "192.168.3.117"
USER = "nbcy"
KEY  = posixpath.expanduser("~/.ssh/id_rsa")

def log(m, lvl="INFO"): print(f"[{lvl}] {m}", flush=True)

def sh_run(cli, cmd, timeout=120, check=True):
    """exec_command 跑一条，输出末尾 800 字"""
    log(f"  $ {cmd[:200]}{'...' if len(cmd) > 200 else ''}")
    sin, sout, serr = cli.exec_command(cmd, timeout=timeout)
    rc = sout.channel.recv_exit_status()
    out = (sout.read() or b"").decode("utf-8", "replace")
    err = (serr.read() or b"").decode("utf-8", "replace")
    # 关键输出（错误/结尾）
    tail = (out + err).strip().splitlines()[-25:]
    for line in tail:
        log(f"    {line}")
    if check and rc != 0:
        log(f"  rc={rc} 失败", "FATAL"); sys.exit(1)
    return rc, out, err

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(KEY)
    cli.connect(HOST, 22, USER, pkey=pkey, timeout=10, allow_agent=False, look_for_keys=False)
    log("免密 SSH ✓")

    # 1) 时区 + chrony
    log("=== 1) 时区+chrony ===")
    sh_run(cli, "sudo -n timedatectl set-timezone Asia/Shanghai")
    sh_run(cli, "sudo -n timedatectl set-ntp true")
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y chrony")
    # 配 NTP 服务器（cn.pool 优先 + 阿里云兜底）
    sh_run(cli, r"""sudo -n bash -c 'cat > /etc/chrony/chrony.conf <<CONF
# 悦悦 2026-06-24
pool cn.pool.ntp.org iburst maxsources 4
pool ntp.aliyun.com iburst maxsources 2
pool time.cloudflare.com iburst maxsources 2
makestep 1.0 3
rtcsync
logdir /var/log/chrony
CONF'""")
    sh_run(cli, "sudo -n systemctl enable --now chrony")
    sh_run(cli, "sudo -n timedatectl status | head -8")
    sh_run(cli, "sudo -n chronyc sources -v 2>&1 | head -20")

    # 2) apt update + upgrade
    log("=== 2) apt update/upgrade ===")
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get update -y", timeout=180)
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold'", timeout=600)
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get autoremove -y")

    # 3) 基础工具 + fail2ban
    log("=== 3) 基础工具+fail2ban ===")
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y curl wget git vim htop net-tools unzip rsync jq lsb-release ca-certificates apt-transport-https software-properties-common fail2ban", timeout=300)

    # fail2ban 配 ssh jail
    sh_run(cli, r"""sudo -n bash -c 'cat > /etc/fail2ban/jail.local <<JAIL
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = ssh
backend = systemd
JAIL'""")
    sh_run(cli, "sudo -n systemctl enable --now fail2ban")
    sh_run(cli, "sudo -n fail2ban-client status sshd")

    # 4) ufw 防火墙
    log("=== 4) ufw ===")
    sh_run(cli, "sudo -n ufw allow 22/tcp comment 'ssh'")
    sh_run(cli, "sudo -n ufw allow 80/tcp comment 'http'")
    sh_run(cli, "sudo -n ufw allow 443/tcp comment 'https'")
    sh_run(cli, "sudo -n ufw --force enable")
    sh_run(cli, "sudo -n ufw status verbose")

    # 5) 收尾验证
    log("=== 5) 验证 ===")
    sh_run(cli, "date")
    sh_run(cli, "timedatectl | head -6")
    sh_run(cli, "systemctl is-active ssh fail2ban chrony ufw 2>&1 || true")
    sh_run(cli, "uptime; uname -r")

    cli.close()
    log("阶段一全部完成 🎉")

if __name__ == "__main__":
    main()
