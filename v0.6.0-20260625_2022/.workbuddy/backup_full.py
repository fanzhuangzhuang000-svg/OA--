"""
全量备份到本地工作目录
- 服务器 /var/www/oa-api  →  backups/<tag>/pc-api/    (排除 vendor/ storage/logs/ storage/framework/cache+data / node_modules)
- 本地    pc-web/          →  backups/<tag>/pc-web/    (排除 node_modules/ dist/)
- 服务器 /var/www/oa-web  →  backups/<tag>/pc-web-build/  (线上构建产物，含 assets/index-*.js)
- 生成 backups/<tag>/MANIFEST.md
"""

import os
import sys
import shutil
import hashlib
import paramiko
import datetime as dt
from pathlib import Path

# ----- config -----
HOST = "172.20.0.139"
USER = "nbcy"
PASSWORD = "admin123"
PORT = 22
LOCAL_ROOT = Path(r"D:\work\website\OA")
BACKUPS_ROOT = LOCAL_ROOT / ".workbuddy" / "backups"
TAG = sys.argv[1] if len(sys.argv) > 1 else f"v0.3.0-{dt.datetime.now().strftime('%Y%m%d_%H%M')}"
DEST = BACKUPS_ROOT / TAG
DEST.mkdir(parents=True, exist_ok=True)

API_SRC = "/var/www/oa-api"
WEB_DEPLOYED_SRC = "/var/www/oa-web"
LOCAL_WEB_SRC = LOCAL_ROOT / "pc-web"

# 排除项（rsync-style 前缀匹配）
API_EXCLUDE_DIRS = {"vendor", "node_modules"}
API_EXCLUDE_DIR_PARTS = {"storage/logs", "storage/framework/cache", "storage/framework/sessions", "storage/framework/testing", "storage/framework/views", "storage/app/public"}
API_EXCLUDE_FILES = {".env"}  # 改用 .env.example 替代

LOCAL_WEB_EXCLUDE = {"node_modules", "dist"}


