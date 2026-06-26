#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本地公钥推到 192.168.3.117（密码 admin123），实现免密登录。
1) 密码连一次，探一下服务器 (uname / whoami)
2) 拼 authorized_keys（避免重复）
3) 写回服务器并修权限
4) 关掉连接，再用 key 重连验证
"""
import os, sys, posixpath
import paramiko

HOST = "192.168.3.117"
PORT = 22
USER = "nbcy"
PASS = "admin123"
PUB_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")

def log(msg, lvl="INFO"):
    print(f"[{lvl}] {msg}", flush=True)

def main():
    if not os.path.isfile(PUB_PATH):
        log(f"公钥不存在: {PUB_PATH}", "FATAL"); sys.exit(1)
    with open(PUB_PATH, "r", encoding="utf-8") as f:
        pub = f.read().strip()
    log(f"本地公钥长度: {len(pub)} chars")

    # 1) 密码连入
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        cli.connect(HOST, PORT, USER, PASS, timeout=10, allow_agent=False, look_for_keys=False)
    except Exception as e:
        log(f"密码 SSH 失败: {e}", "FATAL"); sys.exit(2)
    log("密码 SSH 成功 ✓")

    # 探环境
    for cmd in ["uname -a", "whoami", "id", "cat /etc/os-release | head -3"]:
        try:
            sin, sout, serr = cli.exec_command(cmd, timeout=8)
            out = (sout.read() or b"").decode("utf-8", "replace").strip()
            err = (serr.read() or b"").decode("utf-8", "replace").strip()
            log(f"  $ {cmd}\n    {out or err}")
        except Exception as e:
            log(f"  $ {cmd} 失败: {e}", "WARN")

    # 2) 检查 sshd 是否允许公钥登录 + authorized_keys 现状
    checks = [
        "mkdir -p ~/.ssh && chmod 700 ~/.ssh",
        "touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys",
    ]
    for c in checks:
        cli.exec_command(c, timeout=8)

    # 读现有 authorized_keys
    sin, sout, serr = cli.exec_command("cat ~/.ssh/authorized_keys", timeout=8)
    existing = (sout.read() or b"").decode("utf-8", "replace")
    if pub in existing:
        log("公钥已在 authorized_keys 中，跳过追加")
    else:
        # 用 sftp 写最稳
        sftp = cli.open_sftp()
        try:
            with sftp.open(".ssh/authorized_keys", "a") as f:
                f.write(pub + "\n")
            log("公钥已追加到 authorized_keys ✓")
        except Exception as e:
            log(f"sftp 追加失败，改用 heredoc: {e}", "WARN")
            cmd = f"printf '%s\\n' {pub!r} >> ~/.ssh/authorized_keys"
            cli.exec_command(cmd, timeout=8)
        finally:
            sftp.close()

    # 3) 修权限 + 关 PasswordAuthentication 视情况
    for c in [
        "chmod 700 ~/.ssh",
        "chmod 600 ~/.ssh/authorized_keys",
        "ls -la ~/.ssh/",
    ]:
        sin, sout, serr = cli.exec_command(c, timeout=8)
        out = (sout.read() or b"").decode("utf-8", "replace").strip()
        if out: log(f"  $ {c}\n{out}")

    cli.close()
    log("密码连接关闭，下面用 key 验证免密")

    # 4) 用 key 重连验证
    pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"))
    cli2 = paramiko.SSHClient()
    cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        cli2.connect(HOST, PORT, USER, pkey=pkey, timeout=10, allow_agent=False, look_for_keys=False)
        sin, sout, serr = cli2.exec_command("whoami && hostname && date", timeout=8)
        out = (sout.read() or b"").decode("utf-8", "replace").strip()
        log(f"免密 SSH 成功 ✓\n  {out}")
        cli2.close()
    except Exception as e:
        log(f"免密 SSH 失败: {e}", "FATAL"); sys.exit(3)

if __name__ == "__main__":
    main()
