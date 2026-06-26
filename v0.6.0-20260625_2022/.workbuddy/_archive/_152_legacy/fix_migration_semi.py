#!/usr/bin/env python3
"""修 PG migration 的语法 bug:
原本是 $table->enum(...) 改成 $table->string(...) + chain methods
但是 chain methods 没有正确加上 ->default() 或 ->comment() 的尾巴, 看起来 line 18 末尾少 ;"""
import os
import re

ROOT = r'D:\work\website\OA\pc-api\database\migrations_pg'

# 找: $table->string('xxx', 50)->default('yy')->comment('zz')\n 后面没 ;
# 真正问题: 多行 chain, 第一个 chain 没 ;
# 解决: 找到行末没 ; 的 chain, 加上 ->;

count = 0
for fn in sorted(os.listdir(ROOT)):
    if not fn.endswith('.php'):
        continue
    fp = os.path.join(ROOT, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        src = f.read()
    # 匹配: $table->xxx(...)\n  (没 ; 的)
    new = re.sub(r"(\$table->[a-zA-Z0-9_]+(?:\([^)]*\))?(?:->[a-zA-Z0-9_]+(?:\([^)]*\))?)*)\n(?![\s]*[;\$])", r"\1;\n", src)
    if new != src:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new)
        count += 1
        print(f'  {fn}: 修复')

print(f'修 {count} 个文件')
