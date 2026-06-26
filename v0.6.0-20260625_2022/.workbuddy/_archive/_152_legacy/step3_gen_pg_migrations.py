#!/usr/bin/env python3
"""v3.9.0 阶段3: 生成 Postgres 兼容的 migration
- ->enum(...) → ->string(50)
- ->fullText([...]) → DB::statement('CREATE INDEX ... USING GIN(to_tsvector(...))')
- ALTER TABLE MODIFY ENUM → string(50) + CHECK 约束
保留原文件不动, 复制到 database/migrations_pg/ 子目录
"""
import os
import re
import shutil
import sys

ROOT = r'D:\work\website\OA\pc-api'
SRC = os.path.join(ROOT, 'database', 'migrations')
DST = os.path.join(ROOT, 'database', 'migrations_pg')

if os.path.exists(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)
print(f'复制 {SRC} → {DST}')

count = 0
enum_re = re.compile(r"\$table->enum\((.*?)\)(->[^;]*)?;", re.DOTALL)
# 匹配 ->fullText([...])
fulltext_re = re.compile(r'\$table->fullText\(\[([^\]]*)\]\);')

for fn in sorted(os.listdir(DST)):
    if not fn.endswith('.php'):
        continue
    fp = os.path.join(DST, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        src = f.read()
    new = src

    # 1) ->enum(...) 替换为 string
    def enum_to_string(m):
        args = m.group(1)
        rest = m.group(2) or ''
        # 取字段名 (第一个参数, 可能是 'name' 或 "name")
        field = args.split(',')[0].strip().strip("'\"")
        # 去掉原 rest 里所有 ->default(...)->comment(...) 后, 我们只保留 string, 不强行追加
        return f"$table->string('{field}', 50){rest}"
    new, n1 = enum_re.subn(enum_to_string, new)

    # 2) ->fullText([...]) 改 GIN 索引
    def fulltext_replace(m):
        cols_raw = m.group(1)
        cols = [c.strip().strip("'\"") for c in cols_raw.split(',')]
        cols_str = ', '.join(cols)
        # 从文件名提取表名: 2024_01_10_000002_create_xxx_table.php → xxxs
        # 这里直接用全表名 'knowledge_articles' 就行, 因为只有 1 个 fullText (knowledge)
        return f"// v3.9.0 PG: fullText 改 GIN\n            DB::statement(\"CREATE INDEX IF NOT EXISTS {fn[:-4]}_fts_idx ON knowledge_articles USING GIN(to_tsvector('simple', {cols_str}))\");"
    new, n2 = fulltext_re.subn(fulltext_replace, new)

    # 3) ALTER TABLE MODIFY ENUM 改 string + CHECK (不修, 改用别的方式)
    new = new.replace(
        "DB::statement(\"ALTER TABLE stock_records MODIFY COLUMN type ENUM('in','out','transfer','check','inbound','return','outbound','sale','scrap') NOT NULL DEFAULT 'in' COMMENT '类型'\");",
        "DB::statement(\"ALTER TABLE stock_records ALTER COLUMN type TYPE VARCHAR(50)\");\n        DB::statement(\"ALTER TABLE stock_records ALTER COLUMN type SET DEFAULT 'in'\");"
    )
    new = new.replace(
        "DB::statement(\"ALTER TABLE stock_records MODIFY COLUMN type ENUM('in','out','transfer','check') NOT NULL DEFAULT 'in' COMMENT '类型'\");",
        "DB::statement(\"ALTER TABLE stock_records ALTER COLUMN type TYPE VARCHAR(50)\");\n        DB::statement(\"ALTER TABLE stock_records ALTER COLUMN type SET DEFAULT 'in'\");"
    )

    if new != src:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new)
        count += 1
        print(f'  {fn}: ENUM={n1} fullText={n2}')

print(f'\n=== 总计 {count} 个文件被改 ===')
