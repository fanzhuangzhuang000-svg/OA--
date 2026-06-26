<?php
// D:\work\website\OA\.workbuddy\generate_comprehensive_data.php
// 为152服务器生成全面的测试数据，覆盖所有模块，时间跨度至少6个月

require_once __DIR__ . '/../pc-api/vendor/autoload.php';

use Illuminate\Database\Capsule\Manager as Capsule;
use Illuminate\Database\Eloquent\Model;

// 加载Laravel环境
$app = require_once __DIR__ . '/../pc-api/vendor/autoload.php';
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__ . '/../pc-api');
$dotenv->load();

// 数据库配置
$capsule = new Capsule;
$capsule->addConnection([
    'driver'   => 'pgsql',
    'host'     => env('DB_HOST', '127.0.0.1'),
    'port'     => env('DB_PORT', '5432'),
    'database' => env('DB_DATABASE', 'oa_db'),
    'username' => env('DB_USERNAME', 'oa_user'),
    'password' => env('DB_PASSWORD', 'oa_pass'),
    'charset'  => 'utf8',
    'prefix'   => '',
    'schema'   => 'public',
]);

$capsule->setAsGlobal();
$capsule->bootEloquent();

use Illuminate\Support\Facades\DB;

echo "🚀 开始为152服务器生成全面的测试数据...\n";
echo "📅 时间跨度: 2025-12-01 至 2026-06-22 (至少6个月)\n\n";

$startDate = '2025-12-01';
$endDate = '2026-06-22';

// 获取现有数据用于关联
$users = DB::table('users')->pluck('id')->toArray();
$customers = DB::table('customers')->pluck('id')->toArray();
$projects = DB::table('projects')->pluck('id')->toArray();
$vehicles = DB::table('vehicles')->pluck('id')->toArray();
$items = DB::table('inventory_items')->pluck('id')->toArray();
$accounts = DB::table('finance_accounts')->pluck('id')->toArray();
$folders = DB::table('disk_folders')->pluck('id')->toArray();
$suppliers = DB::table('suppliers')->pluck('id')->toArray();

echo "📊 现有数据: \n";
echo "   - 用户: " . count($users) . " 个\n";
echo "   - 客户: " . count($customers) . " 个\n";
echo "   - 项目: " . count($projects) . " 个\n";
echo "   - 车辆: " . count($vehicles) . " 辆\n";
echo "   - 库存物品: " . count($items) . " 个\n";
echo "   - 财务账户: " . count($accounts) . " 个\n";
echo "   - 网盘文件夹: " . count($folders) . " 个\n";
echo "   - 供应商: " . count($suppliers) . " 个\n\n";

