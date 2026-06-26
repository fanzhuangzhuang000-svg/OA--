<?php
/**
 * 检查线索和商机数据状态
 */

// 引导Laravel应用
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

echo "🔍 检查线索和商机数据状态...\n\n";

// 1. 检查leads表
echo "📋 1. 线索(leads)数据:\n";
$leadsCount = DB::table('leads')->count();
echo "  总记录数: {$leadsCount} 条\n";

if ($leadsCount > 0) {
    echo "  示例数据:\n";
    $leads = DB::table('leads')->limit(3)->get();
    foreach ($leads as $lead) {
        echo "    - ID:{$lead->id}, 姓名:{$lead->name}, 状态:" . ($lead->status ?? 'N/A') . "\n";
    }
    
    // 检查状态分布
    echo "\n  状态分布:\n";
    $statusCounts = DB::table('leads')
        ->select('status', DB::raw('COUNT(*) as count'))
        ->groupBy('status')
        ->get();
    
    foreach ($statusCounts as $status) {
        echo "    {$status->status}: {$status->count} 条\n";
    }
}

echo "\n" . str_repeat("-", 60) . "\n\n";

// 2. 检查opportunities表
echo "📈 2. 商机(opportunities)数据:\n";
$oppCount = DB::table('opportunities')->count();
echo "  总记录数: {$oppCount} 条\n";

if ($oppCount > 0) {
    echo "  示例数据:\n";
    $opps = DB::table('opportunities')->limit(3)->get();
    foreach ($opps as $opp) {
        echo "    - ID:{$opp->id}, 标题:{$opp->title}, 状态:" . ($opp->status ?? 'N/A') . "\n";
    }
    
    // 检查状态分布
    echo "\n  状态分布:\n";
    $statusCounts = DB::table('opportunities')
        ->select('status', DB::raw('COUNT(*) as count'))
        ->groupBy('status')
        ->get();
    
    foreach ($statusCounts as $status) {
        echo "    {$status->status}: {$status->count} 条\n";
    }
}

echo "\n" . str_repeat("=", 60) . "\n";
echo "✅ 检查完成\n";
