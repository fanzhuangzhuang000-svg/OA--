<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;

// ========== 报销 ==========

class ExpenseClaim extends Model
{
    use HasFactory;

    protected $fillable = [
        'claim_no', 'user_id', 'category', 'total_amount', 'project_id',
        'description', 'status', 'approver_id', 'approved_at', 'paid_at', 'paid_amount', 'reject_reason',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2', 'paid_amount' => 'decimal:2',
        'approved_at' => 'datetime', 'paid_at' => 'datetime',
    ];

    protected static function booted()
    {
        static::creating(function ($claim) {
            if (empty($claim->claim_no)) {
                $count = ExpenseClaim::whereDate('created_at', today())->count() + 1;
                $claim->claim_no = 'EXP-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function items(): HasMany { return $this->hasMany(ExpenseItem::class); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
    public function approvals(): MorphMany { return $this->morphMany(ApprovalRecord::class, 'approvable'); }
}

class ExpenseItem extends Model
{
    use HasFactory;

    protected $fillable = ['expense_claim_id', 'item_date', 'description', 'amount', 'category', 'attachment'];

    protected $casts = ['item_date' => 'date', 'amount' => 'decimal:2'];

    public function expenseClaim(): BelongsTo { return $this->belongsTo(ExpenseClaim::class); }
}

class ApprovalRecord extends Model
{
    use HasFactory;

    protected $fillable = ['approvable_type', 'approvable_id', 'user_id', 'action', 'comment', 'status'];

    public function approvable() { return $this->morphTo(); }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
}

// ========== 车辆 ==========

class Vehicle extends Model
{
    use HasFactory;

    protected $fillable = ['plate_no', 'brand', 'model', 'color', 'purchase_date', 'purchase_price', 'department_id', 'responsible_user_id', 'status', 'vin', 'engine_no', 'seats', 'fuel_type'];

    protected $casts = ['purchase_date' => 'date', 'purchase_price' => 'decimal:2'];

    public function department(): BelongsTo { return $this->belongsTo(Department::class); }
    public function responsibleUser(): BelongsTo { return $this->belongsTo(User::class, 'responsible_user_id'); }
    public function insurances(): HasMany { return $this->hasMany(VehicleInsurance::class); }
    public function maintenanceRecords(): HasMany { return $this->hasMany(VehicleMaintenanceRecord::class); }
    public function usageRequests(): HasMany { return $this->hasMany(VehicleUsageRequest::class); }
}

class VehicleInsurance extends Model
{
    use HasFactory;

    protected $fillable = ['vehicle_id', 'insurance_company', 'policy_no', 'type', 'premium', 'start_date', 'end_date', 'status', 'notes'];

    protected $casts = ['premium' => 'decimal:2', 'start_date' => 'date', 'end_date' => 'date'];

    public function vehicle(): BelongsTo { return $this->belongsTo(Vehicle::class); }
}

class VehicleMaintenanceRecord extends Model
{
    use HasFactory;

    protected $fillable = ['vehicle_id', 'maintenance_type', 'mileage', 'cost', 'maintenance_date', 'description', 'next_maintenance_mileage', 'next_maintenance_date', 'handled_by'];

    protected $casts = ['cost' => 'decimal:2', 'maintenance_date' => 'date', 'next_maintenance_date' => 'date'];

    public function vehicle(): BelongsTo { return $this->belongsTo(Vehicle::class); }
    public function handledByUser(): BelongsTo { return $this->belongsTo(User::class, 'handled_by'); }
}

class VehicleUsageRequest extends Model
{
    use HasFactory;

    protected $fillable = [
        'vehicle_id', 'applicant_id', 'usage_date', 'start_time', 'end_time',
        'destination', 'purpose', 'passengers', 'self_drive', 'status',
        'approver_id', 'approved_at', 'actual_mileage', 'actual_fuel', 'start_mileage', 'end_mileage',
    ];

    protected $casts = ['usage_date' => 'date', 'approved_at' => 'datetime', 'passengers' => 'integer', 'self_drive' => 'boolean', 'actual_mileage' => 'integer', 'actual_fuel' => 'decimal:2'];

    public function vehicle(): BelongsTo { return $this->belongsTo(Vehicle::class); }
    public function applicant(): BelongsTo { return $this->belongsTo(User::class, 'applicant_id'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
}

// ========== 库存 ==========

class Warehouse extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'code', 'type', 'address', 'manager_id', 'status', 'description'];

    public function manager(): BelongsTo { return $this->belongsTo(User::class, 'manager_id'); }
    public function inventoryItems(): HasMany { return $this->hasMany(InventoryItem::class); }
}

class InventoryItem extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'code', 'category', 'specification', 'unit', 'safety_stock', 'current_stock', 'cost_price', 'sell_price', 'warehouse_id', 'location', 'has_serial', 'status'];

    protected $casts = ['safety_stock' => 'integer', 'current_stock' => 'integer', 'cost_price' => 'decimal:2', 'sell_price' => 'decimal:2', 'has_serial' => 'boolean'];

    public function warehouse(): BelongsTo { return $this->belongsTo(Warehouse::class); }
    public function serialNumbers(): HasMany { return $this->hasMany(DeviceSerialNumber::class); }
    public function stockRecords(): HasMany { return $this->hasMany(StockRecord::class); }

    public function isLowStock(): bool { return $this->current_stock <= $this->safety_stock; }
}

class StockRecord extends Model
{
    use HasFactory;

    protected $fillable = ['record_no', 'inventory_item_id', 'warehouse_id', 'type', 'quantity', 'remaining_stock', 'related_id', 'related_type', 'operator_id', 'remark'];

    protected $casts = ['quantity' => 'integer', 'remaining_stock' => 'integer'];

    public function inventoryItem(): BelongsTo { return $this->belongsTo(InventoryItem::class); }
    public function warehouse(): BelongsTo { return $this->belongsTo(Warehouse::class); }
    public function operator(): BelongsTo { return $this->belongsTo(User::class, 'operator_id'); }
}

class DeviceSerialNumber extends Model
{
    use HasFactory;

    protected $fillable = ['inventory_item_id', 'serial_number', 'status', 'project_id', 'customer_device_id', 'stock_record_id', 'install_date', 'notes'];

    protected $casts = ['install_date' => 'date'];

    public function inventoryItem(): BelongsTo { return $this->belongsTo(InventoryItem::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function customerDevice(): BelongsTo { return $this->belongsTo(CustomerDevice::class); }
}

// ========== 财务 ==========

class Receivable extends Model
{
    use HasFactory;

    protected $fillable = ['customer_id', 'project_id', 'contract_id', 'amount', 'received_amount', 'remaining_amount', 'due_date', 'received_date', 'overdue_days', 'status', 'notes'];

    protected $casts = ['amount' => 'decimal:2', 'received_amount' => 'decimal:2', 'remaining_amount' => 'decimal:2', 'due_date' => 'date', 'received_date' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
}

class Payable extends Model
{
    use HasFactory;

    protected $fillable = ['supplier_id', 'project_id', 'amount', 'paid_amount', 'remaining_amount', 'due_date', 'paid_date', 'payment_term', 'status', 'notes'];

    protected $casts = ['amount' => 'decimal:2', 'paid_amount' => 'decimal:2', 'remaining_amount' => 'decimal:2', 'due_date' => 'date', 'paid_date' => 'date'];

    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
}

// ========== 网盘 ==========

class DiskFolder extends Model
{
    use HasFactory;

    protected $fillable = ['parent_id', 'name', 'path', 'created_by', 'is_system', 'project_id'];

    protected $casts = ['is_system' => 'boolean'];

    public function parent(): BelongsTo { return $this->belongsTo(DiskFolder::class, 'parent_id'); }
    public function children(): HasMany { return $this->hasMany(DiskFolder::class, 'parent_id'); }
    public function files(): HasMany { return $this->hasMany(DiskFile::class, 'folder_id'); }
    public function createdByUser(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
}

class DiskFile extends Model
{
    use HasFactory;

    protected $fillable = ['folder_id', 'name', 'original_name', 'extension', 'mime_type', 'size', 'path', 'uploaded_by', 'version', 'description', 'is_starred'];

    protected $casts = ['size' => 'integer', 'version' => 'integer', 'is_starred' => 'boolean'];

    public function folder(): BelongsTo { return $this->belongsTo(DiskFolder::class); }
    public function uploadedByUser(): BelongsTo { return $this->belongsTo(User::class, 'uploaded_by'); }
}

// ========== 知识库 ==========

class KnowledgeCategory extends Model
{
    use HasFactory;

    protected $fillable = ['parent_id', 'name', 'icon', 'sort_order', 'description'];

    public function parent(): BelongsTo { return $this->belongsTo(KnowledgeCategory::class, 'parent_id'); }
    public function children(): HasMany { return $this->hasMany(KnowledgeCategory::class, 'parent_id'); }
    public function articles(): HasMany { return $this->hasMany(KnowledgeArticle::class, 'category_id'); }
}

class KnowledgeArticle extends Model
{
    use HasFactory;

    protected $fillable = ['category_id', 'title', 'content', 'author_id', 'tags', 'view_count', 'like_count', 'status', 'published_at', 'summary', 'cover_image'];

    protected $casts = ['tags' => 'array', 'published_at' => 'datetime'];

    public function category(): BelongsTo { return $this->belongsTo(KnowledgeCategory::class); }
    public function author(): BelongsTo { return $this->belongsTo(User::class, 'author_id'); }
}

// ========== 通知 ==========

class Notification extends Model
{
    use HasFactory;

    protected $fillable = [
        'type', 'title', 'content', 'data', 'read_at',
        'notifiable_id', 'notifiable_type', 'sender_id', 'level',
    ];

    protected $casts = [
        'data' => 'array',
        'read_at' => 'datetime',
    ];

    public function notifiable()
    {
        return $this->morphTo();
    }

    public function sender()
    {
        return $this->belongsTo(User::class, 'sender_id');
    }
}

// ========== 系统设置 ==========

class SystemSetting extends Model
{
    use HasFactory;
    protected $table = 'system_settings';
    protected $primaryKey = 'key';
    public $incrementing = false;
    protected $keyType = 'string';
    public $timestamps = false;

    protected $fillable = ['key', 'value', 'description', 'updated_at', 'updated_by'];
    protected $casts = [
        'updated_at' => 'datetime',
        // value 是 PG JSONB 字段，Eloquent 读出来已是 PHP 数组/标量，不要 cast 成 string
    ];

    /** 静态便捷：读取一个 key（已自动 json_decode） */
    public static function get(string $key, $default = null)
    {
        $row = static::find($key);
        if (!$row) return $default;
        $v = $row->value;
        // 兜底：某些驱动把 JSONB 当字符串返回
        if (is_string($v) && strlen($v) > 0) {
            $decoded = json_decode($v, true);
            if (json_last_error() === JSON_ERROR_NONE) return $decoded;
        }
        return $v ?? $default;
    }
}

// ========== 审批流程模板 ==========

class ApprovalTemplate extends Model
{
    use HasFactory;
    protected $table = 'approval_templates';

    protected $fillable = ['name', 'module', 'description', 'nodes', 'status', 'created_by', 'updated_by'];

    protected $casts = [
        'nodes'      => 'array',  // JSONB → 数组
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];
}
