<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * v0.5.8 线索看板 BUG 修复
 *
 * 问题：DB leads.status 字段是 string(20) 但前端看板是 7 段 (new/contacted/qualified/proposal/negotiating/won/lost)，
 *      后端 boardMap 把 proposal/negotiating 都硬归一到 qualified，导致这两列永远空着。
 * 修法：业务上把 leads.status 升级为 7 段真值（兼容老数据，proposal/negotiating 是合法值）。
 *       字段本身够长（string(20) 装得下 negotiating），无结构变更，本 migration 仅更新 comment 文档。
 */
return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable('leads')) {
            return;
        }
        DB::statement("COMMENT ON COLUMN leads.status IS '状态: new/contacting/contacted/qualified/proposal/negotiating/converted/discarded/won/lost'");
    }

    public function down(): void
    {
        if (!Schema::hasTable('leads')) {
            return;
        }
        DB::statement("COMMENT ON COLUMN leads.status IS '状态: new/contacting/qualified/converted/discarded'");
    }
};
