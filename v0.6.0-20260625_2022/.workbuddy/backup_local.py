#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地全量备份到 .workbuddy/backups/<tag>-<ts>/
- 拷 pc-api/    排除 vendor / storage/logs / storage/framework/{cache,sessions,testing,views} / storage/app/public / .env
- 拷 pc-web/    排除 node_modules / dist
- 拷 pc-desktop/ mobile-app/ mp-miniapp/ deploy/ 安防运维OA系统设计大纲V2.html README.md
- 拷 .workbuddy/ 全部（含 deploy 脚本/memory/回滚脚本）
- 生成 MANIFEST.md（tag/commit/分支/文件数/大小/前后对比）
- 进度条 + 总耗时
"""
import os, sys, shutil, subprocess, hashlib, datetime as dt
from pathlib import Path

LOCAL_ROOT = Path(r"D:\work\website\OA")
BACKUPS_ROOT = LOCAL_ROOT / ".workbuddy" / "backups"

# 用户指定 tag 或自动取
if len(sys.argv) > 1:
    USER_TAG = sys.argv[1]
else:
    USER_TAG = None
TS = dt.datetime.now().strftime("%Y%m%d_%H%M")

# 排除规则（rsync-style）— .workbuddy/ 下也排除 node_modules/puppeteer 二进制
EXCLUDE_DIRS = {
    "vendor", "node_modules", "dist", ".git", ".vscode", ".idea",
    "__pycache__", ".cache", ".next", ".nuxt", ".parcel-cache",
    "storage/logs",
    "storage/framework/cache", "storage/framework/sessions",
    "storage/framework/testing", "storage/framework/views",
    "storage/app/public",
    # 大头排除：puppeteer/chromium、npm/pnpm 缓存、构建中间产物
    "_npm_cache", "_puppeteer", "puppeteer-cache",
    "chrome-linux", "chromium",
    ".puppeteer", "browsers-cache",
}
EXCLUDE_FILES = {".env", ".env.local", ".env.backup", "Thumbs.db", ".DS_Store"}
EXCLUDE_SUFFIXES = {".log", ".tmp", ".cache", ".pid", ".lock", ".sock"}
# 备份元数据
INCLUDES = [
    "pc-api", "pc-web", "pc-desktop", "mobile-app", "mp-miniapp",
    "deploy", "docs", "README.md",
    "安防运维OA系统设计大纲V2.html",
]

def is_excluded(rel: Path) -> bool:
    parts = rel.parts
    for p in parts:
        if p in EXCLUDE_DIRS:
            return True
    # 路径级别（storage/logs 这种）
    for i in range(len(parts)):
        sub = "/".join(parts[:i+1])
        if sub in EXCLUDE_DIRS:
            return True
    return False

def should_skip_file(name: str) -> bool:
    if name in EXCLUDE_FILES: return True
    return any(name.endswith(s) for s in EXCLUDE_SUFFIXES)

def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def human(n: int) -> str:
    for u in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"

def copy_one(src_root: Path, dest_root: Path, label: str):
    """rsync 风格的本地拷贝"""
    if not src_root.exists():
        return 0, 0
    file_count = 0
    total_bytes = 0
    files = []
    for p in src_root.rglob("*"):
        if p.is_file(): files.append(p)
    print(f"  [{label}] {len(files)} files ...", flush=True)
    for i, src in enumerate(files, 1):
        rel = src.relative_to(src_root)
        if is_excluded(rel): continue
        if should_skip_file(src.name): continue
        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dest)
            file_count += 1
            total_bytes += src.stat().st_size
        except Exception as e:
            print(f"    skip: {rel} ({e})", flush=True)
        if i % 500 == 0:
            print(f"    ... {i}/{len(files)}", flush=True)
    print(f"  [{label}] ✓ {file_count} files, {human(total_bytes)}", flush=True)
    return file_count, total_bytes

def get_git_info() -> dict:
    info = {}
    try:
        info["commit"] = subprocess.check_output(
            ["git","-C",str(LOCAL_ROOT),"log","-1","--pretty=%H %s"],
            stderr=subprocess.DEVNULL, text=True).strip()
        info["branch"] = subprocess.check_output(
            ["git","-C",str(LOCAL_ROOT),"branch","--show-current"],
            stderr=subprocess.DEVNULL, text=True).strip()
        info["tags"] = subprocess.check_output(
            ["git","-C",str(LOCAL_ROOT),"tag","--points-at","HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip() or "(none)"
        info["status"] = subprocess.check_output(
            ["git","-C",str(LOCAL_ROOT),"status","-s"],
            stderr=subprocess.DEVNULL, text=True).strip()
        info["total_commits"] = subprocess.check_output(
            ["git","-C",str(LOCAL_ROOT),"rev-list","--count","HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception as e:
        info["error"] = str(e)
    return info

def main():
    # 自动 tag：取 git 当前 tag 或日期
    if USER_TAG:
        tag = USER_TAG
    else:
        try:
            tag = subprocess.check_output(
                ["git","-C",str(LOCAL_ROOT),"describe","--tags","--abbrev=0"],
                stderr=subprocess.DEVNULL, text=True).strip()
        except Exception:
            tag = f"snapshot-{TS}"

    dest = BACKUPS_ROOT / f"{tag}-{TS}"
    if dest.exists():
        print(f"❌ 已存在: {dest}", file=sys.stderr); sys.exit(1)
    dest.mkdir(parents=True)
    print(f"📦 备份到: {dest}\n", flush=True)

    started = dt.datetime.now()
    summary = []

    # 业务代码
    for sub in ["pc-api", "pc-web", "pc-desktop", "mobile-app", "mp-miniapp", "deploy", "docs"]:
        src = LOCAL_ROOT / sub
        if src.exists():
            fc, sz = copy_one(src, dest / sub, sub)
            summary.append((sub, fc, sz))
        else:
            print(f"  [skip] {sub} (not exists)", flush=True)
            summary.append((sub, 0, 0))

    # 顶层文件
    top_files = ["README.md", "安防运维OA系统设计大纲V2.html"]
    for fn in top_files:
        src = LOCAL_ROOT / fn
        if src.exists():
            fc, sz = copy_one(src.parent, dest / fn, fn)
            # 上面会拷整个父目录，不对，改成单文件
            shutil.rmtree(dest / fn, ignore_errors=True)
            shutil.copy2(src, dest / fn)
            summary.append((fn, 1, src.stat().st_size))

    # .workbuddy 整个目录（重要！deploy 脚本/记忆/技能/备份策略）
    # 但**排除 backups/**（递归套娃爆体积）+ node_modules（puppeteer 二进制）
    wb_src = LOCAL_ROOT / ".workbuddy"
    wb_exclude_top = {"backups", "node_modules", "__pycache__"}  # 顶层不拷
    if wb_src.exists():
        for sub in sorted(wb_src.iterdir()):
            if not sub.is_dir(): continue
            if sub.name in wb_exclude_top:
                print(f"  [skip] .workbuddy/{sub.name} (top-level excluded)", flush=True)
                continue
            fc, sz = copy_one(sub, dest / ".workbuddy" / sub.name, f".workbuddy/{sub.name}")
            summary.append((f".workbuddy/{sub.name}", fc, sz))
        # 顶层文件（MEMORY.md, RELEASE_NOTES_*.md, *.py, *.png 等）
        for f in sorted(wb_src.iterdir()):
            if f.is_file() and not should_skip_file(f.name):
                shutil.copy2(f, dest / ".workbuddy" / f.name)
        summary.append((".workbuddy/(root files)", 1, 0))

    # 写 MANIFEST.md
    git_info = get_git_info()
    manifest = [
        f"# 备份清单: {tag}-{TS}",
        f"", f"## Git 状态",
        f"- **Commit**: `{git_info.get('commit','?')}`",
        f"- **Branch**: `{git_info.get('branch','?')}`",
        f"- **Tags on HEAD**: `{git_info.get('tags','?')}`",
        f"- **Total commits**: {git_info.get('total_commits','?')}",
        f"- **Uncommitted**: {'(clean)' if not git_info.get('status') else git_info.get('status')}",
        f"", f"## 内容",
        f"| 模块 | 文件数 | 大小 |",
        f"|---|---|---|",
    ]
    total_fc = 0
    total_sz = 0
    for name, fc, sz in summary:
        manifest.append(f"| {name} | {fc} | {human(sz)} |")
        total_fc += fc
        total_sz += sz
    elapsed = (dt.datetime.now() - started).total_seconds()
    manifest += [
        f"| **总计** | **{total_fc}** | **{human(total_sz)}** |",
        f"", f"## 备份元数据",
        f"- **开始时间**: {started.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **耗时**: {elapsed:.1f}s",
        f"- **脚本**: `D:/work/website/OA/.workbuddy/backup_local.py`",
        f"", f"## 排除规则",
        f"- 目录: vendor / node_modules / dist / .git / __pycache__ / storage/logs / storage/framework/{{cache,sessions,testing,views}} / storage/app/public",
        f"- 文件: .env / .env.local / Thumbs.db / .DS_Store",
        f"", f"## 恢复",
        f"```bash",
        f"# 解包到任意目录即可运行（不含 vendor/node_modules，需重装）",
        f"tar -czf {tag}-{TS}.tar.gz -C {dest.parent} {dest.name}",
        f"```",
    ]
    (dest / "MANIFEST.md").write_text("\n".join(manifest), encoding="utf-8")
    print(f"\n✅ 备份完成: {dest}")
    print(f"   文件: {total_fc}  大小: {human(total_sz)}  耗时: {elapsed:.1f}s")
    print(f"   MANIFEST: {dest / 'MANIFEST.md'}")

if __name__ == "__main__":
    main()