def md5_file(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sftp_walk_dir(sftp, remote_dir: str):
    """递归 yield (relpath, is_dir, size, full)

    关键：paramiko SFTP 的 listdir_attr 对深层目录不稳定，改用显式栈递归
    """
    remote_dir = remote_dir.rstrip("/")
    stack = [remote_dir]
    seen = set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        try:
            entries = sftp.listdir_attr(cur)
        except Exception as e:
            print(f"      ! 跳过 {cur}: {e}")
            continue
        for entry in entries:
            full = cur + "/" + entry.filename
            rel = full[len(remote_dir) + 1:]
            is_dir = entry.st_mode and (entry.st_mode & 0o170000) == 0o040000
            yield rel, is_dir, entry.st_size or 0, full
            if is_dir:
                stack.append(full)


def should_exclude_api(rel: str) -> bool:
    parts = rel.split("/")
    if parts[0] in API_EXCLUDE_DIRS:
        return True
    if "/".join(parts[:2]) in API_EXCLUDE_DIR_PARTS:
        return True
    if rel in API_EXCLUDE_FILES:
        return True
    return False


def backup_api(sftp, dest: Path) -> dict:
    print(f"[1/4] 同步服务器 API 源码 → {dest}")
    stats = {"files": 0, "dirs": 0, "bytes": 0, "skipped": 0, "excluded": []}
    for rel, is_dir, size, full in sftp_walk_dir(sftp, API_SRC):
        if should_exclude_api(rel):
            stats["excluded"].append(rel + ("/" if is_dir else ""))
            stats["skipped"] += 1
            continue
        target = dest / rel
        if is_dir:
            target.mkdir(parents=True, exist_ok=True)
            stats["dirs"] += 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                sftp.get(full, str(target))
                stats["files"] += 1
                stats["bytes"] += size
            except IOError as e:
                # 跳过无权限文件（如 .env 即使被排除也可能列出）
                print(f"      ! 跳过 {rel}: {e}")
                stats["skipped"] += 1
                continue
            if stats["files"] % 50 == 0:
                print(f"      …{stats['files']} files / {stats['bytes']/1024/1024:.1f} MB")
    # 兜底：用 .env.example 替代 .env
    env_example = dest / ".env.example"
    if not env_example.exists():
        env_example.write_text("# 由备份脚本生成：原 .env 已被排除以保护 DB 凭据\n"
                               "APP_NAME=Laravel\nAPP_ENV=production\nAPP_KEY=\nAPP_DEBUG=false\nAPP_URL=http://localhost\n"
                               "DB_CONNECTION=mysql\nDB_HOST=127.0.0.1\nDB_PORT=3306\nDB_DATABASE=oa_db\nDB_USERNAME=oa_user\nDB_PASSWORD=changeme\n",
                               encoding="utf-8")
    return stats


def backup_web_deployed(sftp, dest: Path) -> dict:
    print(f"[2/4] 同步服务器 部署产物 → {dest}")
    stats = {"files": 0, "dirs": 0, "bytes": 0, "skipped": 0}
    for rel, is_dir, size, full in sftp_walk_dir(sftp, WEB_DEPLOYED_SRC):
        target = dest / rel
        if is_dir:
            target.mkdir(parents=True, exist_ok=True)
            stats["dirs"] += 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                sftp.get(full, str(target))
                stats["files"] += 1
                stats["bytes"] += size
            except IOError as e:
                print(f"      ! 跳过 {rel}: {e}")
                stats["skipped"] += 1
    return stats


def backup_local_web(dest: Path) -> dict:
    print(f"[3/4] 复制本地 pc-web 源码 → {dest}")
    stats = {"files": 0, "dirs": 0, "bytes": 0, "skipped": 0}
    src = LOCAL_WEB_SRC
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        # prune
        dirs[:] = [d for d in dirs if d not in LOCAL_WEB_EXCLUDE]
        if rel != Path("."):
            for d in dirs:
                stats["skipped"] += 1  # 排除目录计数
        target_dir = dest / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        if rel != Path("."):
            stats["dirs"] += 1
        for f in files:
            sp = Path(root) / f
            tp = target_dir / f
            shutil.copy2(sp, tp)
            stats["files"] += 1
            stats["bytes"] += sp.stat().st_size
    return stats


def write_manifest(dest: Path, manifest: dict):
    print(f"[4/4] 写 MANIFEST.md")
    m = dest / "MANIFEST.md"
    lines = [
        f"# 备份清单 — {manifest['tag']}",
        "",
        f"- **备份时间** (本地): {manifest['local_time']}",
        f"- **服务器时间** (UTC): {manifest['server_time_utc']}",
        f"- **服务器**  : {HOST}",
        f"- **备份源**  : 服务器 `/var/www/oa-api` + `/var/www/oa-web` + 本地 `pc-web/`",
        "",
        "## 内容统计",
        "",
        "| 区块 | 来源 | 文件数 | 目录数 | 大小 | 排除项 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for name, s in manifest["sections"].items():
        excl = ", ".join(s.get("excluded", [])[:5])
        if len(s.get("excluded", [])) > 5:
            excl += f" … (+{len(s['excluded'])-5} more)"
        lines.append(f"| {name} | `{s['src']}` | {s['files']} | {s['dirs']} | {s['bytes']/1024/1024:.2f} MB | {excl or '—'} |")
    lines += [
        "",
        "## 排除规则（保护密钥与可重生成产物）",
        "",
        "- `pc-api/`:",
        "  - `vendor/` (composer 装回来即可)",
        "  - `node_modules/` (前端依赖)",
        "  - `storage/logs/`, `storage/framework/{cache,sessions,testing,views}/` (运行时缓存)",
        "  - `.env` 替换为 `.env.example`（含占位密码）",
        "- `pc-web/`: `node_modules/`, `dist/`（构建产物已另存到 `pc-web-build/`）",
        "",
        "## 还原指引",
        "",
        "```powershell",
        f"# 1. 还原 API（不含 vendor，需要 composer install）",
        f"xcopy /E /I /Y {dest.name}\\\\pc-api\\\\*  D:\\\\work\\\\website\\\\OA\\\\pc-api\\\\",
        "cd D:\\work\\website\\OA\\pc-api",
        "composer install",
        "cp .env.example .env  # 手动改 DB 凭据",
        "php artisan key:generate",
        "",
        f"# 2. 还原前端源码（不含 node_modules/dist）",
        f"xcopy /E /I /Y {dest.name}\\\\pc-web\\\\*  D:\\\\work\\\\website\\\\OA\\\\pc-web\\\\",
        "cd D:\\work\\website\\OA\\pc-web",
        "npm install",
        "npm run build   # 或直接用 pc-web-build/ 里的产物部署到 /var/www/oa-web",
        "",
        f"# 3. 部署前端到服务器（可选：直接用 pc-web-build/）",
        f"# 用 .workbuddy\\\\deploy_web.py 重新部署",
        "```",
        "",
        "## 本次已修复/已变更（决定快照价值的变更）",
        "",
        "1. 路由顺序修正：`projects/{id}/suppliers` 不再被 `{project}` 吞掉",
        "2. `ProjectContract::paymentNodes` 外键显式指定 `contract_id`",
        "3. 新增 `GET /api/projects/{id}/contracts` 与 `{id}/suppliers`",
        "4. 前端系统名称绑定 store（login / router / screen / index.html 全部改为可配置）",
        "5. 前端重新构建并部署到 /var/www/oa-web",
    ]
    m.write_text("\n".join(lines), encoding="utf-8")


def main():
    print(f"=== 全量备份 → {DEST} ===")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, PORT, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    # 拿服务器时间
    _, stdout, _ = ssh.exec_command("date '+%Y-%m-%d %H:%M:%S %Z'")
    server_time = stdout.read().decode().strip()

    api_dest = DEST / "pc-api"
    web_deployed_dest = DEST / "pc-web-build"
    web_local_dest = DEST / "pc-web"

    try:
        api_stats = backup_api(sftp, api_dest)
        web_dep_stats = backup_web_deployed(sftp, web_deployed_dest)
    finally:
        sftp.close()
        ssh.close()

    web_local_stats = backup_local_web(web_local_dest)

    manifest = {
        "tag": TAG,
        "local_time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z"),
        "server_time_utc": server_time,
        "sections": {
            "pc-api (服务器源码)": {"src": "/var/www/oa-api", "files": api_stats["files"], "dirs": api_stats["dirs"], "bytes": api_stats["bytes"], "excluded": api_stats["excluded"][:20]},
            "pc-web-build (服务器部署产物)": {"src": "/var/www/oa-web", "files": web_dep_stats["files"], "dirs": web_dep_stats["dirs"], "bytes": web_dep_stats["bytes"], "excluded": []},
            "pc-web (本地源码)": {"src": "./pc-web", "files": web_local_stats["files"], "dirs": web_local_stats["dirs"], "bytes": web_local_stats["bytes"], "excluded": list(LOCAL_WEB_EXCLUDE)},
        },
    }
    write_manifest(DEST, manifest)

    print()
    print("=== 备份完成 ===")
    print(f"路径: {DEST}")
    for name, s in manifest["sections"].items():
        print(f"  {name:40s} {s['files']:5d} files  {s['bytes']/1024/1024:7.2f} MB")


if __name__ == "__main__":
    main()
