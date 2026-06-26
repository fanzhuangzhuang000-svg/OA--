<?php
/**
 * 调试版本：检查为什么数据插入失败
 */

// 引导Laravel应用
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

echo "🔍 开始调试数据插入失败原因...\n\n";

// 测试插入一条员工档案记录，看是什么错误
echo "📝 测试1：插入员工档案记录...\n";
try {
    $userId = DB::table('users')->where('id', '>', 0)->value('id');
    if ($userId) {
        DB::table('employee_profiles')->insert([
            'user_id' => $userId,
            'employee_no' => 'TEST001',
            'hire_date' => '2024-01-01',
            'contract_type' => '全职',
            'base_salary' => 10000,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        echo "  ✅ 插入成功\n";
    } else {
        echo "  ⚠️  没有用户数据\n";
    }
} catch (\Exception $e) {
    echo "  ❌ 错误: " . $e->getMessage() . "\n";
    echo "  📋 完整错误: " . $e->getTraceAsString() . "\n";
}

// 检查employee_profiles表结构
echo "\n📋 检查employee_profiles表结构...\n";
try {
    $columns = Schema::getColumnListing('employee_profiles');
    echo "  字段列表: " . implode(', ', $columns) . "\n";
} catch (\Exception $e) {
    echo "  ❌ 错误: " . $e->getMessage() . "\n";
}

// 测试插入一条销售产品记录
echo "\n📝 测试2：插入销售产品记录...\n";
try {
    DB::table('sales_products')->insert([
        'name' => '测试产品',
        'created_at' => now(),
        'updated_at' => now(),
    ]);
    echo "  ✅ 插入成功\n";
} catch (\Exception $e) {
    echo "  ❌ 错误: " . $e->getMessage() . "\n";
}

// 检查sales_products表结构
echo "\n📋 检查sales_products表结构...\n";
try {
    $columns = Schema::getColumnListing('sales_products');
    echo "  字段列表: " . implode(', ', $columns) . "\n";
} catch (\Exception $e) {
    echo "  ❌ 错误: " . $e->getMessage() . "\n";
}

// 列出所有空白表并检查其中一个的表结构
echo "\n📊 检查所有空白表的字段...\n";
$emptyTables = [
    'sales_products',
    'certificates',
    'quotation_items',
    'project_pool',
    'purchase_requirements',
    'employee_skills',
    'purchase_plans',
    'sales_follow_up_attachments',
    'purchase_shipment_items',
];

foreach ($emptyTables as $table) {
    echo "\n  📋 表: {$table}\n";
    try {
        $columns = Schema::getColumnListing($table);
        if ($columns) {
            echo "    字段: " . implode(', ', $columns) . "\n";
        } else {
            echo "    ⚠️  表不存在或没有字段\n";
        }
    } catch (\Exception $e) {
        echo "    ❌ 错误: " . $e->getMessage() . "\n";
    }
}

echo "\n✅ 调试完成\n";
