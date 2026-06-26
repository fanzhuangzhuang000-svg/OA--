#!/usr/bin/env python3
"""
安防运维OA系统 - 统一部署入口

替代前任遗留的 80+ 个 fix_*/step*/deploy_v* 脚本。

子命令:
  web           部署前端 (调用 ../.workbuddy/deploy_web.py)
  api           部署后端 (scp + composer install + 缓存清理)
  full          全栈部署 (web + api)
  status        服务器状态 (PHP/nginx/MySQL/磁盘/服务进程)
  health        健康检查 (调用 ../.workbuddy/regression.py)
  backup        全量备份 (调用 ../.workbuddy/backup_full.py)
  shell         SSH 登录服务器 (交互式)

用法:
  python deploy.py web
  python deploy.py full
  python deploy.py status
  python deploy.py health
  python deploy.py backup v0.3.2
  python deploy.py shell
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = ROOT / ".workbuddy"

# 颜色
G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"; B = "\033[94m"; N = "\033[0m"


def header(s):
    print(f"\n{B}{'=' * 60}{N}")
    print(f"{B}  {s}{N}")
    print(f"{B}{'=' * 60}{N}\n")


def run_external(name, *args):
    """调 .workbuddy 里的脚本"""
    header(f"→ 调 {name} {args}")
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode


def cmd_web(args):
    """前端部署: build + sftp"""
    return run_external("deploy_web.py")


def cmd_api(args):
    """后端部署: scp 源码 + composer install + migrate (可选) + 缓存清理"""
    print("API 部署建议流程:")
    print("  1) git 在服务器提交变更 → tag v0.x.y")
    print("  2) 在服务器: cd /var/www/oa-api && git pull  (尚未配 remote)")
    print("  3) composer install --no-dev")
    print("  4) php artisan migrate --force  (如改了 migration)")
    print("  5) php artisan route:clear / config:clear / cache:clear")
    print("  6) sudo systemctl reload php8.3-fpm")
    print()
    print("首次部署: sudo bash deploy_full.sh  (在服务器上跑)")
    return 0


def cmd_full(args):
    print(f"{Y}== 全栈部署 =={N}\n")
    rc = cmd_web([])
    if rc != 0:
        return rc
    print(f"\n{Y}前端 OK，接下来手动跑后端:{N}")
    cmd_api([])
    return 0


def cmd_status(args):
    return run_external("ssh.py",
                        "echo '=== 主机 ==='; uname -a",
                        "echo '=== CPU/RAM ==='; nproc; free -h | head -3",
                        "echo '=== 磁盘 ==='; df -h /var/www | tail -2",
                        "echo '=== 服务 ==='; systemctl is-active php8.3-fpm nginx mysql 2>&1",
                        "echo '=== 端口 ==='; ss -tln 2>/dev/null | grep -E ':(80|443|3000|3001|3306)' | head -10",
                        "echo '=== 进程 ==='; ps -ef 2>/dev/null | grep -E 'php-fpm|nginx|mysql' | grep -v grep | head -10",
                        "echo '=== /var/www ==='; du -sh /var/www/* 2>/dev/null",
                        )


def cmd_health(args):
    return run_external("regression.py")


def cmd_backup(args):
    tag = args[0] if args else None
    return run_external("backup_full.py", *([tag] if tag else []))


def cmd_shell(args):
    """直接 SSH 进服务器"""
    from deploy_credentials import get_ssh_credentials_172, connect_ssh
    creds = get_ssh_credentials_172()
    ssh = connect_ssh(creds)
    chan = ssh.get_transport().open_session()
    chan.get_pty()
    chan.invoke_shell()
    print(f"{G}连上服务器，输入 'exit' 退出{N}")
    import select
    import os
    while True:
        if chan.recv_ready():
            sys.stdout.write(chan.recv(4096).decode("utf-8", "replace"))
            sys.stdout.flush()
        if chan.exit_status_ready():
            break
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            line = sys.stdin.readline()
            if not line:
                break
            chan.send(line.encode())
    ssh.close()
    return 0


CMDS = {
    "web": cmd_web,
    "api": cmd_api,
    "full": cmd_full,
    "status": cmd_status,
    "health": cmd_health,
    "backup": cmd_backup,
    "shell": cmd_shell,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print(f"可用子命令: {', '.join(CMDS.keys())}")
        return 0
    sub = sys.argv[1]
    if sub not in CMDS:
        print(f"{R}未知子命令: {sub}{N}")
        print(f"可用: {', '.join(CMDS.keys())}")
        return 1
    return CMDS[sub](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
