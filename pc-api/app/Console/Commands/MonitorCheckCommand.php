<?php

namespace App\Console\Commands;

use App\Services\AlertService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

/**
 * 系统监控告警命令
 *
 * 定时运行（建议每 5 分钟），检查各项指标是否超过阈值，
 * 超过时自动通过 AlertService 发送告警通知。
 *
 * 用法:
 *   php artisan monitor:check           — 检查所有指标
 *   php artisan monitor:check --dry-run — 仅输出不发送告警
 *
 * 建议在 crontab 中配置:
 *   */5 * * * * cd /path/to/oa && php artisan monitor:check >> /dev/null 2>&1
 */
class MonitorCheckCommand extends Command
{
    protected $signature = 'monitor:check {--dry-run : 仅输出不发送告警}';
    protected $description = '检查系统监控指标并发送告警';

    /** 告警冷却时间（秒），同一告警在此时间内不重复发送 */
    private const COOLDOWN = 1800; // 30 分钟

    public function handle(): int
    {
        $dryRun = $this->option('dry-run');
        $this->info('🔍 开始系统监控检查...');
        $this->newLine();

        $alerts = [];

        // 1. 磁盘检查
        $alerts = array_merge($alerts, $this->checkDisk($dryRun));

        // 2. 数据库检查
        $alerts = array_merge($alerts, $this->checkDatabase($dryRun));

        // 3. 错误日志检查
        $alerts = array_merge($alerts, $this->checkErrorLogs($dryRun));

        // 4. 备份检查
        $alerts = array_merge($alerts, $this->checkBackups($dryRun));

        // 5. 系统负载
        $alerts = array_merge($alerts, $this->checkLoadAverage($dryRun));

        $this->newLine();
        if (empty($alerts)) {
            $this->info('✅ 所有指标正常，无需告警。');
        } else {
            $this->warn("⚠️  本次检查触发 " . count($alerts) . " 条告警:");
            foreach ($alerts as $alert) {
                $this->line("  • {$alert}");
            }
        }

        return self::SUCCESS;
    }

    private function checkDisk(bool $dryRun): array
    {
        $alerts = [];
        $rootTotal = @disk_total_space('/');
        $rootFree  = @disk_free_space('/');

        if ($rootTotal === false || $rootFree === false) {
            return $alerts;
        }

        $percent = round(($rootTotal - $rootFree) / $rootTotal * 100, 1);
        $warn = config('monitoring.thresholds.disk_warn_percent', 85);
        $crit = config('monitoring.thresholds.disk_crit_percent', 95);

        $this->line("💿 磁盘使用率: {$percent}% (warn={$warn}%, crit={$crit}%)");

        if ($percent >= $warn) {
            $key = 'alert_disk_' . floor($percent / 5) * 5;
            if ($this->shouldAlert($key)) {
                $alerts[] = "磁盘使用率 {$percent}%";
                if (!$dryRun) {
                    AlertService::diskWarning($percent);
                    $this->markAlerted($key);
                }
            }
        }

        return $alerts;
    }

    private function checkDatabase(bool $dryRun): array
    {
        $alerts = [];

        try {
            // 连接数
            $conn = DB::selectOne("SELECT count(*) AS cnt FROM pg_stat_activity WHERE datname = current_database()");
            $count = (int) $conn->cnt;
            $warn = config('monitoring.thresholds.db_connections_warn', 80);

            $this->line("🗄️  数据库连接数: {$count} (warn={$warn})");

            if ($count >= $warn) {
                $key = 'alert_db_conn_' . floor($count / 20) * 20;
                if ($this->shouldAlert($key)) {
                    $alerts[] = "数据库连接数 {$count}";
                    if (!$dryRun) {
                        AlertService::dbConnectionHigh($count);
                        $this->markAlerted($key);
                    }
                }
            }

            // 慢查询
            $slow = DB::selectOne("SELECT count(*) AS cnt FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > INTERVAL '1 second'");
            $slowCount = (int) $slow->cnt;
            $slowWarn = config('monitoring.thresholds.slow_queries_warn', 3);

            $this->line("🐢 慢查询数: {$slowCount} (warn={$slowWarn})");

            if ($slowCount >= $slowWarn) {
                $key = 'alert_slow_q_' . floor($slowCount / 3) * 3;
                if ($this->shouldAlert($key)) {
                    $alerts[] = "慢查询 {$slowCount} 条";
                    if (!$dryRun) {
                        AlertService::slowQueryAlert($slowCount);
                        $this->markAlerted($key);
                    }
                }
            }

            // 缓存命中率
            $cache = DB::selectOne("SELECT CASE WHEN (blks_hit + blks_read) = 0 THEN 0 ELSE round(blks_hit::numeric / (blks_hit + blks_read) * 100, 2) END AS hit_rate FROM pg_stat_database WHERE datname = current_database()");
            $hitRate = (float) ($cache->hit_rate ?? 100);
            $cacheWarn = config('monitoring.thresholds.cache_hit_rate_warn', 90);

            $this->line("📊 缓存命中率: {$hitRate}% (warn={$cacheWarn}%)");

            if ($hitRate < $cacheWarn && $hitRate > 0) {
                $key = 'alert_cache_hit';
                if ($this->shouldAlert($key)) {
                    $alerts[] = "缓存命中率 {$hitRate}%";
                    if (!$dryRun) {
                        AlertService::cacheHitRateLow($hitRate);
                        $this->markAlerted($key);
                    }
                }
            }
        } catch (\Throwable $e) {
            $this->error("❌ 数据库检查失败: {$e->getMessage()}");
            $alerts[] = "数据库连接失败";
            if (!$dryRun) {
                AlertService::serviceDown('PostgreSQL', $e->getMessage());
            }
        }

        return $alerts;
    }

