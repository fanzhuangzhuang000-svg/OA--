<?php
/**
 * 检查线索和商机表结构及数据
 */

require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

echo "🔍 检查线索和商机表结构及数据...\n\n";

// 1. 检查leads表结构
echo "📋 1. leads表结构:\n";
$leadsColumns = Schema::getColumnListing('leads');
echo "  字段: " . implode(', ', $leadsColumns) . "\n\n";

// 2. 检查leads数据
$leadsCount = DB::table('leads')->count();
echo "  数据量: {$leadsCount} 条\n";

if ($leadsCount > 0) {
    echo "  示例数据 (前3条):\n";
    $leads = DB::table('leads')->limit(3)->get();
    foreach ($leads as $index => $lead) {
        echo "    [{$index}] ";
        foreach ($leadsColumns as $col) {
            if (isset($lead->$col)) {
                echo "{$col}={$lead->$col} ";
            }
        }
        echo "\n";
    }
    
    // 检查状态分布
    if (in_array('status', $leadsColumns)) {
        echo "\n  状态分布:\n";
        $statusCounts = DB::table('leads')
            ->select('status', DB::raw('COUNT(*) as count'))
            ->groupBy('status')
            ->get();
        
        foreach ($statusCounts as $status) {
            echo "    {$status->status}: {$status->count} 条\n";
        }
    }
}

echo "\n" . str_repeat("-", 60) . "\n\n";

// 3. 检查opportunities表结构
echo "📈 2. opportunites表结构:\n";
$oppColumns = Schema::getColumnListing('opportunities');
echo "  字段: " . implode(', ', $oppColumns) . "\n\n";

// 4. 检查opportunities数据
$oppCount = DB::table('opportunities')->count();
echo "  数据量: {$oppCount} 条\n";

if ($oppCount > 0) {
    echo "  示例数据 (前3条):\n";
    $opps = DB::table('opportunities')->limit(3)->get();
    foreach ($opps as $index => $opp) {
        echo "    [{$index}] ";
        foreach ($oppColumns as $col) {
            if (isset($opp->$col)) {
                echo "{$col}={$opp->$col} ";
            }
        }
        echo "\n";
    }
    
    // 检查状态分布
    if (in_array('status', $oppColumns)) {
        echo "\n  状态分布:\n";
        $statusCounts = DB::table('opportunities')
            ->select('status', DB::raw('COUNT(*) as count'))
            ->groupBy('status')
            ->get();
        
        foreach ($statusCounts as $status) {
            echo "    {$status->status}: {$status->count} 条\n";
        }
    }
    
    // 检查阶段分布（看板通常需要阶段字段）
    if (in_array('stage', $oppColumns)) {
        echo "\n  阶段分布:\n";
        $stageCounts = DB::table('opportunities')
            ->select('stage', DB::raw('COUNT(*) as count'))
            ->groupBy('stage')
            ->get();
        
        foreach ($stageCounts as $stage) {
            echo "    {$stage->stage}: {$stage->count} 条\n";
        }
    }
}

echo "\n" . str_repeat("=", 60) . "\n";
echo "✅ 检查完成\n";
