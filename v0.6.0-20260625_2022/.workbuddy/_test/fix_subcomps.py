"""修复批量生成的子组件模板里 '{{...}}' 误写（应该是 '{...}'）"""
import os
import glob

pattern = "D:\\work\\website\\OA\\pc-web\\src\\views\\purchase\\components\\*\\*.vue"
files = glob.glob(pattern)
for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    # 修复: 把 :header-cell-style="{{{...}}}" 改回 :header-cell-style="{...}"
    c2 = c.replace('{{{{{', '{').replace('}}}}}}', '}')
    if c != c2:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c2)
        print(f'  ✓ fixed: {os.path.basename(p)}')
print('done')