// 1. 生成更多员工数据
echo "1. 生成更多员工数据...\n";
$employeeCount = DB::table('employee_profiles')->count();
if ($employeeCount < 30) {
    $needCount = 30 - $employeeCount;
    echo "   📝 需要生成 {$needCount} 条员工记录...\n";
    
    $positions = ['软件工程师', '项目经理', '销售代表', '财务分析师', '人事专员', '运维工程师', '测试工程师', '产品经理', 'UI设计师', '网络工程师'];
    $departments = ['技术部', '销售部', '财务部', '人事部', '运维部', '产品部'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            $userId = $users[array_rand($users)];
            $position = $positions[array_rand($positions)];
            $department = $departments[array_rand($departments)];
            
            DB::table('employee_profiles')->insert([
                'user_id' => $userId,
                'employee_id' => 'EMP' . str_pad($employeeCount + $i + 1, 4, '0', STR_PAD_LEFT),
                'position' => $position,
                'department' => $department,
                'phone' => '1' . rand(3, 9) . str_pad(rand(0, 999999999), 9, '0', STR_PAD_LEFT),
                'hire_date' => date('Y-m-d', rand(strtotime($startDate), strtotime($endDate))),
                'status' => 'active',
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略重复错误
        }
    }
    echo "   ✅ 员工数据生成完成\n";
} else {
    echo "   ℹ️ 员工数据已足够了 ({$employeeCount} 条)\n";
}

// 2. 生成更多服务工单数据
echo "\n2. 生成更多服务工单数据...\n";
$serviceCount = DB::table('service_tickets')->count();
if ($serviceCount < 100) {
    $needCount = 100 - $serviceCount;
    echo "   📝 需要生成 {$needCount} 条服务工单...\n";
    
    $ticketTypes = ['repair', 'maintenance', 'installation', 'consultation', 'emergency'];
    $priorities = ['low', 'medium', 'high', 'urgent'];
    $statuses = ['open', 'in_progress', 'resolved', 'closed'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('service_tickets')->insert([
                'customer_id' => $customers[array_rand($customers)],
                'project_id' => $projects ? $projects[array_rand($projects)] : null,
                'type' => $ticketTypes[array_rand($ticketTypes)],
                'title' => '服务工单 #' . ($serviceCount + $i + 1),
                'description' => '这是服务工单的详细描述，用于测试系统功能。',
                'priority' => $priorities[array_rand($priorities)],
                'status' => $statuses[array_rand($statuses)],
                'assigned_to' => $users[array_rand($users)],
                'created_by' => $users[array_rand($users)],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 服务工单数据生成完成\n";
} else {
    echo "   ℹ️ 服务工单数据已足够了 ({$serviceCount} 条)\n";
}

// 3. 生成更多采购订单数据
echo "\n3. 生成更多采购订单数据...\n";
$purchaseCount = DB::table('purchase_orders')->count();
if ($purchaseCount < 50) {
    $needCount = 50 - $purchaseCount;
    echo "   📝 需要生成 {$needCount} 条采购订单...\n";
    
    $statuses = ['draft', 'pending', 'approved', 'received', 'cancelled'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('purchase_orders')->insert([
                'supplier_id' => $suppliers[array_rand($suppliers)],
                'order_number' => 'PO-' . date('Ymd') . '-' . str_pad($purchaseCount + $i + 1, 4, '0', STR_PAD_LEFT),
                'order_date' => date('Y-m-d', rand(strtotime($startDate), strtotime($endDate))),
                'total_amount' => rand(1000, 50000) + (rand(0, 99) / 100),
                'status' => $statuses[array_rand($statuses)],
                'created_by' => $users[array_rand($users)],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 采购订单数据生成完成\n";
} else {
    echo "   ℹ️ 采购订单数据已足够了 ({$purchaseCount} 条)\n";
}

// 4. 生成更多销售机会数据
echo "\n4. 生成更多销售机会数据...\n";
$opportunityCount = DB::table('sales_opportunities')->count();
if ($opportunityCount < 100) {
    $needCount = 100 - $opportunityCount;
    echo "   📝 需要生成 {$needCount} 条销售机会...\n";
    
    $statuses = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('sales_opportunities')->insert([
                'customer_id' => $customers[array_rand($customers)],
                'title' => '销售机会 #' . ($opportunityCount + $i + 1),
                'description' => '这是销售机会的详细描述。',
                'estimated_value' => rand(5000, 200000) + (rand(0, 99) / 100),
                'probability' => rand(10, 90),
                'status' => $statuses[array_rand($statuses)],
                'expected_close_date' => date('Y-m-d', rand(strtotime($startDate), strtotime($endDate))),
                'assigned_to' => $users[array_rand($users)],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 销售机会数据生成完成\n";
} else {
    echo "   ℹ️ 销售机会数据已足够了 ({$opportunityCount} 条)\n";
}

// 5. 生成更多车辆数据
echo "\n5. 生成更多车辆数据...\n";
$vehicleCount = DB::table('vehicles')->count();
if ($vehicleCount < 20) {
    $needCount = 20 - $vehicleCount;
    echo "   📝 需要生成 {$needCount} 辆车辆...\n";
    
    $brands = ['丰田', '本田', '大众', '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '蔚来', '小鹏'];
    $types = ['sedan', 'suv', 'truck', 'van', 'electric'];
    $statuses = ['available', 'in_use', 'maintenance', 'retired'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('vehicles')->insert([
                'plate_number' => '粤B' . str_pad(rand(10000, 99999), 5, '0', STR_PAD_LEFT),
                'brand' => $brands[array_rand($brands)],
                'model' => 'Model-' . chr(rand(65, 90)) . rand(1, 9),
                'type' => $types[array_rand($types)],
                'year' => rand(2018, 2025),
                'color' => ['黑色', '白色', '灰色', '蓝色', '红色'][array_rand(['黑色', '白色', '灰色', '蓝色', '红色'])],
                'status' => $statuses[array_rand($statuses)],
                'purchase_date' => date('Y-m-d', rand(strtotime($startDate), strtotime($endDate))),
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 车辆数据生成完成\n";
} else {
    echo "   ℹ️ 车辆数据已足够了 ({$vehicleCount} 条)\n";
}

// 6. 生成更多库存物品数据
echo "\n6. 生成更多库存物品数据...\n";
$itemCount = DB::table('inventory_items')->count();
if ($itemCount < 100) {
    $needCount = 100 - $itemCount;
    echo "   📝 需要生成 {$needCount} 个库存物品...\n";
    
    $categories = DB::table('inventory_categories')->pluck('id')->toArray();
    $warehouses = DB::table('warehouses')->pluck('id')->toArray();
    $names = ['笔记本电脑', '台式电脑', '显示器', '键盘', '鼠标', '打印机', '路由器', '交换机', '网线', '硬盘', '内存条', 'CPU', '主板', '显卡', '电源'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('inventory_items')->insert([
                'name' => $names[array_rand($names)] . ' ' . chr(rand(65, 90)) . rand(1, 99),
                'category_id' => $categories ? $categories[array_rand($categories)] : null,
                'warehouse_id' => $warehouses ? $warehouses[array_rand($warehouses)] : null,
                'quantity' => rand(1, 100),
                'unit' => ['台', '个', '件', '套', '箱'][array_rand(['台', '个', '件', '套', '箱'])],
                'unit_price' => rand(100, 5000) + (rand(0, 99) / 100),
                'status' => ['in_stock', 'out_of_stock', 'reserved'][array_rand(['in_stock', 'out_of_stock', 'reserved'])],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 库存物品数据生成完成\n";
} else {
    echo "   ℹ️ 库存物品数据已足够了 ({$itemCount} 条)\n";
}

// 7. 生成更多网盘文件夹和文件数据
echo "\n7. 生成更多网盘数据...\n";
$folderCount = DB::table('disk_folders')->count();
if ($folderCount < 50) {
    $needCount = 50 - $folderCount;
    echo "   📝 需要生成 {$needCount} 个网盘文件夹...\n";
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('disk_folders')->insert([
                'name' => '文件夹 ' . ($folderCount + $i + 1),
                'parent_id' => null,
                'created_by' => $users[array_rand($users)],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 网盘文件夹数据生成完成\n";
} else {
    echo "   ℹ️ 网盘文件夹数据已足够了 ({$folderCount} 条)\n";
}

// 8. 生成更多知识库文章数据
echo "\n8. 生成更多知识库文章数据...\n";
$articleCount = DB::table('knowledge_articles')->count();
if ($articleCount < 50) {
    $needCount = 50 - $articleCount;
    echo "   📝 需要生成 {$needCount} 篇知识库文章...\n";
    
    $categories = DB::table('knowledge_categories')->pluck('id')->toArray();
    $titles = ['技术文档', '操作手册', '常见问题', '最佳实践', '培训材料', '产品说明', 'API文档', '设计规范', '测试用例', '项目总结'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('knowledge_articles')->insert([
                'title' => $titles[array_rand($titles)] . ' ' . ($articleCount + $i + 1),
                'content' => '这是知识库文章的详细内容。可以使用Markdown格式编写。',
                'category_id' => $categories ? $categories[array_rand($categories)] : null,
                'created_by' => $users[array_rand($users)],
                'status' => ['draft', 'published', 'archived'][array_rand(['draft', 'published', 'archived'])],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 知识库文章数据生成完成\n";
} else {
    echo "   ℹ️ 知识库文章数据已足够了 ({$articleCount} 条)\n";
}

// 9. 生成更多考勤数据（确保时间跨度）
echo "\n9. 生成更多考勤数据（确保时间跨度）...\n";
$attendanceCount = DB::table('attendance_records')->count();
if ($attendanceCount < 2000) {
    $needCount = 2000 - $attendanceCount;
    echo "   📝 需要生成 {$needCount} 条考勤记录...\n";
    
    $types = ['check_in', 'check_out', 'leave', 'overtime'];
    $statuses = ['pending', 'approved', 'rejected'];
    
    // 生成从2025-12-01到2026-06-22的考勤数据
    $start = new DateTime($startDate);
    $end = new DateTime($endDate);
    $interval = new DateInterval('P1D');
    $dateRange = new DatePeriod($start, $interval, $end);
    
    $generated = 0;
    foreach ($dateRange as $date) {
        $dateStr = $date->format('Y-m-d');
        
        // 每天为每个员工生成考勤记录
        $employees = DB::table('employee_profiles')->pluck('id')->toArray();
        foreach ($employees as $employeeId) {
            if ($generated >= $needCount) break;
            
            try {
                DB::table('attendance_records')->insert([
                    'employee_id' => $employeeId,
                    'date' => $dateStr,
                    'check_in_time' => $dateStr . ' ' . sprintf('%02d', rand(7, 9)) . ':' . sprintf('%02d', rand(0, 59)) . ':' . sprintf('%02d', rand(0, 59)),
                    'check_out_time' => $dateStr . ' ' . sprintf('%02d', rand(17, 19)) . ':' . sprintf('%02d', rand(0, 59)) . ':' . sprintf('%02d', rand(0, 59)),
                    'status' => ['normal', 'late', 'early_leave', 'absent'][array_rand(['normal', 'late', 'early_leave', 'absent'])],
                    'created_at' => $dateStr . ' ' . sprintf('%02d', rand(7, 9)) . ':' . sprintf('%02d', rand(0, 59)) . ':' . sprintf('%02d', rand(0, 59)),
                    'updated_at' => now(),
                ]);
                $generated++;
            } catch (Exception $e) {
                // 忽略重复错误
            }
        }
        if ($generated >= $needCount) break;
    }
    echo "   ✅ 考勤数据生成完成 (时间跨度: {$startDate} 至 {$endDate})\n";
} else {
    echo "   ℹ️ 考勤数据已足够了 ({$attendanceCount} 条)\n";
}

// 10. 生成更多报销数据（确保时间跨度）
echo "\n10. 生成更多报销数据（确保时间跨度）...\n";
$expenseCount = DB::table('expense_claims')->count();
if ($expenseCount < 500) {
    $needCount = 500 - $expenseCount;
    echo "   📝 需要生成 {$needCount} 条报销记录...\n";
    
    $categories = ['差旅费', '交通费', '住宿费', '餐饮费', '办公用品', '培训费', '其他'];
    $statuses = ['draft', 'submitted', 'approved', 'rejected', 'reimbursed'];
    
    for ($i = 0; $i < $needCount; $i++) {
        try {
            DB::table('expense_claims')->insert([
                'user_id' => $users[array_rand($users)],
                'category' => $categories[array_rand($categories)],
                'amount' => rand(100, 5000) + (rand(0, 99) / 100),
                'description' => '报销描述 #' . ($expenseCount + $i + 1),
                'expense_date' => date('Y-m-d', rand(strtotime($startDate), strtotime($endDate))),
                'status' => $statuses[array_rand($statuses)],
                'created_at' => date('Y-m-d H:i:s', rand(strtotime($startDate), strtotime($endDate))),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {
            // 忽略错误
        }
    }
    echo "   ✅ 报销数据生成完成 (时间跨度: {$startDate} 至 {$endDate})\n";
} else {
    echo "   ℹ️ 报销数据已足够了 ({$expenseCount} 条)\n";
}

echo "\n" . str_repeat("=", 60) . "\n";
echo "🎉 全面的测试数据生成完成！\n";
echo "📅 所有数据时间跨度: {$startDate} 至 {$endDate} (至少6个月)\n";
echo str_repeat("=", 60) . "\n";

// 显示最终统计
echo "\n📊 最终数据量统计:\n";
$tables = [
    'users' => '用户',
    'customers' => '客户',
    'projects' => '项目',
    'vehicles' => '车辆',
    'inventory_items' => '库存物品',
    'finance_accounts' => '财务账户',
    'disk_folders' => '网盘文件夹',
    'knowledge_articles' => '知识库文章',
    'employee_profiles' => '员工',
    'attendance_records' => '考勤记录',
    'expense_claims' => '报销记录',
    'receivables' => '应收记录',
    'payables' => '应付记录',
    'notifications' => '消息通知',
    'service_tickets' => '服务工单',
    'purchase_orders' => '采购订单',
    'sales_opportunities' => '销售机会',
];

foreach ($tables as $table => $name) {
    try {
        $count = DB::table($table)->count();
        echo "   - {$name}: {$count} 条\n";
    } catch (Exception $e) {
        echo "   - {$name}: 表不存在或无法统计\n";
    }
}

echo "\n✅ 所有模块数据生成完成！\n";
?>