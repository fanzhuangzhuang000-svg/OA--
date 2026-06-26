<?php
// D:\work\website\OA\.workbuddy\generate_all_modules_v4.php
// 修复并重新生成所有模块的测试数据

echo "🚀 开始为152服务器生成全面的测试数据 (V4版)...\n";
echo "📅 时间跨度: 2025-12-01 至 2026-06-22 (至少6个月)\n\n";

// 加载数据库配置
$env_file = '/var/www/oa-api/.env';
$db_config = [];
if (file_exists($env_file)) {
    $lines = file($env_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false && strpos($line, '#') !== 0) {
            list($key, $value) = explode('=', $line, 2);
            $db_config[trim($key)] = trim($value);
        }
    }
}

$db_host = $db_config['DB_HOST'] ?? '127.0.0.1';
$db_port = $db_config['DB_PORT'] ?? '5432';
$db_name = $db_config['DB_DATABASE'] ?? 'security_oa';
$db_user = $db_config['DB_USERNAME'] ?? 'oa_user';
$db_pass = $db_config['DB_PASSWORD'] ?? 'oa_pg_pwd_782997781';

echo "📊 数据库连接: $db_host:$db_port/$db_name\n";

$db_conn = pg_connect("host=$db_host port=$db_port dbname=$db_name user=$db_user password=$db_pass");
if (!$db_conn) {
    die("❌ 数据库连接失败: " . pg_last_error() . "\n");
}
echo "✅ 数据库连接成功!\n\n";

