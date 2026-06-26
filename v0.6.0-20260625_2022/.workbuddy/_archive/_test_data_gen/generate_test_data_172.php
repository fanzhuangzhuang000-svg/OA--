<?php
// 172 服务器测试数据生成脚本
// 使用方法：上传到 172 服务器，然后运行 `php generate_test_data_172.php`

echo "🚀 开始生成测试数据...\n";
echo str_repeat("=", 60) . "\n\n";

// 读取 .env 文件获取数据库配置
$env = file_get_contents('/var/www/oa-api/.env');
$lines = explode("\n", $env);
$config = [];
foreach ($lines as $line) {
    if (strpos($line, '=') !== false) {
        list($key, $value) = explode('=', $line, 2);
        $config[trim($key)] = trim($value);
    }
}

// 连接数据库
$db_host = $config['DB_HOST'] ?? '127.0.0.1';
$db_port = $config['DB_PORT'] ?? '5432';
$db_name = $config['DB_DATABASE'] ?? 'security_oa';
$db_user = $config['DB_USERNAME'] ?? 'oa_user';
$db_pass = $config['DB_PASSWORD'] ?? '';

$conn = pg_connect("host=$db_host port=$db_port dbname=$db_name user=$db_user password=$db_pass");
if (!$conn) {
    echo "❌ 数据库连接失败\n";
    exit(1);
}

echo "✅ 数据库连接成功\n\n";

// 开始事务
pg_query($conn, "BEGIN");

