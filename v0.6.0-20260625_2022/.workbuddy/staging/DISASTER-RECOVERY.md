# 灾备恢复 (DISASTER RECOVERY)

## RPO / RTO 目标

| 指标 | 当前 | 生产目标 |
|------|------|----------|
| RPO (数据丢失) | 24 小时 | ≤ 1 小时 (备: 启用 WAL 流复制) |
| RTO (恢复时间) | 1 小时 | ≤ 30 分钟 |

> 现状为单台机器 + 每日 03:00 全量备份 + 15 分钟文件备份。
> 生产应再加 WAL 流复制 (Streaming Replication) 达到 RPO < 5min。

## 备份位置

- 数据库: `/var/backups/oa/db/oa-YYYY-MM-DD.sql.gz` (保留 30 天)
- 数据库异地: `/var/backups/oa-offsite/` (rsync 同步,占位)
- 应用文件: `/var/backups/oa/files/oa-files-YYYY-MM-DD.tar.gz` (保留 30 天)
- 备份日志: `/var/log/oa-backup.log`

## 单项恢复

### 数据库恢复 (整库覆盖)

```bash
# 1. 停 PHP-FPM 防止新写入
sudo systemctl stop php8.3-fpm

# 2. 列出备份内容确认
pg_restore -l /var/backups/oa/db/oa-2026-06-20.sql.gz | head

# 3. drop + restore (用 oa_user 权限)
PGPASSWORD='oa_pg_pwd_782997781' pg_restore \
  -h 127.0.0.1 -U oa_user -d security_oa \
  --clean --if-exists --no-owner --role=oa_user \
  /var/backups/oa/db/oa-2026-06-20.sql.gz

# 4. 启动
sudo systemctl start php8.3-fpm

# 5. 验证
curl -s http://127.0.0.1:3001/api/health
```

### 文件恢复 (附件 + storage/app)

```bash
# 备份到临时目录再 cp,避免直接覆盖损坏中
cd /var/www/oa-api
tar -xzf /var/backups/oa/files/oa-files-2026-06-20.tar.gz -C /tmp/oa-restore/

# 比对差异
diff -r storage/app /tmp/oa-restore/var/www/oa-api/storage/app | head

# 覆盖 (先备份当前)
sudo cp -a storage/app /var/backups/oa/app-$(date +%s).bak
sudo cp -a /tmp/oa-restore/var/www/oa-api/storage/app/* storage/app/
sudo chown -R www-data:www-data storage/app

# 清理
rm -rf /tmp/oa-restore
```

## 全量恢复 (整机重建)

**前提**: 已有 OS + Nginx + PHP + PostgreSQL,只恢复数据。

```bash
# 1. 拉代码
cd /var/www
sudo git clone <REPO_URL> oa-api
cd oa-api
sudo chown -R www-data:www-data .
sudo -u www-data composer install --no-dev

# 2. 配 .env (从备份服务器 / 1Password 拿)
sudo -u www-data cp .env.example .env
sudo -u www-data vim .env
#   DB_DATABASE=security_oa
#   DB_USERNAME=oa_user
#   DB_PASSWORD=oa_pg_pwd_782997781
sudo -u www-data php artisan key:generate
sudo -u www-data php artisan migrate --force

# 3. 恢复 DB
sudo systemctl stop php8.3-fpm
PGPASSWORD='oa_pg_pwd_782997781' pg_restore \
  -h 127.0.0.1 -U oa_user -d security_oa \
  --clean --if-exists --no-owner \
  /var/backups/oa/db/oa-LATEST.sql.gz
sudo systemctl start php8.3-fpm

# 4. 恢复文件
cd /var/www/oa-api
tar -xzf /var/backups/oa/files/oa-files-LATEST.tar.gz
sudo chown -R www-data:www-data storage

# 5. 验证
curl -s http://127.0.0.1:3001/api/health
sudo -u www-data php artisan tinker --execute='echo \App\Models\User::count();'
```

## 演练

- **频率**: 每月 1 次,选周日低峰
- **范围**: 数据库 + 文件各恢复一次到测试库
- **记录**: 用 `docs/DR-DRILL-LOG.md` 记录

```bash
# 测试库恢复演练 (不动生产)
sudo -u postgres createdb security_oa_drill
PGPASSWORD='oa_pg_pwd_782997781' pg_restore \
  -h 127.0.0.1 -U oa_user -d security_oa_drill \
  /var/backups/oa/db/oa-LATEST.sql.gz
# 验证后清理
sudo -u postgres dropdb security_oa_drill
```

## 待办
- [ ] 上 WAL 流复制 (备机)
- [ ] 异地 (S3 / OSS) 同步,替代 `/var/backups/oa-offsite` 占位
- [ ] 季度全量 DR 演练
- [ ] 备份加密 (GPG)
