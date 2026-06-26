<?php
/**
 * 检查线索stage分布，并生成看板数据
 */

require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

echo "🔍 检查线索和商机数据，为看板做准备...\n\n";

$startDate = '2025-12-01';
$endDate = '2026-06-22';

// ==================== 1. 检查线索stage分布 ====================

echo "📋 1. 线索(leads) stage分布:\n";

$leadStageCounts = DB::table('leads')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->get();

if (count($leadStageCounts) > 0) {
    foreach ($leadStageCounts as $stage) {
        echo "  {$stage->stage}: {$stage->count} 条\n";
    }
} else {
    echo "  ⚠️  没有stage分布数据\n";
}

// 检查是否所有看板列都有数据
$allStages = ['new', 'contacted', 'qualified', 'proposal', 'negotiating', 'won', 'lost'];
$existingStages = DB::table('leads')->select('stage')->distinct()->pluck('stage')->toArray();

echo "\n  看板列检查:\n";
foreach ($allStages as $stage) {
    if (in_array($stage, $existingStages)) {
        $count = DB::table('leads')->where('stage', $stage)->count();
        echo "    ✅ {$stage}: {$count} 条\n";
    } else {
        echo "    ❌ {$stage}: 0 条 (需要生成)\n";
    }
}

// ==================== 2. 生成线索看板数据 ====================

echo "\n📝 2. 生成线索看板数据...\n";

$stagesToGenerate = [];
foreach ($allStages as $stage) {
    $count = DB::table('leads')->where('stage', $stage)->count();
    if ($count < 3) { // 每个阶段至少3条
        $stagesToGenerate[$stage] = 3 - $count;
    }
}

if (count($stagesToGenerate) > 0) {
    echo "  需要补充的阶段: " . implode(', ', array_keys($stagesToGenerate)) . "\n";
    
    $customerIds = DB::table('customers')->pluck('id')->toArray();
    $userIds = DB::table('users')->pluck('id')->toArray();
    $leadCount = 0;
    
    foreach ($stagesToGenerate as $stage => $numToGenerate) {
        for ($i = 0; $i < $numToGenerate; $i++) {
            try {
                $customerId = randomElement($customerIds);
                $customerName = DB::table('customers')->where('id', $customerId)->value('name');
                
                DB::table('leads')->insert([
                    'lead_no' => 'LD-' . date('Ym') . '-' . str_pad(DB::table('leads')->count() + 1, 4, '0', STR_PAD_LEFT),
                    'customer_id' => $customerId,
                    'customer_name' => $customerName,
                    'contact_name' => '联系人' . (DB::table('leads')->count() + 1),
                    'contact_phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                    'source' => randomElement(['cold_call', 'website', 'referral', 'exhibition']),
                    'rating' => randomElement(['A', 'B', 'C']),
                    'stage' => $stage,
                    'estimated_amount' => mt_rand(50000, 500000),
                    'notes' => '看板测试线索',
                    'owner_id' => randomElement($userIds),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $leadCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$leadCount} 条线索看板数据\n";
} else {
    echo "  ✅ 所有看板列都有数据，无需补充\n";
}

// ==================== 3. 检查商机stage分布 ====================

echo "\n📈 3. 商机(opportunities) stage分布:\n";

$oppStageCounts = DB::table('opportunities')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->get();

if (count($oppStageCounts) > 0) {
    foreach ($oppStageCounts as $stage) {
        echo "  {$stage->stage}: {$stage->count} 条\n";
    }
} else {
    echo "  ⚠️  没有stage分布数据\n";
}

// 检查是否所有看板列都有数据
$allOppStages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost'];
$existingOppStages = DB::table('opportunities')->select('stage')->distinct()->pluck('stage')->toArray();

echo "\n  看板列检查:\n";
foreach ($allOppStages as $stage) {
    if (in_array($stage, $existingOppStages)) {
        $count = DB::table('opportunities')->where('stage', $stage)->count();
        echo "    ✅ {$stage}: {$count} 条\n";
    } else {
        echo "    ❌ {$stage}: 0 条 (需要生成)\n";
    }
}

// ==================== 4. 生成商机看板数据 ====================

echo "\n📊 4. 生成商机看板数据...\n";

$oppStagesToGenerate = [];
foreach ($allOppStages as $stage) {
    $count = DB::table('opportunities')->where('stage', $stage)->count();
    if ($count < 3) { // 每个阶段至少3条
        $oppStagesToGenerate[$stage] = 3 - $count;
    }
}

if (count($oppStagesToGenerate) > 0) {
    echo "  需要补充的阶段: " . implode(', ', array_keys($oppStagesToGenerate)) . "\n";
    
    $leadIds = DB::table('leads')->pluck('id')->toArray();
    $customerIds = DB::table('customers')->pluck('id')->toArray();
    $userIds = DB::table('users')->pluck('id')->toArray();
    $oppCount = 0;
    
    foreach ($oppStagesToGenerate as $stage => $numToGenerate) {
        for ($i = 0; $i < $numToGenerate; $i++) {
            try {
                $leadId = count($leadIds) > 0 ? randomElement($leadIds) : null;
                $customerId = randomElement($customerIds);
                $customerName = DB::table('customers')->where('id', $customerId)->value('name');
                
                DB::table('opportunities')->insert([
                    'opportunity_no' => 'OPP-' . date('Ym') . '-' . str_pad(DB::table('opportunities')->count() + 1, 4, '0', STR_PAD_LEFT),
                    'lead_id' => $leadId,
                    'customer_id' => $customerId,
                    'customer_name' => $customerName,
                    'name' => '商机' . (DB::table('opportunities')->count() + 1),
                    'stage' => $stage,
                    'estimated_amount' => mt_rand(100000, 1000000),
                    'probability' => mt_rand(10, 90),
                    'expected_sign_date' => randomDate('2026-07-01', '2026-12-31'),
                    'sales_id' => randomElement($userIds),
                    'presale_id' => randomElement($userIds),
                    'owner_id' => randomElement($userIds),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $oppCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$oppCount} 条商机看板数据\n";
} else {
    echo "  ✅ 所有看板列都有数据，无需补充\n";
}

// ==================== 5. 最终统计 ====================

echo "\n📊 5. 最终看板数据统计...\n";
echo str_repeat("=", 60) . "\n";

// 线索看板数据
echo "线索看板数据:\n";
$leadStages = DB::table('leads')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->orderBy('stage')
    ->get();

foreach ($leadStages as $stage) {
    echo "  {$stage->stage}: {$stage->count} 条\n";
}

echo "\n";

// 商机看板数据
echo "商机看板数据:\n";
$oppStages = DB::table('opportunities')
    ->select('stage', DB::raw('COUNT(*) as count'))
    ->groupBy('stage')
    ->orderBy('stage')
    ->get();

foreach ($oppStages as $stage) {
    echo "  {$stage->stage}: {$stage->count} 条\n";
}

echo str_repeat("=", 60) . "\n";
echo "✅ 看板数据准备完成！\n";
echo "⏰ 时间跨度: {$startDate} 至 {$endDate} (至少6个月)\n";

function randomDate($start, $end) {
    $timestamp = mt_rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

function randomElement($array) {
    return $array[array_rand($array)];
}