try {
    // 1. 生成用户数据（如果 users 表只有 1 条记录）
    echo "1️⃣ 生成用户数据...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM users");
    $row = pg_fetch_assoc($result);
    $user_count = $row['cnt'];
    
    if ($user_count < 10) {
        $users = [
            ['name' => '张三', 'email' => 'zhangsan@example.com', 'password' => password_hash('123456', PASSWORD_DEFAULT), 'role' => '员工', 'department' => '技术部'],
            ['name' => '李四', 'email' => 'lisi@example.com', 'password' => password_hash('123456', PASSWORD_DEFAULT), 'role' => '员工', 'department' => '销售部'],
            ['name' => '王五', 'email' => 'wangwu@example.com', 'password' => password_hash('123456', PASSWORD_DEFAULT), 'role' => '经理', 'department' => '技术部'],
            ['name' => '赵六', 'email' => 'zhaoliu@example.com', 'password' => password_hash('123456', PASSWORD_DEFAULT), 'role' => '员工', 'department' => '财务部'],
            ['name' => '钱七', 'email' => 'qianqi@example.com', 'password' => password_hash('123456', PASSWORD_DEFAULT), 'role' => '员工', 'department' => '行政部'],
        ];
        
        foreach ($users as $user) {
            $sql = "INSERT INTO users (name, email, password, role, department, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$user['name'], $user['email'], $user['password'], $user['role'], $user['department']]);
            if (!$result) {
                echo "  ❌ 用户 {$user['name']} 创建失败: " . pg_last_error($conn) . "\n";
            } else {
                echo "  ✅ 用户 {$user['name']} 创建成功\n";
            }
        }
            if ($result) {
                echo "  ✅ 用户 {$user['name']} 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 用户数据已存在（$user_count 条），跳过\n";
    }
    
    // 2. 生成线索数据
    echo "\n2️⃣ 生成线索数据...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM leads");
    $row = pg_fetch_assoc($result);
    $leads_count = $row['cnt'];
    
    if ($leads_count < 50) {
        $sources = ['网站留言', '电话咨询', '朋友介绍', '线上广告', '展会收集'];
        $stages = ['new', 'contacted', 'proposal', 'negotiating', 'won', 'lost'];
        
        for ($i = 1; $i <= 50; $i++) {
            $name = "线索客户 $i";
            $phone = "138" . str_pad($i, 8, '0', STR_PAD_LEFT);
            $email = "lead$i@example.com";
            $source = $sources[array_rand($sources)];
            $stage = $stages[array_rand($stages)];
            
            $sql = "INSERT INTO leads (name, phone, email, source, stage, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$name, $phone, $email, $source, $stage]);
            if ($result) {
                echo "  ✅ 线索 $name 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 线索数据已存在（$leads_count 条），跳过\n";
    }
    
    // 3. 生成商机数据
    echo "\n3️⃣ 生成商机数据...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM opportunities");
    $row = pg_fetch_assoc($result);
    $opp_count = $row['cnt'];
    
    if ($opp_count < 30) {
        $stages = ['inquiry', 'qualification', 'proposal', 'negotiating', 'quoted', 'won', 'lost'];
        
        for ($i = 1; $i <= 30; $i++) {
            $title = "商机项目 $i";
            $amount = rand(10000, 500000);
            $stage = $stages[array_rand($stages)];
            $customer_id = rand(1, 27); // 假设有 27 个客户
            
            $sql = "INSERT INTO opportunities (title, amount, stage, customer_id, created_at, updated_at) VALUES ($1, $2, $3, $4, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$title, $amount, $stage, $customer_id]);
            if ($result) {
                echo "  ✅ 商机 $title 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 商机数据已存在（$opp_count 条），跳过\n";
    }
    
    // 4. 生成考勤记录
    echo "\n4️⃣ 生成考勤记录...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM attendance_records");
    $row = pg_fetch_assoc($result);
    $att_count = $row['cnt'];
    
    if ($att_count < 100) {
        $users = pg_query($conn, "SELECT id FROM users LIMIT 10");
        $user_ids = [];
        while ($row = pg_fetch_assoc($users)) {
            $user_ids[] = $row['id'];
        }
        
        $statuses = ['正常', '迟到', '早退', '缺勤'];
        
        for ($i = 0; $i < 100; $i++) {
            $user_id = $user_ids[array_rand($user_ids)];
            $date = date('Y-m-d', strtotime("-$i days"));
            $status = $statuses[array_rand($statuses)];
            
            $sql = "INSERT INTO attendance_records (user_id, date, status, created_at, updated_at) VALUES ($1, $2, $3, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$user_id, $date, $status]);
            if ($result) {
                echo "  ✅ 考勤记录 $date (用户 $user_id) 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 考勤记录已存在（$att_count 条），跳过\n";
    }
    
    // 5. 生成车辆数据
    echo "\n5️⃣ 生成车辆数据...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM vehicles");
    $row = pg_fetch_assoc($result);
    $veh_count = $row['cnt'];
    
    if ($veh_count < 10) {
        $vehicles = [
            ['plate' => '京A12345', 'model' => '奥迪A6', 'status' => '可用'],
            ['plate' => '京B67890', 'model' => '宝马5系', 'status' => '可用'],
            ['plate' => '京C54321', 'model' => '奔驰E级', 'status' => '维修中'],
            ['plate' => '京D09876', 'model' => '丰田凯美瑞', 'status' => '可用'],
            ['plate' => '京E13579', 'model' => '本田雅阁', 'status' => '已分配'],
        ];
        
        foreach ($vehicles as $vehicle) {
            $sql = "INSERT INTO vehicles (plate, model, status, created_at, updated_at) VALUES ($1, $2, $3, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$vehicle['plate'], $vehicle['model'], $vehicle['status']]);
            if ($result) {
                echo "  ✅ 车辆 {$vehicle['plate']} 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 车辆数据已存在（$veh_count 条），跳过\n";
    }
    
    // 6. 生成库存物品数据
    echo "\n6️⃣ 生成库存物品数据...\n";
    $result = pg_query($conn, "SELECT COUNT(*) as cnt FROM inventory_items");
    $row = pg_fetch_assoc($result);
    $inv_count = $row['cnt'];
    
    if ($inv_count < 50) {
        $items = [
            ['name' => '笔记本', 'category' => '办公用品', 'quantity' => 100],
            ['name' => '签字笔', 'category' => '办公用品', 'quantity' => 500],
            ['name' => 'A4纸', 'category' => '办公用品', 'quantity' => 50],
            ['name' => '订书机', 'category' => '办公用品', 'quantity' => 20],
            ['name' => '计算器', 'category' => '办公用品', 'quantity' => 15],
        ];
        
        foreach ($items as $item) {
            $sql = "INSERT INTO inventory_items (name, category, quantity, created_at, updated_at) VALUES ($1, $2, $3, NOW(), NOW())";
            $result = pg_query_params($conn, $sql, [$item['name'], $item['category'], $item['quantity']]);
            if ($result) {
                echo "  ✅ 库存物品 {$item['name']} 创建成功\n";
            }
        }
    } else {
        echo "  ⚠️ 库存物品已存在（$inv_count 条），跳过\n";
    }
    
    // 提交事务
    pg_query($conn, "COMMIT");
    echo "\n" . str_repeat("=", 60) . "\n";
    echo "✅ 测试数据生成完成！\n";
    
} catch (Exception $e) {
    pg_query($conn, "ROLLBACK");
    echo "\n❌ 错误: " . $e->getMessage() . "\n";
}

pg_close($conn);
?>
