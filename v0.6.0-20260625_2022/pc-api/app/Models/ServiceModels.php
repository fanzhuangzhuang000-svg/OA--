<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;

class ServiceOrder extends Model
{
    use HasFactory;

    protected $fillable = [
        'order_no', 'customer_id', 'project_id', 'customer_device_id',
        'fault_description', 'fault_photos', 'urgency', 'service_type', 'status',
        'assigned_to', 'assigned_at', 'started_at', 'completed_at', 'confirmed_at',
        'rating', 'review', 'created_by', 'sla_hours',
    ];

    protected $casts = [
        'fault_photos' => 'array', 'urgency' => \App\Enums\Urgency::class,
        'status' => \App\Enums\ServiceOrderStatus::class,
        'assigned_at' => 'datetime', 'started_at' => 'datetime', 'completed_at' => 'datetime',
        'confirmed_at' => 'datetime',
    ];

    protected static function booted()
    {
        static::creating(function ($order) {
            if (empty($order->order_no)) {
                $count = ServiceOrder::whereDate('created_at', today())->count() + 1;
                $order->order_no = 'SO-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function device(): BelongsTo { return $this->belongsTo(CustomerDevice::class, 'customer_device_id'); }
    public function assignedUser(): BelongsTo { return $this->belongsTo(User::class, 'assigned_to'); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function logs(): HasMany { return $this->hasMany(ServiceOrderLog::class); }
    public function parts(): HasMany { return $this->hasMany(ServiceOrderPart::class); }
    public function approvals(): MorphMany { return $this->morphMany(ApprovalRecord::class, 'approvable'); }

    public function isOverdue(): bool
    {
        if ($this->status === \App\Enums\ServiceOrderStatus::PENDING && $this->created_at) {
            return $this->created_at->diffInHours(now()) > $this->sla_hours;
        }
        return false;
    }
}

class ServiceOrderLog extends Model
{
    use HasFactory;

    protected $fillable = ['service_order_id', 'user_id', 'action', 'content', 'photos', 'location', 'gps_lat', 'gps_lng'];

    protected $casts = ['photos' => 'array', 'gps_lat' => 'decimal:7', 'gps_lng' => 'decimal:7'];

    public function serviceOrder(): BelongsTo { return $this->belongsTo(ServiceOrder::class); }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
}

class ServiceOrderPart extends Model
{
    use HasFactory;

    protected $fillable = ['service_order_id', 'inventory_item_id', 'part_name', 'quantity', 'unit_cost', 'total_cost'];

    protected $casts = ['quantity' => 'integer', 'unit_cost' => 'decimal:2', 'total_cost' => 'decimal:2'];

    public function serviceOrder(): BelongsTo { return $this->belongsTo(ServiceOrder::class); }
}

class MaintenanceContract extends Model
{
    use HasFactory;

    protected $fillable = ['contract_no', 'customer_id', 'amount', 'start_date', 'end_date', 'inspection_frequency', 'scope', 'status', 'notes'];

    protected $casts = ['amount' => 'decimal:2', 'start_date' => 'date', 'end_date' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
}

// ========== 考勤 ==========

class AttendanceRecord extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'date', 'clock_in', 'clock_in_location', 'clock_in_lat', 'clock_in_lng',
        'clock_out', 'clock_out_location', 'clock_out_lat', 'clock_out_lng',
        'status', 'work_hours', 'overtime_hours', 'project_id', 'remark',
    ];

    protected $casts = [
        'date' => 'date', 'clock_in_lat' => 'decimal:7', 'clock_in_lng' => 'decimal:7',
        'clock_out_lat' => 'decimal:7', 'clock_out_lng' => 'decimal:7',
        'work_hours' => 'decimal:1', 'overtime_hours' => 'decimal:1',
    ];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
}

class LeaveRequest extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'type', 'start_date', 'end_date', 'days', 'reason', 'status', 'approver_id', 'approved_at', 'reject_reason'];

    protected $casts = ['start_date' => 'date', 'end_date' => 'date', 'days' => 'decimal:1', 'approved_at' => 'datetime'];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
    public function approvals(): \Illuminate\Database\Eloquent\Relations\MorphMany { return $this->morphMany(ApprovalRecord::class, 'approvable'); }
}

class OvertimeRequest extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'overtime_date', 'start_time', 'end_time', 'hours', 'reason', 'compensation_type', 'status', 'approver_id', 'approved_at', 'timesheet_leave_hours'];

    protected $casts = ['overtime_date' => 'date', 'hours' => 'decimal:1', 'approved_at' => 'datetime', 'timesheet_leave_hours' => 'decimal:1'];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
}

class Shift extends Model
{
    use HasFactory;
    protected $table = 'shifts';
    protected $fillable = [
        'name', 'code', 'start_time', 'end_time', 'late_threshold_minutes',
        'early_leave_threshold_minutes', 'work_hours', 'color', 'is_overnight',
        'is_active', 'sort_order', 'remark',
    ];
    protected $casts = [
        'is_overnight' => 'boolean', 'is_active' => 'boolean',
        'late_threshold_minutes' => 'integer', 'early_leave_threshold_minutes' => 'integer',
        'work_hours' => 'decimal:1', 'sort_order' => 'integer',
    ];
    public function schedules(): HasMany { return $this->hasMany(Schedule::class); }
}

class ShiftGroup extends Model
{
    use HasFactory;
    protected $table = 'shift_groups';
    protected $fillable = ['name', 'code', 'leader_id', 'color', 'description', 'is_active'];
    protected $casts = ['is_active' => 'boolean'];
    public function leader(): BelongsTo { return $this->belongsTo(User::class, 'leader_id'); }
    public function members(): HasMany { return $this->hasMany(ShiftGroupMember::class, 'group_id'); }
}

class ShiftGroupMember extends Model
{
    use HasFactory;
    protected $table = 'shift_group_members';
    protected $fillable = ['group_id', 'user_id', 'joined_at'];
    protected $casts = ['joined_at' => 'date'];
    public function group(): BelongsTo { return $this->belongsTo(ShiftGroup::class, 'group_id'); }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
}

class Schedule extends Model
{
    use HasFactory;
    protected $table = 'schedules';
    protected $fillable = ['user_id', 'group_id', 'shift_id', 'date', 'status', 'note', 'created_by'];
    protected $casts = ['date' => 'date'];
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function group(): BelongsTo { return $this->belongsTo(ShiftGroup::class, 'group_id'); }
    public function shift(): BelongsTo { return $this->belongsTo(Shift::class); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
}
