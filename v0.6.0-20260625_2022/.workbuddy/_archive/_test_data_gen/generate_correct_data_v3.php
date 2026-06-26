<?php
// D:\work\website\OA\.workbuddy\generate_correct_data_v3.php
// 根据实际表结构生成测试数据

echo "🚀 开始为152服务器生成正确的测试数据...\n";
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

function randomTime($start_hour, $end_hour) {
    $hour = rand($start_hour, $end_hour);
    $minute = rand(0, 59);
    $second = rand(0, 59);
    return sprintf('%02d:%02d:%02d', $hour, $minute, $second);
}

// 获取现有数据
echo "📋 获取现有数据...\n";
$users = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM users LIMIT 20"), 0);
$customers = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM customers LIMIT 50"), 0);
$projects = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM projects LIMIT 20"), 0);
$suppliers = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM suppliers LIMIT 50"), 0);
$vehicles = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM vehicles LIMIT 20"), 0);

echo "📊 现有数据: \n";
echo "   - 用户: " . count($users) . " 个\n";
echo "   - 客户: " . count($customers) . " 个\n";
echo "   - 项目: " . count($projects) . " 个\n";
echo "   - 供应商: " . count($suppliers) . " 个\n";
echo "   - 车辆: " . count($vehicles) . " 辆\n\n";

$start_date = '2025-12-01';
$end_date = '2026-06-22';

// 1. 生成员工档案数据
echo "1. 生成员工档案数据...\n";
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
        
        $sql = "INSERT INTO employee_profiles (user_id, employee_no, hire_date, base_salary, salary_allowance, contract_type, created_at, updated_at) VALUES ({$user_id}, '{$employee_no}', '{$hire_date}', {$base_salary}, {$salary_allowance}, 'open', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 员工数据生成完成\n";
} else {
    echo "   ℹ️ 员工数据已足够 ({$emp_count} 条)\n";
}

// 2. 生成考勤记录
echo "\n2. 生成考勤记录...\n";
$att_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM attendance_records"), 0, 0);
if ($att_count < 2000) {
    $need = 2000 - $att_count;
    echo "   📝 需要生成 {$need} 条考勤记录...\n";
    
    $statuses = ['normal', 'late', 'early_leave', 'absent'];
    $employee_profiles = pg_fetch_all_columns(pg_query($db_conn, "SELECT id FROM employee_profiles LIMIT 30"), 0);
    
    foreach ($employee_profiles as $emp_id) {
        if ($att_count >= 2000) break;
        
        // 为每个月生成考勤记录
        $start = new DateTime($start_date);
        $end = new DateTime($end_date);
        $interval = new DateInterval('P1D');
        $date_range = new DatePeriod($start, $interval, $end);
        
        foreach ($date_range as $date) {
            if ($att_count >= 2000) break;
            
            $date_str = $date->format('Y-m-d');
            $clock_in = randomTime(7, 9);
            $clock_out = randomTime(17, 19);
            $status = $statuses[array_rand($statuses)];
            $work_hours = rand(7, 9) + (rand(0, 9) / 10);
            $overtime_hours = rand(0, 3) + (rand(0, 9) / 10);
            $created_at = $date_str . ' ' . $clock_in;
            
            $sql = "INSERT INTO attendance_records (user_id, date, clock_in, clock_out, status, work_hours, overtime_hours, created_at, updated_at) SELECT u.id, '{$date_str}', '{$clock_in}', '{$clock_out}', '{$status}', {$work_hours}, {$overtime_hours}, '{$created_at}', NOW() FROM users u JOIN employee_profiles ep ON u.id = ep.user_id WHERE ep.id = {$emp_id} LIMIT 1";
            
            if (@pg_query($db_conn, $sql)) {
                $att_count++;
            }
        }
    }
    echo "   ✅ 考勤数据生成完成 (时间跨度: {$start_date} 至 {$end_date})\n";
} else {
    echo "   ℹ️ 考勤数据已足够 ({$att_count} 条)\n";
}

