"""把生成的子组件里所有 ':style="{{...' 改为 ':style="{...'"""
import os
import glob
import re

pattern = "D:\\work\\website\\OA\\pc-web\\src\\views\\purchase\\components\\*\\*.vue"
files = glob.glob(pattern)
for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    # 修复 :style="{{...}}"  → :style="{...}"
    c2 = re.sub(r':style="\{\{', ':style="{', c)
    c2 = re.sub(r'\}\}"', '}"', c2)
    if c != c2:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c2)
        print(f'  ✓ fixed: {os.path.basename(p)}')
print('done')
