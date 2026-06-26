# OA 运维手册 (OPS RUNBOOK)

> 适用: 172.20.0.139 / nbcy / Ubuntu 24.04 / 单台生产
> 最后更新: 2026-06-20

## 服务清单

| 服务 | 类型 | 端口 | 配置 |
|------|------|------|------|
| nginx | systemd | 80, 443 | `/etc/nginx/sites-available/oa-api` |
| php8.3-fpm | systemd | `/run/php/php8.3-fpm.sock` | `/etc/php/8.3/fpm/` |
| postgresql | systemd | 5432 | `/etc/postgresql/16/main/` |
| oa-api (Laravel) | php-fpm | 127.0.0.1:3001 | `/var/www/oa-api` |
| ufw | firewall | 22/80/443/3001 | `sudo ufw status` |

## 启停命令

```bash
# 单服务
sudo systemctl status nginx
sudo systemctl restart nginx
sudo systemctl restart php8.3-fpm
sudo systemctl restart postgresql

# 全栈
sudo systemctl restart postgresql php8.3-fpm nginx

# 验证
sudo systemctl is-active nginx php8.3-fpm postgresql
curl -s http://127.0.0.1:3001/api/health
```

## 部署

> 单台机器的 "金丝雀" = 重启前 nginx → 平滑 reload

```bash
# 1. 拉代码
cd /var/www/oa-api
sudo -u www-data git pull

# 2. 安装依赖 (生产)
sudo -u www-data composer install --no-dev --optimize-autoloader

# 3. 跑迁移
sudo -u www-data php artisan migrate --force

# 4. 清缓存
sudo -u www-data php artisan config:cache
sudo -u www-data php artisan route:cache
sudo -u www-data php artisan view:cache

# 5. 重启 PHP-FPM
sudo systemctl reload php8.3-fpm

# 6. 验证
curl -s http://127.0.0.1:3001/api/health
```

> 自动化脚本: `.workbuddy/deploy_api.py` (本地机器跑)

## 备份 / 恢复

```bash
# 立即备份 DB
sudo /usr/local/bin/backup-oa.sh

# 立即备份文件
sudo /usr/local/bin/backup-oa-files.sh

# 列出备份
ls -lh /var/backups/oa/db/
ls -lh /var/backups/oa/files/

# 恢复 DB
sudo systemctl stop php8.3-fpm
PGPASSWORD='oa_pg_pwd_782997781' pg_restore \
  -h 127.0.0.1 -U oa_user -d security_oa \
  --clean --if-exists --no-owner \
  /var/backups/oa/db/oa-DATE.sql.gz
sudo systemctl start php8.3-fpm
```

详细: `docs/DISASTER-RECOVERY.md`

## 监控

| 项 | 频率 | 位置 |
|----|------|------|
| 服务存活 + /api/health | 5 min | `/var/log/oa-monitor.log` |
| 备份日志 | 每日 03:00 | `/var/log/oa-backup.log` |
| Laravel 应用日志 | 实时 | `/var/www/oa-api/storage/logs/laravel.log` |
| Nginx 访问日志 | 实时 | `/var/log/nginx/oa-api.access.log` |
| PostgreSQL 日志 | 实时 | `/var/log/postgresql/postgresql-16-main.log` |

手动跑监控:
```bash
bash /usr/local/bin/oa-monitor.sh && tail -3 /var/log/oa-monitor.log
```

## cron 任务

> 安装位置: **root crontab** (`sudo crontab -l`),不是 nbcy。
> 因为备份脚本需要 chmod 700 / 写 root 拥有的日志文件,放 nbcy 会出现权限问题。

```bash
sudo crontab -l
```
```
0 3 * * * /usr/local/bin/backup-oa.sh >> /var/log/oa-backup.log 2>&1
15 3 * * * /usr/local/bin/backup-oa-files.sh >> /var/log/oa-backup.log 2>&1
*/5 * * * * /usr/local/bin/oa-monitor.sh >> /var/log/oa-monitor.log 2>&1
```

## 防火墙

```bash
sudo ufw status verbose
sudo ufw status numbered
# 拒绝某个 IP 攻击:  sudo ufw insert 1 deny from 1.2.3.4
```

## 紧急联系 (占位)

| 角色 | 联系人 | 渠道 | 响应时间 |
|------|--------|------|----------|
| 系统运维 | <待填> | 电话 / 微信 | 15 min |
| DBA | <待填> | 电话 | 30 min |
| 业务方 | <待填> | 企业微信 | 1 hour |
| 上级审批 | <待填> | 电话 | 1 hour |

## 待办 (生产化清单)

- [ ] 真实域名 + certbot (HTTPS, 强 TLS 1.3)
- [ ] 告警 webhook 接入企业微信 / 钉钉
- [ ] WAL 流复制 → RPO < 5min
- [ ] 异地 S3 / OSS 同步,替代 `/var/backups/oa-offsite` 占位
- [ ] Prometheus + Grafana (可视化指标)
- [ ] Sentry (异常聚合)
- [ ] fail2ban (防 SSH 爆破)
- [ ] 季度 DR 演练

## 文档清单

- `docs/ALERTING.md` - 告警与监控接入
- `docs/DISASTER-RECOVERY.md` - 灾备恢复
- `docs/OPS-RUNBOOK.md` - 本文档
