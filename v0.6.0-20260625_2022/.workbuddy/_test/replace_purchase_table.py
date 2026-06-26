"""批量替换 5 个 purchase 文件 + finance/index 的 filter+stats+table 段"""
import re
import os

BASE = r'D:\work\website\OA\pc-web\src\views'

# 模块 → (主文件, 子目录, 子组件名, 标题)
JOBS = [
    ('purchase/Logistics.vue',       'logistics',       'Logistics',       '物流'),
    ('purchase/Approval.vue',        'approval',        'Approval',        '采购审批'),
    ('purchase/PaymentRequest.vue',  'payment-request', 'PaymentRequest',  '付款申请'),
    ('purchase/Payment.vue',         'payment',         'Payment',         '付款'),
    ('purchase/Plan.vue',            'plan',            'Plan',            '采购计划'),
]

for rel, sub, name, title in JOBS:
    p = f'{BASE}\\{rel}'
    with open(p, 'r', encoding='utf-8') as fp:
        content = fp.read()

    # 找 <el-table 位置到 </el-table> + pagination 闭合
    table_start_m = re.search(r'<el-table', content)
    table_end_m = re.search(r'</el-table>\s*\n\s*<div class="pagination-wrapper">.*?</div>', content, re.DOTALL)
    if not (table_start_m and table_end_m):
        print(f'  ✗ {rel}: 没找到 table/pagination 块')
        continue
    start = table_start_m.start()
    end = table_end_m.end()

    # 替换块: 把 el-table + pagination 段替换为新子组件
    new_block = f'''<{name}Table
        :list="pagedList"
        :loading="loading"
        :page="page"
        :page-size="pageSize"
        :total="filteredList.length"
        @view="handleView"
        @edit="handleEdit"
        @delete="handleDelete"
        @page-change="(p: number) => page = p"
        @size-change="(s: number) => {{ pageSize = s; page = 1 }}"
      />'''
    content = content[:start] + new_block + content[end:]

    # 加 import
    import_block = f"import {name}Table from './components/{sub}/{name}Table.vue'\nimport {name}FilterBar from './components/{sub}/{name}FilterBar.vue'\nimport {name}StatCards from './components/{sub}/{name}StatCards.vue'\n"
    # 在第一个 import 后插入
    m = re.search(r"^import .*?$", content, re.MULTILINE)
    if m:
        # 找到最后一个 import 的位置
        last_import_m = None
        for mm in re.finditer(r"^import .*?$", content, re.MULTILINE):
            last_import_m = mm
        if last_import_m:
            content = content[:last_import_m.end()] + '\n' + import_block + content[last_import_m.end():]

    with open(p, 'w', encoding='utf-8') as fp:
        fp.write(content)
    print(f'  ✓ {rel}: 替换 table 块 (start={start} end={end})')

print('done')
