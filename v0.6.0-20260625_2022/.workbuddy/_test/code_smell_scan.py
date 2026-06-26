"""
OA 系统死代码 / 死路由 / 死 import 扫描器
- 扫 routes/api.php vs Controller public method
- 扫 Controller 顶部的 use 但没引用
- 扫 Model 类 vs 实际引用
"""
import re
import os
import sys
from pathlib import Path
from collections import defaultdict

API_DIR = Path(r'D:\work\website\OA\pc-api\app\Http\Controllers\Api')
MODEL_DIR = Path(r'D:\work\website\OA\pc-api\app\Models')
ROUTES_FILE = Path(r'D:\work\website\OA\pc-api\routes\api.php')
APP_DIR = Path(r'D:\work\website\OA\pc-api\app')

# 排除的方法
EXCLUDE_METHODS = {'__construct', '__destruct', '__call', '__callStatic', 'middleware', 'authorize', 'rules', 'messages', 'withValidator'}

# === 1. 扫路由里所有注册的 controller + method ===
print("=== 阶段 1: 解析 routes/api.php ===")
route_text = ROUTES_FILE.read_text(encoding='utf-8')
route_pattern = re.compile(r'\[(\w+Controller)::class\s*,\s*[\'"](\w+)[\'"]\s*\]')
routes = []  # (controller_short, method, line_no)
for i, line in enumerate(route_text.split('\n'), 1):
    for m in route_pattern.finditer(line):
        ctrl = m.group(1)
        method = m.group(2)
        routes.append((ctrl, method, i))
print(f"  路由注册数: {len(routes)}")

# 按 Controller 分组
routes_by_ctrl = defaultdict(list)
for ctrl, method, line in routes:
    routes_by_ctrl[ctrl].append((method, line))

# === 2. 扫每个 Controller 实际定义的 public method ===
print("\n=== 阶段 2: 解析 Controller 文件 ===")
controllers = {}  # file_name -> {class_name, methods: {name: line}}
class_pattern = re.compile(r'class\s+(\w+Controller)\s+extends')
method_pattern = re.compile(r'public\s+function\s+(\w+)\s*\(')

for f in sorted(API_DIR.glob('*Controller.php')):
    text = f.read_text(encoding='utf-8')
    # 类名
    cm = class_pattern.search(text)
    if not cm:
        continue
    class_name = cm.group(1)  # e.g. SalesController
    # 排除 'extends BaseController' 里的字符
    methods = {}
    for i, line in enumerate(text.split('\n'), 1):
        for mm in method_pattern.finditer(line):
            name = mm.group(1)
            if name not in EXCLUDE_METHODS and not name.startswith('_'):
                methods[name] = i
    controllers[class_name] = {
        'file': f,
        'methods': methods,
    }
print(f"  Controller 数: {len(controllers)}, 方法总数: {sum(len(c['methods']) for c in controllers.values())}")

# === 3. 对比: 未注册的 public method (死方法) ===
print("\n=== 阶段 3: 死方法 (未注册路由) ===")
dead_methods = []
for ctrl_name, info in controllers.items():
    registered = {m for m, _ in routes_by_ctrl.get(ctrl_name, [])}
    for m, line in info['methods'].items():
        if m not in registered:
            dead_methods.append((ctrl_name, m, info['file'], line))

# 过滤明显是 alias 的（同一个 method 在别处注册但跟不同 Controller 同名的不算）
# 比如 oppsUpdateStatus + leadsUpdateStatus 都是不同名
for c, m, f, l in dead_methods:
    print(f"  ❌ {c}::{m}  (文件: {f.name}:{l})")

print(f"  死方法总数: {len(dead_methods)}")

# === 4. 死路由 (注册了但 Controller 找不到方法) ===
print("\n=== 阶段 4: 死路由 (方法不存在) ===")
dead_routes = []
for ctrl, method, line in routes:
    if ctrl not in controllers:
        # Controller 类找不到
        dead_routes.append((ctrl, method, f'<class not found>', line))
    elif method not in controllers[ctrl]['methods']:
        dead_routes.append((ctrl, method, controllers[ctrl]['file'], line))

for c, m, f, l in dead_routes:
    fname = f.name if hasattr(f, 'name') else f
    print(f"  ⚠️  路由→{c}::{m} (期望: {fname}:{l})  但方法不存在")
print(f"  死路由总数: {len(dead_routes)}")

