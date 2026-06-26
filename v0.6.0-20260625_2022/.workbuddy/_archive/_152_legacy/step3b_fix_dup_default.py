#!/usr/bin/env python3
"""v3.9.0 阶段3 v2: 修正 ENUM 改写后产生的重复 ->default()"""
import os
import re

ROOT = r'D:\work\website\OA\pc-api\database\migrations_pg'

# ->default('xx')->default(null) → ->default('xx')
DUP_DEFAULT = re.compile(r"->default\((['\"][^'\"]+['\"])\)->default\(null\)")

count = 0
for fn in sorted(os.listdir(ROOT)):
    if not fn.endswith('.php'):
        continue
    fp = os.path.join(ROOT, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        src = f.read()
    new, n = DUP_DEFAULT.subn(r"->default(\1)", src)
    if n > 0 and new != src:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new)
        count += n

print(f'修复 {count} 处重复 ->default()')
