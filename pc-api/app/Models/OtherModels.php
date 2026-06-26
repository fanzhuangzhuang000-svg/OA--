<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use App\Concerns\HasDataScope;

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

    /** 状态常量 */
    const STATUS_PENDING     = 'pending';
    const STATUS_APPROVED    = 'approved';
    const STATUS_REJECTED    = 'rejected';
    const STATUS_TRANSFERRED = 'transferred';
    const STATUS_CANCELLED   = 'cancelled';

    /**
     * 实际表名: approval_records_v2 (聚合财务/运营/项目 3 大类审批)
     * 原 approval_records (多态关联) 表继续存在,但本 Model 走 v2 表
     * @see database/migrations/2024_01_05_000004_create_approval_records_v2_table.php
     */
    protected $table = 'approval_records_v2';

    protected $fillable = [
        'code', 'type', 'sub_type', 'title', 'priority', 'status',
        'amount', 'bank_account', 'start_date', 'end_date', 'to_stage',
        'applicant_id', 'current_approver_id', 'payload', 'flow', 'cc', 'comment',
    ];

    protected $casts = [
        'amount'     => 'decimal:2',
        'start_date' => 'date',
        'end_date'   => 'date',
        'payload'    => 'array',
        'flow'       => 'array',
        'cc'         => 'array',
    ];

    public function approvable() { return $this->morphTo(); }
    public function user(): BelongsTo { return $this->belongsTo(User::class, 'applicant_id'); }
    public function currentApprover(): BelongsTo { return $this->belongsTo(User::class, 'current_approver_id'); }
}

// ========== 车辆 ==========

class Vehicle extends Model
{
    use HasFactory;

    protected $fillable = ['plate_no', 'brand', 'model', 'year', 'color', 'vin', 'engine_no', 'purchase_date', 'purchase_price', 'department_id', 'responsible_user_id', 'status', 'mileage', 'seats', 'fuel_type'];

    protected $casts = ['purchase_date' => 'date', 'purchase_price' => 'decimal:2'];

    public function department(): BelongsTo { return $this->belongsTo(Department::class); }
    public function responsibleUser(): BelongsTo { return $this->belongsTo(User::class, 'responsible_user_id'); }
    public function insurances(): HasMany { return $this->hasMany(VehicleInsurance::class); }
    public function maintenanceRecords(): HasMany { return $this->hasMany(VehicleMaintenanceRecord::class); }
    public function fuelCards(): HasMany { return $this->hasMany(FuelCard::class); }
    public function usageRequests(): HasMany { return $this->hasMany(VehicleUsageRequest::class); }
}

class VehicleInsurance extends Model
{
    use HasFactory;

    protected $table = 'vehicle_insurance';
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

// ========== 油卡 ==========

class FuelCard extends Model
{
    use HasFactory;
    protected $table = 'fuel_cards';
    protected $fillable = ['card_no', 'card_name', 'vehicle_id', 'balance', 'status', 'issue_date', 'expire_date', 'notes'];
    protected $casts = [
        'balance' => 'decimal:2',
        'issue_date' => 'date',
        'expire_date' => 'date',
    ];
    public function vehicle(): BelongsTo { return $this->belongsTo(Vehicle::class); }
    public function recharges(): HasMany { return $this->hasMany(FuelCardRecharge::class, 'card_id'); }
}

class FuelCardRecharge extends Model
{
    use HasFactory;
    protected $table = 'fuel_card_recharges';
    protected $fillable = ['card_id', 'amount', 'recharge_date', 'payment_method', 'operator', 'voucher_no', 'notes'];
    protected $casts = [
        'amount' => 'decimal:2',
        'recharge_date' => 'date',
    ];
    public function card(): BelongsTo { return $this->belongsTo(FuelCard::class, 'card_id'); }
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

    protected $fillable = ['name', 'code', 'category', 'category_id', 'specification', 'unit', 'safety_stock', 'min_stock', 'shelf_life_days', 'expiry_date', 'current_stock', 'cost_price', 'sell_price', 'warehouse_id', 'location', 'has_serial', 'status'];

    protected $casts = ['safety_stock' => 'integer', 'min_stock' => 'integer', 'shelf_life_days' => 'integer', 'expiry_date' => 'date', 'current_stock' => 'integer', 'cost_price' => 'decimal:2', 'sell_price' => 'decimal:2', 'has_serial' => 'boolean'];

    public function warehouse(): BelongsTo { return $this->belongsTo(Warehouse::class); }
    public function serialNumbers(): HasMany { return $this->hasMany(DeviceSerialNumber::class); }
    public function stockRecords(): HasMany { return $this->hasMany(StockRecord::class); }
    public function categoryRef(): BelongsTo { return $this->belongsTo(InventoryCategory::class, 'category_id'); }

