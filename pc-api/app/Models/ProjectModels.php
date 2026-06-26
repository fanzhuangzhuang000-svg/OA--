<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Facades\DB;
use App\Concerns\HasDataScope;

class Project extends Model
{
    use HasFactory, HasDataScope;

    protected $fillable = [
        'project_no', 'name', 'customer_id', 'type', 'stage', 'status', 'description',
        'budget_device', 'budget_material', 'budget_labor', 'budget_outsource', 'budget_other',
        'progress', 'manager_id', 'start_date', 'end_date', 'actual_end_date', 'priority',
    ];

    protected $casts = [
        'budget_device' => 'decimal:2', 'budget_material' => 'decimal:2',
        'budget_labor' => 'decimal:2', 'budget_outsource' => 'decimal:2', 'budget_other' => 'decimal:2',
        'start_date' => 'date', 'end_date' => 'date', 'actual_end_date' => 'date',
        'stage' => \App\Enums\ProjectStage::class, 'status' => 'string',
    ];

    protected static function booted()
    {
        static::creating(function ($project) {
            if (empty($project->project_no)) {
                $count = Project::whereDate('created_at', today())->count() + 1;
                $project->project_no = 'PRJ-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function manager(): BelongsTo { return $this->belongsTo(User::class, 'manager_id'); }
    public function members(): BelongsToMany { return $this->belongsToMany(User::class, 'project_members')->withPivot('role', 'status')->withTimestamps(); }
    public function contract(): HasMany { return $this->hasMany(ProjectContract::class); }
    public function purchaseOrders(): HasMany { return $this->hasMany(PurchaseOrder::class); }
    public function constructionLogs(): HasMany { return $this->hasMany(ConstructionLog::class); }
    public function materials(): HasMany { return $this->hasMany(ProjectMaterial::class); }
    public function settlement(): HasMany { return $this->hasMany(ProjectSettlement::class); }
    public function serviceOrders(): HasMany { return $this->hasMany(ServiceOrder::class); }
    public function devices(): HasMany { return $this->hasMany(CustomerDevice::class, 'project_id'); }
    public function budgets(): HasMany { return $this->hasMany(ProjectBudget::class); }
    public function budget(): HasOne { return $this->hasOne(ProjectBudget::class)->latestOfMany('id'); }
    public function actualCosts(): HasMany { return $this->hasMany(ProjectActualCost::class); }
    public function receivables(): HasMany { return $this->hasMany(Receivable::class); }
    public function warranties(): HasMany { return $this->hasMany(Warranty::class); }
    public function rectifications(): HasMany { return $this->hasMany(Rectification::class); }
    public function processInstances(): HasMany { return $this->hasMany(WorkProcess::class, 'project_id'); }
    public function commencementOrder(): HasOne { return $this->hasOne(ProjectCommencementOrder::class)->latestOfMany('id'); }
    public function settlements(): HasMany { return $this->hasMany(ProjectSettlement::class); }
    public function followUps(): HasMany { return $this->hasMany(SalesFollowUp::class, 'target_id')->where('target_type', 'project'); }

    public function getTotalBudgetAttribute(): float
    {
        return (float) ($this->budget_device + $this->budget_material + $this->budget_labor + $this->budget_outsource + $this->budget_other);
    }

    public function getTotalActualCostAttribute(): float
    {
        return (float) $this->actualCosts()->sum('amount');
    }
}

class ProjectContract extends Model
{
    use HasFactory;

    protected $fillable = ['project_id', 'contract_no', 'contract_amount', 'payment_method', 'contract_start', 'contract_end', 'status', 'attachment', 'signed_at', 'notes'];

    protected $casts = ['contract_amount' => 'decimal:2', 'contract_start' => 'date', 'contract_end' => 'date', 'signed_at' => 'datetime'];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function paymentNodes(): HasMany { return $this->hasMany(ContractPaymentNode::class, 'contract_id'); }
}

class ContractPaymentNode extends Model
{
    use HasFactory;

    protected $fillable = ['contract_id', 'name', 'percentage', 'amount', 'planned_date', 'actual_date', 'status', 'paid_amount', 'notes'];

    protected $casts = ['percentage' => 'decimal:2', 'amount' => 'decimal:2', 'paid_amount' => 'decimal:2', 'planned_date' => 'date', 'actual_date' => 'date'];

    public function contract(): BelongsTo { return $this->belongsTo(ProjectContract::class, 'contract_id'); }
}

// v0.5.8 修复: 旧 Supplier 类 (无 contacts/attachments 关系) 已迁移到独立文件 app/Models/Supplier.php
// 这里删除, 否则 composer files[] 加载顺序冲突, 仍是老版本生效

class PurchaseOrder extends Model
{
    use HasFactory, HasDataScope;

    protected $fillable = ['project_id', 'supplier_id', 'po_no', 'total_amount', 'status', 'approved_by', 'approved_at', 'notes', 'code', 'tender_id', 'title', 'created_by'];

    protected $casts = ['total_amount' => 'decimal:2', 'approved_at' => 'datetime'];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function supplier(): BelongsTo { return $this->belongsTo(Supplier::class); }
    public function items(): HasMany { return $this->hasMany(PurchaseItem::class); }

    protected static function booted()
    {
        static::creating(function ($po) {
            if (empty($po->po_no)) {
                $count = PurchaseOrder::whereDate('created_at', today())->count() + 1;
                $po->po_no = 'PO-' . date('Ymd') . '-' . str_pad($count, 3, '0', STR_PAD_LEFT);
            }
        });
    }
}

class PurchaseItem extends Model
{
    use HasFactory;

    protected $fillable = ['purchase_order_id', 'item_name', 'specification', 'quantity', 'unit', 'unit_price', 'total_price', 'received_quantity', 'notes'];

    protected $casts = ['quantity' => 'decimal:2', 'unit_price' => 'decimal:2', 'total_price' => 'decimal:2', 'received_quantity' => 'decimal:2'];

    public function purchaseOrder(): BelongsTo { return $this->belongsTo(PurchaseOrder::class); }
}

// V0.4.3 拆分: ConstructionLog 已移到独立文件 app/Models/ConstructionLog.php (V0.4.3 P2)
//   - 增加字段: team_id, commencement_order_id, process_progress, is_rectification, rectification_order_id, reviewer_id, reviewed_at, review_remark
//   - 增加关系: team(), commencementOrder(), reviewer(), dailyRequired()
//   - 增加常量: STATUS_DRAFT/SUBMITTED/APPROVED/REJECTED
// 老类已废弃, 注释掉避免与 PSR-4 重复声明报错
/*
class ConstructionLog extends Model
{
    use HasFactory;

    protected $fillable = ['project_id', 'user_id', 'work_date', 'weather', 'content', 'problems', 'solutions', 'photos', 'work_hours', 'location', 'status'];

    protected $casts = ['photos' => 'array', 'work_date' => 'date', 'work_hours' => 'decimal:1'];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function operator(): BelongsTo { return $this->belongsTo(User::class, 'user_id'); }
}
*/

class ProjectMaterial extends Model
{
    use HasFactory;

    protected $fillable = ['project_id', 'material_name', 'specification', 'quantity', 'unit', 'unit_cost', 'total_cost', 'used_by', 'use_date', 'inventory_item_id', 'notes'];

    protected $casts = ['quantity' => 'decimal:2', 'unit_cost' => 'decimal:2', 'total_cost' => 'decimal:2', 'use_date' => 'date'];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function usedByUser(): BelongsTo { return $this->belongsTo(User::class, 'used_by'); }
}

class ProjectSettlement extends Model
{
    use HasFactory;

    protected $fillable = ['project_id', 'total_income', 'total_cost', 'cost_labor', 'cost_material', 'cost_outsource', 'cost_other', 'profit', 'profit_rate', 'settlement_date', 'status', 'notes'];

    protected $casts = ['total_income' => 'decimal:2', 'total_cost' => 'decimal:2', 'cost_labor' => 'decimal:2', 'cost_material' => 'decimal:2', 'cost_outsource' => 'decimal:2', 'cost_other' => 'decimal:2', 'profit' => 'decimal:2', 'profit_rate' => 'decimal:2', 'settlement_date' => 'date'];

    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    /** 合同 — 实际外键是 contract_id */
    public function contract(): BelongsTo { return $this->belongsTo(ProjectContract::class, 'contract_id'); }
}

// === 销售前链路 — 线索 / 商机 / 报价 / 项目池 / 跟进 ===

class Lead extends Model
{
    protected $table = 'leads';
    protected $fillable = [
        'lead_no', 'customer_id', 'customer_name', 'contact_name', 'contact_phone', 'contact_title',
        'source', 'referrer_id', 'requirement', 'estimated_amount', 'rating', 'status',
        'owner_id', 'follow_up_at', 'last_contact_at', 'discard_reason'
    ];
    protected $casts = ['estimated_amount' => 'decimal:2', 'follow_up_at' => 'date', 'last_contact_at' => 'datetime'];

    protected static function booted()
    {
        static::creating(function ($lead) {
            if (empty($lead->lead_no)) {
                $lead->lead_no = 'LEAD-' . date('YmdHis') . substr((string) microtime(true), -4) . random_int(100, 999);
            }
        });
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function owner(): BelongsTo { return $this->belongsTo(User::class, 'owner_id'); }
    public function referrer(): BelongsTo { return $this->belongsTo(Referrer::class, 'referrer_id'); }
    public function followUps(): HasMany { return $this->hasMany(SalesFollowUp::class, 'target_id')->where('target_type', 'lead'); }
}

class Opportunity extends Model
{
    protected $table = 'opportunities';
    protected $fillable = [
        'opp_no', 'name', 'customer_id', 'lead_id', 'type', 'estimated_amount', 'expected_sign_date',
        'stage', 'probability', 'sales_id', 'presale_id', 'competitor', 'lost_reason',
        'project_id', 'pool_id', 'last_contact_at', 'next_action', 'next_action_at', 'notes'
    ];
    protected $casts = ['estimated_amount' => 'decimal:2', 'expected_sign_date' => 'date', 'last_contact_at' => 'datetime', 'next_action_at' => 'date'];

    protected static function booted()
    {
        static::creating(function ($opp) {
            if (empty($opp->opp_no)) {
                $opp->opp_no = 'OPP-' . date('YmdHis') . substr((string) microtime(true), -4) . random_int(100, 999);
            }
        });
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function lead(): BelongsTo { return $this->belongsTo(Lead::class); }
    public function sales(): BelongsTo { return $this->belongsTo(User::class, 'sales_id'); }
    public function presale(): BelongsTo { return $this->belongsTo(User::class, 'presale_id'); }
    public function quotations(): HasMany { return $this->hasMany(Quotation::class); }
    public function followUps(): HasMany { return $this->hasMany(SalesFollowUp::class, 'target_id')->where('target_type', 'opp'); }
}

class Quotation extends Model
{
    protected $table = 'quotations';
    protected $fillable = [
        'quote_no', 'opportunity_id', 'version', 'subtotal', 'discount_rate', 'discount_amount',
        'tax_rate', 'tax_amount', 'total_amount', 'valid_until', 'status', 'notes',
        'created_by', 'approved_by', 'sent_at', 'responded_at'
    ];
    protected $casts = ['subtotal' => 'decimal:2', 'discount_rate' => 'decimal:2', 'discount_amount' => 'decimal:2', 'tax_rate' => 'decimal:2', 'tax_amount' => 'decimal:2', 'total_amount' => 'decimal:2', 'valid_until' => 'date', 'sent_at' => 'datetime', 'responded_at' => 'datetime'];

    protected static function booted()
    {
        static::creating(function ($quote) {
            if (empty($quote->quote_no)) {
                $quote->quote_no = 'QT-' . date('YmdHis') . substr((string) microtime(true), -4) . random_int(100, 999);
            }
        });
    }

    public function opportunity(): BelongsTo { return $this->belongsTo(Opportunity::class); }
    public function items(): HasMany { return $this->hasMany(QuotationItem::class); }
    public function createdBy(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function approvedBy(): BelongsTo { return $this->belongsTo(User::class, 'approved_by'); }
}

class QuotationItem extends Model
{
    protected $table = 'quotation_items';
    protected $fillable = ['quotation_id', 'inventory_item_id', 'product_id', 'code', 'name', 'specification', 'unit', 'quantity', 'unit_price', 'total_price', 'remark'];
    protected $casts = ['quantity' => 'decimal:2', 'unit_price' => 'decimal:2', 'total_price' => 'decimal:2'];

    public function quotation(): BelongsTo { return $this->belongsTo(Quotation::class); }
    public function inventoryItem(): BelongsTo { return $this->belongsTo(\App\Models\InventoryItem::class, 'inventory_item_id'); }
    public function product(): BelongsTo { return $this->belongsTo(SalesProduct::class, 'product_id'); }
}

class Referrer extends Model
{
    protected $table = 'referrers';
    protected $fillable = ['name', 'phone', 'customer_id', 'bank_account', 'bank_name', 'commission_rate', 'total_commission', 'notes'];
    protected $casts = ['commission_rate' => 'decimal:2', 'total_commission' => 'decimal:2'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
}

class ProjectPool extends Model
{
    protected $table = 'project_pool';
    protected $fillable = ['pool_no', 'opportunity_id', 'name', 'customer_id', 'contract_amount', 'signed_at', 'status', 'related_project_id', 'notes'];
    protected $casts = ['contract_amount' => 'decimal:2', 'signed_at' => 'date'];

    public function opportunity(): BelongsTo { return $this->belongsTo(Opportunity::class); }
    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class, 'related_project_id'); }
}

/**
 * 推荐人居间费结算单 (v0.3.11 P0)
 *
 * 触发：oppsMarkWon 事务内自动建 pending 单（若 lead.referrer_id 非空）
 * 状态：pending → approved (财务审核) → paid (财务发放 + 上传回单)
 */
class ReferralSettlement extends Model
{
    protected $table = 'referral_settlements';
    protected $fillable = [
        'opportunity_id', 'referrer_id', 'lead_id', 'amount', 'commission_rate', 'contract_amount',
        'status', 'created_by', 'approved_by', 'approved_at', 'paid_by', 'paid_at',
        'payment_voucher', 'payment_no', 'notes',
    ];
    protected $casts = [
        'amount' => 'decimal:2',
        'commission_rate' => 'decimal:2',
        'contract_amount' => 'decimal:2',
        'approved_at' => 'datetime',
        'paid_at' => 'datetime',
    ];

    public function opportunity(): BelongsTo { return $this->belongsTo(Opportunity::class); }
    public function referrer(): BelongsTo { return $this->belongsTo(Referrer::class); }
    public function lead(): BelongsTo { return $this->belongsTo(Lead::class); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approved_by'); }
    public function payer(): BelongsTo { return $this->belongsTo(User::class, 'paid_by'); }
}

class SalesFollowUp extends Model
{
    protected $table = 'sales_follow_ups';
    protected $fillable = ['target_type', 'target_id', 'contact_method', 'content', 'result', 'next_action', 'next_action_at', 'user_id'];
    protected $casts = ['next_action_at' => 'date'];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function attachments(): HasMany { return $this->hasMany(SalesFollowUpAttachment::class, 'follow_up_id'); }
}

class SalesFollowUpAttachment extends Model
{
    protected $table = 'sales_follow_up_attachments';
    protected $fillable = ['follow_up_id', 'name', 'path', 'mime', 'size'];
}

class SalesProduct extends Model
{
    protected $table = 'sales_products';
    protected $fillable = [
        'code', 'name', 'category_id', 'unit', 'spec',
        'sale_price', 'cost_price', 'description', 'status',
    ];
    protected $casts = [
        'sale_price' => 'decimal:2',
        'cost_price' => 'decimal:2',
    ];

    protected static function booted()
    {
        static::creating(function ($prod) {
            if (empty($prod->code)) {
                $prod->code = 'SP-' . date('YmdHis') . substr((string) microtime(true), -4) . random_int(100, 999);
            }
        });
    }

    public function categoryRef(): BelongsTo { return $this->belongsTo(InventoryCategory::class, 'category_id'); }
}
