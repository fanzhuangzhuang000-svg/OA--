<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class TenderProject extends Model
{
    protected $table = 'tender_projects';
    protected $fillable = [
        'code', 'name', 'description', 'project_id', 'rfq_id', 'created_by',
        'type', 'status', 'required_items', 'invited_supplier_ids',
        'publish_at', 'deadline', 'open_at', 'public_token',
        'awarded_bid_id', 'awarded_supplier_id', 'awarded_at', 'score_config',
    ];

    protected $casts = [
        'required_items'      => 'array',
        'invited_supplier_ids' => 'array',
        'score_config'        => 'array',
        'publish_at'          => 'datetime',
        'deadline'            => 'datetime',
        'open_at'             => 'datetime',
        'awarded_at'          => 'datetime',
    ];

    public function bids(): HasMany { return $this->hasMany(TenderBid::class); }
    public function attachments(): HasMany { return $this->hasMany(TenderAttachment::class); }
    public function project(): BelongsTo { return $this->belongsTo(Project::class); }
    public function rfq(): BelongsTo { return $this->belongsTo(ExternalQuoteRequest::class, 'rfq_id'); }
    public function creator(): BelongsTo { return $this->belongsTo(User::class, 'created_by'); }
    public function awardedSupplier(): BelongsTo { return $this->belongsTo(Supplier::class, 'awarded_supplier_id'); }
    public function awardedBid(): BelongsTo { return $this->belongsTo(TenderBid::class, 'awarded_bid_id'); }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'draft'      => '草稿',
            'published'  => '已发布',
            'bidding'    => '投标中',
            'evaluating' => '评标中',
            'awarded'    => '已定标',
            'cancelled'  => '已取消',
            'closed'     => '已关闭',
            default      => $this->status,
        };
    }
}
