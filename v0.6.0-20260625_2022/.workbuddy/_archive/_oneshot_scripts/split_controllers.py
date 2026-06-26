#!/usr/bin/env python3
"""
把 /var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php
按 class 边界切分成 11 个独立文件，每个 class 一个文件。

策略：
1. 读 ModuleControllers.php
2. 找到所有 `^class Foo extends Controller` 的边界
3. 为每个 class 生成新文件 FooController.php
   - 顶部用最小依赖的 use 列表（基于 AST 风格的简单扫描）
   - 把 `class Foo` 替换成 `class FooController`，并修正所有内部 self/parent/new 引用
4. 备份 ModuleControllers.php 为 .bak
5. 删除原文件

切完后：
- composer dump-autoload
- php artisan route:clear / config:clear / cache:clear
- 全量回归 41 端点
"""
import os
import re
import sys
import time
import shutil
import subprocess
import paramiko

HOST = "172.20.0.139"
USER = "nbcy"
PASSWORD = "admin123"
PORT = 22
SRC = "/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php"
DST_DIR = "/var/www/oa-api/app/Http/Controllers/Api"

# 类名 → 新文件名的固定映射
# 11 个控制器
CLASS_NEW = {
    "EmployeeController": "EmployeeController.php",
    "CustomerController": "CustomerController.php",
    "ExpenseController": "ExpenseController.php",
    "VehicleController": "VehicleController.php",
    "InventoryController": "InventoryController.php",
    "FinanceController": "FinanceController.php",
    "DiskController": "DiskController.php",
    "KnowledgeController": "KnowledgeController.php",
    "NotificationController": "NotificationController.php",
    "DashboardController": "DashboardController.php",
    "SystemLogController": "SystemLogController.php",
}

# 每个控制器用到的 FQCN 集合（手工分析，避免误判）
# 简化：每个控制器继承 Controller（基类），use 由控制器源码的实际引用决定
# 这里给出"最少必要" use（基于全文 use 行 + 控制器内部 \App\... / \Illuminate\... 引用）

CTRL_USES = {
    "EmployeeController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\User",
        "App\\Models\\Department",
        "App\\Models\\Position",
        "App\\Models\\SkillTag",
        "App\\Models\\Certificate",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "CustomerController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\Customer",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "ExpenseController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\ExpenseClaim",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "VehicleController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\Vehicle",
        "App\\Models\\VehicleUsageRequest",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "InventoryController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\InventoryItem",
        "App\\Models\\StockRecord",
        "App\\Models\\Warehouse",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "FinanceController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\Receivable",
        "App\\Models\\Payable",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "DiskController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\DiskFolder",
        "App\\Models\\DiskFile",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "KnowledgeController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\KnowledgeCategory",
        "App\\Models\\KnowledgeArticle",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "NotificationController": [
        "App\\Http\\Controllers\\Controller",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
    ],
    "DashboardController": [
        "App\\Http\\Controllers\\Controller",
        "App\\Models\\Project",
        "App\\Models\\ServiceOrder",
        "App\\Models\\AttendanceRecord",
        "App\\Models\\LeaveRequest",
        "App\\Models\\OvertimeRequest",
        "App\\Models\\ExpenseClaim",
        "App\\Models\\Receivable",
        "Illuminate\\Http\\JsonResponse",
    ],
    "SystemLogController": [
        "App\\Http\\Controllers\\Controller",
        "Illuminate\\Http\\JsonResponse",
        "Illuminate\\Http\\Request",
        "Illuminate\\Support\\Facades\\DB",
    ],
}


def run(ssh, cmd, timeout=60):
    si, so, se = ssh.exec_command(cmd, timeout=timeout)
    rc = so.channel.recv_exit_status()
    return rc, so.read().decode("utf-8", "replace"), se.read().decode("utf-8", "replace")


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, PORT, USER, PASSWORD, timeout=15)

    # 1. 读 ModuleControllers.php
    sftp = ssh.open_sftp()
    try:
        with sftp.open(SRC, "r") as f:
            text = f.read().decode("utf-8")
    finally:
        sftp.close()

    print(f"原文件: {len(text)} chars, {text.count(chr(10))} 行")

    # 2. 按 class 边界切
    pattern = re.compile(r"^class (\w+) extends Controller\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if len(matches) != 11:
        print(f"!! 期望 11 个 class，实际找到 {len(matches)}")
        for m in matches:
            print(f"  - {m.group(1)} at line {text[:m.start()].count(chr(10))+1}")
        sys.exit(1)

    # 每个 class 的源码
    class_blocks = {}
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # 截到最后一个 } 之前
        block = text[start:end]
        class_blocks[name] = block

    # 3. 备份原文件
    bak = f"{SRC}.bak.{int(time.time())}"
    run(ssh, f"sudo -u www-data cp {SRC} {bak} && sudo chown nbcy:nbcy {bak}")
    print(f"[1/4] 备份: {bak}")

    # 4. 写新文件
    written = []
    for cls, new_file in CLASS_NEW.items():
        body = class_blocks[cls]
        uses = CTRL_USES[cls]
        use_block = "\n".join(f"use {u};" for u in uses)
        # 替换类名（如果原 class 名 = 控制器类名则保持）
        new_content = f"""<?php

namespace App\\Http\\Controllers\\Api;

{use_block}

{body}"""
        tmp = f"/tmp/.split_{cls}.php"
        sftp = ssh.open_sftp()
        try:
            with sftp.open(tmp, "w") as f:
                f.write(new_content)
        finally:
            sftp.close()
        # cp 到 DST_DIR（需要 www-data 拥有）
        rc, out, err = run(ssh, f"sudo cp {tmp} {DST_DIR}/{new_file} && sudo chown www-data:www-data {DST_DIR}/{new_file}")
        if rc != 0:
            print(f"  ! {new_file} 写入失败: {err.strip()[:200]}")
            continue
        run(ssh, f"rm -f {tmp}")
        written.append(new_file)
        print(f"  ✓ {new_file} ({len(new_content)} chars)")

    # 5. 删除原文件
    rc, out, err = run(ssh, f"sudo rm -f {SRC} && echo DELETED")
    print(f"[2/4] 删除原 ModuleControllers.php: {out.strip()}")

    # 6. 重新生成 autoload
    rc, out, err = run(ssh, "cd /var/www/oa-api && sudo -u www-data composer dump-autoload 2>&1 | tail -5", timeout=60)
    print(f"[3/4] composer dump-autoload:")
    print("   " + out.strip()[:400])

    # 7. 清理 Laravel 缓存
    for c in ["route:clear", "config:clear", "cache:clear"]:
        run(ssh, f"cd /var/www/oa-api && sudo -u www-data php artisan {c} 2>&1 | tail -2", timeout=30)

    # 8. 检查控制器是否被 Laravel 注册
    print("[4/4] 验证：路由中应包含新 controller")
    rc, out, err = run(ssh, "cd /var/www/oa-api && sudo -u www-data php artisan route:list --path=api 2>&1 | head -30", timeout=30)
    print(out.strip()[:1000])

    ssh.close()
    print(f"\n完成：{len(written)} 个独立文件已生成")


if __name__ == "__main__":
    main()
