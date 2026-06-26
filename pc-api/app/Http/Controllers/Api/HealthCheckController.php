<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Str;

/**
 * 健康检查控制器 — V1.1 增强版
 *
 * 端点:
 *   GET /api/health              — 综合健康检查（公开，无需认证）
 *   GET /api/health/ready        — 就绪探针（K8s readinessProbe）
 *   GET /api/health/live         — 存活探针（K8s livenessProbe）
 *   GET /api/health/metrics      — Prometheus 格式指标（需认证）
 *
 * 用途:
 *   1. 负载均衡器后端健康检查
 *   2. Kubernetes / Docker 探针
 *   3. 外部监控系统 (UptimeRobot, Pingdom, Zabbix)
 *   4. CI/CD 部署后验证
 */
class HealthCheckController extends Controller
{
    /**
     * GET /api/health — 综合健康检查
     *
     * 返回所有子系统的健康状态。
     * 任何关键子系统故障时返回 HTTP 503。
     */
    public function check(Request $request): JsonResponse
    {
        $start = microtime(true);
        $checks = [];
        $allHealthy = true;

        // 1. 应用基础信息
        $checks['app'] = [
            'status'       => 'ok',
            'name'         => config('app.name'),
            'environment'  => app()->environment(),
            'php_version'  => PHP_VERSION,
            'laravel'      => app()->version(),
            'debug_mode'   => (bool) config('app.debug'),
        ];

        // 2. 数据库检查
        $dbResult = $this->checkDatabase();
        $checks['database'] = $dbResult;
        if ($dbResult['status'] !== 'ok') {
            $allHealthy = false;
        }

        // 3. 缓存检查
        $cacheResult = $this->checkCache();
        $checks['cache'] = $cacheResult;
        if ($cacheResult['status'] !== 'ok') {
            $allHealthy = false;
        }

        // 4. Redis 检查（如果启用）
        if (config('cache.default') === 'redis' || config('database.redis.client') === 'phpredis') {
            $redisResult = $this->checkRedis();
            $checks['redis'] = $redisResult;
            if ($redisResult['status'] !== 'ok') {
                $allHealthy = false;
            }
        }

        // 5. 文件系统检查
        $storageResult = $this->checkStorage();
        $checks['storage'] = $storageResult;
        if ($storageResult['status'] !== 'ok') {
            $allHealthy = false;
        }

        // 6. 磁盘空间检查
        $diskResult = $this->checkDisk();
        $checks['disk'] = $diskResult;
        if ($diskResult['status'] === 'critical') {
            $allHealthy = false;
        }

        // 7. 队列检查
        $queueResult = $this->checkQueue();
        $checks['queue'] = $queueResult;

        $duration = round((microtime(true) - $start) * 1000, 2);

        $response = [
            'code'    => $allHealthy ? 0 : 1001,
            'message' => $allHealthy ? 'healthy' : 'degraded',
            'data'    => [
                'status'    => $allHealthy ? 'healthy' : 'degraded',
                'timestamp' => now()->toIso8601String(),
                'duration'  => "{$duration}ms",
                'checks'    => $checks,
            ],
        ];

        return response()->json($response, $allHealthy ? 200 : 503)
            ->header('Cache-Control', 'no-cache, no-store, must-revalidate');
    }

    /**
     * GET /api/health/ready — 就绪探针
     *
     * 检查应用是否准备好接受流量。
     * 用于 Kubernetes readinessProbe 或负载均衡器健康检查。
     */
    public function ready(): JsonResponse
    {
        try {
            DB::select('SELECT 1');
            return response()->json(['status' => 'ready'], 200);
        } catch (\Throwable $e) {
            return response()->json(['status' => 'not_ready', 'reason' => 'database_unavailable'], 503);
        }
    }

    /**
     * GET /api/health/live — 存活探针
     *
     * 最简检查，仅确认进程存活。
     * 用于 Kubernetes livenessProbe。
     */
    public function live(): JsonResponse
    {
        return response()->json(['status' => 'alive', 'timestamp' => now()->toIso8601String()], 200);
    }

