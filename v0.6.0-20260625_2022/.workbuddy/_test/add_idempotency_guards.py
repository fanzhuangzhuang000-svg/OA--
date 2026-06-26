#!/usr/bin/env python3
"""v0.3.18 批量加 migration 幂等守卫

对 83 个缺守卫的 migration 自动注入:
  - create_X_table: `Schema::hasTable('X')` up + `Schema::dropIfExists('X')` 已天然幂等
  - add_Y_to_X / add_xxx_fields: `Schema::hasColumn('X', 'first_added_col')` up+down
  - create_Y_table (database manipulation): `Schema::hasTable` up

跳过:
  - dropForeign/->change()/dropIndex 这类 alter-only（不能加 hasColumn 守卫）
  - DB::table 操作（insertOrIgnore/delete 已天然幂等）

使用:
  python add_idempotency_guards.py --dry-run  # 预览
  python add_idempotency_guards.py             # 实际修改
"""
import re
import sys
import glob
import argparse
from pathlib import Path


def detect_pattern(content: str) -> str:
    """根据内容判断 migration 类型"""
    if 'Schema::create' in content and 'Schema::table' not in content:
        return 'create'
    if 'Schema::table' in content and '->change()' not in content:
        return 'add_columns'
    if '->change()' in content or 'dropForeign' in content:
        return 'alter_only'
    if 'DB::table' in content:
        return 'db_op'
    return 'unknown'


def extract_table_and_first_col(content: str):
    """从内容里提取表名 + 第一个添加的列名"""
    # Schema::create('xxx', ...)
    m = re.search(r"Schema::create\(['\"](\w+)['\"]", content)
    if m:
        return m.group(1), None
    # Schema::table('xxx', ...)
    m = re.search(r"Schema::table\(['\"](\w+)['\"]", content)
    if not m:
        return None, None
    table = m.group(1)
    # 找第一个 $table->xxx('col_name', ...)
    m2 = re.search(r"\$table->\w+\(['\"]([a-z_][a-z0-9_]*)['\"]", content)
    col = m2.group(1) if m2 else None
    return table, col


def inject_create_guard(content: str, table: str) -> str:
    """给 create_X_table migration 加 hasTable 守卫"""
    if 'hasTable' in content:
        return content  # 已加过
    # 在 up() 体内第一行插入守卫
    pattern = re.compile(
        r"(public function up\(\): void\s*\{\s*\n)",
        re.MULTILINE,
    )
    guard = f"        // v0.3.18 幂等保护：v0.3.14 全量部署时已建表，重跑会报 42P07\n        if (Schema::hasTable('{table}')) {{\n            return;\n        }}\n\n"
    new_content, n = pattern.subn(r"\1" + guard, content, count=1)
    return new_content if n else content


def inject_alter_guard(content: str, table: str, col: str) -> str:
    """给 add columns migration 加 hasColumn 守卫"""
    if not col or 'hasColumn' in content:
        return content
    # up()
    up_pattern = re.compile(
        r"(public function up\(\): void\s*\{\s*\n)",
        re.MULTILINE,
    )
    up_guard = f"        // v0.3.18 幂等保护：列已存在则跳过\n        if (Schema::hasColumn('{table}', '{col}')) {{\n            return;\n        }}\n\n"
    new_content, n = up_pattern.subn(r"\1" + up_guard, content, count=1)
    if not n:
        return content

    # down()：如果有 down 函数，添加 hasColumn ! 守卫
    down_pattern = re.compile(
        r"(public function down\(\): void\s*\{\s*\n)",
        re.MULTILINE,
    )
    down_guard = f"        // v0.3.18 幂等保护：列不存在则跳过 rollback\n        if (!Schema::hasColumn('{table}', '{col}')) {{\n            return;\n        }}\n\n"
    new_content, n2 = down_pattern.subn(r"\1" + down_guard, new_content, count=1)
    return new_content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='预览，不写文件')
    parser.add_argument('--dir', default='pc-api/database/migrations')
    args = parser.parse_args()

    files = sorted(glob.glob(f'{args.dir}/*.php'))
    print(f'扫描 {len(files)} 个 migration\n')

    stats = {'create': 0, 'add_columns': 0, 'alter_only': 0, 'db_op': 0, 'skipped_guarded': 0, 'unknown': 0}

    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        fname = Path(f).name

        # 跳过已有守卫的（v0.3.17 加过的）
        if 'hasColumn' in content or 'hasTable' in content:
            stats['skipped_guarded'] += 1
            continue

        pattern = detect_pattern(content)
        if pattern == 'create':
            table, _ = extract_table_and_first_col(content)
            if not table:
                stats['unknown'] += 1
                continue
            new_content = inject_create_guard(content, table)
            if new_content == content:
                continue
            stats['create'] += 1
            print(f'  CREATE   {fname}  → guard hasTable({table})')
            if not args.dry_run:
                with open(f, 'w', encoding='utf-8') as fp:
                    fp.write(new_content)

        elif pattern == 'add_columns':
            table, col = extract_table_and_first_col(content)
            if not table or not col:
                stats['unknown'] += 1
                continue
            new_content = inject_alter_guard(content, table, col)
            if new_content == content:
                continue
            stats['add_columns'] += 1
            print(f'  ALTER    {fname}  → guard hasColumn({table}, {col})')
            if not args.dry_run:
                with open(f, 'w', encoding='utf-8') as fp:
                    fp.write(new_content)

        elif pattern == 'alter_only':
            # ->change() / dropForeign 类不能加 hasColumn 守卫（可能列已存在但需要 alter）
            # 跳过，只在 release notes 标为手工检查
            stats['alter_only'] += 1

        elif pattern == 'db_op':
            # DB::table 操作天然幂等（insertOrIgnore / where delete）
            stats['db_op'] += 1

        else:
            stats['unknown'] += 1
            print(f'  ???      {fname}')

    print(f'\n统计:')
    print(f'  create guard 加:  {stats["create"]}')
    print(f'  alter guard 加:   {stats["add_columns"]}')
    print(f'  alter_only 跳过:  {stats["alter_only"]}  (change()/dropForeign 类)')
    print(f'  db_op 跳过:       {stats["db_op"]}  (天然幂等)')
    print(f'  guarded 跳过:     {stats["skipped_guarded"]}  (v0.3.17 已加)')
    print(f'  unknown:          {stats["unknown"]}')


if __name__ == '__main__':
    main()