# === 5. 死 import (use 了但没用) ===
print("\n=== 阶段 5: 死 use 导入 ===")
use_pattern = re.compile(r'use\s+([\w\\]+)(?:\s+as\s+(\w+))?\s*;')
short_use_pattern = re.compile(r'\b(\w+)\b')  # 简化：扫所有单词

dead_uses_total = 0
for f in sorted(API_DIR.glob('*Controller.php')):
    text = f.read_text(encoding='utf-8')
    # 只看顶部 use 行 (跳过 namespace 行)
    lines = text.split('\n')
    use_lines = []
    for i, line in enumerate(lines, 1):
        m = use_pattern.match(line.strip())
        if m:
            full = m.group(1)
            alias = m.group(2)
            short = full.split('\\')[-1]
            use_lines.append((i, full, short, alias))
    if not use_lines:
        continue
    # 移除 use 段，扫剩余的代码是否有 short 引用
    body = '\n'.join(lines)
    body_no_use = re.sub(r'use\s+[\w\\]+(?:\s+as\s+\w+)?\s*;', '', body)
    file_dead = []
    for i, full, short, alias in use_lines:
        target = alias or short
        # 全文搜这个 short 名（排除 use 行本身）
        # 用 \b 边界
        if not re.search(r'\b' + re.escape(target) + r'\b', body_no_use):
            file_dead.append((i, full, target))
    if file_dead:
        for i, full, t in file_dead:
            print(f"  🗑️  {f.name}:{i}  use {full}  (短名 `{t}` 在文件中未引用)")
        dead_uses_total += len(file_dead)
print(f"  死 use 总数: {dead_uses_total}")

# === 6. Model 类引用计数 ===
print("\n=== 阶段 6: Model 类引用计数 ===")
# 收集所有 Model 类名
model_classes = []
for f in sorted(MODEL_DIR.glob('*.php')):
    if f.name == 'User.php':
        continue  # User 算核心
    text = f.read_text(encoding='utf-8')
    for m in re.finditer(r'class\s+(\w+)\s+extends\s+Model\b', text):
        model_classes.append((f, m.group(1), text[:m.start()].count('\n') + 1))

# 全文 grep
app_text = ''
for f in APP_DIR.rglob('*.php'):
    app_text += '\n' + f.read_text(encoding='utf-8', errors='ignore')

print(f"  找到 {len(model_classes)} 个 Model 类")
for f, name, line in model_classes:
    # 引用计数（排除定义自身 + use 引入）
    refs = len(re.findall(r'\b' + name + r'\b', app_text))
    if refs <= 2:  # 1 处定义 + 1 处 use = 0 真实引用
        print(f"  🗑️  {name}  (定义于 {f.name}:{line}, 全文引用: {refs})")

# 写报告
print("\n=== 报告输出到 memory/CODE_SMELL_REPORT.md ===")
report = []
report.append("# OA 系统代码质量检查报告\n")
report.append(f"> 生成时间: 2026-06-23 14:50\n")
report.append(f"> 扫描范围: 后端 42 个 Controller + 6 个 Model 聚合文件 + routes/api.php\n\n")

report.append("## 一、Controller 死方法 (未注册路由)\n")
report.append(f"共 {len(dead_methods)} 个 public method 没在任何路由里注册。\n\n")
report.append("| Controller | 方法 | 文件 | 行 |\n|---|---|---|---|\n")
for c, m, f, l in dead_methods:
    report.append(f"| {c} | `{m}` | `{f.name}` | {l} |\n")
if not dead_methods:
    report.append("_无_\n")

report.append("\n## 二、死路由 (路由注册但方法不存在)\n")
report.append(f"共 {len(dead_routes)} 个路由指向不存在的 method。\n\n")
report.append("| Controller | 方法 | 期望文件 | 行 |\n|---|---|---|---|\n")
for c, m, f, l in dead_routes:
    fname = f.name if hasattr(f, 'name') else f
    report.append(f"| {c} | `{m}` | `{fname}` | {l} |\n")
if not dead_routes:
    report.append("_无_\n")

report.append("\n## 三、死 use 导入 (use 了但未引用)\n")
report.append(f"共 {dead_uses_total} 处。详见控制台输出。\n\n")

report.append("\n## 四、死 Model 类 (0 真实引用)\n")
report.append("_见控制台输出。_\n\n")

report_path = Path(r'D:\work\website\OA\.workbuddy\memory\CODE_SMELL_REPORT.md')
report_path.write_text(''.join(report), encoding='utf-8')
print(f"✅ 报告写入: {report_path}")
