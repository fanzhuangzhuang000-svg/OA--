<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Department extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'parent_id', 'manager_id', 'sort_order', 'status', 'description'];

    protected $casts = ['status' => 'string'];

    public function parent(): BelongsTo { return $this->belongsTo(Department::class, 'parent_id'); }
    public function children(): HasMany { return $this->hasMany(Department::class, 'parent_id'); }
    public function manager(): BelongsTo { return $this->belongsTo(User::class, 'manager_id'); }
    public function positions(): HasMany { return $this->hasMany(Position::class); }
    public function users(): HasMany { return $this->hasMany(User::class); }
}

class Position extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'department_id', 'level', 'description', 'status', 'sort_order'];

    public function department(): BelongsTo { return $this->belongsTo(Department::class); }
    public function users(): HasMany { return $this->hasMany(User::class); }
}

class EmployeeProfile extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'employee_no', 'hire_date', 'leave_date',
        'contract_type', 'contract_start', 'contract_end',
        'base_salary', 'salary_allowance', 'emergency_contact', 'emergency_phone',
        'bank_name', 'bank_account', 'notes',
    ];

    protected $casts = [
        'hire_date' => 'date', 'leave_date' => 'date',
        'contract_start' => 'date', 'contract_end' => 'date',
        'base_salary' => 'decimal:2', 'salary_allowance' => 'decimal:2',
    ];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function certificates(): HasMany { return $this->hasMany(Certificate::class); }
    public function skills(): BelongsToMany
    {
        return $this->belongsToMany(SkillTag::class, 'employee_skills')
            ->withPivot('proficiency')
            ->withTimestamps();
    }
}

class SkillTag extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'category', 'color', 'description', 'sort_order'];

    public function employees(): BelongsToMany
    {
        return $this->belongsToMany(EmployeeProfile::class, 'employee_skills')
            ->withPivot('proficiency')
            ->withTimestamps();
    }
}

class Certificate extends Model
{
    use HasFactory;

    protected $fillable = [
        'employee_profile_id', 'certificate_name', 'certificate_no',
        'issue_date', 'expire_date', 'issuer', 'status', 'attachment', 'remind_days',
    ];

    protected $casts = [
        'issue_date' => 'date', 'expire_date' => 'date',
    ];

    public function profile(): BelongsTo { return $this->belongsTo(EmployeeProfile::class); }

    public function isExpiringSoon(int $days = 30): bool
    {
        return $this->expire_date && $this->expire_date->diffInDays(now()) <= $days;
    }
}

class Customer extends Model
{
    use HasFactory;

    protected $fillable = [
        'name', 'credit_code', 'industry', 'category',
        'province', 'city', 'district', 'address',
        'longitude', 'latitude', 'tags', 'source', 'status',
        'assigned_user_id', 'description',
    ];

    protected $casts = ['tags' => 'array', 'longitude' => 'decimal:7', 'latitude' => 'decimal:7'];

    public function contacts(): HasMany { return $this->hasMany(CustomerContact::class); }
    public function primaryContact() { return $this->hasOne(CustomerContact::class)->where('is_primary', true); }
    public function devices(): HasMany { return $this->hasMany(CustomerDevice::class); }
    public function followUps(): HasMany { return $this->hasMany(FollowUpRecord::class); }
    public function projects(): HasMany { return $this->hasMany(Project::class); }
    public function serviceOrders(): HasMany { return $this->hasMany(ServiceOrder::class); }
    public function receivables(): HasMany { return $this->hasMany(Receivable::class); }
    public function maintenanceContracts(): HasMany { return $this->hasMany(MaintenanceContract::class); }
    public function invoiceInfos(): HasMany { return $this->hasMany(CustomerInvoiceInfo::class); }
    public function assignedUser(): BelongsTo { return $this->belongsTo(User::class, 'assigned_user_id'); }
    public function opportunities(): HasMany { return $this->hasMany(Opportunity::class); }
    public function leads(): HasMany { return $this->hasMany(Lead::class); }
    public function warranties(): HasMany { return $this->hasMany(Warranty::class); }
    public function serviceOrderCount(): int { return $this->serviceOrders()->count(); }
    public function activeProjectsCount(): int { return $this->projects()->whereIn('status', ['in_progress', 'execution'])->count(); }

    public function scopeActive($query) { return $query->where('status', 'active'); }
    public function scopeOfCategory($query, string $cat) { return $query->where('category', $cat); }
}

class CustomerContact extends Model
{
    use HasFactory;

