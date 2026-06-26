#!/usr/bin/env python3
"""
服务器端 git 仓库初始化与版本对齐
- /var/www/oa-api  init git (www-data 拥有 → sudo tee)
- /var/www/oa-web  init git (nbcy 拥有)
- 提交"现场版本" + 标签
"""
import os
import sys
import paramiko

HOST = "172.20.0.139"
USER = "nbcy"
PASSWORD = "admin123"
PORT = 22

REMOTE_PROJECTS = [
    {
        "path": "/var/www/oa-api",
        "tag": "v0.3.0-api",
        "name": "Laravel API 现场快照",
        "owner": "www-data",
    },
    {
        "path": "/var/www/oa-web",
        "tag": "v0.3.0-web",
        "name": "Vite 部署产物现场快照",
        "owner": "nbcy",
    },
]


def run_ssh(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    rc = so.channel.recv_exit_status()
    return rc, so.read().decode("utf-8", "replace"), se.read().decode("utf-8", "replace")


def write_with_sudo(ssh, path, content):
    """SFTP 写 nbcy 可写的 tmp，然后 sudo -u <owner> cp 到 path"""
    tmp = f"/tmp/.tmp_git_init_{os.getpid()}_{int(time.time()*1000)}"
    sftp = ssh.open_sftp()
    try:
        with sftp.open(tmp, "w") as f:
            f.write(content)
    finally:
        sftp.close()

    # 用 cat | sudo tee（避免 heredoc 转义）
    # 简单做法：先 scp 到 /tmp/<owner> 可写的位置，然后 sudo cp
    rc, out, err = run_ssh(ssh, f"cat '{tmp}' | sudo -S tee '{path}' >/dev/null 2>&1 && echo OK", timeout=10)
    if rc != 0 or "OK" not in out:
        # 改用直接 sftp + sudo 链
        rc, out, err = run_ssh(ssh, f"sudo -n chown nbcy:nbcy '{path}' 2>&1; echo RC={rc}", timeout=10)
        sftp = ssh.open_sftp()
        try:
            with sftp.open(path, "w") as f:
                f.write(content)
        finally:
            sftp.close()
        run_ssh(ssh, f"sudo -n chown {REMOTE_PROJECTS[0]['owner']}:{REMOTE_PROJECTS[0]['owner']} '{path}' 2>&1", timeout=10)
    run_ssh(ssh, f"rm -f '{tmp}'", timeout=5)


import time


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, PORT, USER, PASSWORD, timeout=15)

    # global config（给 nbcy）
    run_ssh(ssh, "git config --global user.email 'senior-dev@oa.local' && git config --global user.name 'Senior Developer' && git config --global init.defaultBranch main && git config --global core.autocrlf false")
    # 给 www-data 也配一份（用 sudo -u www-data 写 git config）
    run_ssh(ssh, "sudo -u www-data git config --global user.email 'senior-dev@oa.local' 2>&1; sudo -u www-data git config --global user.name 'Senior Developer' 2>&1; sudo -u www-data git config --global init.defaultBranch main 2>&1; sudo -u www-data git config --global core.autocrlf false 2>&1; sudo -u www-data git config --global safe.directory '*' 2>&1")
    print("[1/3] global git config OK (nbcy + www-data)\n")

    # 写 .gitignore 内容
    GI = """# Laravel storage 运行时
storage/logs/*
storage/framework/cache/*
storage/framework/sessions/*
storage/framework/views/*
storage/framework/testing/*
public/build/
public/hot/
public/storage/
# 依赖
vendor/
node_modules/
# 环境
.env
.env.backup
.phpunit.result.cache
.phpunit.cache
"""

    for proj in REMOTE_PROJECTS:
        path = proj["path"]
        tag = proj["tag"]
        name = proj["name"]
        owner = proj["owner"]
        print(f"[2/3] {name} ({path}, owned by {owner})")

        # 检查是否已 init
        rc, out, _ = run_ssh(ssh, f"cd {path} && test -d .git && echo HAS || echo NO")
        if "HAS" in out:
            print(f"  已是 git 仓库，跳过 init")
            rc, out, _ = run_ssh(ssh, f"cd {path} && git log --oneline -1 && git tag -l '{tag}*'")
            print(f"  HEAD: {out.strip().replace(chr(10), ' | ')}")
            continue

        # 写 .gitignore
        run_ssh(ssh, f"cat > /tmp/.gitignore.tmp <<'GIEOF'\n{GI}GIEOF", timeout=10)
        if owner == "www-data":
            rc, out, err = run_ssh(ssh, f"sudo cp /tmp/.gitignore.tmp {path}/.gitignore && sudo chown www-data:www-data {path}/.gitignore", timeout=10)
        else:
            rc, out, err = run_ssh(ssh, f"cp /tmp/.gitignore.tmp {path}/.gitignore", timeout=10)
        if rc != 0:
            print(f"  ! 写 .gitignore 失败: {err.strip()[:200]}")
            continue
        run_ssh(ssh, "rm -f /tmp/.gitignore.tmp", timeout=5)

        # 占位 gitignore in storage/
        for sub in ["storage/logs", "storage/framework/cache", "storage/framework/sessions", "storage/framework/views"]:
            run_ssh(ssh, f"test -d {path}/{sub}", timeout=5)  # exit code 0/1 不重要
            placeholder = "*\n!.gitignore\n"
            run_ssh(ssh, f"printf '*\\n!.gitignore\\n' > /tmp/.gi.tmp", timeout=5)
            if owner == "www-data":
                run_ssh(ssh, f"test -d {path}/{sub} && sudo cp /tmp/.gi.tmp {path}/{sub}/.gitignore && sudo chown www-data:www-data {path}/{sub}/.gitignore", timeout=10)
            else:
                run_ssh(ssh, f"test -d {path}/{sub} && cp /tmp/.gi.tmp {path}/{sub}/.gitignore", timeout=10)
        run_ssh(ssh, "rm -f /tmp/.gi.tmp", timeout=5)

        # 用 sudo -u www-data 执行 git 动作（API 是 www-data 拥有）
        if owner == "www-data":
            git_prefix = f"sudo -u www-data"
        else:
            git_prefix = ""

        for c in [
            f"cd {path} && {git_prefix} git init -b main 2>&1 | tail -2",
            f"cd {path} && {git_prefix} git add -A 2>&1 | tail -3",
            f"cd {path} && {git_prefix} git -c core.fileMode=false commit -m '{tag} server snapshot' 2>&1 | tail -3",
            f"cd {path} && {git_prefix} git tag {tag}",
        ]:
            rc, out, err = run_ssh(ssh, c, timeout=60)
            print("  ", out.strip()[:300])
        print(f"  ✓ {tag} 已建\n")

    # 验证
    print("[3/3] 验证")
    for proj in REMOTE_PROJECTS:
        rc, out, _ = run_ssh(ssh, f"cd {proj['path']} && git log --oneline -1 && echo '  tag:' && git tag -l 'v0.3.0*'")
        print(f"  {proj['path']}:")
        print("    " + out.strip().replace("\n", "\n    "))

    ssh.close()


if __name__ == "__main__":
    main()
