<?php
// 在152服务器上生成所有模块的测试数据
// 保存为 /tmp/generate_all_test_data.php

// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\n\n";

// 设置中文faker
$faker = Faker\Factory::create('zh_CN');

// 生成数据的起始和结束日期（6个月）
$startDate = '2025-12-01';
$endDate = '2026-06-22';

echo "开始生成测试数据...\n";
echo "时间范围: {$startDate} 至 {$endDate}\n\n";

// 1. 生成员工数据（如果需要）
echo "1. 检查员工数据...\n";
$userCount = DB::table('users')->count();
echo "   当前用户数: {$userCount}\n";

if ($userCount < 20) {
    echo "   生成员工数据...\n";
    // 生成员工
    for ($i = 0; $i < 30; $i++) {
        try {
            $userId = DB::table('users')->insertGetId([
                'name' => $faker->name,
                'email' => $faker->unique()->safeEmail,
                'password' => bcrypt('password'),
                'created_at' => $faker->dateTimeBetween($startDate, $endDate),
                'updated_at' => now(),
            ]);
            echo "     创建用户: {$userId}\n";
        } catch (Exception $e) {
            echo "     错误: " . $e->getMessage() . "\n";
        }
    }
}

// 2. 生成考勤数据
echo "\n2. 生成考勤数据...\n";
$userIds = DB::table('users')->pluck('id')->toArray();

for ($i = 0; $i < 200; $i++) {
    try {
        $date = $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d');
        $userId = $faker->randomElement($userIds);
        
        // 检查是否已存在
        $exists = DB::table('attendance_records')
            ->where('user_id', $userId)
            ->where('date', $date)
            ->exists();
        
        if (!$exists) {
            DB::table('attendance_records')->insert([
                'user_id' => $userId,
                'date' => $date,
                'check_in_time' => $date . ' ' . $faker->time('H:i:s', '09:00:00'),
                'check_out_time' => $date . ' ' . $faker->time('H:i:s', '18:00:00'),
                'status' => $faker->randomElement(['normal', 'late', 'early_leave']),
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 考勤数据生成完成\n";

// 3. 生成报销数据
echo "\n3. 生成报销数据...\n";
for ($i = 0; $i < 50; $i++) {
    try {
        $expenseId = DB::table('expense_claims')->insertGetId([
            'user_id' => $faker->randomElement($userIds),
            'amount' => $faker->randomFloat(2, 100, 5000),
            'type' => $faker->randomElement(['travel', 'meal', 'office']),
            'description' => $faker->sentence,
            'status' => $faker->randomElement(['pending', 'approved', 'rejected']),
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 报销数据生成完成\n";

// 4. 生成应收数据
echo "\n4. 生成应收数据...\n";
$customerIds = DB::table('customers')->pluck('id')->toArray();
for ($i = 0; $i < 30; $i++) {
    try {
        DB::table('receivables')->insert([
            'customer_id' => $faker->randomElement($customerIds),
            'amount' => $faker->randomFloat(2, 1000, 50000),
            'due_date' => $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d'),
            'status' => $faker->randomElement(['pending', 'partial', 'paid']),
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 应收数据生成完成\n";

// 5. 生成应付数据
echo "\n5. 生成应付数据...\n";
for ($i = 0; $i < 30; $i++) {
    try {
        DB::table('payables')->insert([
            'supplier_id' => null, // 可能为null
            'amount' => $faker->randomFloat(2, 1000, 50000),
            'due_date' => $faker->dateTimeBetween($startDate, $endDate)->format('Y-m-d'),
            'status' => $faker->randomElement(['pending', 'partial', 'paid']),
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 应付数据生成完成\n";

// 6. 生成消息数据
echo "\n6. 生成消息数据...\n";
for ($i = 0; $i < 100; $i++) {
    try {
        DB::table('notifications')->insert([
            'user_id' => $faker->randomElement($userIds),
            'type' => $faker->randomElement(['info', 'warning', 'error']),
            'title' => $faker->sentence,
            'content' => $faker->paragraph,
            'is_read' => $faker->boolean,
            'created_at' => $faker->dateTimeBetween($startDate, $endDate),
            'updated_at' => now(),
        ]);
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 消息数据生成完成\n";

echo "\n✅ 测试数据生成完成！\n";
echo "⚠️ 注意: 这只是部分数据，还需要为其他模块生成数据\n";
?>