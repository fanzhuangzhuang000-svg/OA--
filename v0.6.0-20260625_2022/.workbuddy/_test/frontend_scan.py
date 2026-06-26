"""
前端死代码 / 错位 API / 拖拽状态机问题扫描器
"""
import re
from pathlib import Path
from collections import defaultdict, Counter

VIEWS_DIR = Path(r'D:\work\website\OA\pc-web\src\views')
API_DIR = Path(r'D:\work\website\OA\pc-web\src\api')
ROUTER_FILE = Path(r'D:\work\website\OA\pc-web\src\router\index.ts')
ALL_VUE = list(VIEWS_DIR.rglob('*.vue'))

# 1. 路由注册的组件 vs 实际存在的 .vue 文件
print("=== 阶段 1: 路由 ↔ Vue 组件对照 ===")
router_text = ROUTER_FILE.read_text(encoding='utf-8')
import_pattern = re.compile(r"import\(['\"]@/views/([^'\"]+)['\"]\)")
registered_components = set()
for m in import_pattern.finditer(router_text):
    registered_components.add(m.group(1))

existing_vue = set()
for f in ALL_VUE:
    rel = str(f.relative_to(VIEWS_DIR.parent / 'views' if False else VIEWS_DIR)).replace('\\', '/')
    existing_vue.add(rel)

# dead vue（实际存在但没被路由注册）
dead_vue = existing_vue - registered_components
print(f"  Vue 文件总数: {len(existing_vue)}, 路由注册: {len(registered_components)}")
print(f"  死 Vue 组件 (写了但没路由): {len(dead_vue)}")
for f in sorted(dead_vue):
    print(f"    🗑️  {f}")

# 路由里引用但文件不存在
missing_vue = registered_components - existing_vue
print(f"  路由引用但文件不存在: {len(missing_vue)}")
for f in sorted(missing_vue):
    print(f"    ⚠️  {f}")

# 2. 扫描每个 Vue 文件的 import / 模板用法，找出未使用的 import
print("\n=== 阶段 2: Vue 死 import (script setup) ===")
dead_imports_total = 0
for f in sorted(ALL_VUE):
    text = f.read_text(encoding='utf-8')
    # 提取 <script setup> 块
    m = re.search(r'<script setup[^>]*>(.*?)</script>', text, re.DOTALL)
    if not m:
        continue
    script = m.group(1)
    # 提取所有 import 语句
    imports = []
    for im in re.finditer(r"import\s+(?:\{([^}]+)\}|(\w+))(?:\s*,\s*\{([^}]+)\})?\s+from\s+['\"]([^'\"]+)['\"]", script):
        if im.group(1):
            for name in im.group(1).split(','):
                name = name.strip().split(' as ')[-1].strip()
                if name and name != 'type':
                    imports.append((name, im.group(4)))
        if im.group(2):
            imports.append((im.group(2), im.group(4)))
        if im.group(3):
            for name in im.group(3).split(','):
                name = name.strip().split(' as ')[-1].strip()
                if name and name != 'type':
                    imports.append((name, im.group(4)))
    # 扫模板和 script 里是否引用
    template_match = re.search(r'<template>(.*?)</template>', text, re.DOTALL)
    template = template_match.group(1) if template_match else ''
    body = text  # 全文搜索
    file_dead = []
    for name, src in imports:
        if not re.search(r'\b' + re.escape(name) + r'\b', script.replace('import ', '_import_ ', 1)) or \
           re.search(r'\b' + re.escape(name) + r'\b', script[script.find(name)+len(name):]):
            # 简化：直接在 script + template 里搜
            pass
    # 极简：直接在全文搜 \b name \b 出现次数
    for name, src in imports:
        # 在 import 块本身去掉，看其他地方是否引用
        # 用 re.sub 去掉该 name 的 import 行
        cleaned_script = re.sub(r"import\s+[^;]*\b" + re.escape(name) + r"\b[^;]*;?", '', script, count=1)
        cleaned_script = re.sub(r"import\s+[^;]*\{[^}]*\b" + re.escape(name) + r"\b[^}]*\}[^;]*;?", '', cleaned_script)
        # 全文（包括 template）搜 name
        if not re.search(r'\b' + re.escape(name) + r'\b', cleaned_script + template):
            file_dead.append((name, src))
    if file_dead:
        rel = str(f.relative_to(VIEWS_DIR))
        for name, src in file_dead:
            print(f"    🗑️  {rel}: import {{{name}}} from '{src}'")
        dead_imports_total += len(file_dead)

