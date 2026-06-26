#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 192.168.3.117 ens32 从 DHCP 切到静态 IP（IP/网关/DNS 不变，禁 IPv6）。
1) sudo 备份原 netplan
2) 写新 yaml（v4 静态 + IPv6 关闭）
3) netplan try 超时回滚保护
4) 验证：ip addr / ip route / DNS / 外网 ping
"""
import sys, time, posixpath
import paramiko

HOST = "192.168.3.117"
USER = "nbcy"
KEY = posixpath.expanduser("~/.ssh/id_rsa")
BACKUP = "/root/00-installer-config.yaml.bak.{ts}"
NETPLAN = "/etc/netplan/00-installer-config.yaml"

NEW_YAML = """# Managed by 悦悦 / 2026-06-24
# 把 ens32 从 DHCP 切到静态，禁 IPv6，DNS 保持原 DHCP 下发值
network:
  version: 2
  renderer: networkd
  ethernets:
    ens32:
      dhcp4: false
      dhcp6: false
      accept-ra: false
      addresses:
        - 192.168.3.117/24
      routes:
        - to: default
          via: 192.168.3.1
      nameservers:
        addresses: [221.12.33.227, 114.114.114.114]
"""

def log(m, lvl="INFO"): print(f"[{lvl}] {m}", flush=True)

def ssh_exec(cli, cmd, timeout=10, sudo=False, get_output=True):
    if sudo and not cmd.startswith("sudo "):
        cmd = "sudo -n " + cmd
    sin, sout, serr = cli.exec_command(cmd, timeout=timeout)
    out = (sout.read() or b"").decode("utf-8", "replace")
    err = (serr.read() or b"").decode("utf-8", "replace")
    rc = sout.channel.recv_exit_status()
    if get_output and out.strip():
        log(f"  $ {cmd}\n{out.rstrip()}")
    if err.strip() and rc != 0:
        log(f"  $ {cmd}  (rc={rc})\n{err.rstrip()}", "WARN")
    return rc, out, err

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(KEY)
    cli.connect(HOST, 22, USER, pkey=pkey, timeout=10, allow_agent=False, look_for_keys=False)
    log("免密 SSH 成功 ✓")

    # 0) sudo 免密前置校验
    rc, _, _ = ssh_exec(cli, "sudo -n whoami", timeout=5)
    if rc != 0:
        log("sudo 不是 NOPASSWD，请先 1.5 节加免密", "FATAL"); sys.exit(1)
    log("sudo NOPASSWD ✓")

    # 1) 备份原文件
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = BACKUP.format(ts=ts)
    rc, _, _ = ssh_exec(cli, f"sudo -n cp -a {NETPLAN} {backup}", timeout=8)
    if rc != 0:
        log(f"备份失败 rc={rc}", "FATAL"); sys.exit(2)
    rc, out, _ = ssh_exec(cli, f"sudo -n ls -la {backup} {NETPLAN}", timeout=5)
    log(f"备份: {backup}")

    # 2) 写新配置（用 heredoc 走 stdin，避免引号转义）
    heredoc = f"cat > /tmp/00-installer-config.yaml.new <<'__EOF__'\n{NEW_YAML}__EOF__"
    rc, _, _ = ssh_exec(cli, heredoc, timeout=5)
    if rc != 0:
        log("写临时文件失败", "FATAL"); sys.exit(3)
    rc, _, _ = ssh_exec(cli,
        f"sudo -n install -m 600 /tmp/00-installer-config.yaml.new {NETPLAN} && sudo -n rm /tmp/00-installer-config.yaml.new",
        timeout=5)
    if rc != 0:
        log("覆盖 netplan 失败", "FATAL"); sys.exit(4)
    log(f"新配置已写入 {NETPLAN} ✓")

    # 3) netplan try (带 120s 自动回滚保护)
    log(">>> netplan try (120s 超时自动回滚)")
    chan = cli.get_transport().open_session(timeout=10)
    chan.settimeout(130)
    chan.exec_command("sudo -n netplan try --timeout 120")
    # 等用户/自动确认 — 我们直接 echo y 走默认
    time.sleep(2)
    try:
        chan.send("y\n")
    except Exception:
        pass
    # 等命令跑完
    end = time.time() + 125
    while time.time() < end:
        if chan.exit_status_ready():
            break
        time.sleep(1)
    rc = chan.recv_exit_status() if chan.exit_status_ready() else -1
    out = b""
    try:
        if chan.recv_ready():
            out += chan.recv(65535)
    except Exception:
        pass
    log(f"netplan try rc={rc}\n{out.decode('utf-8','replace').strip()}")
    if rc != 0:
        log("netplan try 失败，尝试 netplan apply 兜底", "WARN")
        rc2, _, _ = ssh_exec(cli, "sudo -n netplan apply", timeout=15)
        if rc2 != 0:
            log("netplan apply 也失败，SSH 通道可能已断 — 等大哥用备份恢复", "FATAL")
            sys.exit(5)

    # 4) 验证
    cli.close()
    time.sleep(2)
    cli2 = paramiko.SSHClient()
    cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        cli2.connect(HOST, 22, USER, pkey=pkey, timeout=10, allow_agent=False, look_for_keys=False)
    except Exception as e:
        log(f"重连失败（可能 IP 真的变了）: {e}", "FATAL"); sys.exit(6)
    log("重连成功 ✓")

    cmds = [
        "ip -br addr show ens32",
        "ip route show default",
        "ip -6 addr show ens32 | grep -v 'fe80\\|::1' || echo 'no global v6 (good)'",
        "cat /etc/resolv.conf",
        "resolvectl status ens32 2>/dev/null | grep -E 'DNS Servers|Current DNS'",
        "ping -c2 -W2 114.114.114.114",
        "ping -c2 -W2 221.12.33.227",
    ]
    for c in cmds:
        rc, out, _ = ssh_exec(cli2, c, timeout=10)
    cli2.close()
    log("全部完成 🎉")

if __name__ == "__main__":
    main()
