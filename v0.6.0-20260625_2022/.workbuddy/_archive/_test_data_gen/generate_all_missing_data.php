<?php
/**
 * 152服务器缺失测试数据生成脚本
 * 为所有空白表和低数据表生成测试数据
 * 时间跨度：2025-12-01 至 2026-06-22（至少6个月）
 */

// 引导Laravel应用
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

echo "🚀 开始为152服务器生成缺失的测试数据...\n\n";

$startDate = '2025-12-01';
$endDate = '2026-06-22';

// 辅助函数
function randomDate($start, $end) {
    $timestamp = mt_rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

function randomElement($array) {
    return $array[array_rand($array)];
}

// ==================== 1. 基础数据补充 ====================

echo "📊 1. 补充基础数据...\n";

// 1.1 补充用户账号（users表已有9个，增加到30个）
$currentUsers = DB::table('users')->count();
if ($currentUsers < 30) {
    $newUsers = 30 - $currentUsers;
    echo "  补充 {$newUsers} 个用户账号...\n";
    
    $userNames = ['张伟', '王芳', '李强', '刘洋', '陈静', '杨明', '赵丽', '黄勇', '周杰', '吴秀'];
    $positions = ['技术总监', '项目经理', '前端工程师', '后端工程师', '测试工程师', 'UI设计师', '运维工程师', '产品经理', '销售经理', '财务专员'];
    
    for ($i = 0; $i < $newUsers; $i++) {
        try {
            DB::table('users')->insert([
                'username' => 'user' . ($currentUsers + $i + 1),
                'password' => Hash::make('password123'),
                'name' => $userNames[$i % count($userNames)] . ($i + 1),
                'email' => 'user' . ($currentUsers + $i + 1) . '@example.com',
                'phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                'position' => $positions[$i % count($positions)],
                'department' => randomElement(['技术部', '项目部', '销售部', '财务部', '人事部']),
                'status' => 1,
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
        } catch (\Exception $e) {
            // 忽略重复
        }
    }
    echo "    ✅ 用户账号补充完成\n";
}

// 1.2 补充员工档案（employee_profiles）
$currentProfiles = DB::table('employee_profiles')->count();
$userIds = DB::table('users')->pluck('id')->toArray();
$newProfiles = 0;

foreach ($userIds as $userId) {
    $exists = DB::table('employee_profiles')->where('user_id', $userId)->exists();
    if (!$exists) {
        try {
            DB::table('employee_profiles')->insert([
                'user_id' => $userId,
                'employee_no' => 'EMP' . str_pad($userId, 4, '0', STR_PAD_LEFT),
                'hire_date' => randomDate('2023-01-01', '2025-11-30'),
                'contract_type' => randomElement(['全职', '兼职', '实习']),
                'base_salary' => mt_rand(5000, 25000),
                'salary_allowance' => mt_rand(500, 3000),
                'emergency_contact' => '紧急联系人' . $userId,
                'emergency_phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                'bank_name' => randomElement(['工商银行', '建设银行', '农业银行', '中国银行']),
                'bank_account' => '622' . mt_rand(1000, 9999) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $newProfiles++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
}
echo "  ✅ 员工档案补充了 {$newProfiles} 条\n";

// ==================== 2. 生成空白表数据 ====================

echo "\n📝 2. 为空白表生成数据...\n";

// 2.1 sales_products（销售产品）
$count = DB::table('sales_products')->count();
if ($count == 0) {
    echo "  生成销售产品数据...\n";
    $products = [
        ['name' => '安防监控摄像头', 'category' => '硬件', 'price' => 599.00],
        ['name' => '门禁控制器', 'category' => '硬件', 'price' => 1299.00],
        ['name' => '报警器', 'category' => '硬件', 'price' => 299.00],
        ['name' => '监控安装服务', 'category' => '服务', 'price' => 200.00],
        ['name' => '年度维护服务', 'category' => '服务', 'price' => 5000.00],
    ];
    
    $productCount = 0;
    foreach ($products as $product) {
        for ($i = 0; $i < 10; $i++) {
            try {
                DB::table('sales_products')->insert([
                    'name' => $product['name'] . '（型号' . ($i + 1) . '）',
                    'category' => $product['category'],
                    'price' => $product['price'] + mt_rand(-100, 100),
                    'description' => $product['name'] . '的详细描述',
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $productCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$productCount} 条销售产品记录\n";
}

// 2.2 certificates（证书管理）
$count = DB::table('certificates')->count();
if ($count == 0) {
    echo "  生成证书管理数据...\n";
    $certTypes = ['安全员证', '消防证', '电工证', '项目经理证', '建造师证'];
    $certCount = 0;
    
    foreach ($userIds as $userId) {
        if (mt_rand(0, 1)) { // 50%概率有证书
            try {
                DB::table('certificates')->insert([
                    'user_id' => $userId,
                    'type' => randomElement($certTypes),
                    'cert_no' => 'CERT' . str_pad($userId, 6, '0', STR_PAD_LEFT),
                    'issue_date' => randomDate('2023-01-01', '2025-12-31'),
                    'expire_date' => randomDate('2026-01-01', '2028-12-31'),
                    'status' => randomElement(['valid', 'expired', 'pending']),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $certCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$certCount} 条证书记录\n";
}

// 2.3 quotation_items（报价单明细）
$quotationIds = DB::table('quotations')->pluck('id')->toArray();
$count = DB::table('quotation_items')->count();
if ($count == 0 && count($quotationIds) > 0) {
    echo "  生成报价单明细数据...\n";
    $itemCount = 0;
    
    foreach ($quotationIds as $quotationId) {
        $numItems = mt_rand(3, 8);
        for ($i = 0; $i < $numItems; $i++) {
            try {
                DB::table('quotation_items')->insert([
                    'quotation_id' => $quotationId,
                    'product_name' => randomElement(['安防摄像头', '门禁系统', '报警器', '监控硬盘', '网线']),
                    'quantity' => mt_rand(1, 50),
                    'unit_price' => mt_rand(100, 5000),
                    'total_price' => 0, // 会在数据库计算
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $itemCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$itemCount} 条报价单明细记录\n";
}

// 2.4 project_pool（项目池）
$count = DB::table('project_pool')->count();
if ($count == 0) {
    echo "  生成项目池数据...\n";
    $poolCount = 0;
    
    for ($i = 0; $i < 20; $i++) {
        try {
            DB::table('project_pool')->insert([
                'name' => '潜在项目' . ($i + 1),
                'customer_name' => '潜在客户' . ($i + 1),
                'estimated_amount' => mt_rand(50000, 500000),
                'probability' => mt_rand(10, 90),
                'expected_close_date' => randomDate('2026-07-01', '2026-12-31'),
                'status' => randomElement(['pending', 'in_progress', 'won', 'lost']),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $poolCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "    ✅ 生成了 {$poolCount} 条项目池记录\n";
}

// 2.5 purchase_requirements（采购需求）
$count = DB::table('purchase_requirements')->count();
if ($count == 0) {
    echo "  生成采购需求数据...\n";
    $reqCount = 0;
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('purchase_requirements')->insert([
                'title' => '采购需求' . ($i + 1),
                'description' => '需要采购' . randomElement(['摄像头', '门禁', '报警器', '线材', '硬盘']),
                'quantity' => mt_rand(1, 100),
                'estimated_price' => mt_rand(1000, 50000),
                'status' => randomElement(['pending', 'approved', 'rejected', 'completed']),
                'created_by' => randomElement($userIds),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $reqCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "    ✅ 生成了 {$reqCount} 条采购需求记录\n";
}

// 2.6 employee_skills（员工技能）
$count = DB::table('employee_skills')->count();
if ($count == 0) {
    echo "  生成员工技能数据...\n";
    $skillCount = 0;
    $skills = ['PHP', 'Vue.js', 'Laravel', 'MySQL', '项目管理', 'UI设计', '测试', '运维', '安防技术', '电工'];
    
    foreach ($userIds as $userId) {
        $numSkills = mt_rand(1, 4);
        $userSkills = array_rand(array_flip($skills), $numSkills);
        if (!is_array($userSkills)) $userSkills = [$userSkills];
        
        foreach ($userSkills as $skill) {
            try {
                DB::table('employee_skills')->insert([
                    'user_id' => $userId,
                    'skill' => $skill,
                    'level' => randomElement(['初级', '中级', '高级', '专家']),
                    'years' => mt_rand(1, 10),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $skillCount++;
            } catch (\Exception $e) {
                // 忽略重复
            }
        }
    }
    echo "    ✅ 生成了 {$skillCount} 条员工技能记录\n";
}

// 2.7 purchase_plans（采购计划）
$count = DB::table('purchase_plans')->count();
if ($count == 0) {
    echo "  生成采购计划数据...\n";
    $planCount = 0;
    
    for ($i = 0; $i < 15; $i++) {
        try {
            DB::table('purchase_plans')->insert([
                'title' => '采购计划' . ($i + 1),
                'description' => '季度采购计划',
                'total_amount' => mt_rand(10000, 200000),
                'status' => randomElement(['draft', 'pending', 'approved', 'completed']),
                'created_by' => randomElement($userIds),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $planCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "    ✅ 生成了 {$planCount} 条采购计划记录\n";
}

// 2.8 sales_follow_up_attachments（销售跟进附件）
$count = DB::table('sales_follow_up_attachments')->count();
if ($count == 0) {
    echo "  生成销售跟进附件数据...\n";
    $followUpIds = DB::table('sales_follow_ups')->pluck('id')->toArray();
    $attachCount = 0;
    
    foreach ($followUpIds as $followUpId) {
        if (mt_rand(0, 1)) { // 50%概率有附件
            try {
                DB::table('sales_follow_up_attachments')->insert([
                    'follow_up_id' => $followUpId,
                    'file_name' => '跟进记录附件' . $followUpId . '.pdf',
                    'file_path' => '/uploads/sales/' . $followUpId . '.pdf',
                    'file_size' => mt_rand(100000, 5000000),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $attachCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$attachCount} 条销售跟进附件记录\n";
}

// 2.9 purchase_shipment_items（采购发货明细）
$count = DB::table('purchase_shipment_items')->count();
if ($count == 0) {
    echo "  生成采购发货明细数据...\n";
    $shipmentIds = DB::table('purchase_shipments')->pluck('id')->toArray();
    $itemCount = 0;
    
    foreach ($shipmentIds as $shipmentId) {
        $numItems = mt_rand(1, 5);
        for ($i = 0; $i < $numItems; $i++) {
            try {
                DB::table('purchase_shipment_items')->insert([
                    'shipment_id' => $shipmentId,
                    'product_name' => randomElement(['安防摄像头', '门禁控制器', '报警器', '网线', '硬盘']),
                    'quantity' => mt_rand(1, 50),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $itemCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$itemCount} 条采购发货明细记录\n";
}

echo "\n✅ 空白表数据生成完成\n";

// ==================== 3. 补充低数据表 ====================

echo "\n📈 3. 补充低数据表...\n";

// 3.1 positions（职位）
$count = DB::table('positions')->count();
if ($count < 20) {
    echo "  补充职位数据...\n";
    $positions = [
        ['name' => '技术总监', 'department' => '技术部'],
        ['name' => '项目经理', 'department' => '项目部'],
        ['name' => '前端工程师', 'department' => '技术部'],
        ['name' => '后端工程师', 'department' => '技术部'],
        ['name' => '测试工程师', 'department' => '技术部'],
        ['name' => 'UI设计师', 'department' => '技术部'],
        ['name' => '运维工程师', 'department' => '技术部'],
        ['name' => '产品经理', 'department' => '项目部'],
        ['name' => '销售经理', 'department' => '销售部'],
        ['name' => '财务专员', 'department' => '财务部'],
        ['name' => '人事专员', 'department' => '人事部'],
        ['name' => '行政专员', 'department' => '行政部'],
        ['name' => '保安队长', 'department' => '安防部'],
        ['name' => '电工班长', 'department' => '工程部'],
        ['name' => '仓库管理员', 'department' => '仓储部'],
    ];
    
    $posCount = 0;
    foreach ($positions as $position) {
        try {
            DB::table('positions')->insert([
                'name' => $position['name'],
                'department' => $position['department'],
                'description' => $position['name'] . '职位描述',
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $posCount++;
        } catch (\Exception $e) {
            // 忽略重复
        }
    }
    echo "    ✅ 补充了 {$posCount} 个职位\n";
}

// 3.2 warehouses（仓库）
$count = DB::table('warehouses')->count();
if ($count < 10) {
    echo "  补充仓库数据...\n";
    $warehouseCount = 0;
    
    $warehouses = ['主仓库', '安防设备库', '电子设备库', '线材库', '工具库', '备品备件库', '危险品库'];
    foreach ($warehouses as $warehouse) {
        try {
            DB::table('warehouses')->insert([
                'name' => $warehouse,
                'location' => '仓库地址' . ($warehouseCount + 1),
                'manager' => randomElement($userIds),
                'phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                'status' => 1,
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $warehouseCount++;
        } catch (\Exception $e) {
            // 忽略重复
        }
    }
    echo "    ✅ 补充了 {$warehouseCount} 个仓库\n";
}

// 3.3 shifts（排班）
$count = DB::table('shifts')->count();
if ($count < 30) {
    echo "  生成排班数据...\n";
    $shiftCount = 0;
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('shifts')->insert([
                'user_id' => randomElement($userIds),
                'shift_date' => randomDate($startDate, $endDate),
                'shift_type' => randomElement(['早班', '晚班', '夜班', '休息']),
                'start_time' => randomElement(['08:00:00', '16:00:00', '00:00:00']),
                'end_time' => randomElement(['16:00:00', '00:00:00', '08:00:00']),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $shiftCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "    ✅ 生成了 {$shiftCount} 条排班记录\n";
}

// 3.4 knowledge_categories（知识库分类）
$count = DB::table('knowledge_categories')->count();
if ($count < 15) {
    echo "  补充知识库分类...\n";
    $categories = ['技术文档', '操作手册', '培训资料', '产品介绍', '常见问题', '案例分析', '规章制度', '会议纪要'];
    $catCount = 0;
    
    foreach ($categories as $category) {
        try {
            DB::table('knowledge_categories')->insert([
                'name' => $category,
                'description' => $category . '分类',
                'created_by' => randomElement($userIds),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $catCount++;
        } catch (\Exception $e) {
            // 忽略重复
        }
    }
    echo "    ✅ 补充了 {$catCount} 个知识库分类\n";
}

// 3.5 disk_files（网盘文件）
$count = DB::table('disk_files')->count();
if ($count < 50) {
    echo "  生成网盘文件数据...\n";
    $folderIds = DB::table('disk_folders')->pluck('id')->toArray();
    $fileCount = 0;
    
    if (count($folderIds) > 0) {
        for ($i = 0; $i < 50; $i++) {
            try {
                DB::table('disk_files')->insert([
                    'folder_id' => randomElement($folderIds),
                    'name' => '文件' . ($i + 1) . '.pdf',
                    'file_path' => '/uploads/disk/' . ($i + 1) . '.pdf',
                    'file_size' => mt_rand(100000, 10000000),
                    'file_type' => 'pdf',
                    'created_by' => randomElement($userIds),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $fileCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "    ✅ 生成了 {$fileCount} 个网盘文件\n";
}

// 3.6 leave_requests（请假申请）
$count = DB::table('leave_requests')->count();
if ($count < 50) {
    echo "  生成请假申请数据...\n";
    $leaveCount = 0;
    
    for ($i = 0; $i < 50; $i++) {
        try {
            DB::table('leave_requests')->insert([
                'user_id' => randomElement($userIds),
                'type' => randomElement(['年假', '病假', '事假', '婚假', '产假']),
                'start_date' => randomDate($startDate, $endDate),
                'end_date' => randomDate($startDate, $endDate),
                'days' => mt_rand(1, 14),
                'reason' => '请假原因说明',
                'status' => randomElement(['pending', 'approved', 'rejected']),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $leaveCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "    ✅ 生成了 {$leaveCount} 条请假申请记录\n";
}

echo "\n✅ 低数据表补充完成\n";

// ==================== 4. 最终统计 ====================

echo "\n📊 4. 最终数据量统计...\n";
echo str_repeat("=", 60) . "\n";

$allTables = DB::select("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename");
$totalRecords = 0;

foreach ($allTables as $table) {
    $tableName = $table->tablename;
    $count = DB::table($tableName)->count();
    $totalRecords += $count;
    
    if ($count > 0) {
        echo sprintf("  %-35s %6d 条\n", $tableName, $count);
    }
}

echo str_repeat("=", 60) . "\n";
echo "📈 总记录数: {$totalRecords} 条\n";
echo "📋 总表数: " . count($allTables) . " 张\n";

echo "\n🎉 测试数据生成完成！\n";
echo "⏰ 时间跨度: {$startDate} 至 {$endDate} (至少6个月)\n";
