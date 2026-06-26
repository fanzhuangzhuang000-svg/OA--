#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配 nbcy sudo NOPASSWD — V3：用 sudo tee 避免重定向权限问题。
"""
import sys, os, base64, time, posixpath
import paramiko

HOST = "192.168.3.117"
USER = "nbcy"
PASS = "admin123"
KEY  = posixpath.expanduser("~/.ssh/id_rsa")
SUDOERS_D = "/etc/sudoers.d/nbcy"
LINE = "nbcy ALL=(ALL) NOPASSWD:ALL\n"

def log(m, lvl="INFO"): print(f"[{lvl}] {m}", flush=True)

def run_sudo(sh, cmd, timeout=12):
    sh.send(f"sudo -S -p 'SUDOPWD' {cmd}\n")
    end = time.time() + timeout
    buf = b""
    sent = False
    while time.time() < end:
        if sh.recv_ready():
            data = sh.recv(65535)
            buf += data
            if not sent and b"SUDOPWD" in buf:
                sh.send(PASS + "\n"); sent = True
        else:
            time.sleep(0.15)
        if sent and (b"\nnbcy@nbcy" in buf or b"command not found" in buf):
            time.sleep(0.3)
            if sh.recv_ready(): buf += sh.recv(65535)
            break
    return buf.decode("utf-8", "replace")

def main():
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(HOST, 22, USER, PASS, timeout=10, allow_agent=False, look_for_keys=False)
    log("密码 SSH 成功 ✓")
    sh = cli.invoke_shell(term="xterm", width=200, height=50)
    time.sleep(0.5)
    if sh.recv_ready(): sh.recv(65535)

    # 1) 准备 base64 内容（直接走 stdin 给 sudo tee，不走 shell 重定向）
    payload = base64.b64encode(LINE.encode()).decode()

    # 2) 用 sudo tee 写文件 —— 关键！重定向发生在 sudo 内部
    out = run_sudo(sh, f"bash -c \"echo {payload} | base64 -d | sudo -S -p 'SUDOPWD2' tee {SUDOERS_D} >/dev/null\"")
    log(f"  tee {SUDOERS_D}: {out.strip()[-200:] if out.strip() else '(no output)'}")

    out = run_sudo(sh, f"sudo -S -p 'SUDOPWD3' chmod 0440 {SUDOERS_D} && sudo -S -p 'SUDOPWD4' chown root:root {SUDOERS_D}")
    log(f"  chmod/chown: {out.strip()[-200:] if out.strip() else '(no output)'}")

    out = run_sudo(sh, f"sudo -S -p 'SUDOPWD5' visudo -c -f {SUDOERS_D}")
    log(f"  visudo -c: {out.strip()[-200:] if out.strip() else '(no output)'}")

    out = run_sudo(sh, f"sudo -S -p 'SUDOPWD6' cat {SUDOERS_D}")
    log(f"  文件内容: {out.strip()[-200:] if out.strip() else '(empty)'}")

    cli.close()

    # 3) 免密 sudo 验证
    cli2 = paramiko.SSHClient()
    cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(KEY)
    cli2.connect(HOST, 22, USER, pkey=pkey, timeout=10, allow_agent=False, look_for_keys=False)
    sin, sout, serr = cli2.exec_command("sudo -n whoami; sudo -n id; sudo -n ls -l " + SUDOERS_D, timeout=8)
    out = (sout.read() or b"").decode("utf-8","replace").strip()
    err = (serr.read() or b"").decode("utf-8","replace").strip()
    log(f"  免密 sudo 验证:\n{out or err}")
    cli2.close()

    if out and "root" in out and "nbcy" in out:
        log("sudo NOPASSWD 配通 ✓")
    else:
        log("sudo NOPASSWD 没配通，详看上", "FATAL"); sys.exit(1)

if __name__ == "__main__":
    main()