    /**
     * GET /api/health/metrics — Prometheus 格式指标
     *
     * 输出 Prometheus exposition format，可直接被 Prometheus 抓取。
     * 需要认证（避免暴露内部指标）。
     */
    public function metrics(): JsonResponse
    {
        $lines = [];

        // 应用信息
        $lines[] = '# HELP oa_app_info Application information';
        $lines[] = '# TYPE oa_app_info gauge';
        $lines[] = 'oa_app_info{version="' . app()->version() . '",php="' . PHP_VERSION . '",env="' . app()->environment() . '"} 1';

        // 数据库连接数
        try {
            $conn = DB::selectOne("SELECT count(*) AS cnt FROM pg_stat_activity WHERE datname = current_database()");
            $lines[] = '# HELP oa_db_connections Current database connections';
            $lines[] = '# TYPE oa_db_connections gauge';
            $lines[] = 'oa_db_connections ' . (int) $conn->cnt;
        } catch (\Throwable $e) {
            $lines[] = 'oa_db_connections -1';
        }

        // 缓存命中率
        try {
            $cache = DB::selectOne("SELECT CASE WHEN (blks_hit + blks_read) = 0 THEN 0 ELSE round(blks_hit::numeric / (blks_hit + blks_read) * 100, 2) END AS hit_rate FROM pg_stat_database WHERE datname = current_database()");
            $lines[] = '# HELP oa_db_cache_hit_rate Database cache hit rate percent';
            $lines[] = '# TYPE oa_db_cache_hit_rate gauge';
            $lines[] = 'oa_db_cache_hit_rate ' . (float) ($cache->hit_rate ?? 0);
        } catch (\Throwable $e) {
            $lines[] = 'oa_db_cache_hit_rate -1';
        }

        // 磁盘使用率
        $rootTotal = @disk_total_space('/');
        $rootFree  = @disk_free_space('/');
        if ($rootTotal !== false && $rootFree !== false) {
            $usedPercent = round(($rootTotal - $rootFree) / $rootTotal * 100, 1);
            $lines[] = '# HELP oa_disk_usage_percent Root disk usage percent';
            $lines[] = '# TYPE oa_disk_usage_percent gauge';
            $lines[] = 'oa_disk_usage_percent ' . $usedPercent;
        }

        // 系统负载
        $load = sys_getloadavg();
        $lines[] = '# HELP oa_load_average System load average';
        $lines[] = '# TYPE oa_load_average gauge';
        $lines[] = 'oa_load_average{window="1m"} ' . ($load[0] ?? 0);
        $lines[] = 'oa_load_average{window="5m"} ' . ($load[1] ?? 0);
        $lines[] = 'oa_load_average{window="15m"} ' . ($load[2] ?? 0);

        return response(implode("\n", $lines) . "\n", 200)
            ->header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
    }

    // ========== 私有检查方法 ==========

    private function checkDatabase(): array
    {
        try {
            $start = microtime(true);
            $result = DB::select('SELECT 1 AS ok');
            $duration = round((microtime(true) - $start) * 1000, 2);

            if (empty($result) || $result[0]->ok != 1) {
                return ['status' => 'error', 'message' => 'unexpected result'];
            }

            return [
                'status'   => 'ok',
                'driver'   => config('database.default'),
                'latency'  => "{$duration}ms",
            ];
        } catch (\Throwable $e) {
            Log::error('Health check: database failed', ['error' => $e->getMessage()]);
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    private function checkCache(): array
    {
        try {
            $key = '_health_check_' . Str::random(8);
            $start = microtime(true);
            Cache::put($key, 'ok', 5);
            $value = Cache::get($key);
            Cache::forget($key);
            $duration = round((microtime(true) - $start) * 1000, 2);

            return [
                'status'  => $value === 'ok' ? 'ok' : 'error',
                'driver'  => config('cache.default'),
                'latency' => "{$duration}ms",
            ];
        } catch (\Throwable $e) {
            Log::error('Health check: cache failed', ['error' => $e->getMessage()]);
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    private function checkRedis(): array
    {
        try {
            $start = microtime(true);
            $pong = Redis::ping();
            $duration = round((microtime(true) - $start) * 1000, 2);

            return [
                'status'  => ($pong === true || $pong === 'PONG') ? 'ok' : 'error',
                'latency' => "{$duration}ms",
            ];
        } catch (\Throwable $e) {
            Log::error('Health check: redis failed', ['error' => $e->getMessage()]);
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    private function checkStorage(): array
    {
        try {
            $testFile = storage_path('framework/cache/.health_check');
            $start = microtime(true);
            file_put_contents($testFile, 'ok');
            $read = file_get_contents($testFile);
            @unlink($testFile);
            $duration = round((microtime(true) - $start) * 1000, 2);

            return [
                'status'  => $read === 'ok' ? 'ok' : 'error',
                'latency' => "{$duration}ms",
            ];
        } catch (\Throwable $e) {
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    private function checkDisk(): array
    {
        $rootTotal = @disk_total_space('/');
        $rootFree  = @disk_free_space('/');

        if ($rootTotal === false || $rootFree === false) {
            return ['status' => 'unknown'];
        }

        $usedPercent = round(($rootTotal - $rootFree) / $rootTotal * 100, 1);
        $warnThreshold = config('monitoring.health.disk_warn_percent', 85);
        $critThreshold = config('monitoring.health.disk_crit_percent', 95);

        $status = 'ok';
        if ($usedPercent >= $critThreshold) {
            $status = 'critical';
        } elseif ($usedPercent >= $warnThreshold) {
            $status = 'warning';
        }

        return [
            'status'      => $status,
            'total'       => $this->formatBytes($rootTotal),
            'free'        => $this->formatBytes($rootFree),
            'used_percent' => $usedPercent,
        ];
    }

    private function checkQueue(): array
    {
        try {
            $driver = config('queue.default');
            if ($driver === 'sync') {
                return ['status' => 'ok', 'driver' => 'sync', 'note' => 'synchronous, no queue depth'];
            }

            // 仅对 database 驱动做深度检查
            if ($driver === 'database') {
                $pending = DB::table('jobs')->count();
                $failed  = DB::table('failed_jobs')->count();
                return [
                    'status'  => 'ok',
                    'driver'  => 'database',
                    'pending' => $pending,
                    'failed'  => $failed,
                ];
            }

            return ['status' => 'ok', 'driver' => $driver];
        } catch (\Throwable $e) {
            return ['status' => 'unknown', 'message' => $e->getMessage()];
        }
    }

    private function formatBytes(int $bytes): string
    {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];
        $i = 0;
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes /= 1024;
            $i++;
        }
        return round($bytes, 1) . ' ' . $units[$i];
    }
}