// 3. 生成报销数据
echo "\n3. 生成报销数据...\n";
$exp_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM expense_claims"), 0, 0);
if ($exp_count < 500) {
    $need = 500 - $exp_count;
    echo "   📝 需要生成 {$need} 条报销记录...\n";
    
    $categories = ['差旅费', '交通费', '住宿费', '餐饮费', '办公用品', '培训费', '其他'];
    $statuses = ['draft', 'submitted', 'approved', 'rejected', 'reimbursed'];
    
    for ($i = 0; $i < $need; $i++) {
        $user_id = $users[array_rand($users)];
        $claim_no = 'EXP' . date('Ymd') . str_pad($exp_count + $i + 1, 4, '0', STR_PAD_LEFT);
        $category = $categories[array_rand($categories)];
        $total_amount = rand(100, 5000) + (rand(0, 99) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO expense_claims (claim_no, user_id, category, total_amount, description, status, created_at, updated_at) VALUES ('{$claim_no}', {$user_id}, '{$category}', {$total_amount}, '报销描述', '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 报销数据生成完成 (时间跨度: {$start_date} 至 {$end_date})\n";
} else {
    echo "   ℹ️ 报销数据已足够 ({$exp_count} 条)\n";
}

// 4. 生成服务工单数据
echo "\n4. 生成服务工单数据...\n";
$svc_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM service_orders"), 0, 0);
if ($svc_count < 100) {
    $need = 100 - $svc_count;
    echo "   📝 需要生成 {$need} 条服务工单...\n";
    
    $types = ['repair', 'maintenance', 'installation', 'consultation', 'emergency'];
    $priorities = ['low', 'medium', 'high', 'urgent'];
    $statuses = ['open', 'in_progress', 'resolved', 'closed'];
    
    for ($i = 0; $i < $need; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $project_id = $projects ? $projects[array_rand($projects)] : 'NULL';
        $type = $types[array_rand($types)];
        $title = '服务工单 #' . ($svc_count + $i + 1);
        $priority = $priorities[array_rand($priorities)];
        $status = $statuses[array_rand($statuses)];
        $assigned_to = $users[array_rand($users)];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO service_orders (customer_id, project_id, type, title, priority, status, assigned_to, created_by, created_at, updated_at) VALUES ({$customer_id}, {$project_id}, '{$type}', '{$title}', '{$priority}', '{$status}', {$assigned_to}, {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 服务工单数据生成完成\n";
} else {
    echo "   ℹ️ 服务工单数据已足够 ({$svc_count} 条)\n";
}

// 5. 生成销售机会数据
echo "\n5. 生成销售机会数据...\n";
$opp_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM opportunities"), 0, 0);
if ($opp_count < 100) {
    $need = 100 - $opp_count;
    echo "   📝 需要生成 {$need} 条销售机会...\n";
    
    $statuses = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
    
    for ($i = 0; $i < $need; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $title = '销售机会 #' . ($opp_count + $i + 1);
        $estimated_value = rand(5000, 200000) + (rand(0, 99) / 100);
        $probability = rand(10, 90);
        $status = $statuses[array_rand($statuses)];
        $expected_close_date = randomDate($start_date, $end_date);
        $assigned_to = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO opportunities (customer_id, title, estimated_value, probability, status, expected_close_date, assigned_to, created_at, updated_at) VALUES ({$customer_id}, '{$title}', {$estimated_value}, {$probability}, '{$status}', '{$expected_close_date}', {$assigned_to}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 销售机会数据生成完成\n";
} else {
    echo "   ℹ️ 销售机会数据已足够 ({$opp_count} 条)\n";
}

// 6. 生成采购订单数据
echo "\n6. 生成采购订单数据...\n";
$pur_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM purchase_orders"), 0, 0);
if ($pur_count < 50) {
    $need = 50 - $pur_count;
    echo "   📝 需要生成 {$need} 条采购订单...\n";
    
    $statuses = ['draft', 'pending', 'approved', 'received', 'cancelled'];
    
    for ($i = 0; $i < $need; $i++) {
        $supplier_id = $suppliers[array_rand($suppliers)];
        $po_no = 'PO-' . date('Ymd') . '-' . str_pad($pur_count + $i + 1, 4, '0', STR_PAD_LEFT);
        $total_amount = rand(1000, 50000) + (rand(0, 99) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO purchase_orders (supplier_id, po_no, total_amount, status, created_at, updated_at) VALUES ({$supplier_id}, '{$po_no}', {$total_amount}, '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 采购订单数据生成完成\n";
} else {
    echo "   ℹ️ 采购订单数据已足够 ({$pur_count} 条)\n";
}

// 7. 生成车辆数据
echo "\n7. 生成车辆数据...\n";
$veh_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM vehicles"), 0, 0);
if ($veh_count < 20) {
    $need = 20 - $veh_count;
    echo "   📝 需要生成 {$need} 辆车...\n";
    
    $brands = ['丰田', '本田', '大众', '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '蔚来', '小鹏'];
    $fuel_types = ['汽油', '柴油', '电动', '混合'];
    $statuses = ['available', 'in_use', 'maintenance', 'retired'];
    
    for ($i = 0; $i < $need; $i++) {
        $plate_no = '粤B' . str_pad(rand(10000, 99999), 5, '0', STR_PAD_LEFT);
        $brand = $brands[array_rand($brands)];
        $model = 'Model-' . chr(rand(65, 90)) . rand(1, 9);
        $color = ['黑色', '白色', '灰色', '蓝色', '红色'][array_rand(['黑色', '白色', '灰色', '蓝色', '红色'])];
        $fuel_type = $fuel_types[array_rand($fuel_types)];
        $status = $statuses[array_rand($statuses)];
        $purchase_date = randomDate($start_date, $end_date);
        $purchase_price = rand(100000, 500000) + (rand(0, 99) / 100);
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO vehicles (plate_no, brand, model, color, purchase_date, purchase_price, fuel_type, status, created_at, updated_at) VALUES ('{$plate_no}', '{$brand}', '{$model}', '{$color}', '{$purchase_date}', {$purchase_price}, '{$fuel_type}', '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 车辆数据生成完成\n";
} else {
    echo "   ℹ️ 车辆数据已足够 ({$veh_count} 条)\n";
}

// 8. 生成库存物品数据
echo "\n8. 生成库存物品数据...\n";
$inv_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM inventory_items"), 0, 0);
if ($inv_count < 100) {
    $need = 100 - $inv_count;
    echo "   📝 需要生成 {$need} 个库存物品...\n";
    
    $names = ['笔记本电脑', '台式电脑', '显示器', '键盘', '鼠标', '打印机', '路由器', '交换机', '网线', '硬盘', '内存条', 'CPU', '主板', '显卡', '电源'];
    $units = ['台', '个', '件', '套', '箱'];
    $statuses = ['in_stock', 'out_of_stock', 'reserved'];
    
    for ($i = 0; $i < $need; $i++) {
        $name = $names[array_rand($names)] . ' ' . chr(rand(65, 90)) . rand(1, 99);
        $code = 'INV' . str_pad($inv_count + $i + 1, 6, '0', STR_PAD_LEFT);
        $category = ['电子产品', '办公设备', '网络器材', '电脑配件'][array_rand(['电子产品', '办公设备', '网络器材', '电脑配件'])];
        $current_stock = rand(1, 100);
        $unit = $units[array_rand($units)];
        $cost_price = rand(100, 5000) + (rand(0, 99) / 100);
        $sell_price = $cost_price * (1 + rand(10, 30) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO inventory_items (name, code, category, current_stock, unit, cost_price, sell_price, status, created_at, updated_at) VALUES ('{$name}', '{$code}', '{$category}', {$current_stock}, '{$unit}', {$cost_price}, {$sell_price}, '{$status}', '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 库存物品数据生成完成\n";
} else {
    echo "   ℹ️ 库存物品数据已足够 ({$inv_count} 条)\n";
}

// 9. 生成网盘文件夹数据
echo "\n9. 生成网盘文件夹数据...\n";
$folder_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM disk_folders"), 0, 0);
if ($folder_count < 50) {
    $need = 50 - $folder_count;
    echo "   📝 需要生成 {$need} 个网盘文件夹...\n";
    
    for ($i = 0; $i < $need; $i++) {
        $name = '文件夹 ' . ($folder_count + $i + 1);
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO disk_folders (name, created_by, created_at, updated_at) VALUES ('{$name}', {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 网盘文件夹数据生成完成\n";
} else {
    echo "   ℹ️ 网盘文件夹数据已足够 ({$folder_count} 条)\n";
}

// 10. 生成知识库文章数据
echo "\n10. 生成知识库文章数据...\n";
$article_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM knowledge_articles"), 0, 0);
if ($article_count < 50) {
    $need = 50 - $article_count;
    echo "   📝 需要生成 {$need} 篇知识库文章...\n";
    
    $titles = ['技术文档', '操作手册', '常见问题', '最佳实践', '培训材料', '产品说明', 'API文档', '设计规范', '测试用例', '项目总结'];
    $statuses = ['draft', 'published', 'archived'];
    
    for ($i = 0; $i < $need; $i++) {
        $title = $titles[array_rand($titles)] . ' ' . ($article_count + $i + 1);
        $content = '这是知识库文章的详细内容。可以使用Markdown格式编写。';
        $status = $statuses[array_rand($statuses)];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO knowledge_articles (title, content, status, created_by, created_at, updated_at) VALUES ('{$title}', '{$content}', '{$status}', {$created_by}, '{$created_at}', NOW())";
        @pg_query($db_conn, $sql);
    }
    echo "   ✅ 知识库文章数据生成完成\n";
} else {
    echo "   ℹ️ 知识库文章数据已足够 ({$article_count} 条)\n";
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