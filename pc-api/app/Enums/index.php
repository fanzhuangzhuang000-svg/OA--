<?php

namespace App\Enums;

enum UserStatus: string
{
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';

    public function label(): string
    {
        return match ($this) {
            self::ACTIVE => '在职',
            self::INACTIVE => '离职',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::ACTIVE => 'success',
            self::INACTIVE => 'danger',
        };
    }
}

enum Gender: string
{
    case MALE = 'male';
    case FEMALE = 'female';
    case OTHER = 'other';

    public function label(): string
    {
        return match ($this) {
            self::MALE => '男',
            self::FEMALE => '女',
            self::OTHER => '其他',
        };
    }
}

enum ProjectStage: string
{
    case INITIATION = 'initiation';
    case INQUIRY = 'inquiry';
    case CONTRACT = 'contract';
    case PURCHASE = 'purchase';
    case CONSTRUCTION = 'construction';
    case SETTLEMENT = 'settlement';
    case WARRANTY = 'warranty';

    public function label(): string
    {
        return match ($this) {
            self::INITIATION => '立项',
            self::INQUIRY => '询价',
            self::CONTRACT => '合同',
            self::PURCHASE => '采购',
            self::CONSTRUCTION => '施工',
            self::SETTLEMENT => '结算',
            self::WARRANTY => '质保',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::INITIATION => 'primary',
            self::INQUIRY => 'success',
            self::CONTRACT => 'warning',
            self::PURCHASE => 'info',
            self::CONSTRUCTION => 'danger',
            self::SETTLEMENT => 'success',
            self::WARRANTY => 'danger',
        };
    }

    public function order(): int
    {
        return match ($this) {
            self::INITIATION => 1,
            self::INQUIRY => 2,
            self::CONTRACT => 3,
            self::PURCHASE => 4,
            self::CONSTRUCTION => 5,
            self::SETTLEMENT => 6,
            self::WARRANTY => 7,
        };
    }
}

enum ServiceOrderStatus: string
{
    case PENDING = 'pending';
    case ASSIGNED = 'assigned';
    case IN_PROGRESS = 'in_progress';
    case COMPLETED = 'completed';
    case CONFIRMED = 'confirmed';
    case ARCHIVED = 'archived';
    case CANCELLED = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::PENDING => '待处理',
            self::ASSIGNED => '已派单',
            self::IN_PROGRESS => '维修中',
            self::COMPLETED => '待确认',
            self::CONFIRMED => '已完成',
            self::ARCHIVED => '已归档',
            self::CANCELLED => '已取消',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::PENDING => 'warning',
            self::ASSIGNED => 'info',
            self::IN_PROGRESS => 'primary',
            self::COMPLETED => 'success',
            self::CONFIRMED => 'success',
            self::ARCHIVED => 'info',
            self::CANCELLED => 'danger',
        };
    }
}

enum Urgency: string
{
    case NORMAL = 'normal';
    case URGENT = 'urgent';
    case CRITICAL = 'critical';

    public function label(): string
    {
        return match ($this) {
            self::NORMAL => '普通',
            self::URGENT => '紧急',
            self::CRITICAL => '特急',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::NORMAL => 'info',
            self::URGENT => 'warning',
            self::CRITICAL => 'danger',
        };
    }
}

enum ApprovalStatus: string
{
    case PENDING = 'pending';
    case APPROVED = 'approved';
    case REJECTED = 'rejected';
    case CANCELLED = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::PENDING => '待审批',
            self::APPROVED => '已通过',
            self::REJECTED => '已驳回',
            self::CANCELLED => '已取消',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::PENDING => 'warning',
            self::APPROVED => 'success',
            self::REJECTED => 'danger',
            self::CANCELLED => 'info',
        };
    }
}

enum CustomerCategory: string
{
    case VIP = 'vip';
    case NORMAL = 'normal';
    case POTENTIAL = 'potential';

    public function label(): string
    {
        return match ($this) {
            self::VIP => 'VIP客户',
            self::NORMAL => '普通客户',
            self::POTENTIAL => '潜在客户',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::VIP => 'warning',
            self::NORMAL => 'success',
            self::POTENTIAL => 'info',
        };
    }
}

enum LeaveType: string
{
    case ANNUAL = 'annual';
    case PERSONAL = 'personal';
    case SICK = 'sick';
    case MATERNITY = 'maternity';
    case MARRIAGE = 'marriage';
    case COMPASSIONATE = 'compassionate';
    case OTHER = 'other';

    public function label(): string
    {
        return match ($this) {
            self::ANNUAL => '年假',
            self::PERSONAL => '事假',
            self::SICK => '病假',
            self::MATERNITY => '产假',
            self::MARRIAGE => '婚假',
            self::COMPASSIONATE => '丧假',
            self::OTHER => '其他',
        };
    }
}

enum ExpenseCategory: string
{
    case TRAVEL = 'travel';
    case HOSPITALITY = 'hospitality';
    case OFFICE = 'office';
    case TRANSPORT = 'transport';
    case PROJECT_COST = 'project_cost';
    case OTHER = 'other';

    public function label(): string
    {
        return match ($this) {
            self::TRAVEL => '差旅费',
            self::HOSPITALITY => '招待费',
            self::OFFICE => '办公费',
            self::TRANSPORT => '交通费',
            self::PROJECT_COST => '项目成本',
            self::OTHER => '其他',
        };
    }
}
