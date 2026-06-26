<?php
/**
 * 152服务器缺失测试数据生成脚本（修正版）
 * 根据实际表结构生成数据
 */

// 引导Laravel应用
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Schema;

echo "🚀 开始为152服务器生成缺失的测试数据（修正版）...\n\n";

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

// ==================== 1. 补充用户账号 ====================

echo "📊 1. 补充用户账号...\n";

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

$userIds = DB::table('users')->pluck('id')->toArray();

// ==================== 2. 补充员工档案 ====================

echo "\n📝 2. 补充员工档案...\n";

$existingProfileUserIds = DB::table('employee_profiles')->pluck('user_id')->toArray();
$newProfiles = 0;

foreach ($userIds as $userId) {
    if (!in_array($userId, $existingProfileUserIds)) {
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

$employeeProfileIds = DB::table('employee_profiles')->pluck('id')->toArray();

// ==================== 3. 生成销售产品数据 ====================

echo "\n📦 3. 生成销售产品数据...\n";

$count = DB::table('sales_products')->count();
if ($count == 0) {
    $productCount = 0;
    
    $products = [
        ['code' => 'CAM-001', 'name' => '安防监控摄像头', 'category_id' => 1, 'unit' => '台', 'spec' => '1080P', 'sale_price' => 599.00, 'cost_price' => 399.00],
        ['code' => 'ACC-001', 'name' => '门禁控制器', 'category_id' => 1, 'unit' => '个', 'spec' => '标准型', 'sale_price' => 1299.00, 'cost_price' => 899.00],
        ['code' => 'ALM-001', 'name' => '报警器', 'category_id' => 1, 'unit' => '个', 'spec' => '无线', 'sale_price' => 299.00, 'cost_price' => 199.00],
        ['code' => 'SRV-001', 'name' => '监控安装服务', 'category_id' => 2, 'unit' => '次', 'spec' => '标准安装', 'sale_price' => 200.00, 'cost_price' => 100.00],
        ['code' => 'SRV-002', 'name' => '年度维护服务', 'category_id' => 2, 'unit' => '年', 'spec' => '全年4次', 'sale_price' => 5000.00, 'cost_price' => 3000.00],
    ];
    
    foreach ($products as $product) {
        for ($i = 0; $i < 10; $i++) {
            try {
                DB::table('sales_products')->insert([
                    'code' => $product['code'] . '-' . str_pad($i + 1, 3, '0', STR_PAD_LEFT),
                    'name' => $product['name'] . '（型号' . ($i + 1) . '）',
                    'category_id' => $product['category_id'],
                    'unit' => $product['unit'],
                    'spec' => $product['spec'],
                    'sale_price' => $product['sale_price'] + mt_rand(-100, 100),
                    'cost_price' => $product['cost_price'],
                    'description' => $product['name'] . '的详细描述',
                    'status' => 'active',
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $productCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$productCount} 条销售产品记录\n";
}

// ==================== 4. 生成证书管理数据 ====================

echo "\n📜 4. 生成证书管理数据...\n";

$count = DB::table('certificates')->count();
if ($count == 0) {
    $certTypes = ['安全员证', '消防证', '电工证', '项目经理证', '建造师证'];
    $certCount = 0;
    
    foreach ($employeeProfileIds as $profileId) {
        if (mt_rand(0, 1)) { // 50%概率有证书
            try {
                DB::table('certificates')->insert([
                    'employee_profile_id' => $profileId,
                    'certificate_name' => randomElement($certTypes),
                    'certificate_no' => 'CERT' . str_pad($profileId, 6, '0', STR_PAD_LEFT),
                    'issue_date' => randomDate('2023-01-01', '2025-12-31'),
                    'expire_date' => randomDate('2026-01-01', '2028-12-31'),
                    'issuer' => randomElement(['人力资源和社会保障局', '安全生产监督管理局', '消防局']),
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
    echo "  ✅ 生成了 {$certCount} 条证书记录\n";
}

// ==================== 5. 生成报价单明细 ====================

echo "\n📑 5. 生成报价单明细...\n";

$count = DB::table('quotation_items')->count();
$quotationIds = DB::table('quotations')->pluck('id')->toArray();
$inventoryItemIds = DB::table('inventory_items')->pluck('id')->toArray();

if ($count == 0 && count($quotationIds) > 0) {
    $itemCount = 0;
    
    foreach ($quotationIds as $quotationId) {
        $numItems = mt_rand(3, 8);
        for ($i = 0; $i < $numItems; $i++) {
            $quantity = mt_rand(1, 50);
            $unitPrice = mt_rand(100, 5000);
            $subtotal = $quantity * $unitPrice;
            
            try {
                DB::table('quotation_items')->insert([
                    'quotation_id' => $quotationId,
                    'inventory_item_id' => count($inventoryItemIds) > 0 ? randomElement($inventoryItemIds) : null,
                    'product_name' => randomElement(['安防摄像头', '门禁系统', '报警器', '监控硬盘', '网线']),
                    'spec' => randomElement(['标准', '高级', '豪华']),
                    'unit' => randomElement(['台', '个', '米', '次']),
                    'quantity' => $quantity,
                    'unit_price' => $unitPrice,
                    'subtotal' => $subtotal,
                    'sort' => $i,
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $itemCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$itemCount} 条报价单明细记录\n";
}

// ==================== 6. 生成项目池数据 ====================

echo "\n📁 6. 生成项目池数据...\n";

$count = DB::table('project_pool')->count();
$opportunityIds = DB::table('opportunities')->pluck('id')->toArray();
$customerIds = DB::table('customers')->pluck('id')->toArray();

if ($count == 0 && count($opportunityIds) > 0) {
    $poolCount = 0;
    
    for ($i = 0; $i < min(20, count($opportunityIds)); $i++) {
        try {
            DB::table('project_pool')->insert([
                'opportunity_id' => $opportunityIds[$i],
                'customer_id' => count($customerIds) > 0 ? $customerIds[array_rand($customerIds)] : null,
                'customer_name' => '潜在客户' . ($i + 1),
                'name' => '潜在项目' . ($i + 1),
                'contract_amount' => mt_rand(50000, 500000),
                'status' => randomElement(['pending', 'in_progress', 'won', 'lost']),
                'expected_start_date' => randomDate('2026-07-01', '2026-12-31'),
                'expected_end_date' => randomDate('2026-12-31', '2027-12-31'),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $poolCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "  ✅ 生成了 {$poolCount} 条项目池记录\n";
}

// ==================== 7. 生成采购需求 ====================

echo "\n📋 7. 生成采购需求...\n";

$count = DB::table('purchase_requirements')->count();
if ($count == 0) {
    $reqCount = 0;
    
    for ($i = 0; $i < 30; $i++) {
        try {
            DB::table('purchase_requirements')->insert([
                'code' => 'PR-' . date('Ymd') . '-' . str_pad($i + 1, 4, '0', STR_PAD_LEFT),
                'project_id' => null,
                'material' => randomElement(['安防摄像头', '门禁控制器', '报警器', '网线', '硬盘', '交换机']),
                'spec' => randomElement(['标准', '高级', '防爆']),
                'quantity' => mt_rand(1, 100),
                'unit' => randomElement(['台', '个', '米', '箱']),
                'need_date' => randomDate($startDate, $endDate),
                'priority' => randomElement(['low', 'medium', 'high', 'urgent']),
                'status' => randomElement(['pending', 'approved', 'rejected', 'completed']),
                'creator' => randomElement($userIds),
                'remark' => '采购需求说明',
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $reqCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "  ✅ 生成了 {$reqCount} 条采购需求记录\n";
}

// ==================== 8. 生成员工技能 ====================

echo "\n🎓 8. 生成员工技能...\n";

$count = DB::table('employee_skills')->count();
$skillTagIds = DB::table('skill_tags')->pluck('id')->toArray();

if ($count == 0 && count($skillTagIds) > 0) {
    $skillCount = 0;
    
    foreach ($employeeProfileIds as $profileId) {
        $numSkills = mt_rand(1, 3);
        $selectedTags = array_rand(array_flip($skillTagIds), min($numSkills, count($skillTagIds)));
        if (!is_array($selectedTags)) $selectedTags = [$selectedTags];
        
        foreach ($selectedTags as $tagId) {
            try {
                DB::table('employee_skills')->insert([
                    'employee_profile_id' => $profileId,
                    'skill_tag_id' => $tagId,
                    'proficiency' => randomElement(['初级', '中级', '高级', '专家']),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $skillCount++;
            } catch (\Exception $e) {
                // 忽略重复
            }
        }
    }
    echo "  ✅ 生成了 {$skillCount} 条员工技能记录\n";
}

// ==================== 9. 生成采购计划 ====================

echo "\n📈 9. 生成采购计划...\n";

$count = DB::table('purchase_plans')->count();
$requirementIds = DB::table('purchase_requirements')->pluck('id')->toArray();

if ($count == 0 && count($requirementIds) > 0) {
    $planCount = 0;
    
    for ($i = 0; $i < 15; $i++) {
        try {
            DB::table('purchase_plans')->insert([
                'code' => 'PP-' . date('Ymd') . '-' . str_pad($i + 1, 4, '0', STR_PAD_LEFT),
                'requirement_id' => $requirementIds[array_rand($requirementIds)],
                'project_id' => null,
                'title' => '采购计划' . ($i + 1),
                'total_amount' => mt_rand(10000, 200000),
                'plan_date' => randomDate($startDate, $endDate),
                'priority' => randomElement(['low', 'medium', 'high']),
                'status' => randomElement(['draft', 'pending', 'approved', 'completed']),
                'submitter_id' => randomElement($userIds),
                'submitted_at' => randomDate($startDate, $endDate),
                'remark' => '采购计划说明',
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $planCount++;
        } catch (\Exception $e) {
            // 忽略错误
        }
    }
    echo "  ✅ 生成了 {$planCount} 条采购计划记录\n";
}

// ==================== 10. 生成销售跟进附件 ====================

echo "\n📎 10. 生成销售跟进附件...\n";

$count = DB::table('sales_follow_up_attachments')->count();
$followUpIds = DB::table('sales_follow_ups')->pluck('id')->toArray();

if ($count == 0 && count($followUpIds) > 0) {
    $attachCount = 0;
    
    foreach ($followUpIds as $followUpId) {
        if (mt_rand(0, 1)) { // 50%概率有附件
            try {
                DB::table('sales_follow_up_attachments')->insert([
                    'follow_up_id' => $followUpId,
                    'filename' => '跟进记录附件' . $followUpId . '.pdf',
                    'original_name' => '附件' . $followUpId . '.pdf',
                    'mime_type' => 'application/pdf',
                    'size' => mt_rand(100000, 5000000),
                    'path' => '/uploads/sales/' . $followUpId . '.pdf',
                    'uploader_id' => randomElement($userIds),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $attachCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$attachCount} 条销售跟进附件记录\n";
}

// ==================== 11. 生成采购发货明细 ====================

echo "\n🚚 11. 生成采购发货明细...\n";

$count = DB::table('purchase_shipment_items')->count();
$shipmentIds = DB::table('purchase_shipments')->pluck('id')->toArray();

if ($count == 0 && count($shipmentIds) > 0) {
    $itemCount = 0;
    
    foreach ($shipmentIds as $shipmentId) {
        $numItems = mt_rand(1, 5);
        for ($i = 0; $i < $numItems; $i++) {
            try {
                DB::table('purchase_shipment_items')->insert([
                    'shipment_id' => $shipmentId,
                    'material' => randomElement(['安防摄像头', '门禁控制器', '报警器', '网线', '硬盘']),
                    'spec' => randomElement(['标准', '高级', '防爆']),
                    'quantity' => mt_rand(1, 50),
                    'unit' => randomElement(['台', '个', '米', '箱']),
                    'remark' => '发货明细说明',
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $itemCount++;
            } catch (\Exception $e) {
                // 忽略错误
            }
        }
    }
    echo "  ✅ 生成了 {$itemCount} 条采购发货明细记录\n";
}

echo "\n✅ 所有缺失数据生成完成！\n";

// ==================== 12. 最终统计 ====================

echo "\n📊 12. 最终数据量统计...\n";
echo str_repeat("=", 60) . "\n";

$allTables = DB::select("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename");
$totalRecords = 0;
$emptyTables = [];

foreach ($allTables as $table) {
    $tableName = $table->tablename;
    $count = DB::table($tableName)->count();
    $totalRecords += $count;
    
    if ($count == 0) {
        $emptyTables[] = $tableName;
    }
    
    if ($count > 0) {
        echo sprintf("  %-35s %6d 条\n", $tableName, $count);
    }
}

echo str_repeat("=", 60) . "\n";
echo "📈 总记录数: {$totalRecords} 条\n";
echo "📋 总表数: " . count($allTables) . " 张\n";

if (count($emptyTables) > 0) {
    echo "\n⚠️  仍然为空的表 (" . count($emptyTables) . " 张):\n";
    foreach ($emptyTables as $table) {
        echo "  - {$table}\n";
    }
} else {
    echo "\n🎉 所有表都有数据了！\n";
}

echo "\n🎉 测试数据生成完成！\n";
echo "⏰ 时间跨度: {$startDate} 至 {$endDate} (至少6个月)\n";
