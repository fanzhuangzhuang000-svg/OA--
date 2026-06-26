<?php

namespace App\Providers;

use App\Models\Customer;
use App\Models\EmployeeProfile;
use App\Models\ExpenseClaim;
use App\Models\InventoryItem;
use App\Models\KnowledgeArticle;
use App\Models\Payable;
use App\Models\Project;
use App\Models\PurchaseOrder;
use App\Models\Receivable;
use App\Models\ServiceOrder;
use App\Models\VehicleUsageRequest;
use App\Observers\AuditObserver;
use App\Services\ErrorReporter;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Database\Events\QueryExecuted;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 慢查询阈值（毫秒）— 超过则记 warning
     * 生产环境建议 200~500ms
     */
    private const SLOW_QUERY_THRESHOLD_MS = 500;

    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        // 这里手动注册 — 全局默认 1200 req/min, 按 IP 维度
        // (600/min 在 10 并发就接近上限, 调到 1200 给生产余量)
        // 登录和改密的 throttle:5,1 单独走更严的限流, 不受这个影响
        RateLimiter::for('api', function (Request $request) {
            return Limit::perMinute(1200)->by($request->ip());
        });

        // 注册审计 Observer 到所有核心业务 Model
        $watched = [
            Project::class,
            Customer::class,
            EmployeeProfile::class,
            ServiceOrder::class,
            ExpenseClaim::class,
            VehicleUsageRequest::class,
            InventoryItem::class,
            KnowledgeArticle::class,
            PurchaseOrder::class,
            Receivable::class,
            Payable::class,
            Role::class,
            Permission::class,
        ];
        foreach ($watched as $modelClass) {
            $modelClass::observe(AuditObserver::class);
        }

        // ===== T6 慢 SQL 监控 =====
        // 只在生产环境启用 — dev 环境查询慢是常态
        if (app()->environment('production')) {
            DB::listen(function (QueryExecuted $q) {
                if ($q->time > self::SLOW_QUERY_THRESHOLD_MS) {
                    $payload = [
                        'sql'      => $q->sql,
                        'bindings' => $this->sanitizeBindings($q->bindings),
                        'time_ms'  => $q->time,
                        'connection' => $q->connectionName,
                    ];
                    // 既写 daily 错误日志,又写 laravel.log (供日常排查)
                    Log::warning('SLOW_SQL', $payload);
                    ErrorReporter::warn('SLOW_SQL', $payload);
                }
            });
        }

        // V0.4.1 注册 Observer（实时记录项目实际成本）
        \App\Models\StockRecord::observe(\App\Observers\StockRecordObserver::class);
        \App\Models\ExpenseClaim::observe(\App\Observers\ExpenseClaimObserver::class);

        // V0.4.3 施工链路 Observer
        \App\Models\ConstructionLog::observe(\App\Observers\ConstructionLogObserver::class);
        \App\Models\ProjectCommencementOrder::observe(\App\Observers\CommencementOrderObserver::class);
        \App\Models\ExternalConstructionBid::observe(\App\Observers\ExternalConstructionBidObserver::class);
    }

    /**
     * 截断过长的 binding (避免日志爆掉)
     */
    private function sanitizeBindings(array $bindings): array
    {
        return array_map(function ($b) {
            if (is_string($b) && strlen($b) > 200) {
                return substr($b, 0, 200) . '...(truncated)';
            }
            return $b;
        }, $bindings);
    }
}
