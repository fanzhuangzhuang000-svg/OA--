#!/usr/bin/env python
# 更新 deploy_152.py 的 API_CHANGED 列表
import re, os

# 读清单
files = []
with open('.workbuddy/v058_php_files.txt', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue
        files.append(line)

# 转 windows 风格 (deploy_152.py 用 os.path.join 处理, 实际用 / 也可, 但保持原文件风格)
new_lines = []
for f in files:
    fp = f.replace('/', chr(92))
    # 用 forward slash 避免 python 转义问题
    fp = f.replace('/', '/')  # 实际就用正斜杠, SFTP 兼容
    new_lines.append(f"    '{fp}',")

# 读 deploy_152.py
deploy_path = '.workbuddy/deploy_152.py'
with open(deploy_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 替换 API_CHANGED = [...] 块
pattern = re.compile(r"API_CHANGED = \[.*?\]", re.DOTALL)
new_block = "API_CHANGED = [\n" + '\n'.join(new_lines) + "\n]"
text = re.sub(r"API_CHANGED = \[.*?\]", lambda m: new_block, text, flags=re.DOTALL, count=1)

with open(deploy_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('updated', len(new_lines), 'files')
