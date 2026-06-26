#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
117 阶段二 V2：PHP 8.5 + Composer + PG 18 + Node 22 + Nginx + Redis
全走 Ubuntu 26.04 官方源，不加第三方 PPA。
"""
import sys, time, posixpath
import paramiko

HOST = "192.168.3.117"
USER = "nbcy"
KEY  = posixpath.expanduser("~/.ssh/id_rsa")

def log(m, lvl="INFO"): print(f"[{lvl}] {m}", flush=True)

def sh_run(cli, cmd, timeout=300, check=True):
    log(f"  $ {cmd[:180]}{'...' if len(cmd) > 180 else ''}")
    sin, sout, serr = cli.exec_command(cmd, timeout=timeout)
    rc = sout.channel.recv_exit_status()
    out = (sout.read() or b"").decode("utf-8", "replace")
    err = (serr.read() or b"").decode("utf-8", "replace")
    tail = (out + err).strip().splitlines()[-30:]
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

    # ===== 1) PHP 8.5 + 扩展 =====
    log("=== 1) PHP 8.5 + 扩展 ===")
    # json/tokenizer/fileinfo 是 PHP 8.5 核心，不需要单独包
    # dom/simplexml/xsl 都在 php8.5-xml 里
    PHP_EXTS = [
        "php8.5-fpm", "php8.5-cli", "php8.5-common",
        "php8.5-pgsql", "php8.5-redis",
        "php8.5-bcmath", "php8.5-gd", "php8.5-zip",
        "php8.5-intl", "php8.5-mbstring", "php8.5-curl",
        "php8.5-xml",
        "php8.5-sqlite3", "php8.5-readline",
    ]
    sh_run(cli, f"sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y {' '.join(PHP_EXTS)}", timeout=300)
    # opcache 单独试（可能已在 common 里）
    sh_run(cli, "sudo -n apt-get install -y php8.5-opcache 2>/dev/null || echo 'opcache in common'", check=False)
    sh_run(cli, "php -v | head -2")
    sh_run(cli, "php -m | sort | tr '\n' ' '")
    sh_run(cli, "sudo -n systemctl enable --now php8.5-fpm")
    sh_run(cli, "sudo -n systemctl is-active php8.5-fpm")

    # PHP 调优
    sh_run(cli, r"""sudo -n bash -c 'cat > /etc/php/8.5/fpm/conf.d/99-oa-tune.ini <<INI
memory_limit = 256M
upload_max_filesize = 50M
post_max_size = 50M
max_execution_time = 120
opcache.enable = 1
opcache.memory_consumption = 128
opcache.max_accelerated_files = 10000
opcache.revalidate_freq = 0
opcache.validate_timestamps = 1
INI'""")
    sh_run(cli, "sudo -n systemctl restart php8.5-fpm")

    # ===== 2) Composer =====
    log("=== 2) Composer 2.x ===")
    sh_run(cli, "curl -sS https://getcomposer.org/installer | sudo -n php -- --install-dir=/usr/local/bin --filename=composer", timeout=60)
    sh_run(cli, "composer --version")

    # ===== 3) PostgreSQL 18 =====
    log("=== 3) PostgreSQL 18 ===")
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-18 postgresql-client-18", timeout=300)
    sh_run(cli, "sudo -n systemctl enable --now postgresql")
    sh_run(cli, "sudo -n systemctl is-active postgresql")
    sh_run(cli, "sudo -n -u postgres psql -c 'SELECT version();' 2>&1 | head -2")

    # ===== 4) Node 22 LTS =====
    log("=== 4) Node 22 LTS + pnpm ===")
    sh_run(cli, "curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -n -E bash -", timeout=60)
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs", timeout=120)
    sh_run(cli, "node -v && npm -v")
    sh_run(cli, "sudo -n npm install -g pnpm", timeout=60)
    sh_run(cli, "pnpm -v")

    # ===== 5) Nginx + Redis =====
    log("=== 5) Nginx + Redis ===")
    sh_run(cli, "sudo -n DEBIAN_FRONTEND=noninteractive apt-get install -y nginx redis-server", timeout=120)
    sh_run(cli, "sudo -n systemctl enable --now nginx")
    sh_run(cli, "sudo -n systemctl enable --now redis-server")
    sh_run(cli, "sudo -n systemctl is-active nginx redis-server")
    sh_run(cli, "nginx -v 2>&1")
    sh_run(cli, "redis-cli ping")

    # ===== 6) 最终验证 =====
    log("=== 6) 全部版本汇总 ===")
    sh_run(cli, 'echo "PHP:      $(php -v | head -1)"')
    sh_run(cli, 'echo "Composer: $(composer --version | head -1)"')
    sh_run(cli, 'echo "PG:       $(sudo -n -u postgres psql -t -c "SHOW server_version;")"')
    sh_run(cli, 'echo "Node:     $(node -v)"')
    sh_run(cli, 'echo "pnpm:     $(pnpm -v)"')
    sh_run(cli, 'echo "Nginx:    $(nginx -v 2>&1)"')
    sh_run(cli, 'echo "Redis:    $(redis-cli info server | grep redis_version)"')
    sh_run(cli, "systemctl is-active php8.5-fpm postgresql nginx redis-server")

    cli.close()
    log("阶段二全部完成 🎉")

if __name__ == "__main__":
    main()
