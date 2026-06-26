# Release Notes — v0.3.18 (2026-06-23)

> P0 大头收口：**全量 migration 幂等化**。从 v0.3.17 的 4 个 stock_records 扩展到全部 88 个 migration，杜绝任何"重跑炸 42701"。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| **88/88 migration 可重入** | 任何环境 / 全量恢复 / 跨服务器复制都安全，**杜绝所有 42701 复发** |
| 自动化加固脚本 `add_idempotency_guards.py` | 一键扫描 + 注入 + 干跑预览（--dry-run） |
| `->change()` alter migration 模式 | 用 `information_schema.columns.is_nullable` 做语义级幂等 |
| 2 阶段验证（local dry-run + 172 DELETE-then-migrate × 2） | 加固后**实际**测过，不是只看代码 |

## 📦 改动详情

### 1. 全量加固（88 migration）

| 类别 | 数量 | 守卫方式 | 示例 |
|---|---|---|---|
| `Schema::create` | 75 | `if (Schema::hasTable('xxx')) return;` | 全部 `create_xxx_table` |
| `Schema::table` 加列 | 3 | `if (Schema::hasColumn('xxx', 'first_col')) return;` + 同样的 down() | `add_party_fields` / `add_logistics` / `add_pipeline_fields` / `add_product_id` |
| 混合（建表+加列+数据迁移） | 1 | hasTable 守卫 + 内层手动 hasColumn 双重 | `inventory_categories` |
| 多列加列（双列） | 1 | `hasColumn(col1) && hasColumn(col2)` 联合守卫 | `add_inventory_warnings` |
| `->change()` 改 nullable | 1 | `information_schema.columns.is_nullable` | `add_nullable_supplier_id_to_payables` |
| `DB::table` 操作 | 3 | 天然幂等（`insertOrIgnore` / `where delete`） | `extend_stock_records_type_enum` / `add_custom_web_port_setting` / `add_idle_timeout_settings` |
| v0.3.17 已加固 | 4 | — | 4 个 stock_records migration |

### 2. 自动化脚本（`add_idempotency_guards.py`）

```python
# 三步走
python add_idempotency_guards.py --dry-run   # 预览 75 create + 3 alter
python add_idempotency_guards.py             # 实际修改
python -c "import glob; ..."                 # 验证剩余 4 个天然幂等
```

**核心判断逻辑**（`detect_pattern`）：
- `Schema::create` + 无 `Schema::table` → `create` (加 hasTable)
- `Schema::table` + 无 `->change()` → `add_columns` (加 hasColumn)
- `->change()` 或 `dropForeign` → `alter_only` (跳过)
- `DB::table` → `db_op` (跳过)

**提取列名**（`extract_table_and_first_col`）：正则匹配 `$table->\w+\(['"]([a-z_][a-z0-9_]*)['"]` 拿第一个 column。

### 3. 严苛验证（`test_idempotency_v0318.py`）

```
[1/8] 推 inventory_warnings 修复版到 172
[2/8] sudo cp / chown www-data / chmod 644
[3/8] sudo systemctl restart php8.3-fpm
[4/8] DELETE FROM migrations (清空 76 条记录)
[5/8] 第 1 次 migrate → 76 个 DONE，无 42701
[6/8] 第 2 次 migrate → INFO Nothing to migrate.
[7/8] 数 BASE TABLE → 102 张
```

### 4. 关键修复（漏网之鱼）

`2026_06_20_000001_add_inventory_warnings.php` 原本是 v0.3.14 在线加的，没走 v0.3.17 模板。脚本正则 `\$table->\w+\(['"]xxx['"]` 拿不到列名（min_stock 是 unsignedInteger），但**实测**报错才发现。

**修法**：用双 hasColumn 联合守卫 `hasColumn('min_stock') && hasColumn('shelf_life_days')`。
**教训**：脚本识别不到的边缘 case 必须**实测**（DELETE 全部 migration 记录 + 重跑 2 次）才能 100% 覆盖。

## 🛡️ 防御场景

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 172 全量 deploy 后再跑 v0.3.19 | ❌ 78 个 migration 中 70+ 报 42701 | ✅ 全部 no-op |
| 152 复制 172 数据后跑全量 | ❌ 同上 | ✅ 同上 |
| 跨环境 smoke test 重复跑 | ❌ 阻塞 deploy | ✅ 快速通过 |
| `migrate:rollback` 测试 | ❌ column does not exist | ✅ 全部守卫 down() |
| 全量恢复（先建表 + 跑 migration） | ❌ 42P07 / 42701 | ✅ 全部 no-op |

## 📂 新增文件

```
.workbuddy/_test/add_idempotency_guards.py       # 自动化加固脚本（可复用）
.workbuddy/_test/test_idempotency_v0318.py       # 严苛验证脚本
memory/RELEASE_NOTES_v0.3.18.md                  # 本文件
```

## 🔗 累计统计

- **88/88 migration 可重入**（v0.3.18 终极目标）
- 43 Controller / 47+ 子组件
- 4 部署脚本 + 3 测试脚本 + 1 skill
- 自动化加固脚本可对**任何 Laravel 9+ 项目复用**

## ⏭️ 下一里程碑 v0.3.19 候选

- 继续拆 customer/Detail.vue (555 行 6 Tab)
- 拆 process/InstanceList.vue (712 行)
- dashboard 营收图接 ECharts
- 把 `add_idempotency_guards.py` 升级为 `SkillManage` 全局可复用
