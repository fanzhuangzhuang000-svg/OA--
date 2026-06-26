<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * V0.5.7 块B — 系统数据字典
 *
 * 用于集中管理 7 类枚举:
 *   - repair_method  维修方式 (4 选 1)
 *   - customer_source 客户来源
 *   - device_type 设备类型
 *   - region 区域
 *   - fault_type 故障类型
 *   - urgency 紧急度
 *   - payment_method 支付方式
 *   - product_unit 产品单位
 *
 * 改这里 = 改所有引用页面的下拉
 */
class SystemDict extends Model
{
    use HasFactory;

    protected $table = 'system_dicts';

    protected $fillable = [
        'kind', 'code', 'label', 'color', 'icon',
        'sort_order', 'is_active', 'is_default',
        'description', 'extra',
        'created_by', 'updated_by',
    ];

    protected $casts = [
        'is_active'   => 'boolean',
        'is_default'  => 'boolean',
        'sort_order'  => 'integer',
        'extra'       => 'array',
    ];

    /** 7+1 类字典 kind 常量 */
    public const KIND_REPAIR_METHOD   = 'repair_method';
    public const KIND_CUSTOMER_SOURCE = 'customer_source';
    public const KIND_DEVICE_TYPE     = 'device_type';
    public const KIND_REGION          = 'region';
    public const KIND_FAULT_TYPE      = 'fault_type';
    public const KIND_URGENCY         = 'urgency';
    public const KIND_PAYMENT_METHOD  = 'payment_method';
    public const KIND_PRODUCT_UNIT    = 'product_unit';

    /** 所有 kind 列表 (前端初始化用) */
    public static function kinds(): array
    {
        return [
            self::KIND_REPAIR_METHOD   => '维修方式',
            self::KIND_CUSTOMER_SOURCE => '客户来源',
            self::KIND_DEVICE_TYPE     => '设备类型',
            self::KIND_REGION          => '区域',
            self::KIND_FAULT_TYPE      => '故障类型',
            self::KIND_URGENCY         => '紧急度',
            self::KIND_PAYMENT_METHOD  => '支付方式',
            self::KIND_PRODUCT_UNIT    => '产品单位',
        ];
    }
}
