<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use App\Concerns\HasDataScope;
use Carbon\Carbon;

/**
 * V0.4.5 质保期管理 - 质保服务工单
 *
 * 表: warranty_service_orders
 * 主键: id
 *
 * 状态机: pending → assigned → in_progress → completed
 *                              └→ cancelled
 */
class WarrantyServiceOrder extends Model
{
    use SoftDeletes, HasDataScope;

    protected $table = 'warranty_service_orders';

    protected $fillable = [
        'warranty_id', 'customer_id', 'device_id',
        'order_no', 'service_type', 'priority',
        'title', 'description',
        'scheduled_date', 'completed_date',
        'technician_id', 'fee', 'status',
        'result_notes', 'customer_signature',
        'created_by', 'completed_by',
    ];

    protected $casts = [
        'scheduled_date'  => 'date',
        'completed_date'  => 'date',
        'fee'             => 'decimal:2',
    ];

    /** 状态 */
    public const STATUS_PENDING     = 'pending';      // 待派工
    public const STATUS_ASSIGNED    = 'assigned';     // 已派工
    public const STATUS_IN_PROGRESS = 'in_progress';  // 进行中
    public const STATUS_COMPLETED   = 'completed';    // 已完成
    public const STATUS_CANCELLED   = 'cancelled';    // 已取消

    /** 服务类型 */
    public const SERVICE_TYPE_INSPECT   = 'inspect';    // 巡检
    public const SERVICE_TYPE_REPAIR    = 'repair';     // 维修
    public const SERVICE_TYPE_CLEAN     = 'clean';      // 清洁
    public const SERVICE_TYPE_CALIBRATE = 'calibrate';  // 校准
    public const SERVICE_TYPE_REPLACE   = 'replace';    // 更换

    /** 优先级 */
    public const PRIORITY_LOW    = 'low';
    public const PRIORITY_NORMAL = 'normal';
    public const PRIORITY_HIGH   = 'high';
    public const PRIORITY_URGENT = 'urgent';

    // ========== 关联 ==========

    public function warranty(): BelongsTo
    {
        return $this->belongsTo(Warranty::class, 'warranty_id');
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function device(): BelongsTo
    {
        return $this->belongsTo(CustomerDevice::class, 'device_id');
    }

    public function technician(): BelongsTo
    {
        return $this->belongsTo(User::class, 'technician_id');
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function completer(): BelongsTo
    {
        return $this->belongsTo(User::class, 'completed_by');
    }

    // ========== Scope ==========

    public function scopePending($query)
    {
        return $query->where('status', self::STATUS_PENDING);
    }

    public function scopeUnfinished($query)
    {
        return $query->whereIn('status', [
            self::STATUS_PENDING,
            self::STATUS_ASSIGNED,
            self::STATUS_IN_PROGRESS,
        ]);
    }

    public function scopeForTechnician($query, int $technicianId)
    {
        return $query->where('technician_id', $technicianId);
    }

    public function scopeByPriority($query, string $priority)
    {
        return $query->where('priority', $priority);
    }

    // ========== Helper ==========

    /**
     * 是否逾期（scheduled_date 已过且未完成/取消）。
     */
    public function isOverdue(): bool
    {
        if (in_array($this->status, [self::STATUS_COMPLETED, self::STATUS_CANCELLED], true)) {
            return false;
        }
        if (empty($this->scheduled_date)) {
            return false;
        }
        return Carbon::parse($this->scheduled_date)->startOfDay()->lt(Carbon::now()->startOfDay());
    }

    public function isCompleted(): bool
    {
        return $this->status === self::STATUS_COMPLETED;
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            self::STATUS_PENDING     => '待派工',
            self::STATUS_ASSIGNED    => '已派工',
            self::STATUS_IN_PROGRESS => '进行中',
            self::STATUS_COMPLETED   => '已完成',
            self::STATUS_CANCELLED   => '已取消',
            default                  => (string) $this->status,
        };
    }

    public function getPriorityLabelAttribute(): string
    {
        return match ($this->priority) {
            self::PRIORITY_LOW    => '低',
            self::PRIORITY_NORMAL => '普通',
            self::PRIORITY_HIGH   => '高',
            self::PRIORITY_URGENT => '紧急',
            default               => (string) $this->priority,
        };
    }

    public function getServiceTypeLabelAttribute(): string
    {
        return match ($this->service_type) {
            self::SERVICE_TYPE_INSPECT   => '巡检',
            self::SERVICE_TYPE_REPAIR    => '维修',
            self::SERVICE_TYPE_CLEAN     => '清洁',
            self::SERVICE_TYPE_CALIBRATE => '校准',
            self::SERVICE_TYPE_REPLACE   => '更换',
            default                      => (string) $this->service_type,
        };
    }
}
