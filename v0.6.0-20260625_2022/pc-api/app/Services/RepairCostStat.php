<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;

/**
 * V0.5.7 维修成本归集服务
 *
 * 4 个维度汇总:
 *   - byMonth     月度成本 (按 created_at 月份)
 *   - byProject   按项目
 *   - byCustomer  按客户
 *   - byMethod    按维修方式 (4 选 1)
 *
 * 全部从 repair_orders 主表聚合 (parts/labor/shipping/total_cost)
 * 状态过滤: 只算已完成 (completed/closed), 排除 received/returned/cancelled
 */
class RepairCostStat
{
    /** 计入成本的完成状态 */
    public const COMPLETED_STATUSES = ['completed', 'closed', 'shipped_back'];

    /**
     * KPI 概览: 总成本/工时/件数/已完成数
     */
    public function overview(array $filters = []): array
    {
        [$where, $bindings] = $this->buildFilters($filters);

        $row = DB::selectOne("
            SELECT
                COUNT(*)                                            AS completed_orders,
                COALESCE(SUM(parts_cost),    0)::numeric(14,2)      AS total_parts_cost,
                COALESCE(SUM(labor_cost),    0)::numeric(14,2)      AS total_labor_cost,
                COALESCE(SUM(shipping_cost), 0)::numeric(14,2)      AS total_shipping_cost,
                COALESCE(SUM(total_cost),    0)::numeric(14,2)      AS total_cost,
                COALESCE(SUM(CASE WHEN is_warranty THEN total_cost ELSE 0 END), 0)::numeric(14,2) AS warranty_cost,
                COALESCE(SUM(CASE WHEN NOT is_warranty THEN total_cost ELSE 0 END), 0)::numeric(14,2) AS paid_cost
            FROM repair_orders
            WHERE status IN ('completed','closed','shipped_back')
              {$where}
        ", $bindings);

        // 工时从 repair_methods 聚合
        $hours = DB::selectOne("
            SELECT COALESCE(SUM(rm.hours_spent), 0)::numeric(10,2) AS total_hours
            FROM repair_methods rm
            JOIN repair_orders ro ON ro.id = rm.repair_order_id
            WHERE ro.status IN ('completed','closed','shipped_back')
              {$where}
        ", $bindings);

        return [
            'completed_orders'    => (int) $row->completed_orders,
            'total_parts_cost'    => (float) $row->total_parts_cost,
            'total_labor_cost'    => (float) $row->total_labor_cost,
            'total_shipping_cost' => (float) $row->total_shipping_cost,
            'total_cost'          => (float) $row->total_cost,
            'warranty_cost'       => (float) $row->warranty_cost,
            'paid_cost'           => (float) $row->paid_cost,
            'total_hours'         => (float) ($hours->total_hours ?? 0),
        ];
    }

    /**
     * 月度成本 (近 12 个月)
     */
    public function byMonth(int $months = 12, array $filters = []): array
    {
        [$where, $bindings] = $this->buildFilters($filters);
        $bindings['months'] = $months;

        $rows = DB::select("
            SELECT
                TO_CHAR(received_at, 'YYYY-MM')                    AS month,
                COUNT(*)                                            AS orders_count,
                COALESCE(SUM(parts_cost),    0)::numeric(14,2)      AS parts_cost,
                COALESCE(SUM(labor_cost),    0)::numeric(14,2)      AS labor_cost,
                COALESCE(SUM(shipping_cost), 0)::numeric(14,2)      AS shipping_cost,
                COALESCE(SUM(total_cost),    0)::numeric(14,2)      AS total_cost
            FROM repair_orders
            WHERE status IN ('completed','closed','shipped_back')
              AND received_at >= (CURRENT_DATE - (:months || ' months')::interval)
              {$where}
            GROUP BY month
            ORDER BY month DESC
        ", $bindings);

        return array_map(fn($r) => [
            'month'         => $r->month,
            'orders_count'  => (int) $r->orders_count,
            'parts_cost'    => (float) $r->parts_cost,
            'labor_cost'    => (float) $r->labor_cost,
            'shipping_cost' => (float) $r->shipping_cost,
            'total_cost'    => (float) $r->total_cost,
        ], $rows);
    }

    /**
     * 按项目汇总
     */
    public function byProject(array $filters = []): array
    {
        [$where, $bindings] = $this->buildFilters($filters);

        $rows = DB::select("
            SELECT
                ro.project_id,
                COALESCE(p.name, '未关联项目')                     AS project_name,
                COALESCE(p.project_no, '')                        AS project_code,
                COUNT(*)                                            AS orders_count,
                COALESCE(SUM(ro.total_cost), 0)::numeric(14,2)     AS total_cost
            FROM repair_orders ro
            LEFT JOIN projects p ON p.id = ro.project_id
            WHERE ro.status IN ('completed','closed','shipped_back')
              {$where}
            GROUP BY ro.project_id, p.name, p.project_no
            ORDER BY total_cost DESC
            LIMIT 50
        ", $bindings);

        return array_map(fn($r) => [
            'project_id'   => $r->project_id ? (int) $r->project_id : null,
            'project_name' => $r->project_name,
            'project_code' => $r->project_code,
            'orders_count' => (int) $r->orders_count,
            'total_cost'   => (float) $r->total_cost,
        ], $rows);
    }

    /**
     * 按客户汇总
     */
    public function byCustomer(array $filters = []): array
    {
        [$where, $bindings] = $this->buildFilters($filters);

        $rows = DB::select("
            SELECT
                ro.customer_id,
                COALESCE(c.name, '未关联客户')                    AS customer_name,
                COUNT(*)                                            AS orders_count,
                COALESCE(SUM(ro.total_cost), 0)::numeric(14,2)     AS total_cost,
                COALESCE(SUM(CASE WHEN ro.is_warranty THEN ro.total_cost ELSE 0 END), 0)::numeric(14,2) AS warranty_cost,
                COALESCE(SUM(CASE WHEN NOT ro.is_warranty THEN ro.total_cost ELSE 0 END), 0)::numeric(14,2) AS paid_cost
            FROM repair_orders ro
            LEFT JOIN customers c ON c.id = ro.customer_id
            WHERE ro.status IN ('completed','closed','shipped_back')
              {$where}
            GROUP BY ro.customer_id, c.name
            ORDER BY total_cost DESC
            LIMIT 50
        ", $bindings);

        return array_map(fn($r) => [
            'customer_id'   => $r->customer_id ? (int) $r->customer_id : null,
            'customer_name' => $r->customer_name,
            'orders_count'  => (int) $r->orders_count,
            'total_cost'    => (float) $r->total_cost,
            'warranty_cost' => (float) $r->warranty_cost,
            'paid_cost'     => (float) $r->paid_cost,
        ], $rows);
    }

    /**
     * 按维修方式 (4 选 1) 汇总
     */
    public function byMethod(array $filters = []): array
    {
        [$where, $bindings] = $this->buildFilters($filters);

        $rows = DB::select("
            SELECT
                COALESCE(ro.method_type, 'unspecified')           AS method_type,
                COUNT(*)                                            AS orders_count,
                COALESCE(SUM(ro.total_cost), 0)::numeric(14,2)     AS total_cost
            FROM repair_orders ro
            WHERE ro.status IN ('completed','closed','shipped_back')
              {$where}
            GROUP BY method_type
            ORDER BY total_cost DESC
        ", $bindings);

        // 计算占比
        $total = array_sum(array_column($rows, 'total_cost'));

        return array_map(function($r) use ($total) {
            $cost = (float) $r->total_cost;
            return [
                'method_type'  => $r->method_type,
                'orders_count' => (int) $r->orders_count,
                'total_cost'   => $cost,
                'percentage'   => $total > 0 ? round($cost / $total * 100, 2) : 0,
            ];
        }, $rows);
    }

    /**
     * 本月售后成本 (dashboard 卡片用)
     */
    public function thisMonth(): array
    {
        $rows = DB::selectOne("
            SELECT
                COALESCE(SUM(total_cost), 0)::numeric(14,2) AS cost,
                COUNT(*)                                    AS orders_count
            FROM repair_orders
            WHERE status IN ('completed','closed','shipped_back')
              AND DATE_TRUNC('month', received_at) = DATE_TRUNC('month', CURRENT_DATE)
        ");

        $total = DB::selectOne("
            SELECT COALESCE(SUM(COALESCE(budget_device,0) + COALESCE(budget_material,0) + COALESCE(budget_labor,0) + COALESCE(budget_outsource,0) + COALESCE(budget_other,0)), 0)::numeric(14,2) AS total
            FROM projects
            WHERE status IN ('active', 'completed', 'warranty')
        ");

        $cost = (float) $rows->cost;
        $totalContract = (float) ($total->total ?? 0);
        $ratio = $totalContract > 0 ? round($cost / $totalContract * 100, 2) : 0;

        return [
            'cost'           => $cost,
            'orders_count'   => (int) $rows->orders_count,
            'total_contract' => $totalContract,
            'ratio'          => $ratio, // 售后成本 / 合同金额 (%)
        ];
    }

    /**
     * 构造 WHERE 子句和参数绑定
     */
    private function buildFilters(array $filters): array
    {
        $clauses = [];
        $bindings = [];

        if (!empty($filters['from'])) {
            $clauses[] = 'AND received_at >= :from';
            $bindings['from'] = $filters['from'] . ' 00:00:00';
        }
        if (!empty($filters['to'])) {
            $clauses[] = 'AND received_at <= :to';
            $bindings['to'] = $filters['to'] . ' 23:59:59';
        }
        if (!empty($filters['customer_id'])) {
            $clauses[] = 'AND ro.customer_id = :customer_id';
            $bindings['customer_id'] = (int) $filters['customer_id'];
        }
        if (!empty($filters['project_id'])) {
            $clauses[] = 'AND ro.project_id = :project_id';
            $bindings['project_id'] = (int) $filters['project_id'];
        }
        if (!empty($filters['method_type'])) {
            $clauses[] = 'AND ro.method_type = :method_type';
            $bindings['method_type'] = $filters['method_type'];
        }
        if (!empty($filters['is_warranty'])) {
            $clauses[] = 'AND ro.is_warranty = :is_warranty';
            $bindings['is_warranty'] = filter_var($filters['is_warranty'], FILTER_VALIDATE_BOOLEAN);
        }

        return [implode("\n  ", $clauses), $bindings];
    }
}
