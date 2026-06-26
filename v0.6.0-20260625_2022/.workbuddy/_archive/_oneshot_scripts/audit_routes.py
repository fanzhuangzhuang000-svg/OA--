#!/usr/bin/env python3
"""v0.3.7.5 路由扫描: router.push vs routes 配置"""
import re, os, json, sys

ROOT = 'D:/work/website/OA/pc-web/src'
ROUTES_FILE = f'{ROOT}/router/index.ts'

# 1. 从路由表提取所有可访问的 path
with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
    routes_src = f.read()

route_paths = set()
alias_paths = set()

def extract_blocks(src, start_pos=0):
    """提取 src 中所有顶层 { ... } 块（带括号配对）"""
    blocks = []
    i = start_pos
    while i < len(src):
        if src[i] == '{':
            depth = 1
            j = i + 1
            while j < len(src) and depth > 0:
                if src[j] == '{': depth += 1
                elif src[j] == '}': depth -= 1
                j += 1
            blocks.append((i+1, j-1))  # 块内容在 [i+1, j-1]
            i = j
        else:
            i += 1
    return blocks

def parse_routes(src, prefix=''):
    for (s, e) in extract_blocks(src):
        block = src[s:e]
        p_match = re.search(r"path:\s*['\"`]([^'\"`]+)['\"`]", block)
        if not p_match:
            continue
        p = p_match.group(1)
        if p.startswith('/'):
            full = p
        else:
            full = prefix + '/' + p if prefix else '/' + p
        full = re.sub(r'/+', '/', full)
        full = re.sub(r':\w+', r':id', full)
        route_paths.add(full)
        a_match = re.search(r"alias:\s*['\"`]([^'\"`]+)['\"`]", block)
        if a_match:
            alias_paths.add(a_match.group(1))
        # 递归处理 children
        c_match = re.search(r'children:\s*\[', block)
        if c_match:
            children_start = c_match.end()
            # 找匹配的 ]
            depth = 1
            j = children_start
            while j < len(block) and depth > 0:
                if block[j] == '[': depth += 1
                elif block[j] == ']': depth -= 1
                j += 1
            children_content = block[children_start:j-1]
            parse_routes(children_content, full)

parse_routes(routes_src, '')

def expand(p):
    parts = p.split('/')
    res = []
    for i in range(len(parts)+1):
        sub = '/'.join(parts[:i]) or '/'
        res.append(sub)
    return res

all_routes = set()
for p in route_paths:
    for x in expand(p):
        all_routes.add(x)
for p in alias_paths:
    for x in expand(p):
        all_routes.add(x)

# 2. 扫所有 .vue 文件里 router.push 调用的目标
push_targets = []
for root, dirs, files in os.walk(f'{ROOT}/views'):
    for fn in files:
        if not fn.endswith('.vue'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = fp.replace(ROOT, 'pc-web/src')
        # 匹配 router.push('xxx') / router.push({path: 'xxx'})
        for m in re.finditer(r"router\.push\(\s*['\"`]([^'\"`]+)['\"`]\s*\)", content):
            push_targets.append((rel, m.group(1), 'push-str'))
        for m in re.finditer(r"router\.push\(\s*\{\s*path:\s*['\"`]([^'\"`]+)['\"`]", content):
            push_targets.append((rel, m.group(1), 'push-obj'))
        for m in re.finditer(r"\$router\.push\(\s*['\"`]([^'\"`]+)['\"`]\s*\)", content):
            push_targets.append((rel, m.group(1), 'push-tmpl'))
        for m in re.finditer(r"\$router\.push\(\s*\{\s*path:\s*['\"`]([^'\"`]+)['\"`]", content):
            push_targets.append((rel, m.group(1), 'push-tmpl-obj'))

print(f'已扫 {len(push_targets)} 处 router.push 调用')
print(f'路由表共有 {len(route_paths)} 个 path 模板')
print()

# 3. 比对
miss = []
ok = []
for (file, target, kind) in push_targets:
    # 把 :id 这种去掉 + 把 ${xxx} 模板替换成 :id
    norm = re.sub(r'\$\{[^}]+\}', r':id', target)
    norm = re.sub(r':\w+', r':id', norm)
    # query 部分去掉（?tab=log）
    if '?' in norm:
        norm = norm.split('?')[0]
    # 拿完整 path 列表（含前缀）
    matched = False
    for rp in all_routes:
        if norm == rp or norm == rp + '/list' or norm == rp + '/detail':
            matched = True
            break
    if not matched and target.startswith('/'):
        miss.append((file, target, kind))
    else:
        ok.append((file, target, kind))

if miss:
    print(f'❌ 找到 {len(miss)} 处 404 风险:')
    for file, target, kind in miss:
        print(f'  {file}: {target}  ({kind})')
else:
    print('✅ 所有 router.push 目标都能匹配路由表')

# 4. 扫 router-link 的 to 属性
print()
print('--- 扫 router-link to 属性 ---')
link_targets = []
for root, dirs, files in os.walk(f'{ROOT}/views'):
    for fn in files:
        if not fn.endswith('.vue'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = fp.replace(ROOT, 'pc-web/src')
        for m in re.finditer(r"<router-link[^>]*\sto=['\"]([^'\"]+)['\"]", content):
            link_targets.append((rel, m.group(1)))

link_miss = []
for (file, target) in link_targets:
    norm = re.sub(r':\w+', r':id', target)
    matched = any(norm == rp for rp in all_routes)
    if not matched and target.startswith('/'):
        link_miss.append((file, target))

if link_miss:
    print(f'❌ 找到 {len(link_miss)} 处 router-link 404:')
    for file, target in link_miss:
        print(f'  {file}: to="{target}"')
else:
    print('✅ 所有 router-link 都能匹配')
