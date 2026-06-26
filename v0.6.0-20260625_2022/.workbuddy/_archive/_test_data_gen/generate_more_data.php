<?php
// 在152服务器上生成更多模块的测试数据
// 保存为 /tmp/generate_more_data.php

// 加载Laravel环境
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

echo "✅ Laravel环境加载成功\n\n";

// 获取现有数据
$userIds = DB::table('users')->pluck('id')->toArray();
$customerIds = DB::table('customers')->pluck('id')->toArray();
$projectIds = DB::table('projects')->pluck('id')->toArray();
$supplierIds = DB::table('suppliers')->pluck('id')->toArray();

echo "✅ 找到 " . count($userIds) . " 个用户\n";
echo "✅ 找到 " . count($customerIds) . " 个客户\n";
echo "✅ 找到 " . count($projectIds) . " 个项目\n";
echo "✅ 找到 " . count($supplierIds) . " 个供应商\n\n";

echo "开始生成更多测试数据...\n\n";

// 1. 生成售后服务数据
echo "1. 生成售后服务数据...\n";
$serviceCount = 0;
$statuses = ['pending', 'processing', 'completed'];

if (count($customerIds) > 0) {
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('service_orders')->insert([
                'customer_id' => $customerIds[array_rand($customerIds)],
                'user_id' => $userIds[array_rand($userIds)],
                'title' => '测试服务工单 #' . ($i + 1000),
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
}
echo "   ✅ 生成了 {$serviceCount} 条服务工单\n";

// 2. 生成采购订单数据
echo "\n2. 生成采购订单数据...\n";
$purchaseCount = 0;
$statuses = ['pending', 'approved', 'completed'];

for ($i = 0; $i < 20; $i++) {
    try {
        DB::table('purchase_orders')->insert([
            'user_id' => $userIds[array_rand($userIds)],
            'supplier_id' => $supplierIds[array_rand($supplierIds)],
            'order_number' => 'PO-' . date('Ymd') . '-' . ($i + 1000),
            'total_amount' => rand(1000, 50000) + (rand(0, 99) / 100),
            'status' => $statuses[array_rand($statuses)],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $purchaseCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$purchaseCount} 条采购订单\n";

// 3. 生成销售机会数据
echo "\n3. 生成销售机会数据...\n";
$salesCount = 0;
$statuses = ['pending', 'won', 'lost'];

if (count($customerIds) > 0) {
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('opportunities')->insert([
                'customer_id' => $customerIds[array_rand($customerIds)],
                'user_id' => $userIds[array_rand($userIds)],
                'title' => '测试销售机会 #' . ($i + 1000),
                'amount' => rand(1000, 50000) + (rand(0, 99) / 100),
                'status' => $statuses[array_rand($statuses)],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $salesCount++;
        } catch (Exception $e) {
            // 忽略错误
        }
    }
}
echo "   ✅ 生成了 {$salesCount} 条销售机会\n";

// 4. 生成库存物品数据
echo "\n4. 生成库存物品数据...\n";
$inventoryCount = 0;

for ($i = 0; $i < 30; $i++) {
    try {
        DB::table('inventory_items')->insert([
            'name' => '测试物品 #' . ($i + 1000),
            'category_id' => null,
            'quantity' => rand(1, 100),
            'unit' => '个',
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $inventoryCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$inventoryCount} 个库存物品\n";

// 5. 生成车辆数据
echo "\n5. 检查车辆数据...\n";
$vehicleCount = DB::table('vehicles')->count();
echo "   当前车辆: {$vehicleCount} 辆\n";

if ($vehicleCount < 10) {
    $newVehicleCount = 0;
    for ($i = 0; $i < 10; $i++) {
        try {
            DB::table('vehicles')->insert([
                'name' => '测试车辆 #' . ($i + 1000),
                'license_plate' => '京A' . sprintf('%05d', $i + 1000),
                'status' => ['available', 'in_use'][array_rand(['available', 'in_use'])],
                'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
                'updated_at' => now(),
            ]);
            $newVehicleCount++;
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 生成了 {$newVehicleCount} 辆车\n";
}

// 6. 生成网盘数据
echo "\n6. 生成网盘数据...\n";
$diskCount = 0;

for ($i = 0; $i < 10; $i++) {
    try {
        DB::table('disk_folders')->insert([
            'name' => '测试文件夹 #' . ($i + 1000),
            'parent_id' => null,
            'created_by' => $userIds[array_rand($userIds)],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $diskCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$diskCount} 个网盘文件夹\n";

// 7. 生成知识库数据
echo "\n7. 生成知识库数据...\n";
$articleCount = 0;

for ($i = 0; $i < 20; $i++) {
    try {
        DB::table('knowledge_articles')->insert([
            'title' => '测试文章 #' . ($i + 1000),
            'content' => '这是一篇测试文章的内容。',
            'category_id' => null,
            'created_by' => $userIds[array_rand($userIds)],
            'created_at' => date('Y-m-d H:i:s', strtotime("-" . rand(0, 180) . " days")),
            'updated_at' => now(),
        ]);
        $articleCount++;
    } catch (Exception $e) {
        // 忽略错误
    }
}
echo "   ✅ 生成了 {$articleCount} 篇文章\n";

echo "\n✅ 更多测试数据生成完成！\n";
echo "⚠️ 注意: 还需要确保所有数据都有至少6个月的时间跨度\n";
?>