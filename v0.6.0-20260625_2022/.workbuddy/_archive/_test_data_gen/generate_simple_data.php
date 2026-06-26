<?php
// 在152服务器上生成测试数据（不依赖Faker）
// 保存为 /tmp/generate_simple_data.php

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

for ($i = 0; $i < 300; $i++) {
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
        // 忽略重复错误
    }
}
echo "   ✅ 生成了 {$attendanceCount} 条考勤记录\n";

// 2. 生成报销数据
echo "\n2. 生成报销数据...\n";
$expenseCount = 0;
$types = ['travel', 'meal', 'office', 'other'];
$statuses = ['pending', 'approved', 'rejected'];

for ($i = 0; $i < 80; $i++) {
    try {
        $expenseId = DB::table('expense_claims')->insertGetId([
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
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$expenseCount} 条报销记录\n";

// 3. 生成应收数据
echo "\n3. 生成应收数据...\n";
$receivableCount = 0;
if (count($customerIds) > 0) {
    for ($i = 0; $i < 40; $i++) {
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
            // 忽略错误
        }
    }
}
echo "   ✅ 生成了 {$receivableCount} 条应收记录\n";

// 4. 生成应付数据
echo "\n4. 生成应付数据...\n";
$payableCount = 0;
for ($i = 0; $i < 40; $i++) {
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
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$payableCount} 条应付记录\n";

// 5. 生成消息数据
echo "\n5. 生成消息数据...\n";
$notificationCount = 0;
$types = ['info', 'warning', 'error', 'success'];

for ($i = 0; $i < 150; $i++) {
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
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$notificationCount} 条消息记录\n";

// 6. 生成售后服务数据（如果需要）
echo "\n6. 检查售后服务数据...\n";
$serviceOrderCount = DB::table('service_orders')->count();
echo "   当前服务工单: {$serviceOrderCount} 条\n";

if ($serviceOrderCount < 20 && count($customerIds) > 0) {
    $serviceCount = 0;
    $statuses = ['pending', 'processing', 'completed'];
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('service_orders')->insert([
                'customer_id' => $customerIds[array_rand($customerIds)],
                'user_id' => $userIds[array_rand($userIds)],
                'title' => '测试服务工单 #' . ($i + 1),
                'description' => '这是一条测试服务工单的描述。',
                'status' => $statuses[array_rand($statuses)],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $serviceCount++;
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 生成了 {$serviceCount} 条服务工单\n";
}

echo "\n✅ 第一阶段测试数据生成完成！\n";
echo "⚠️ 注意: 还需要为其他模块生成数据（采购、销售、库存等）\n";
?>