print(f"  死 import 总数: {dead_imports_total}")

# 3. 跨文件 API 调用统计: 哪些 API 函数 0 引用（api/*.ts 里 export 但没人用）
print("\n=== 阶段 3: API 函数 0 引用扫描 ===")
for api_file in API_DIR.glob('*.ts'):
    if api_file.name == 'modules.ts':  # 模块表
        continue
    text = api_file.read_text(encoding='utf-8')
    exports = []
    for m in re.finditer(r'export\s+function\s+(\w+)\s*\(', text):
        exports.append(m.group(1))
    # 全文搜
    views_text = ''
    for f in ALL_VUE:
        views_text += '\n' + f.read_text(encoding='utf-8', errors='ignore')
    for fn in exports:
        # 找使用次数
        usage = len(re.findall(r'\b' + fn + r'\s*\(', views_text))
        # 排除函数自身定义在 views 里
        if usage == 0:
            print(f"    🗑️  {api_file.name}::{fn}  0 引用")

# 4. 拖拽看板专用: OppsBoard 状态机 vs LeadsBoard 状态机 跟后端 DB 不对齐
print("\n=== 阶段 4: 拖拽看板状态机 vs 后端 enum ===")
for board in ['LeadsBoard.vue', 'OppsBoard.vue']:
    f = VIEWS_DIR / 'sales' / board
    if not f.exists():
        continue
    text = f.read_text(encoding='utf-8')
    # 提取 columns 数组的 value
    m = re.search(r'columns\s*=\s*\[(.*?)\]', text, re.DOTALL)
    if not m:
        continue
    cols = re.findall(r"value:\s*['\"](\w+)['\"]", m.group(1))
    print(f"  {board} 列 ({len(cols)}): {cols}")

print("\n  期望对照 (后端 DB 注释):")
print("    leads.status: new/contacting/qualified/converted/discarded (5 段)")
print("    opportunities.stage: requirement/solution/negotiation/contracting/won/lost (6 段)")

# 5. Vue 文件超大（> 1500 行）
print("\n=== 阶段 5: 巨型 Vue 文件 (>1500 行) ===")
for f in ALL_VUE:
    lines = f.read_text(encoding='utf-8').count('\n')
    if lines > 1500:
        print(f"  ⚠️  {f.relative_to(VIEWS_DIR)}: {lines} 行")

# 6. 重复 API 调用模式 (高频出现 get+list)
print("\n=== 阶段 6: 高频 API 调用模式 ===")
api_usage = Counter()
for f in ALL_VUE:
    text = f.read_text(encoding='utf-8')
    for m in re.finditer(r'\b(get|post|put|del|patch)\s*\(\s*[`' + "'" + r'"]([^`' + "'" + r'"]+)', text):
        verb, url = m.group(1), m.group(2)
        api_usage[(verb, url)] += 1
print("  Top 20 高频 (verb, url) 模板调用:")
for (verb, url), n in api_usage.most_common(20):
    print(f"    {n:3d} 次  {verb.upper():5s}  {url}")

# 7. template 里 v-if="!..." 多余 (前后矛盾)
print("\n=== 阶段 7: 模板可疑条件 ===")
for f in ALL_VUE:
    text = f.read_text(encoding='utf-8')
    template = re.search(r'<template>(.*?)</template>', text, re.DOTALL)
    if not template:
        continue
    t = template.group(1)
    # v-if 永远为真的可疑: v-if="true" / v-if="1"
    for m in re.finditer(r'v-if=["\'](\s*(true|1)\s*)["\']', t):
        rel = str(f.relative_to(VIEWS_DIR))
        line = t[:m.start()].count('\n') + 1
        print(f"    ⚠️  {rel}:{line}  v-if={m.group(1)}")
