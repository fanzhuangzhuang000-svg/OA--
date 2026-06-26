<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SupplierAttachment extends Model
{
    protected $table = 'supplier_attachments';

    protected $fillable = [
        'supplier_id', 'type', 'name', 'file_path',
        'file_size', 'mime_type', 'expire_date', 'uploaded_by',
    ];

    protected $casts = [
        'file_size'   => 'integer',
        'expire_date' => 'date',
    ];

    public const TYPE_LICENSE     = 'license';
    public const TYPE_CONTRACT    = 'contract';
    public const TYPE_CERTIFICATE = 'certificate';
    public const TYPE_BANK        = 'bank';
    public const TYPE_OTHER       = 'other';

    public function supplier(): BelongsTo
    {
        return $this->belongsTo(Supplier::class);
    }

    public function uploader(): BelongsTo
    {
        return $this->belongsTo(User::class, 'uploaded_by');
    }

    public function getTypeLabelAttribute(): string
    {
        return match ($this->type) {
            self::TYPE_LICENSE     => '营业执照',
            self::TYPE_CONTRACT    => '合同',
            self::TYPE_CERTIFICATE => '资质证书',
            self::TYPE_BANK        => '银行资料',
            default                => '其他',
        };
    }
}