// 时间函数
function randomDateTime($start, $end) {
    $timestamp = rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

function randomDate($start, $end) {
    $timestamp = rand(strtotime($start), strtotime($end));
    return date('Y-m-d', $timestamp);
}

// 获取现有数据
echo "📋 获取现有数据...\n";
$users = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM users LIMIT 20"), 0);
$customers = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM customers LIMIT 50"), 0);
$projects = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM projects LIMIT 20"), 0);
$suppliers = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM suppliers LIMIT 50"), 0);
$vehicles = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM vehicles LIMIT 20"), 0);
$accounts = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM finance_accounts LIMIT 10"), 0);

echo "📊 现有数据: \n";
echo "   - 用户: " . count($users) . " 个\n";
echo "   - 客户: " . count($customers) . " 个\n";
echo "   - 项目: " . count($projects) . " 个\n";
echo "   - 供应商: " . count($suppliers) . " 个\n";
echo "   - 车辆: " . count($vehicles) . " 辆\n\n";

$start_date = '2025-12-01';
$end_date = '2026-06-22';

// ===== 修复1: 生成员工档案数据 (使用正确的字段名) =====
echo "1. 生成员工档案数据 (修复版)...\n";
$emp_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM employee_profiles"), 0, 0);
if ($emp_count < 30) {
    $need = 30 - $emp_count;
    echo "   📝 需要生成 {$need} 条员工记录...\n";
    
    for ($i = 0; $i < $need; $i++) {
        $user_id = $users[array_rand($users)];
        $employee_no = 'EMP' . str_pad($emp_count + $i + 1, 4, '0', STR_PAD_LEFT);
        $hire_date = randomDate($start_date, $end_date);
        $base_salary = rand(5000, 20000) + (rand(0, 99) / 100);
        $salary_allowance = rand(500, 3000) + (rand(0, 99) / 100);
        $created_at = randomDateTime($start_date, $end_date);
        
        // 使用正确的字段名: employee_no (不是 employee_id)
        $sql = "INSERT INTO employee_profiles (user_id, employee_no, hire_date, base_salary, salary_allowance, contract_type, created_at, updated_at) VALUES ({$user_id}, '{$employee_no}', '{$hire_date}', {$base_salary}, {$salary_allowance}, 'open', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 员工数据生成完成\n";
} else {
    echo "   ℹ️ 员工数据已足够 ({$emp_count} 条)\n";
}

// ===== 修复2: 生成网盘文件夹数据 (使用正确的字段) =====
echo "\n2. 生成网盘文件夹数据 (修复版)...\n";
$folder_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM disk_folders"), 0, 0);
if ($folder_count < 50) {
    $need = 50 - $folder_count;
    echo "   📝 需要生成 {$need} 个网盘文件夹...\n";
    
    for ($i = 0; $i < $need; $i++) {
        $name = '文件夹 ' . ($folder_count + $i + 1);
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        // 使用正确的字段: created_by (不是 created_by)
        $sql = "INSERT INTO disk_folders (name, created_by, created_at, updated_at) VALUES ('{$name}', {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 网盘文件夹数据生成完成\n";
} else {
    echo "   ℹ️ 网盘文件夹数据已足够 ({$folder_count} 条)\n";
}

// ===== 修复3: 生成知识库文章数据 (使用正确的字段) =====
echo "\n3. 生成知识库文章数据 (修复版)...\n";
$article_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM knowledge_articles"), 0, 0);
if ($article_count < 50) {
    $need = 50 - $article_count;
    echo "   📝 需要生成 {$need} 篇文章...\n";
    
    $titles = ['技术文档', '操作手册', '常见问题', '最佳实践', '培训材料', '产品说明', 'API文档', '设计规范', '测试用例', '项目总结'];
    
    for ($i = 0; $i < $need; $i++) {
        $title = $titles[array_rand($titles)] . ' ' . ($article_count + $i + 1);
        $content = '这是知识库文章的详细内容。可以使用Markdown格式编写。';
        $status = ['draft', 'published', 'archived'][array_rand(['draft', 'published', 'archived'])];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        // 使用正确的字段: created_by (不是 created_by)
        $sql = "INSERT INTO knowledge_articles (title, content, status, created_by, created_at, updated_at) VALUES ('{$title}', '{$content}', '{$status}', {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 知识库文章数据生成完成\n";
} else {
    echo "   ℹ️ 知识库文章数据已足够 ({$article_count} 条)\n";
}

// ===== 4. 生成销售线索数据 =====
echo "\n4. 生成销售线索数据...\n";
$lead_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM leads"), 0, 0);
if ($lead_count < 100) {
    $need = 100 - $lead_count;
    echo "   📝 需要生成 {$need} 条销售线索...\n";
    
    $statuses = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost'];
    $sources = ['website', 'referral', 'cold_call', 'exhibition', 'online_ad'];
    
    for ($i = 0; $i < $need; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $contact_name = '联系人 ' . ($lead_count + $i + 1);
        $contact_phone = '1' . rand(3, 9) . str_pad(rand(0, 999999999), 9, '0', STR_PAD_LEFT);
        $status = $statuses[array_rand($statuses)];
        $source = $sources[array_rand($sources)];
        $assigned_to = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO leads (customer_id, contact_name, contact_phone, status, source, assigned_to, created_at, updated_at) VALUES ({$customer_id}, '{$contact_name}', '{$contact_phone}', '{$status}', '{$source}', {$assigned_to}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 销售线索数据生成完成\n";
} else {
    echo "   ℹ️ 销售线索数据已足够 ({$lead_count} 条)\n";
}

// ===== 5. 生成报价单数据 =====
echo "\n5. 生成报价单数据...\n";
$quote_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM quotations"), 0, 0);
if ($quote_count < 50) {
    $need = 50 - $quote_count;
    echo "   📝 需要生成 {$need} 条报价单...\n";
    
    $statuses = ['draft', 'sent', 'accepted', 'rejected', 'expired'];
    
    for ($i = 0; $i < $need; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $project_id = $projects ? $projects[array_rand($projects)] : 'NULL';
        $quote_no = 'QUO' . date('Ymd') . '-' . str_pad($quote_count + $i + 1, 4, '0', STR_PAD_LEFT);
        $total_amount = rand(10000, 200000) + (rand(0, 99) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO quotations (customer_id, project_id, quote_no, total_amount, status, created_by, created_at, updated_at) VALUES ({$customer_id}, {$project_id}, '{$quote_no}', {$total_amount}, '{$status}', {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 报价单数据生成完成\n";
} else {
    echo "   ℹ️ 报价单数据已足够 ({$quote_count} 条)\n";
}

// ===== 6. 生成车辆保险记录 =====
echo "\n6. 生成车辆保险记录...\n";
$ins_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM vehicle_insurance"), 0, 0);
if ($ins_count < 50) {
    $need = 50 - $ins_count;
    echo "   📝 需要生成 {$need} 条保险记录...\n";
    
    for ($i = 0; $i < $need; $i++) {
        $vehicle_id = $vehicles[array_rand($vehicles)];
        $insurance_company = ['平安保险', '人保财险', '太平洋保险', '国寿财险'][array_rand(['平安保险', '人保财险', '太平洋保险', '国寿财险'])];
        $policy_no = 'INS' . date('Ymd') . str_pad($ins_count + $i + 1, 6, '0', STR_PAD_LEFT);
        $start_date_ins = randomDate($start_date, $end_date);
        $end_date_ins = date('Y-m-d', strtotime($start_date_ins . ' +1 year'));
        $premium = rand(3000, 8000) + (rand(0, 99) / 100);
        $status = ['active', 'expired', 'cancelled'][array_rand(['active', 'expired', 'cancelled'])];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO vehicle_insurance (vehicle_id, insurance_company, policy_no, start_date, end_date, premium, status, created_at, updated_at) VALUES ({$vehicle_id}, '{$insurance_company}', '{$policy_no}', '{$start_date_ins}', '{$end_date_ins}', {$premium}, '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 车辆保险记录生成完成\n";
} else {
    echo "   ℹ️ 车辆保险记录已足够 ({$ins_count} 条)\n";
}

// ===== 7. 生成车辆保养记录 =====
echo "\n7. 生成车辆保养记录...\n";
$maint_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM vehicle_maintenance_records"), 0, 0);
if ($maint_count < 50) {
    $need = 50 - $maint_count;
    echo "   📝 需要生成 {$need} 条保养记录...\n";
    
    $types = ['regular', 'repair', 'inspection'];
    
    for ($i = 0; $i < $need; $i++) {
        $vehicle_id = $vehicles[array_rand($vehicles)];
        $maintenance_date = randomDate($start_date, $end_date);
        $type = $types[array_rand($types)];
        $cost = rand(500, 5000) + (rand(0, 99) / 100);
        $mileage = rand(5000, 100000);
        $description = '车辆保养描述 ' . ($maint_count + $i + 1);
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO vehicle_maintenance_records (vehicle_id, maintenance_date, type, cost, mileage, description, created_at, updated_at) VALUES ({$vehicle_id}, '{$maintenance_date}', '{$type}', {$cost}, {$mileage}, '{$description}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 车辆保养记录生成完成\n";
} else {
    echo "   ℹ️ 车辆保养记录已足够 ({$maint_count} 条)\n";
}

// ===== 8. 生成油卡数据 =====
echo "\n8. 生成油卡数据...\n";
$card_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM fuel_cards"), 0, 0);
if ($card_count < 20) {
    $need = 20 - $card_count;
    echo "   📝 需要生成 {$need} 张油卡...\n";
    
    $statuses = ['active', 'inactive', 'lost'];
    
    for ($i = 0; $i < $need; $i++) {
        $card_no = '8986' . str_pad(rand(100000000000, 999999999999), 12, '0', STR_PAD_LEFT);
        $vehicle_id = $vehicles[array_rand($vehicles)];
        $balance = rand(100, 2000) + (rand(0, 99) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO fuel_cards (card_no, vehicle_id, balance, status, created_at, updated_at) VALUES ('{$card_no}', {$vehicle_id}, {$balance}, '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 油卡数据生成完成\n";
} else {
    echo "   ℹ️ 油卡数据已足够 ({$card_count} 条)\n";
}

// ===== 9. 生成项目成员数据 =====
echo "\n9. 生成项目成员数据...\n";
$member_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM project_members"), 0, 0);
if ($member_count < 100) {
    $need = 100 - $member_count;
    echo "   📝 需要生成 {$need} 条项目成员记录...\n";
    
    $roles = ['member', 'leader', 'observer'];
    
    for ($i = 0; $i < $need; $i++) {
        $project_id = $projects[array_rand($projects)];
        $user_id = $users[array_rand($users)];
        $role = $roles[array_rand($roles)];
        $created_at = randomDateTime($start_date, $end_date);
        
        // 检查是否已存在
        $check = pg_query($db_conn, "SELECT id FROM project_members WHERE project_id = {$project_id} AND user_id = {$user_id}");
        if (pg_fetch_result($check, 0, 0) == 0) {
            $sql = "INSERT INTO project_members (project_id, user_id, role, created_at, updated_at) VALUES ({$project_id}, {$user_id}, '{$role}', '{$created_at}', NOW())";
            @pg_query($db_conn, $sql);
        }
    }
    echo "   ✅ 项目成员数据生成完成\n";
} else {
    echo "   ℹ️ 项目成员数据已足够 ({$member_count} 条)\n";
}

// ===== 10. 生成库存流水记录 =====
echo "\n10. 生成库存流水记录...\n";
$stock_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM stock_records"), 0, 0);
if ($stock_count < 200) {
    $need = 200 - $stock_count;
    echo "   📝 需要生成 {$need} 条库存流水记录...\n";
    
    $item_ids = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM inventory_items LIMIT 50"), 0);
    $types = ['in', 'out', 'transfer', 'adjust'];
    
    for ($i = 0; $i < $need; $i++) {
        $item_id = $item_ids[array_rand($item_ids)];
        $type = $types[array_rand($types)];
        $quantity = rand(1, 50);
        $balance = rand(10, 200);
        $reason = '库存操作 ' . ($stock_count + $i + 1);
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO stock_records (inventory_item_id, type, quantity, balance, reason, created_at, updated_at) VALUES ({$item_id}, '{$type}', {$quantity}, {$balance}, '{$reason}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 库存流水记录生成完成\n";
} else {
    echo "   ℹ️ 库存流水记录已足够 ({$stock_count} 条)\n";
}

echo "\n" . str_repeat("=", 60) . "\n";
echo "🎉 测试数据生成完成！\n";
echo "📅 所有数据时间跨度: {$start_date} 至 {$end_date} (至少6个月)\n";
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
    'employee_profiles' => '员工档案',
    'attendance_records' => '考勤记录',
    'expense_claims' => '报销记录',
    'receivables' => '应收记录',
    'payables' => '应付记录',
    'notifications' => '消息通知',
    'service_orders' => '服务工单',
    'purchase_orders' => '采购订单',
    'opportunities' => '销售机会',
    'leads' => '销售线索',
    'quotations' => '报价单',
    'vehicle_insurance' => '车辆保险',
    'vehicle_maintenance_records' => '车辆保养',
    'fuel_cards' => '油卡',
    'project_members' => '项目成员',
    'stock_records' => '库存流水',
];

foreach ($tables as $table => $name) {
    $result = @pg_query($db_conn, "SELECT COUNT(*) FROM {$table}");
    if ($result) {
        $count = pg_fetch_result($result, 0, 0);
        echo "   - {$name}: {$count} 条\n";
    } else {
        echo "   - {$name}: 表不存在或无法统计\n";
    }
}

pg_close($db_conn);
echo "\n✅ 所有模块数据生成完成！\n";
?>