#!/usr/bin/env python3
"""
v0.3.30 批量 dialog 抽取工具

策略：扫描每个 Vue 文件中的 <el-dialog>...</el-dialog> 块，
生成对应子组件，替换主文件。

注：本脚本是"半自动"工具 - 抽出对话框后需要人工调整 import。
"""
import os
import re
import sys

VIEWS = r'D:\work\website\OA\pc-web\src\views'

def find_dialog_blocks(content):
    """找出所有 <el-dialog ...>...</el-dialog> 块（含嵌套）"""
    blocks = []
    pos = 0
    while pos < len(content):
        m = re.search(r'<el-dialog\b', content[pos:])
        if not m:
            break
        start = pos + m.start()
        # 找匹配的 </el-dialog>（简单实现：忽略嵌套，因为 vue dialog 通常不嵌套）
        end_m = re.search(r'</el-dialog>', content[start:])
        if not end_m:
            break
        end = start + end_m.end()
        # 跳过注释行
        if not content[start:end].strip().startswith('<!--'):
            blocks.append((start, end, content[start:end]))
        pos = end
    return blocks


def suggest_component_name(dialog_block, idx):
    """根据 dialog title 推断组件名"""
    m = re.search(r':?title="([^"]+)"', dialog_block)
    if m:
        title = m.group(1)
        # 简单提取中文
        cn = re.findall(r'[\u4e00-\u9fa5]+', title)
        if cn:
            label = ''.join(cn[:3])
            return f"{label}Dialog"
    return f"Dialog{idx+1}"


def process_file(filepath, dry_run=True):
    """处理单个 Vue 文件"""
    rel = filepath.replace(VIEWS, '').replace('\\', '/')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = find_dialog_blocks(content)
    if not blocks:
        return 0

    # 找 import 段位置（v-model 双向需要 defineEmits + props）
    import_m = re.search(r'^<script setup[^>]*>\n', content, re.MULTILINE)
    if not import_m:
        return 0

    # 简单策略：保留原 dialog 块不变，仅打印建议
    # 因为 dialog 块通常有大量 v-model 状态绑定，盲目抽取会破坏逻辑
    return len(blocks)


if __name__ == '__main__':
    import glob
    total_dialogs = 0
    files_with_dialogs = []
    for f in glob.glob(f'{VIEWS}/**/*.vue', recursive=True):
        n = process_file(f)
        if n > 0:
            files_with_dialogs.append((f.replace(VIEWS, '').replace('\\', '/'), n))
            total_dialogs += n

    print(f'\n=== 扫描结果 ===')
    print(f'含 dialog 的文件: {len(files_with_dialogs)}')
    print(f'总 dialog 块数: {total_dialogs}\n')
    print(f'{"行数":<7}{"dialog":<9}文件')
    for path, n in sorted(files_with_dialogs, key=lambda x: -x[1]):
        full = VIEWS + path
        lines = sum(1 for _ in open(full, encoding='utf-8'))
        print(f'{lines:<7}{n:<9}{path}')