    private function checkErrorLogs(bool $dryRun): array
    {
        $alerts = [];
        $logPath = storage_path('logs/laravel.log');

        if (!file_exists($logPath)) {
            $this->line("📝 错误日志: 文件不存在");
            return $alerts;
        }

        // 简单统计最近 24h 的 ERROR 行数
        $cutoff = time() - 86400;
        $errorCount = 0;
        $lines = @file($logPath, FILE_IGNORE_NEW_LINES) ?: [];
        $lines = array_slice($lines, -5000); // 只看最后 5000 行

        foreach ($lines as $line) {
            if (strpos($line, 'ERROR') === false) continue;
            if (preg_match('/^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]/', $line, $m)) {
                if (strtotime($m[1]) >= $cutoff) {
                    $errorCount++;
                }
            }
        }

        $warn = config('monitoring.thresholds.errors_24h_warn', 50);
        $this->line("📝 24h 错误数: {$errorCount} (warn={$warn})");

        if ($errorCount >= $warn) {
            $key = 'alert_errors_' . floor($errorCount / 50) * 50;
            if ($this->shouldAlert($key)) {
                $alerts[] = "24h 错误 {$errorCount} 条";
                if (!$dryRun) {
                    AlertService::errorSpike($errorCount);
                    $this->markAlerted($key);
                }
            }
        }

        return $alerts;
    }

    private function checkBackups(bool $dryRun): array
    {
        $alerts = [];
        $dir = storage_path('app/backups');

        if (!is_dir($dir)) {
            $this->line("💾 备份: 目录不存在");
            return $alerts;
        }

        $files = glob($dir . '/*.{sql.gz,tar.gz}', GLOB_BRACE);
        if (empty($files)) {
            $this->line("💾 备份: 无备份文件");
            $alerts[] = "无备份文件";
            if (!$dryRun) {
                $key = 'alert_no_backup';
                if ($this->shouldAlert($key)) {
                    AlertService::send('未找到任何备份文件', AlertService::LEVEL_WARNING);
                    $this->markAlerted($key);
                }
            }
            return $alerts;
        }

        $latest = max(array_map('filemtime', $files));
        $ageDays = round((time() - $latest) / 86400, 1);
        $warn = config('monitoring.thresholds.backup_age_warn', 3);

        $this->line("💾 最新备份: {$ageDays} 天前 (warn={$warn}天)");

        if ($ageDays >= $warn) {
            $key = 'alert_backup_age';
            if ($this->shouldAlert($key)) {
                $alerts[] = "备份过期 {$ageDays} 天";
                if (!$dryRun) {
                    AlertService::backupStale($ageDays);
                    $this->markAlerted($key);
                }
            }
        }

        return $alerts;
    }

    private function checkLoadAverage(bool $dryRun): array
    {
        $alerts = [];
        $load = sys_getloadavg();
        $load1 = $load[0] ?? 0;
        $warn = config('monitoring.thresholds.load_avg_warn', 4.0);

        $this->line("⚡ 系统负载 (1m): {$load1} (warn={$warn})");

        if ($load1 >= $warn) {
            $key = 'alert_load_' . floor($load1);
            if ($this->shouldAlert($key)) {
                $alerts[] = "系统负载 {$load1}";
                if (!$dryRun) {
                    AlertService::send("系统负载过高: {$load1}", AlertService::LEVEL_WARNING, [
                        'load_1m'  => $load[0] ?? 0,
                        'load_5m'  => $load[1] ?? 0,
                        'load_15m' => $load[2] ?? 0,
                    ]);
                    $this->markAlerted($key);
                }
            }
        }

        return $alerts;
    }

    /**
     * 检查是否在冷却期内（避免重复告警）
     */
    private function shouldAlert(string $key): bool
    {
        return !Cache::has($key);
    }

    /**
     * 标记已告警（设置冷却期）
     */
    private function markAlerted(string $key): void
    {
        Cache::put($key, true, self::COOLDOWN);
    }
}