    protected $fillable = ['customer_id', 'name', 'position', 'phone', 'email', 'is_primary', 'wechat', 'notes'];

    protected $casts = ['is_primary' => 'boolean'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
}

// v0.5.8.9 客户开票信息
class CustomerInvoiceInfo extends Model
{
    use HasFactory;

    protected $fillable = [
        'customer_id', 'invoice_type', 'company_name', 'tax_no',
        'register_address', 'register_phone', 'bank_name', 'bank_account',
        'is_default', 'remark',
    ];

    protected $casts = ['is_default' => 'boolean'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }

    public static function invoiceTypeLabel(string $t): string
    {
        return match ($t) {
            'special'    => '增值税专用发票',
            'electronic' => '电子发票',
            default      => '增值税普通发票',
        };
    }
}

class FollowUpRecord extends Model
{
    use HasFactory;

    protected $fillable = ['customer_id', 'user_id', 'type', 'content', 'next_follow_up_date', 'next_follow_up_note', 'attachments'];

    protected $casts = ['attachments' => 'array', 'next_follow_up_date' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
}

class CustomerDevice extends Model
{
    use HasFactory;

    protected $fillable = [
        'customer_id', 'project_id', 'device_name', 'device_type', 'brand', 'model',
        'serial_number', 'install_location', 'install_date', 'warranty_end', 'status', 'notes',
    ];

    protected $casts = ['install_date' => 'date', 'warranty_end' => 'date'];

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
}

class EmployeeOnboarding extends Model
{
    use HasFactory;
    protected $table = 'employee_onboardings';
    protected $fillable = [
        'user_id', 'hire_date', 'department_id', 'position_id', 'mentor_id',
        'probation_months', 'probation_end_date', 'contract_start', 'contract_end',
        'id_card_no', 'id_card_file_id',
        'driver_license_no', 'driver_license_expire', 'driver_license_file_id',
        'education_level', 'education_school', 'education_major', 'education_file_id',
        'contract_file_id', 'status', 'remark', 'onboarded_by',
    ];
    protected $casts = [
        'hire_date' => 'date', 'probation_end_date' => 'date',
        'contract_start' => 'date', 'contract_end' => 'date',
        'driver_license_expire' => 'date',
    ];
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function department(): BelongsTo { return $this->belongsTo(Department::class); }
    public function position(): BelongsTo { return $this->belongsTo(Position::class); }
    public function mentor(): BelongsTo { return $this->belongsTo(User::class, 'mentor_id'); }
    public function onboarder(): BelongsTo { return $this->belongsTo(User::class, 'onboarded_by'); }
    public function idCardFile(): BelongsTo { return $this->belongsTo(\App\Models\DiskFile::class, 'id_card_file_id'); }
    public function driverLicenseFile(): BelongsTo { return $this->belongsTo(\App\Models\DiskFile::class, 'driver_license_file_id'); }
    public function educationFile(): BelongsTo { return $this->belongsTo(\App\Models\DiskFile::class, 'education_file_id'); }
    public function contractFile(): BelongsTo { return $this->belongsTo(\App\Models\DiskFile::class, 'contract_file_id'); }
}

class EmployeeResignation extends Model
{
    use HasFactory;
    protected $table = 'employee_resignations';
    protected $fillable = [
        'user_id', 'resign_date', 'notice_date', 'last_work_day', 'resign_type',
        'reason', 'handover_to_user_id', 'handover_note',
        'assets_checklist', 'all_assets_returned',
        'final_salary_amount', 'leave_balance_payout', 'severance_pay', 'total_settlement',
        'paid_date', 'paid_method',
        'social_security_cutoff', 'resign_certificate_file_id',
        'status', 'remark', 'approved_by', 'approved_at', 'created_by',
    ];
    protected $casts = [
        'resign_date' => 'date', 'notice_date' => 'date', 'last_work_day' => 'date',
        'paid_date' => 'date', 'social_security_cutoff' => 'date',
        'approved_at' => 'datetime',
        'assets_checklist' => 'array',
        'all_assets_returned' => 'boolean',
        'final_salary_amount' => 'decimal:2',
        'leave_balance_payout' => 'decimal:2',
        'severance_pay' => 'decimal:2',
        'total_settlement' => 'decimal:2',
    ];
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function handoverTo(): BelongsTo { return $this->belongsTo(User::class, 'handover_to_user_id'); }
    public function approver(): BelongsTo { return $this->belongsTo(User::class, 'approved_by'); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function certificateFile(): BelongsTo { return $this->belongsTo(\App\Models\DiskFile::class, 'resign_certificate_file_id'); }
}
