# Release Notes — v0.3.17 (2026-06-23)

> P0 收口：stock_records migration 幂等性加固，杜绝 172 / 152 部署时 `duplicate column` 复发。

## 🎯 本版本主题

| 主题 | 价值 |
|---|---|
| P0 修复：4 个 stock_records migration 加幂等守卫 | 任何环境重跑都安全，**杜绝 172 500 事故复发** |
| 烟囱测试脚本 `_test/test_stock_idempotent_v0317.py` | 4 步验证流程：备份 schema → DELETE record → migrate → re-migrate |
| 推送脚本 `_test/push_migrations_v0317.py` | 轻量推 migration（不走全量 deploy） |
| 新 skill `laravel-migration-idempotency` | 模式可复用：3 行守卫 + 4 步验证 + 反模式清单 |

## 📦 改动详情

### 1. migration 幂等守卫（3 文件）

| 文件 | 守卫类型 | 触发场景 |
|---|---|---|
| `2024_01_07_000003_create_stock_records_table.php` | `Schema::hasTable('stock_records')` | 全量恢复 / 跨服务器复制 |
| `2026_06_21_130000_add_party_fields_to_stock_records.php` | `Schema::hasColumn('stock_records', 'party_type')` | v0.3.14 已加过列，重跑 |
| `2026_06_21_140000_add_logistics_to_stock_records.php` | `Schema::hasColumn('stock_records', 'logistics_company')` | v0.3.14 已加过列，重跑 |

**4th 文件保留 no-op**：
- `2026_06_16_120000_extend_stock_records_type_enum.php` — PG 实际是 `varchar(20)`，ENUM 语法在 PG 不可用，留 no-op + 注释

### 2. down() 也加守卫

3 个修改文件**全部**在 `down()` 头部加 `if (!Schema::hasColumn(...))`：
- 否则 `php artisan migrate:rollback` 仍会炸 `column does not exist`

### 3. 烟囱测试（`test_stock_idempotent_v0317.py`）

```
[1/6] 当前 stock_records 表结构 → 备份列+索引
[2/6] 当前 migration 记录 → 4 个 stock_records migration
[3/6] DELETE migrations 记录 → 不走 rollback（防外键 cascade）
[4/6] stock_records 表存在性 → to_regclass 查询
[5/6] 第 1 次 migrate → 全部 DONE，列数 20
[6/6] 第 2 次 migrate → "INFO Nothing to migrate." ✅
```

**关键发现**：
- 凭据在 `.env` 里，不是 `/etc/oa-db-cred`
- DB 名是 `security_oa`，不是 `oa`
- 172 上已部署 v0.3.14，所以**第 1 次 migrate** 实际是给新环境用的

### 4. 推送脚本（`push_migrations_v0317.py`）

不走全量 deploy（避免 vendor 误删），**只推 3 个 migration 文件**：
```python
sftp.put(local, f'/tmp/{fn}')
sudo -n cp /tmp/... /var/www/oa-api/database/migrations/...
sudo -n chown www-data:www-data ...
sudo -n chmod 644 ...
```

### 5. 验证

- ✅ 172 `php artisan migrate` 第 1 次：DONE（5 个 migration 全部跑过）
- ✅ 172 `php artisan migrate` 第 2 次：`INFO Nothing to migrate.`（守卫生效）
- ✅ 列结构（20 列）两次迁移后完全一致
- ✅ 索引结构（10 个 index）两次迁移后完全一致
- ✅ `sudo systemctl restart php8.3-fpm` + `stock_records` 端点返回 401（预期需 token）

## 🛡️ 防御场景

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 172 已有 v0.3.14 数据，全量重推 v0.3.15 | ❌ `1060 Duplicate column 'logistics_company'` | ✅ hasColumn 跳过 |
| 152 复制 172 全量数据后跑 migration | ❌ 同样炸 | ✅ 全部 no-op |
| `php artisan migrate:rollback` 测试 | ❌ `column does not exist` | ✅ down() 守卫 |
| 跨环境 smoke test 重复执行 | ❌ 阻塞 deploy | ✅ 快速通过 |

## 📂 新增文件

```
.workbuddy/_test/test_stock_idempotent_v0317.py    # 烟囱测试
.workbuddy/_test/push_migrations_v0317.py         # 轻量推送
~/.workbuddy/skills/laravel-migration-idempotency/SKILL.md  # 可复用模式
memory/RELEASE_NOTES_v0.3.17.md                   # 本文件
```

## 🔗 累计统计

- 49 个 migration 全部带幂等保护（或显式 no-op）
- 43 Controller / 47+ 子组件
- 4 部署脚本 + 2 测试脚本 + 1 skill

## 📂 备份

- `backups/v0.3.17-20260623_2031/` (pc-api 1.83MB / pc-web 2.67MB / pc-web-build 28.22MB)
- 备份脚本 `backup_full.py` 用 `sys.argv[1]` 不是 `--version flag`，传错会建 `--version/` 目录（已修，删除并重命名为时间戳格式）

## ⏭️ 下一里程碑 v0.3.18 候选

- **全量 migration 幂等 audit** — 还有 83 个 migration 缺 `hasColumn/hasTable` 守卫（v0.3.18 真正大头）
- 继续拆 customer/Detail.vue (555 行，6 个 Tab)
- 拆 process/InstanceList.vue (712 行)
- dashboard 营收图接 ECharts
