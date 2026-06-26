<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // v0.3.18 幂等保护：v0.3.14 全量部署时已建表，重跑会报 42P07
        if (Schema::hasTable('leads')) {
            return;
        }

        Schema::create('leads', function (Blueprint $table) {
            $table->id();
            $table->string('lead_no', 30)->unique()->comment('线索编号 LEAD-2026-001');
            $table->unsignedBigInteger('customer_id')->nullable()->comment('关联客户ID');
            $table->foreign('customer_id')->references('id')->on('customers')->onDelete('set null');
            $table->string('customer_name', 200)->nullable()->comment('客户名称（未建档时）');
            $table->string('contact_name', 50)->nullable()->comment('联系人');
            $table->string('contact_phone', 20)->nullable()->comment('联系电话');
            $table->string('contact_title', 50)->nullable()->comment('联系人职务');
            $table->string('source', 20)->default('online')->comment('来源: online/phone/exhibition/referral/other');
            $table->unsignedBigInteger('referrer_id')->nullable()->comment('推荐人ID');
            $table->text('requirement')->nullable()->comment('需求描述');
            $table->decimal('estimated_amount', 12, 2)->default(0)->comment('预计金额');
            $table->string('rating', 5)->default('C')->comment('评级 A/B/C/D');
            $table->string('status', 20)->default('new')->comment('状态: new/contacting/qualified/converted/discarded');
            $table->unsignedBigInteger('owner_id')->nullable()->comment('跟进人');
            $table->date('follow_up_at')->nullable()->comment('下次跟进日期');
            $table->timestamp('last_contact_at')->nullable()->comment('最近联系时间');
            $table->text('discard_reason')->nullable()->comment('丢弃原因');
            $table->timestamps();

            $table->index('status');
            $table->index('source');
            $table->index('owner_id');
            $table->index('customer_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('leads');
    }
};
