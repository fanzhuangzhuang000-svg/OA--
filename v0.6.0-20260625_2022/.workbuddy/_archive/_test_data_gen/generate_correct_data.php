<?php
// 在152服务器上生成测试数据（根据实际表结构修正）
// 保存为 /tmp/generate_correct_data.php

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

// 1. 生成考勤数据（根据实际表结构）
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
                'clock_in' => sprintf('%02d:%02d:%02d', rand(8, 9), rand(0, 59), rand(0, 59)),
                'clock_in_location' => '公司',
                'clock_in_lat' => rand(31, 32) + (rand(0, 999999) / 1000000),
                'clock_in_lng' => rand(120, 121) + (rand(0, 999999) / 1000000),
                'clock_out' => sprintf('%02d:%02d:%02d', rand(17, 19), rand(0, 59), rand(0, 59)),
                'clock_out_location' => '公司',
                'clock_out_lat' => rand(31, 32) + (rand(0, 999999) / 1000000),
                'clock_out_lng' => rand(120, 121) + (rand(0, 999999) / 1000000),
                'status' => $statuses[array_rand($statuses)],
                'work_hours' => rand(7, 10) + (rand(0, 9) / 10),
                'overtime_hours' => rand(0, 3) + (rand(0, 9) / 10),
                'project_id' => null,
                'remark' => '测试数据',
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

// 2. 生成报销数据（根据实际表结构）
echo "\n2. 生成报销数据...\n";
$expenseCount = 0;
$categories = ['travel', 'meal', 'office', 'other'];
$statuses = ['pending', 'approved', 'rejected'];

for ($i = 0; $i < 80; $i++) {
    try {
        $claimNo = 'EXP-' . date('Ymd') . '-' . sprintf('%04d', $i + 1);
        DB::table('expense_claims')->insert([
            'claim_no' => $claimNo,
            'user_id' => $userIds[array_rand($userIds)],
            'category' => $categories[array_rand($categories)],
            'total_amount' => rand(100, 5000) + (rand(0, 99) / 100),
            'project_id' => count($projectIds) > 0 ? $projectIds[array_rand($projectIds)] : null,
            'description' => '测试报销 #' . ($i + 1),
            'status' => $statuses[array_rand($statuses)],
            'approver_id' => $userIds[array_rand($userIds)],
            'approved_at' => rand(0, 1) == 1 ? date('Y-m-d H:i:s', strtotime("-" . rand(0, 30) . " days")) : null,
            'paid_at' => null,
            'paid_amount' => 0,
            'reject_reason' => null,
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $expenseCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$expenseCount} 条报销记录\n";

// 3. 生成应付数据（根据实际表结构）
echo "\n3. 生成应付数据...\n";
$payableCount = 0;
$statuses = ['pending', 'partial', 'paid'];

for ($i = 0; $i < 40; $i++) {
    try {
        $amount = rand(1000, 50000) + (rand(0, 99) / 100);
        DB::table('payables')->insert([
            'supplier_id' => null, // 可能为null
            'project_id' => count($projectIds) > 0 ? $projectIds[array_rand($projectIds)] : null,
            'amount' => $amount,
            'paid_amount' => 0,
            'remaining_amount' => $amount,
            'due_date' => date('Y-m-d', strtotime("+" . rand(1, 90) . " days")),
            'paid_date' => null,
            'payment_term' => '月结',
            'status' => $statuses[array_rand($statuses)],
            'notes' => '测试应付 #' . ($i + 1),
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $payableCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$payableCount} 条应付记录\n";

// 4. 生成消息数据（根据实际表结构）
echo "\n4. 生成消息数据...\n";
$notificationCount = 0;
$types = ['info', 'warning', 'error', 'success'];
$levels = ['low', 'normal', 'high', 'urgent'];

for ($i = 0; $i < 150; $i++) {
    try {
        DB::table('notifications')->insert([
            'type' => $types[array_rand($types)],
            'title' => '测试消息 #' . ($i + 1),
            'content' => '这是一条测试消息的内容。' . ($i + 1),
            'data' => json_encode(['test' => true, 'index' => $i + 1]),
            'read_at' => rand(0, 1) == 1 ? date('Y-m-d H:i:s', strtotime("-" . rand(0, 30) . " days")) : null,
            'notifiable_id' => $userIds[array_rand($userIds)],
            'notifiable_type' => 'App\\Models\\User',
            'sender_id' => $userIds[array_rand($userIds)],
            'level' => $levels[array_rand($levels)],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $notificationCount++;
    } catch (Exception $e) {
        echo "  错误: " . $e->getMessage() . "\n";
    }
}
echo "   ✅ 生成了 {$notificationCount} 条消息记录\n";

echo "\n✅ 第一阶段测试数据生成完成！\n";
echo "⚠️ 注意: 还需要为其他模块生成数据（售后服务、采购、销售等）\n";
?>