<?php
/**
 * 检查线索和商机stage字段的所有可能值
 */

require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

echo "🔍 检查线索和商机stage字段的所有可能值...\n\n";

// 1. 检查leads表的所有stage值
echo "📋 1. leads表的所有stage值:\n";
$leadStages = DB::table('leads')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->orderBy('stage')
    ->get();

if (count($leadStages) > 0) {
    foreach ($leadStages as $stage) {
        echo "  '{$stage->stage}': {$stage->count} 条\n";
    }
} else {
    echo "  ⚠️  没有数据\n";
}

echo "\n" . str_repeat("-", 60) . "\n\n";

// 2. 检查opportunities表的所有stage值
echo "📈 2. opportunities表的所有stage值:\n";
$oppStages = DB::table('opportunities')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->orderBy('stage')
    ->get();

if (count($oppStages) > 0) {
    foreach ($oppStages as $stage) {
        echo "  '{$stage->stage}': {$stage->count} 条\n";
    }
} else {
    echo "  ⚠️  没有数据\n";
}

echo "\n" . str_repeat("=", 60) . "\n";
echo "✅ 检查完成\n";
echo "\n💡 现在需要知道前端看板组件定义的stage值，然后进行匹配\n";
