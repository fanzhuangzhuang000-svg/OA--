# D:\work\website\OA\.workbuddy\upload_and_run_quick_data.py
# 上传并运行快速测试数据生成脚本到152服务器

import paramiko
import time
import os

# 服务器配置
host = '152.136.115.121'
username = 'ubuntu'
password = 'Aa782997781.'
remote_path = '/tmp/quick_generate_data.php'
local_path = r'D:\work\website\OA\.workbuddy\quick_generate_data.php'

def upload_and_run():
    try:
        print("🔌 正在连接152服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        print("✅ SSH连接成功!")
        
        # 1. 上传PHP脚本
        print(f"📁 上传脚本到 {remote_path}...")
        sftp = ssh.open_sftp()
        
        # 确保目录存在
        try:
            sftp.mkdir('/tmp')
        except:
            pass
        
        sftp.put(local_path, remote_path)
        sftp.close()
        print("✅ 上传完成!")
        
        # 2. 在服务器上创建完整的PHP脚本（包含数据库连接）
        print("📝 在服务器上创建完整的PHP脚本...")
        
        # 先获取数据库配置
        stdin, stdout, stderr = ssh.exec_command("cd /var/www/oa-api && grep DB_ .env | head -10")
        db_config = stdout.read().decode('utf-8')
        print(f"📄 数据库配置:\n{db_config}")
        
        # 创建完整的PHP脚本
        php_script = """<?php
echo "🚀 开始生成测试数据...\n";

// 从Laravel .env文件加载数据库配置
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

// 数据库连接配置
$db_host = $db_config['DB_HOST'] ?? '127.0.0.1';
$db_port = $db_config['DB_PORT'] ?? '5432';
$db_name = $db_config['DB_DATABASE'] ?? 'oa_db';
$db_user = $db_config['DB_USERNAME'] ?? 'oa_user';
$db_pass = $db_config['DB_PASSWORD'] ?? 'oa_pass';

echo "📊 数据库连接: $db_host:$db_port/$db_name\n";

// 连接PostgreSQL数据库
$db_conn = pg_connect("host=$db_host port=$db_port dbname=$db_name user=$db_user password=$db_pass");
if (!$db_conn) {
    die("❌ 数据库连接失败: " . pg_last_error() . "\n");
}
echo "✅ 数据库连接成功!\n\n";

// 设置时间跨度
$start_date = '2025-12-01';
$end_date = '2026-06-22';

// 生成随机日期时间的函数
function randomDateTime($start, $end) {
    $timestamp = rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

function randomDate($start, $end) {
    $timestamp = rand(strtotime($start), strtotime($end));
    return date('Y-m-d', $timestamp);
}

// 获取现有数据ID用于关联
echo "📋 获取现有数据...\n";
$users_result = pg_query($db_conn, "SELECT id FROM users LIMIT 20");
$users = pg_fetch_all_columns($users_result, 0);

$customers_result = pg_query($db_conn, "SELECT id FROM customers LIMIT 50");
$customers = pg_fetch_all_columns($customers_result, 0);

$projects_result = pg_query($db_conn, "SELECT id FROM projects LIMIT 20");
$projects = pg_fetch_all_columns($projects_result, 0);

$suppliers_result = pg_query($db_conn, "SELECT id FROM suppliers LIMIT 50");
$suppliers = pg_fetch_all_columns($suppliers_result, 0);

echo "📊 现有数据: \n";
echo "   - 用户: " . count($users) . " 个\n";
echo "   - 客户: " . count($customers) . " 个\n";
echo "   - 项目: " . count($projects) . " 个\n";
echo "   - 供应商: " . count($suppliers) . " 个\n\n";

// 1. 生成更多员工数据
echo "1. 生成更多员工数据...\n";
$employee_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM employee_profiles"), 0, 0);
if ($employee_count < 30) {
    $need_count = 30 - $employee_count;
    echo "   📝 需要生成 {$need_count} 条员工记录...\n";
    
    $positions = ['软件工程师', '项目经理', '销售代表', '财务分析师', '人事专员', '运维工程师', '测试工程师', '产品经理', 'UI设计师', '网络工程师'];
    $departments = ['技术部', '销售部', '财务部', '人事部', '运维部', '产品部'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $user_id = $users[array_rand($users)];
        $position = $positions[array_rand($positions)];
        $department = $departments[array_rand($departments)];
        $hire_date = randomDate($start_date, $end_date);
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO employee_profiles (user_id, employee_id, position, department, phone, hire_date, status, created_at, updated_at) VALUES ({$user_id}, 'EMP" . str_pad($employee_count + $i + 1, 4, '0', STR_PAD_LEFT) . "', '{$position}', '{$department}', '1" . rand(3, 9) . str_pad(rand(0, 999999999), 9, '0', STR_PAD_LEFT) . "', '{$hire_date}', 'active', '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 员工数据生成完成\n";
} else {
    echo "   ℹ️ 员工数据已足够了 ({$employee_count} 条)\n";
}

// 2. 生成更多服务工单数据
echo "\\n2. 生成更多服务工单数据...\\n";
$service_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM service_tickets"), 0, 0);
if ($service_count < 100) {
    $need_count = 100 - $service_count;
    echo "   📝 需要生成 {$need_count} 条服务工单...\\n";
    
    $ticket_types = ['repair', 'maintenance', 'installation', 'consultation', 'emergency'];
    $priorities = ['low', 'medium', 'high', 'urgent'];
    $statuses = ['open', 'in_progress', 'resolved', 'closed'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $project_id = $projects ? $projects[array_rand($projects)] : 'NULL';
        $type = $ticket_types[array_rand($ticket_types)];
        $title = "服务工单 #" . ($service_count + $i + 1);
        $description = "这是服务工单的详细描述，用于测试系统功能。";
        $priority = $priorities[array_rand($priorities)];
        $status = $statuses[array_rand($statuses)];
        $assigned_to = $users[array_rand($users)];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO service_tickets (customer_id, project_id, type, title, description, priority, status, assigned_to, created_by, created_at, updated_at) VALUES ({$customer_id}, {$project_id}, '{$type}', '{$title}', '{$description}', '{$priority}', '{$status}', {$assigned_to}, {$created_by}, '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 服务工单数据生成完成\\n";
} else {
    echo "   ℹ️ 服务工单数据已足够了 ({$service_count} 条)\\n";
}

// 3. 生成更多采购订单数据
echo "\\n3. 生成更多采购订单数据...\\n";
$purchase_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM purchase_orders"), 0, 0);
if ($purchase_count < 50) {
    $need_count = 50 - $purchase_count;
    echo "   📝 需要生成 {$need_count} 条采购订单...\\n";
    
    $statuses = ['draft', 'pending', 'approved', 'received', 'cancelled'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $supplier_id = $suppliers[array_rand($suppliers)];
        $order_number = "PO-" . date('Ymd') . "-" . str_pad($purchase_count + $i + 1, 4, '0', STR_PAD_LEFT);
        $order_date = randomDate($start_date, $end_date);
        $total_amount = rand(1000, 50000) + (rand(0, 99) / 100);
        $status = $statuses[array_rand($statuses)];
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO purchase_orders (supplier_id, order_number, order_date, total_amount, status, created_by, created_at, updated_at) VALUES ({$supplier_id}, '{$order_number}', '{$order_date}', {$total_amount}, '{$status}', {$created_by}, '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 采购订单数据生成完成\\n";
} else {
    echo "   ℹ️ 采购订单数据已足够了 ({$purchase_count} 条)\\n";
}

// 4. 生成更多销售机会数据
echo "\\n4. 生成更多销售机会数据...\\n";
$opportunity_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM sales_opportunities"), 0, 0);
if ($opportunity_count < 100) {
    $need_count = 100 - $opportunity_count;
    echo "   📝 需要生成 {$need_count} 条销售机会...\\n";
    
    $statuses = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $customer_id = $customers[array_rand($customers)];
        $title = "销售机会 #" . ($opportunity_count + $i + 1);
        $description = "这是销售机会的详细描述。";
        $estimated_value = rand(5000, 200000) + (rand(0, 99) / 100);
        $probability = rand(10, 90);
        $status = $statuses[array_rand($statuses)];
        $expected_close_date = randomDate($start_date, $end_date);
        $assigned_to = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO sales_opportunities (customer_id, title, description, estimated_value, probability, status, expected_close_date, assigned_to, created_at, updated_at) VALUES ({$customer_id}, '{$title}', '{$description}', {$estimated_value}, {$probability}, '{$status}', '{$expected_close_date}', {$assigned_to}, '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 销售机会数据生成完成\\n";
} else {
    echo "   ℹ️ 销售机会数据已足够了 ({$opportunity_count} 条)\\n";
}

// 5. 生成更多车辆数据
echo "\\n5. 生成更多车辆数据...\\n";
$vehicle_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM vehicles"), 0, 0);
if ($vehicle_count < 20) {
    $need_count = 20 - $vehicle_count;
    echo "   📝 需要生成 {$need_count} 辆车...\\n";
    
    $brands = ['丰田', '本田', '大众', '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '蔚来', '小鹏'];
    $types = ['sedan', 'suv', 'truck', 'van', 'electric'];
    $statuses = ['available', 'in_use', 'maintenance', 'retired'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $plate_number = "粤B" . str_pad(rand(10000, 99999), 5, '0', STR_PAD_LEFT);
        $brand = $brands[array_rand($brands)];
        $model = "Model-" . chr(rand(65, 90)) . rand(1, 9);
        $type = $types[array_rand($types)];
        $year = rand(2018, 2025);
        $color = ['黑色', '白色', '灰色', '蓝色', '红色'][array_rand(['黑色', '白色', '灰色', '蓝色', '红色'])];
        $status = $statuses[array_rand($statuses)];
        $purchase_date = randomDate($start_date, $end_date);
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO vehicles (plate_number, brand, model, type, year, color, status, purchase_date, created_at, updated_at) VALUES ('{$plate_number}', '{$brand}', '{$model}', '{$type}', {$year}, '{$color}', '{$status}', '{$purchase_date}', '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 车辆数据生成完成\\n";
} else {
    echo "   ℹ️ 车辆数据已足够了 ({$vehicle_count} 条)\\n";
}

// 6. 生成更多库存物品数据
echo "\\n6. 生成更多库存物品数据...\\n";
$item_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM inventory_items"), 0, 0);
if ($item_count < 100) {
    $need_count = 100 - $item_count;
    echo "   📝 需要生成 {$need_count} 个库存物品...\\n";
    
    $categories_result = pg_query($db_conn, "SELECT id FROM inventory_categories LIMIT 10");
    $categories = pg_fetch_all_columns($categories_result, 0);
    
    $warehouses_result = pg_query($db_conn, "SELECT id FROM warehouses LIMIT 10");
    $warehouses = pg_fetch_all_columns($warehouses_result, 0);
    
    $names = ['笔记本电脑', '台式电脑', '显示器', '键盘', '鼠标', '打印机', '路由器', '交换机', '网线', '硬盘', '内存条', 'CPU', '主板', '显卡', '电源'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $name = $names[array_rand($names)] . ' ' . chr(rand(65, 90)) . rand(1, 99);
        $category_id = $categories ? $categories[array_rand($categories)] : 'NULL';
        $warehouse_id = $warehouses ? $warehouses[array_rand($warehouses)] : 'NULL';
        $quantity = rand(1, 100);
        $unit = ['台', '个', '件', '套', '箱'][array_rand(['台', '个', '件', '套', '箱'])];
        $unit_price = rand(100, 5000) + (rand(0, 99) / 100);
        $status = ['in_stock', 'out_of_stock', 'reserved'][array_rand(['in_stock', 'out_of_stock', 'reserved'])];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO inventory_items (name, category_id, warehouse_id, quantity, unit, unit_price, status, created_at, updated_at) VALUES ('{$name}', {$category_id}, {$warehouse_id}, {$quantity}, '{$unit}', {$unit_price}, '{$status}', '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 库存物品数据生成完成\\n";
} else {
    echo "   ℹ️ 库存物品数据已够了 ({$item_count} 条)\\n";
}

// 7. 生成更多网盘文件夹数据
echo "\\n7. 生成更多网盘数据...\\n";
$folder_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM disk_folders"), 0, 0);
if ($folder_count < 50) {
    $need_count = 50 - $folder_count;
    echo "   📝 需要生成 {$need_count} 个网盘文件夹...\\n";
    
    for ($i = 0; $i < $need_count; $i++) {
        $name = '文件夹 ' . ($folder_count + $i + 1);
        $created_by = $users[array_rand($users)];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO disk_folders (name, parent_id, created_by, created_at, updated_at) VALUES ('{$name}', NULL, {$created_by}, '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 网盘文件夹数据生成完成\\n";
} else {
    echo "   ℹ️ 网盘文件夹数据已够了 ({$folder_count} 条)\\n";
}

// 8. 生成更多知识库文章数据
echo "\\n8. 生成更多知识库文章数据...\\n";
$article_count = pg_fetch_result(pg_query($db_conn, "SELECT COUNT(*) FROM knowledge_articles"), 0, 0);
if ($article_count < 50) {
    $need_count = 50 - $article_count;
    echo "   📝 需要生成 {$need_count} 篇知识库文章...\\n";
    
    $categories_result = pg_query($db_conn, "SELECT id FROM knowledge_categories LIMIT 10");
    $categories = pg_fetch_all_columns($categories_result, 0);
    
    $titles = ['技术文档', '操作手册', '常见问题', '最佳实践', '培训材料', '产品说明', 'API文档', '设计规范', '测试用例', '项目总结'];
    
    for ($i = 0; $i < $need_count; $i++) {
        $title = $titles[array_rand($titles)] . ' ' . ($article_count + $i + 1);
        $content = '这是知识库文章的详细内容。可以使用Markdown格式编写。';
        $category_id = $categories ? $categories[array_rand($categories)] : 'NULL';
        $created_by = $users[array_rand($users)];
        $status = ['draft', 'published', 'archived'][array_rand(['draft', 'published', 'archived'])];
        $created_at = randomDateTime($start_date, $end_date);
        
        $sql = "INSERT INTO knowledge_articles (title, content, category_id, created_by, status, created_at, updated_at) VALUES ('{$title}', '{$content}', {$category_id}, {$created_by}, '{$status}', '{$created_at}', NOW())";
        
        if (!pg_query($db_conn, $sql)) {
            // 忽略错误
        }
    }
    echo "   ✅ 知识库文章数据生成完成\\n";
} else {
    echo "   ℹ️ 知识库文章数据已够了 ({$article_count} 条)\\n";
}

echo "\\n" . str_repeat("=", 60) . "\\n";
echo "🎉 测试数据生成完成！\\n";
echo "📅 所有数据时间跨度: {$start_date} 至 {$end_date} (至少6个月)\\n";
echo str_repeat("=", 60) . "\\n";

// 显示最终统计
echo "\\n📊 最终数据量统计:\\n";
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
    $result = pg_query($db_conn, "SELECT COUNT(*) FROM {$table}");
    if ($result) {
        $count = pg_fetch_result($result, 0, 0);
        echo "   - {$name}: {$count} 条\\n";
    } else {
        echo "   - {$name}: 表不存在或无法统计\\n";
    }
}

pg_close($db_conn);
echo "\\n✅ 所有模块数据生成完成！\\n";
?>
"""
        
        # 将PHP脚本写入远程文件
        sftp = ssh.open_sftp()
        with sftp.open(remote_path, 'w') as f:
            f.write(php_script)
        sftp.close()
        print("✅ 完整PHP脚本创建完成!")
        
        # 3. 运行PHP脚本
        print("🚀 运行测试数据生成脚本...")
        stdin, stdout, stderr = ssh.exec_command(f"cd /tmp && php {remote_path}", get_pty=True)
        
        # 实时输出
        output = ""
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                output += chunk
                print(chunk, end='')
            time.sleep(0.1)
        
        # 获取剩余输出
        remaining = stdout.read().decode('utf-8', errors='ignore')
        output += remaining
        print(remaining, end='')
        
        error_output = stderr.read().decode('utf-8', errors='ignore')
        
        if error_output:
            print("\\n❌ 错误输出:")
            print(error_output)
        
        # 4. 清理临时文件
        print("\\n🧹 清理临时文件...")
        ssh.exec_command(f"rm -f {remote_path}")
        
        ssh.close()
        print("✅ 任务完成!")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print(" 为152服务器生成全面的测试数据")
    print("=" * 60 + "\\n")
    
    success = upload_and_run()
    
    if success:
        print("\\n" + "=" * 60)
        print(" ✅ 所有模块的测试数据已生成！")
        print("=" * 60)
    else:
        print("\\n" + "=" * 60)
        print(" ❌ 生成测试数据失败")
        print("=" * 60)