    public function isLowStock(): bool { return $this->min_stock > 0 && $this->current_stock <= $this->min_stock; }
}

class InventoryCategory extends Model
{
    use HasFactory;
    protected $table = 'inventory_categories';
    protected $fillable = ['parent_id', 'name', 'code', 'sort_order', 'description'];
    protected $casts = ['sort_order' => 'integer'];
    public function parent(): BelongsTo { return $this->belongsTo(InventoryCategory::class, 'parent_id'); }
    public function children(): HasMany { return $this->hasMany(InventoryCategory::class, 'parent_id'); }
    public function items(): HasMany { return $this->hasMany(InventoryItem::class, 'category_id'); }
}

class StockRecord extends Model
{
    use HasFactory;

    protected $fillable = ['record_no', 'inventory_item_id', 'warehouse_id', 'type', 'quantity', 'remaining_stock', 'related_id', 'related_type', 'party_type', 'party_id', 'settle_id', 'project_id', 'out_method', 'operator_id', 'remark'];

    protected $casts = ['quantity' => 'integer', 'remaining_stock' => 'integer'];

    public function inventoryItem(): BelongsTo { return $this->belongsTo(InventoryItem::class); }
    public function warehouse(): BelongsTo { return $this->belongsTo(Warehouse::class); }
    public function operator(): BelongsTo { return $this->belongsTo(User::class, 'operator_id'); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }

    /**
     * 动态往来单位关联: customer (Customer 模型) / supplier (Supplier 模型)
     * 通过 party_type + party_id 解析
     */
    public function party()
    {
        return $this->party_type === 'customer'
            ? $this->belongsTo(Customer::class, 'party_id')
            : $this->belongsTo(Supplier::class, 'party_id');
    }
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
    use HasFactory, HasDataScope;

    protected $fillable = ['customer_id', 'project_id', 'contract_id', 'amount', 'received_amount', 'remaining_amount', 'due_date', 'received_date', 'overdue_days', 'status', 'notes'];

    protected $casts = ['amount' => 'decimal:2', 'received_amount' => 'decimal:2', 'remaining_amount' => 'decimal:2', 'due_date' => 'date', 'received_date' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
}

class Payable extends Model
{
    use HasFactory, HasDataScope;

    protected $fillable = ['supplier_id', 'project_id', 'amount', 'paid_amount', 'remaining_amount', 'due_date', 'paid_date', 'payment_term', 'status', 'notes', 'ref_no', 'po_id', 'tender_id', 'description'];

    protected $casts = ['amount' => 'decimal:2', 'paid_amount' => 'decimal:2', 'remaining_amount' => 'decimal:2', 'due_date' => 'date', 'paid_date' => 'date'];

    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function payments(): HasMany { return $this->hasMany(FinancePayment::class, 'payable_id'); }
}

class FinancePayment extends Model
{
    use HasFactory;

    protected $fillable = ['receivable_id', 'payable_id', 'account_id', 'amount', 'payment_date', 'method', 'voucher_no', 'operator', 'remark'];

    protected $casts = ['amount' => 'decimal:2', 'payment_date' => 'date'];

    public function receivable(): BelongsTo { return $this->belongsTo(Receivable::class); }
    public function payable(): BelongsTo { return $this->belongsTo(Payable::class); }
    public function account(): BelongsTo { return $this->belongsTo(FinanceAccount::class); }
}

class FinanceAccount extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'type', 'balance', 'bank_name', 'account_no', 'currency', 'status', 'remark'];

    protected $casts = ['balance' => 'decimal:2'];

    public function payments(): HasMany { return $this->hasMany(FinancePayment::class, 'account_id'); }
}

class FinanceInvoice extends Model
{
    use HasFactory;

    protected $fillable = ['invoice_no', 'invoice_type', 'customer_id', 'project_id', 'receivable_id', 'amount', 'tax_rate', 'tax_amount', 'total_amount', 'issue_date', 'status', 'remark'];

    protected $casts = ['amount' => 'decimal:2', 'tax_rate' => 'decimal:2', 'tax_amount' => 'decimal:2', 'total_amount' => 'decimal:2', 'issue_date' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function receivable(): BelongsTo { return $this->belongsTo(Receivable::class); }
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

// ========== 采购管理 ==========

class PurchaseRequirement extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'project_id', 'material', 'spec', 'quantity', 'unit',
        'need_date', 'priority', 'status', 'creator', 'remark',
        'review_remark', 'reviewed_by', 'reviewed_at',
    ];

