#!/usr/bin/env python3
"""批量改分页解包 — 兼容 {data: array} 和 {data: {current_page, data: array, total}}
策略：把所有 `X.data || []` 改成 `X?.data || X || []`
       所有 `X.total || 0` 改成 `(X?.total ?? X?.meta?.total ?? 0)`
支持 X = d / data / res / r / result
"""
import os
import re

ROOT = r'D:\work\website\OA\pc-web\src\views'

# 各种 .data || [] 模式
PATTERNS_DATA = [
    # \w+ = d.data || []   (含可选链)
    (re.compile(r'=\s*(d|data|res|r|result|response)\.data(\s*\|\|\s*\[\])'), r'= \1?.data || \1 || []'),
    # 已有 d?.data 的跳过, 不重写
    # 已有 (data.data || []) 的也跳过
    (re.compile(r'=\s*\((d|data|res|r|result|response)\.data\s*\|\|\s*\[\]\)'), r'= ((\1?.data || \1 || []))'),
]

# 各种 .total || 0 模式
PATTERNS_TOTAL = [
    (re.compile(r'(d|data|res|r|result|response)\.total(\s*\|\|\s*0|\s*\|\|\s*pagination\.total)'),
     r'(\1?.total ?? \1?.meta?.total ?? 0)'),
]

count_total = 0
count_files = 0
for root, dirs, files in os.walk(ROOT):
    for fn in files:
        if not fn.endswith('.vue'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            src = f.read()
        new = src
        n = 0
        for pat, repl in PATTERNS_DATA + PATTERNS_TOTAL:
            new, k = pat.subn(repl, new)
            n += k
        if n > 0 and new != src:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(new)
            count_files += 1
            count_total += n
            print(f'  {os.path.relpath(fp, ROOT)}: {n} 处')

print(f'\n=== 总计 {count_total} 处替换 / {count_files} 个文件 ===')
