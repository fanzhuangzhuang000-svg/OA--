<?php
// 在152服务器上生成所有模块的测试数据（改进版）
// 保存为 /tmp/generate_all_data_v2.php

// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\n\n";

// 获取现有用户ID
$userIds = DB::table('users')->pluck('id')->toArray();
if (count($userIds) == 0) {
    echo "❌ 没有用户数据，无法生成测试数据\n";
    exit(1);
}
echo "✅ 找到 " . count($userIds) . " 个用户\n";

// 获取现有客户ID
$customerIds = DB::table('customers')->pluck('id')->toArray();
echo "✅ 找到 " . count($customerIds) . " 个客户\n";

// 获取现有项目ID
$projectIds = DB::table('projects')->pluck('id')->toArray();
echo "✅ 找到 " . count($projectIds) . " 个项目\n";

// 生成数据的起始和结束日期（6个月）
$startDate = '2025-12-01';
$endDate = '2026-06-22';

echo "\n开始生成测试数据...\n";
echo "时间范围: {$startDate} 至 {$endDate}\n\n";

// 1. 生成考勤数据
echo "1. 生成考勤数据...\n";
$attendanceCount = 0;
$statuses = ['normal', 'late', 'early_leave', 'absent'];

for ($i = 0; $i < 500; $i++) {
    try {
        // 随机生成日期（过去180天内）
        $daysAgo = rand(0, 180);
        $date = date('Y-m-d', strtotime("-{$daysAgo} days"));
        $userId = $userIds[array_rand($userIds)];
        
        // 检查是否已存在
        $exists = DB::table('attendance_records')
            ->where('user_id', $userId)
            ->where('date', $date)
            ->exists();
        
        if (!$exists) {
            DB::table('attendance_records')->insert([
                'user_id' => $userId,
                'date' => $date,
                'check_in' => $date . ' ' . sprintf('%02d:%02d:%02d', rand(8, 9), rand(0, 59), rand(0, 59)),
                'check_out' => $date . ' ' . sprintf('%02d:%02d:%02d', rand(17, 19), rand(0, 59), rand(0, 59)),
                'status' => $statuses[array_rand($statuses)],
                'created_at' => now(),
                'updated_at' => now(),
            ]);
            $attendanceCount++;
        }
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$attendanceCount} 条考勤记录\n";

// 2. 生成报销数据
echo "\n2. 生成报销数据...\n";
$expenseCount = 0;
$types = ['travel', 'meal', 'office', 'other'];
$statuses = ['pending', 'approved', 'rejected'];

for ($i = 0; $i < 100; $i++) {
    try {
        DB::table('expense_claims')->insert([
            'user_id' => $userIds[array_rand($userIds)],
            'amount' => rand(100, 5000) + (rand(0, 99) / 100),
            'type' => $types[array_rand($types)],
            'description' => '测试报销 #' . ($i + 1),
            'status' => $statuses[array_rand($statuses)],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $expenseCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$expenseCount} 条报销记录\n";

// 3. 生成应收数据
echo "\n3. 生成应收数据...\n";
$receivableCount = 0;
if (count($customerIds) > 0) {
    for ($i = 0; $i < 50; $i++) {
        try {
            DB::table('receivables')->insert([
                'customer_id' => $customerIds[array_rand($customerIds)],
                'amount' => rand(1000, 50000) + (rand(0, 99) / 100),
                'due_date' => date('Y-m-d', strtotime("+" . rand(1, 90) . " days")),
                'status' => ['pending', 'partial', 'paid'][array_rand(['pending', 'partial', 'paid'])],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $receivableCount++;
        } catch (Exception $e) {
            echo "  错误: " . $e->getMessage() . "\n";
        }
    }
}
echo "   ✅ 生成了 {$receivableCount} 条应收记录\n";

// 4. 生成应付数据
echo "\n4. 生成应付数据...\n";
$payableCount = 0;
for ($i = 0; $i < 50; $i++) {
    try {
        DB::table('payables')->insert([
            'supplier_id' => null, // 可能为null
            'amount' => rand(1000, 50000) + (rand(0, 99) / 100),
            'due_date' => date('Y-m-d', strtotime("+" . rand(1, 90) . " days")),
            'status' => ['pending', 'partial', 'paid'][array_rand(['pending', 'partial', 'paid'])],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $payableCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$payableCount} 条应付记录\n";

// 5. 生成消息数据
echo "\n5. 生成消息数据...\n";
$notificationCount = 0;
$types = ['info', 'warning', 'error', 'success'];

for ($i = 0; $i < 200; $i++) {
    try {
        DB::table('notifications')->insert([
            'user_id' => $userIds[array_rand($userIds)],
            'type' => $types[array_rand($types)],
            'title' => '测试消息 #' . ($i + 1),
            'content' => '这是一条测试消息的内容。' . ($i + 1),
            'is_read' => rand(0, 1) == 1,
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $notificationCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$notificationCount} 条消息记录\n";

// 6. 生成采购数据（如果需要）
echo "\n6. 检查采购数据...\n";
$purchaseOrderCount = DB::table('purchase_orders')->count();
echo "   当前采购订单: {$purchaseOrderCount} 条\n";

if ($purchaseOrderCount < 20) {
    $purchaseCount = 0;
    $statuses = ['pending', 'approved', 'completed'];
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('purchase_orders')->insert([
                'user_id' => $userIds[array_rand($userIds)],
                'supplier_id' => null,
                'order_number' => 'PO-' . date('Ymd') . '-' . ($i + 1),
                'total_amount' => rand(1000, 50000) + (rand(0, 99) / 100),
                'status' => $statuses[array_rand($statuses)],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $purchaseCount++;
        } catch (Exception $e) {
            echo "  错误: " . $e->getMessage() . "\n";
        }
    }
    echo "   ✅ 生成了 {$purchaseCount} 条采购订单\n";
}

// 7. 生成销售数据（如果需要）
echo "\n7. 检查销售数据...\n";
$opportunityCount = DB::table('opportunities')->count();
echo "   当前销售机会: {$opportunityCount} 条\n";

if ($opportunityCount < 20 && count($customerIds) > 0) {
    $salesCount = 0;
    $statuses = ['pending', 'won', 'lost'];
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('opportunities')->insert([
                'customer_id' => $customerIds[array_rand($customerIds)],
                'user_id' => $userIds[array_rand($userIds)],
                'title' => '测试销售机会 #' . ($i + 1),
                'amount' => rand(1000, 50000) + (rand(0, 99) / 100),
                'status' => $statuses[array_rand($statuses)],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $salesCount++;
        } catch (Exception $e) {
            echo "  错误: " . $e->getMessage() . "\n";
        }
    }
    echo "   ✅ 生成了 {$salesCount} 条销售机会\n";
}

echo "\n✅ 测试数据生成完成！\n";
echo "⚠️ 注意: 还需要为其他模块生成数据（如库存、车辆等）\n";
?>