    protected $casts = [
        'quantity'    => 'decimal:2',
        'need_date'   => 'date',
        'reviewed_at' => 'datetime',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchaseRequirement::whereDate('created_at', today())->count() + 1;
                $m->code = 'REQ-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function reviewer(): BelongsTo { return $this->belongsTo(User::class, 'reviewed_by'); }
    public function plans(): HasMany { return $this->hasMany(PurchasePlan::class, 'requirement_id'); }
}

class PurchasePlan extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'requirement_id', 'project_id', 'title', 'total_amount', 'plan_date',
        'priority', 'status', 'submitter_id', 'submitted_at',
        'approver_id', 'approved_at', 'approve_remark', 'remark',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'plan_date'    => 'date',
        'submitted_at' => 'datetime',
        'approved_at'  => 'datetime',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchasePlan::whereDate('created_at', today())->count() + 1;
                $m->code = 'PP-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function requirement(): BelongsTo { return $this->belongsTo(PurchaseRequirement::class, 'requirement_id'); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function submitter(): BelongsTo { return $this->belongsTo(User::class, 'submitter_id'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
    public function contracts(): HasMany { return $this->hasMany(PurchaseContract::class, 'plan_id'); }
}

class PurchaseContract extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'plan_id', 'project_id', 'supplier_id', 'title', 'total_amount',
        'signed_at', 'start_date', 'end_date', 'payment_terms',
        'delivery_address', 'status', 'signer', 'signer_id', 'remark',
    ];

    protected $casts = [
        'total_amount' => 'decimal:2',
        'signed_at'    => 'date',
        'start_date'   => 'date',
        'end_date'     => 'date',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchaseContract::whereDate('created_at', today())->count() + 1;
                $m->code = 'PC-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function plan(): BelongsTo { return $this->belongsTo(PurchasePlan::class, 'plan_id'); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function signer(): BelongsTo { return $this->belongsTo(User::class, 'signer_id'); }
    public function shipments(): HasMany { return $this->hasMany(PurchaseShipment::class, 'contract_id'); }
    public function paymentRequests(): HasMany { return $this->hasMany(PurchasePaymentRequest::class, 'contract_id'); }
    public function payments(): HasMany { return $this->hasMany(PurchasePayment::class, 'contract_id'); }
}

class PurchasePaymentRequest extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'contract_id', 'supplier_id', 'amount', 'payment_type', 'request_date',
        'status', 'applicant', 'applicant_id', 'reason',
        'approver_id', 'approved_at', 'approve_remark',
    ];

    protected $casts = [
        'amount'      => 'decimal:2',
        'request_date'=> 'date',
        'approved_at' => 'datetime',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchasePaymentRequest::whereDate('created_at', today())->count() + 1;
                $m->code = 'PR-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function contract(): BelongsTo { return $this->belongsTo(PurchaseContract::class, 'contract_id'); }
    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function applicant(): BelongsTo { return $this->belongsTo(User::class, 'applicant_id'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
    public function payments(): HasMany { return $this->hasMany(PurchasePayment::class, 'payment_request_id'); }
}

class PurchasePayment extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'payment_request_id', 'contract_id', 'supplier_id', 'amount',
        'payment_method', 'paid_at', 'voucher_no', 'operator', 'operator_id', 'status', 'remark',
    ];

    protected $casts = [
        'amount'  => 'decimal:2',
        'paid_at' => 'date',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchasePayment::whereDate('created_at', today())->count() + 1;
                $m->code = 'PAY-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function paymentRequest(): BelongsTo { return $this->belongsTo(PurchasePaymentRequest::class, 'payment_request_id'); }
    public function contract(): BelongsTo { return $this->belongsTo(PurchaseContract::class, 'contract_id'); }
    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function operatorUser(): BelongsTo { return $this->belongsTo(User::class, 'operator_id'); }
}

class PurchaseShipment extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'contract_id', 'supplier_id', 'shipped_at', 'expected_arrival_at',
        'arrived_at', 'carrier', 'tracking_no', 'status', 'consignee', 'remark',
    ];

    protected $casts = [
        'shipped_at'           => 'date',
        'expected_arrival_at'  => 'date',
        'arrived_at'           => 'date',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchaseShipment::whereDate('created_at', today())->count() + 1;
                $m->code = 'SH-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function contract(): BelongsTo { return $this->belongsTo(PurchaseContract::class, 'contract_id'); }
    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function items(): HasMany { return $this->hasMany(PurchaseShipmentItem::class, 'shipment_id'); }
    public function logistics(): HasMany { return $this->hasMany(PurchaseLogistics::class, 'shipment_id'); }
}

