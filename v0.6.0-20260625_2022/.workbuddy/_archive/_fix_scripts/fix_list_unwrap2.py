#!/usr/bin/env python3
"""批量修正分页解包 — 适配后端分页结构
后端: {code, data: {current_page, data: array, total}}
拦截器解包后: res = {current_page, data: array, total}

老代码 (BUG): const d = res.data || res → d = array (拿走了 data)
              d.total → undefined ❌

新代码 (FIX):
  const d = res.data || res
  list.value = d.data || d  // 兼容两种结构 (array 或 {data:array})
  total.value = d.total ?? 0  // d 是 array 时 d.total 是 undefined → 0
"""
import os
import re

ROOT = r'D:\work\website\OA\pc-web\src\views'

# 1) 把 const d = res.data || res 改成 const d = res 或 const d = res
#    (因为 res 就是分页结构本体, 不需要再拿一层 data)
PATTERN_D = re.compile(r'const\s+d\s*=\s*(res|response|result)\.data\s*\|\|\s*\1')

# 2) 把 r.data || r 同样修
PATTERN_R = re.compile(r'const\s+d\s*=\s*(r)\.data\s*\|\|\s*\1')

count = 0
for root, dirs, files in os.walk(ROOT):
    for fn in files:
        if not fn.endswith('.vue'):
            continue
        fp = os.path.join(root, fn)
        with open(fp, 'r', encoding='utf-8') as f:
            src = f.read()
        new = src
        new, n1 = PATTERN_D.subn(r'const d = \1', new)
        new, n2 = PATTERN_R.subn(r'const d = \1', new)
        n = n1 + n2
        if n > 0 and new != src:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(new)
            count += n
            print(f'  {os.path.relpath(fp, ROOT)}: {n} 处')

print(f'\n=== 总计 {count} 处替换 ===')