class PurchaseShipmentItem extends Model
{
    use HasFactory;

    protected $fillable = ['shipment_id', 'material', 'spec', 'quantity', 'unit', 'remark'];

    protected $casts = ['quantity' => 'decimal:2'];

    public function shipment(): BelongsTo { return $this->belongsTo(PurchaseShipment::class, 'shipment_id'); }
}

class PurchaseLogistics extends Model
{
    use HasFactory;

    protected $fillable = [
        'shipment_id', 'tracking_no', 'event_at', 'location', 'status', 'description', 'operator',
    ];

    protected $casts = ['event_at' => 'datetime'];

    public function shipment(): BelongsTo { return $this->belongsTo(PurchaseShipment::class, 'shipment_id'); }
}

class PurchaseApproval extends Model
{
    use HasFactory;

    protected $fillable = [
        'code', 'target_type', 'target_id', 'title', 'applicant_id', 'applicant',
        'applied_at', 'status', 'approver_id', 'approved_at', 'approve_remark',
        'reason', 'amount',
    ];

    protected $casts = [
        'applied_at'  => 'datetime',
        'approved_at' => 'datetime',
        'amount'      => 'decimal:2',
    ];

    protected static function booted()
    {
        static::creating(function ($m) {
            if (empty($m->code)) {
                $count = PurchaseApproval::whereDate('created_at', today())->count() + 1;
                $m->code = 'PA-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function applicant(): BelongsTo { return $this->belongsTo(User::class, 'applicant_id'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approver_id'); }
}

// ========== 深化施工 V1.1 工序验收 ==========

class ProcessTemplate extends Model
{
    use HasFactory;

    const INDUSTRY_SECURITY   = 'security';
    const INDUSTRY_BUILDING   = 'building';
    const INDUSTRY_TRANSPORT  = 'transport';
    const INDUSTRY_ENERGY     = 'energy';
    const INDUSTRY_INDUSTRIAL = 'industrial';

    protected $fillable = [
        'industry', 'category', 'code', 'name', 'description',
        'standard_duration_days', 'standard_man_hours',
        'required_qualifications', 'safety_requirements',
        'quality_checkpoints', 'acceptance_criteria',
        'sort_order', 'is_active', 'created_by',
    ];

    protected $casts = [
        'standard_duration_days' => 'integer',
        'standard_man_hours'     => 'decimal:2',
        'required_qualifications'=> 'array',
        'quality_checkpoints'    => 'array',
        'acceptance_criteria'    => 'array',
        'sort_order'             => 'integer',
        'is_active'              => 'boolean',
    ];

    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function instances(): HasMany { return $this->hasMany(ProcessInstance::class, 'template_id'); }

    public static function industries(): array
    {
        return [
            self::INDUSTRY_SECURITY   => '安防监控',
            self::INDUSTRY_BUILDING   => '楼宇自控',
            self::INDUSTRY_TRANSPORT  => '智能交通',
            self::INDUSTRY_ENERGY     => '能源电力',
            self::INDUSTRY_INDUSTRIAL => '工业自动化',
        ];
    }
}

class ProcessInstance extends Model
{
    use HasFactory;

    const STATUS_PENDING    = 'pending';
    const STATUS_IN_PROGRESS= 'in_progress';
    const STATUS_COMPLETED  = 'completed';
    const STATUS_ACCEPTED   = 'accepted';
    const STATUS_REJECTED   = 'rejected';
    const STATUS_BLOCKED    = 'blocked';

    protected $fillable = [
        'project_id', 'template_id', 'parent_id', 'code', 'name', 'sequence',
        'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date',
        'planned_duration_days', 'actual_duration_days',
        'status', 'progress', 'foreman_id', 'workers', 'location', 'description',
        'accepted_at', 'accepted_by',
    ];

    protected $casts = [
        'planned_start_date'    => 'date',
        'planned_end_date'      => 'date',
        'actual_start_date'     => 'date',
        'actual_end_date'       => 'date',
        'planned_duration_days' => 'integer',
        'actual_duration_days'  => 'integer',
        'sequence'              => 'integer',
        'progress'              => 'integer',
        'workers'               => 'array',
        'accepted_at'           => 'datetime',
    ];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function template(): BelongsTo { return $this->belongsTo(ProcessTemplate::class, 'template_id'); }
    public function foreman(): BelongsTo { return $this->belongsTo(User::class, 'foreman_id'); }
    public function acceptedByUser(): BelongsTo { return $this->belongsTo(User::class, 'accepted_by'); }
    public function parent(): BelongsTo { return $this->belongsTo(ProcessInstance::class, 'parent_id'); }
    public function children(): HasMany { return $this->hasMany(ProcessInstance::class, 'parent_id'); }
    public function inspections(): HasMany { return $this->hasMany(ProcessInspection::class); }
    public function images(): HasMany { return $this->hasMany(ProcessImage::class); }
    public function signatures(): HasMany { return $this->hasMany(ProcessSignature::class); }

    public function isOverdue(): bool
    {
        return in_array($this->status, [self::STATUS_PENDING, self::STATUS_IN_PROGRESS], true)
            && $this->planned_end_date
            && $this->planned_end_date->lt(today());
    }
}

class ProcessInspection extends Model
{
    use HasFactory;

    const TYPE_SELF       = 'self';
    const TYPE_MUTUAL     = 'mutual';
    const TYPE_SUPERVISOR = 'supervisor';
    const TYPE_OWNER      = 'owner';

    const RESULT_PENDING = 'pending';
    const RESULT_PASS    = 'pass';
    const RESULT_FAIL    = 'fail';
    const RESULT_PARTIAL = 'partial';

    protected $fillable = [
        'process_instance_id', 'inspection_type', 'inspector_id', 'inspector_name',
        'inspection_date', 'result', 'score', 'checkpoint_results', 'issues',
        'suggestions', 'next_inspection_date', 'image_ids', 'remark',
    ];

    protected $casts = [
        'inspection_date'      => 'date',
        'next_inspection_date' => 'date',
        'score'                => 'decimal:2',
        'checkpoint_results'   => 'array',
        'issues'               => 'array',
        'image_ids'            => 'array',
    ];

    public function processInstance(): BelongsTo { return $this->belongsTo(ProcessInstance::class); }
    public function inspector(): BelongsTo { return $this->belongsTo(User::class, 'inspector_id'); }
    public function images(): HasMany { return $this->hasMany(ProcessImage::class, 'inspection_id'); }
    public function signatures(): HasMany { return $this->hasMany(ProcessSignature::class, 'inspection_id'); }
}

class ProcessImage extends Model
{
    use HasFactory;

    const CATEGORY_BEFORE     = 'before';
    const CATEGORY_DURING     = 'during';
    const CATEGORY_AFTER      = 'after';
    const CATEGORY_ISSUE      = 'issue';
    const CATEGORY_ACCEPTANCE = 'acceptance';

    protected $fillable = [
        'process_instance_id', 'inspection_id', 'category', 'file_type',
        'file_name', 'file_path', 'file_size', 'mime_type',
        'width', 'height', 'duration', 'thumbnail_path',
        'taken_at', 'taken_by', 'location', 'geo', 'description', 'tags',
    ];

    protected $casts = [
        'file_size' => 'integer',
        'width'     => 'integer',
        'height'    => 'integer',
        'duration'  => 'integer',
        'taken_at'  => 'datetime',
        'geo'       => 'array',
        'tags'      => 'array',
    ];

    public function processInstance(): BelongsTo { return $this->belongsTo(ProcessInstance::class); }
    public function inspection(): BelongsTo { return $this->belongsTo(ProcessInspection::class, 'inspection_id'); }
    public function takenByUser(): BelongsTo { return $this->belongsTo(User::class, 'taken_by'); }
}

class ProcessSignature extends Model
{
    use HasFactory;

    const SIGNER_CONTRACTOR = 'contractor';
    const SIGNER_OWNER      = 'owner';
    const SIGNER_SUPERVISOR = 'supervisor';
    const SIGNER_INSPECTOR  = 'inspector';

    protected $fillable = [
        'process_instance_id', 'inspection_id', 'signer_type', 'signer_id',
        'signer_name', 'signer_phone', 'signer_role', 'signature_data', 'signature_image_path',
        'ip_address', 'user_agent', 'signed_at', 'expires_at',
        'verification_code', 'is_verified', 'hash',
    ];

    protected $casts = [
        'signed_at'   => 'datetime',
        'expires_at'  => 'datetime',
        'is_verified' => 'boolean',
    ];

    public function processInstance(): BelongsTo { return $this->belongsTo(ProcessInstance::class); }
    public function inspection(): BelongsTo { return $this->belongsTo(ProcessInspection::class, 'inspection_id'); }
    public function signer(): BelongsTo { return $this->belongsTo(User::class, 'signer_id'); }

    public static function makeHash(array $payload): string
    {
        ksort($payload);
        return hash('sha256', json_encode($payload, JSON_UNESCAPED_UNICODE));
    }
}

