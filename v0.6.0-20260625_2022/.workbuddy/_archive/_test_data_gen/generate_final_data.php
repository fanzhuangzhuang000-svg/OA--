<?php
/**
 * 152服务器最终版测试数据生成脚本
 * 修复之前的问题，并为所有模块生成全面数据
 */

// 数据库连接配置（从152服务器.env文件读取）
$host = '127.0.0.1';
$port = '5432';
$dbname = 'security_oa';
$username = 'oa_user';
$password = 'oa_pg_pwd_782997781';

// 连接数据库
$conn = pg_connect("host=$host port=$port dbname=$dbname user=$username password=$password");
if (!$conn) {
    die("数据库连接失败: " . pg_last_error() . "\n");
}

echo "✅ 数据库连接成功\n\n";

// 设置客户端编码
pg_query($conn, "SET client_encoding = 'UTF8'");

// 时间范围：至少6个月（2025-12-01 至 2026-06-22）
$startDate = '2025-12-01';
$endDate = '2026-06-22';

// 辅助函数：生成随机日期
function randomDate($start, $end) {
    $timestamp = mt_rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

// 辅助函数：生成随机小数
function randomFloat($min, $max) {
    return round(mt_rand($min * 100, $max * 100) / 100, 2);
}

// 辅助函数：随机选择数组元素
function randomElement($array) {
    return $array[array_rand($array)];
}

// ==================== 1. 修复员工档案数据 ====================
echo "1. 修复员工档案数据...\n";

// 先检查users表中有哪些用户
$usersResult = pg_query($conn, "SELECT id, name FROM users ORDER BY id");
$users = [];
while ($row = pg_fetch_assoc($usersResult)) {
    $users[] = $row;
}

echo "   找到 " . count($users) . " 个用户\n";

// 检查employee_profiles表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'employee_profiles'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   employee_profiles表字段: " . implode(', ', $columns) . "\n";

// 生成员工档案数据
$employeeCount = 0;
$positions = ['项目经理', '软件工程师', '硬件工程师', '销售经理', '客户经理', '财务主管', '人事专员', '行政助理', '技术总监', '运维工程师'];
$departments = ['技术部', '销售部', '财务部', '人事部', '行政部', '运维部'];

// 先清空现有的员工档案（如果存在）
pg_query($conn, "DELETE FROM employee_profiles WHERE user_id > 1");

for ($i = 0; $i < 30; $i++) {
    $userId = $users[$i % count($users)]['id'];
    $userName = $users[$i % count($users)]['name'];
    
    // 检查是否已有档案
    $checkExisting = pg_query($conn, "SELECT id FROM employee_profiles WHERE user_id = $userId");
    if (pg_fetch_assoc($checkExisting)) {
        continue; // 跳过已存在的
    }
    
    $employeeNo = 'EMP' . str_pad($i + 1, 4, '0', STR_PAD_LEFT);
    $position = randomElement($positions);
    $department = randomElement($departments);
    $phone = '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999);
    $email = strtolower(str_replace(' ', '', $userName)) . '@company.com';
    $hireDate = randomDate('2023-01-01', '2025-11-30');
    $salary = mt_rand(5000, 25000);
    $status = randomElement(['active', 'active', 'active', 'inactive']); // 75%活跃
    
    // 根据实际的表结构插入
    if (in_array('user_id', $columns)) {
        $sql = "INSERT INTO employee_profiles 
                (user_id, employee_no, position, department, phone, email, hire_date, salary, status, created_at, updated_at)
                VALUES 
                ($userId, '$employeeNo', '$position', '$department', '$phone', '$email', '$hireDate', $salary, '$status', NOW(), NOW())";
        
        if (pg_query($conn, $sql)) {
            $employeeCount++;
        }
    }
}

echo "   ✅ 生成了 {$employeeCount} 条员工档案记录\n\n";

// ==================== 2. 修复网盘文件夹数据 ====================
echo "2. 修复网盘文件夹数据...\n";

// 检查disk_folders表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'disk_folders'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   disk_folders表字段: " . implode(', ', $columns) . "\n";

// 先获取管理员用户ID
$adminResult = pg_query($conn, "SELECT id FROM users WHERE role = 'admin' LIMIT 1");
$admin = pg_fetch_assoc($adminResult);
$adminId = $admin ? $admin['id'] : 1;

// 生成文件夹数据
$folderCount = 0;
$folderTypes = ['folder', 'document', 'image', 'video', 'archive'];

// 先清空现有的测试文件夹（保留前6个）
pg_query($conn, "DELETE FROM disk_folders WHERE id > 6");

$folderNames = [
    '公司文档', '项目资料', '财务报表', '人事档案', '技术文档', '客户资料',
    '市场推广', '培训材料', '合同文件', '研发资料', '会议纪要', '制度建设',
    '质量管理', '安全管理', '应急预案', '设备档案', '采购文档', '销售合同',
    '售后服务', '知识库'
];

for ($i = 0; $i < count($folderNames); $i++) {
    $name = $folderNames[$i];
    $parentId = ($i < 6) ? 'NULL' : mt_rand(1, 6); // 前6个是一级文件夹
    $type = randomElement($folderTypes);
    $size = mt_rand(1024, 1048576); // 1KB 到 1MB
    $fileCount = mt_rand(0, 50);
    $createdAt = randomDate($startDate, $endDate);
    
    // 检查是否已存在
    $checkExisting = pg_query($conn, "SELECT id FROM disk_folders WHERE name = '$name' AND parent_id IS " . ($parentId == 'NULL' ? 'NULL' : "$parentId"));
    if (pg_fetch_assoc($checkExisting)) {
        continue;
    }
    
    $sql = "INSERT INTO disk_folders 
            (name, parent_id, type, size, file_count, created_by, created_at, updated_at)
            VALUES 
            ('$name', $parentId, '$type', $size, $fileCount, $adminId, '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $folderCount++;
    }
}

echo "   ✅ 生成了 {$folderCount} 个网盘文件夹\n\n";

// ==================== 3. 修复知识库文章数据 ====================
echo "3. 修复知识库文章数据...\n";

// 检查knowledge_articles表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'knowledge_articles'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   knowledge_articles表字段: " . implode(', ', $columns) . "\n";

// 生成知识库文章数据
$articleCount = 0;
$categories = ['技术文档', '操作手册', '常见问题', '培训资料', '公司制度', '项目总结', '产品介绍', '解决方案'];
$titles = [
    '系统操作手册', '故障排除指南', '新员工培训资料', '项目管理规范',
    '代码审查流程', '测试标准文档', '安全管理制度', '数据备份策略',
    '客户服务规范', '质量控制手册', '应急预案模板', '技术架构设计',
    '接口文档规范', '部署实施指南', '性能优化方案', '用户权限管理',
    '数据安全防护', '系统监控方案', '版本发布流程', '团队协作工具'
];

// 先清空现有的测试文章（保留前10个）
pg_query($conn, "DELETE FROM knowledge_articles WHERE id > 10");

for ($i = 0; $i < count($titles); $i++) {
    $title = $titles[$i];
    $category = randomElement($categories);
    $content = "本文档详细介绍了{$title}的相关内容，包括操作流程、注意事项和最佳实践。\n\n";
    $content .= "## 简介\n这是{$title}的详细文档内容，适用于所有相关人员学习和参考。\n\n";
    $content .= "## 主要内容\n1. 基础知识\n2. 操作步骤\n3. 常见问题\n4. 附录\n";
    $tags = json_encode([$category, '文档', '培训']);
    $status = randomElement(['published', 'published', 'draft', 'archived']); // 50%已发布
    $viewCount = mt_rand(10, 500);
    $createdAt = randomDate($startDate, $endDate);
    
    // 检查是否已存在
    $checkExisting = pg_query($conn, "SELECT id FROM knowledge_articles WHERE title = '$title'");
    if (pg_fetch_assoc($checkExisting)) {
        continue;
    }
    
    // 根据实际的表结构插入
    if (in_array('title', $columns) && in_array('content', $columns)) {
        $sql = "INSERT INTO knowledge_articles 
                (title, content, category, tags, status, view_count, created_by, created_at, updated_at)
                VALUES 
                ('$title', '$content', '$category', '$tags', '$status', $viewCount, $adminId, '$createdAt', '$createdAt')";
        
        if (pg_query($conn, $sql)) {
            $articleCount++;
        }
    }
}

echo "   ✅ 生成了 {$articleCount} 篇知识库文章\n\n";

// ==================== 4. 生成更多考勤数据 ====================
echo "4. 生成更多考勤数据...\n";

// 检查attendance_records表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'attendance_records'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   attendance_records表字段: " . implode(', ', $columns) . "\n";

// 获取所有员工ID
$employeesResult = pg_query($conn, "SELECT id FROM employee_profiles LIMIT 20");
$employeeIds = [];
while ($row = pg_fetch_assoc($employeesResult)) {
    $employeeIds[] = $row['id'];
}

if (count($employeeIds) == 0) {
    // 如果没有员工档案，使用用户ID
    $usersResult = pg_query($conn, "SELECT id FROM users LIMIT 20");
    while ($row = pg_fetch_assoc($usersResult)) {
        $employeeIds[] = $row['id'];
    }
}

$attendanceCount = 0;
$attendanceTypes = ['normal', 'late', 'early_leave', 'absent', 'leave', 'overtime'];
$attendanceStatuses = ['pending', 'approved', 'rejected'];

// 为每个员工生成6个月的考勤记录
foreach ($employeeIds as $employeeId) {
    // 生成2025-12至2026-06的每个工作日
    $currentDate = strtotime('2025-12-01');
    $endDateStamp = strtotime('2026-06-22');
    
    while ($currentDate <= $endDateStamp) {
        $dayOfWeek = date('N', $currentDate);
        
        // 只生成工作日的考勤（周一到周五）
        if ($dayOfWeek < 6) {
            $date = date('Y-m-d', $currentDate);
            $type = randomElement($attendanceTypes);
            $status = ($type == 'normal') ? 'approved' : randomElement($attendanceStatuses);
            $checkIn = ($type == 'normal' || $type == 'late') ? date('H:i:s', strtotime('08:' . mt_rand(30, 59) . ':00')) : NULL;
            $checkOut = ($type == 'normal' || $type == 'early_leave' || $type == 'overtime') ? date('H:i:s', strtotime('17:' . mt_rand(30, 59) . ':00')) : NULL;
            $hours = ($type == 'normal') ? 8 : (($type == 'overtime') ? mt_rand(1, 4) : 0);
            
            // 检查是否已存在
            $checkExisting = pg_query($conn, "SELECT id FROM attendance_records 
                                             WHERE employee_id = $employeeId AND date = '$date'");
            if (pg_fetch_assoc($checkExisting)) {
                $currentDate = strtotime('+1 day', $currentDate);
                continue;
            }
            
            $sql = "INSERT INTO attendance_records 
                    (employee_id, date, type, status, check_in, check_out, work_hours, created_at, updated_at)
                    VALUES 
                    ($employeeId, '$date', '$type', '$status', " . 
                    ($checkIn ? "'$checkIn'" : "NULL") . ", " . 
                    ($checkOut ? "'$checkOut'" : "NULL") . ", 
                    $hours, NOW(), NOW())";
            
            if (pg_query($conn, $sql)) {
                $attendanceCount++;
            }
        }
        
        $currentDate = strtotime('+1 day', $currentDate);
    }
}

echo "   ✅ 生成了 {$attendanceCount} 条考勤记录\n\n";

// ==================== 5. 生成更多报销数据 ====================
echo "5. 生成更多报销数据...\n";

// 检查expense_claims表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'expense_claims'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   expense_claims表字段: " . implode(', ', $columns) . "\n";

// 获取项目ID
$projectsResult = pg_query($conn, "SELECT id FROM projects LIMIT 10");
$projectIds = [];
while ($row = pg_fetch_assoc($projectsResult)) {
    $projectIds[] = $row['id'];
}

$expenseCount = 0;
$expenseTypes = ['travel', 'meal', 'transport', 'office', 'training', 'other'];
$expenseStatuses = ['pending', 'approved', 'rejected', 'reimbursed'];

for ($i = 0; $i < 100; $i++) {
    $userId = randomElement($employeeIds);
    if (!is_numeric($userId)) $userId = 1;
    $projectId = (count($projectIds) > 0) ? randomElement($projectIds) : 'NULL';
    $type = randomElement($expenseTypes);
    $amount = randomFloat(50, 5000);
    $description = $type . '费用报销';
    $status = randomElement($expenseStatuses);
    $expenseDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO expense_claims 
            (user_id, project_id, type, amount, description, status, expense_date, created_at, updated_at)
            VALUES 
            ($userId, " . ($projectId ?: 'NULL') . ", '$type', $amount, '$description', '$status', '$expenseDate', '$expenseDate', '$expenseDate')";
    
    if (pg_query($conn, $sql)) {
        $expenseCount++;
    }
}

echo "   ✅ 生成了 {$expenseCount} 条报销记录\n\n";

// ==================== 6. 生成更多库存数据 ====================
echo "6. 生成更多库存数据...\n";

// 检查inventory_items表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'inventory_items'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   inventory_items表字段: " . implode(', ', $columns) . "\n";

// 获取仓库ID
$warehousesResult = pg_query($conn, "SELECT id FROM inventory_warehouses LIMIT 5");
$warehouseIds = [];
while ($row = pg_fetch_assoc($warehousesResult)) {
    $warehouseIds[] = $row['id'];
}

// 获取分类ID
$categoriesResult = pg_query($conn, "SELECT id FROM inventory_categories LIMIT 10");
$categoryIds = [];
while ($row = pg_fetch_assoc($categoriesResult)) {
    $categoryIds[] = $row['id'];
}

$itemCount = 0;
$itemNames = [
    '笔记本电脑', '台式电脑', '打印机', '复印机', '投影仪', '扫描仪', '传真机', '碎纸机',
    '办公桌椅', '文件柜', '保险柜', '空调', '饮水机', '微波炉', '冰箱', '电视',
    '路由器', '交换机', '网线', '水晶头', '电源线', '插座', '电池', '灯泡',
    '纸张A4', '纸张A3', '文件夹', '订书机', '计算器', '胶带', '剪刀', '笔筒'
];

// 生成更多库存物品
foreach ($itemNames as $index => $name) {
    $code = 'ITEM' . str_pad($index + 100, 6, '0', STR_PAD_LEFT);
    $warehouseId = (count($warehouseIds) > 0) ? randomElement($warehouseIds) : 'NULL';
    $categoryId = (count($categoryIds) > 0) ? randomElement($categoryIds) : 'NULL';
    $quantity = mt_rand(10, 500);
    $unit = randomElement(['台', '个', '件', '箱', '包', '卷']);
    $price = randomFloat(10, 5000);
    $status = randomElement(['normal', 'normal', 'normal', 'low', 'out']);
    
    // 检查是否已存在
    $checkExisting = pg_query($conn, "SELECT id FROM inventory_items WHERE code = '$code'");
    if (pg_fetch_assoc($checkExisting)) {
        continue;
    }
    
    $sql = "INSERT INTO inventory_items 
            (code, name, warehouse_id, category_id, quantity, unit, price, status, created_at, updated_at)
            VALUES 
            ('$code', '$name', " . ($warehouseId ?: 'NULL') . ", " . ($categoryId ?: 'NULL') . ", 
            $quantity, '$unit', $price, '$status', NOW(), NOW())";
    
    if (pg_query($conn, $sql)) {
        $itemCount++;
    }
}

echo "   ✅ 生成了 {$itemCount} 个库存物品\n\n";

// ==================== 7. 生成更多车辆数据 ====================
echo "7. 生成更多车辆数据...\n";

$vehicleCount = 0;
$vehicleBrands = ['丰田', '本田', '大众', '奔驰', '宝马', '奥迪', '比亚迪', '特斯拉', '蔚来', '小鹏'];
$vehicleTypes = ['轿车', 'SUV', '商务车', '货车', '卡车'];
$vehicleStatuses = ['available', 'in_use', 'maintenance', 'retired'];

for ($i = 0; $i < 15; $i++) {
    $code = 'VEH' . str_pad($i + 100, 6, '0', STR_PAD_LEFT);
    $brand = randomElement($vehicleBrands);
    $model = $brand . ' ' . randomElement($vehicleTypes) . '款';
    $license = chr(mt_rand(65, 90)) . chr(mt_rand(65, 90)) . mt_rand(10, 99) . chr(mt_rand(65, 90)) . chr(mt_rand(65, 90)) . mt_rand(10, 99);
    $type = randomElement($vehicleTypes);
    $status = randomElement($vehicleStatuses);
    $purchaseDate = randomDate('2020-01-01', '2025-12-31');
    
    // 检查是否已存在
    $checkExisting = pg_query($conn, "SELECT id FROM vehicles WHERE code = '$code'");
    if (pg_fetch_assoc($checkExisting)) {
        continue;
    }
    
    $sql = "INSERT INTO vehicles 
            (code, brand, model, license_plate, type, status, purchase_date, created_at, updated_at)
            VALUES 
            ('$code', '$brand', '$model', '$license', '$type', '$status', '$purchaseDate', NOW(), NOW())";
    
    if (pg_query($conn, $sql)) {
        $vehicleCount++;
    }
}

echo "   ✅ 生成了 {$vehicleCount} 辆车辆记录\n\n";

// ==================== 8. 生成审批流程数据 ====================
echo "8. 生成审批流程数据...\n";

// 检查approvals表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'approvals'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   approvals表字段: " . implode(', ', $columns) . "\n";

$approvalCount = 0;
$approvalTypes = ['leave', 'overtime', 'expense', 'purchase', 'travel', 'general'];
$approvalStatuses = ['pending', 'approved', 'rejected', 'cancelled'];

for ($i = 0; $i < 80; $i++) {
    $applicantId = randomElement($employeeIds);
    if (!is_numeric($applicantId)) $applicantId = 1;
    $type = randomElement($approvalTypes);
    $title = $type . '审批申请' . ($i + 1);
    $content = '这是' . $type . '的审批申请内容，请领导审批。';
    $status = randomElement($approvalStatuses);
    $createdAt = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO approvals 
            (applicant_id, type, title, content, status, created_at, updated_at)
            VALUES 
            ($applicantId, '$type', '$title', '$content', '$status', '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $approvalCount++;
        $approvalId = pg_last_oid($conn);
        
        // 生成审批记录
        $approverId = randomElement($employeeIds);
        if (!is_numeric($approverId)) $approverId = 1;
        $result = randomElement(['approved', 'rejected', 'pending']);
        $comment = ($result == 'approved') ? '同意' : (($result == 'rejected') ? '不同意' : '待审批');
        
        $recordSql = "INSERT INTO approval_records 
                     (approval_id, approver_id, result, comment, created_at, updated_at)
                     VALUES 
                     ($approvalId, $approverId, '$result', '$comment', '$createdAt', '$createdAt')";
        
        pg_query($conn, $recordSql);
    }
}

echo "   ✅ 生成了 {$approvalCount} 条审批记录\n\n";

// ==================== 9. 生成财务更多数据 ====================
echo "9. 生成财务更多数据...\n";

// 更多应收数据
$receivableCount = 0;
for ($i = 0; $i < 80; $i++) {
    $customerId = mt_rand(1, 48); // 客户ID从1到48
    $projectId = (count($projectIds) > 0) ? randomElement($projectIds) : 'NULL';
    $amount = randomFloat(1000, 100000);
    $paidAmount = randomFloat(0, $amount);
    $status = ($paidAmount >= $amount) ? 'paid' : (($paidAmount > 0) ? 'partial' : 'pending');
    $dueDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO receivables 
            (customer_id, project_id, amount, paid_amount, status, due_date, created_at, updated_at)
            VALUES 
            ($customerId, " . ($projectId ?: 'NULL') . ", $amount, $paidAmount, '$status', '$dueDate', NOW(), NOW())";
    
    if (pg_query($conn, $sql)) {
        $receivableCount++;
    }
}

echo "   ✅ 生成了 {$receivableCount} 条应收记录\n";

// 更多应付数据
$payableCount = 0;
for ($i = 0; $i < 60; $i++) {
    $supplierId = mt_rand(1, 29); // 供应商ID从1到29
    $amount = randomFloat(1000, 80000);
    $paidAmount = randomFloat(0, $amount);
    $status = ($paidAmount >= $amount) ? 'paid' : (($paidAmount > 0) ? 'partial' : 'pending');
    $dueDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO payables 
            (supplier_id, amount, paid_amount, status, due_date, created_at, updated_at)
            VALUES 
            ($supplierId, $amount, $paidAmount, '$status', '$dueDate', NOW(), NOW())";
    
    if (pg_query($conn, $sql)) {
        $payableCount++;
    }
}

echo "   ✅ 生成了 {$payableCount} 条应付记录\n";

// 更多账户交易记录
$transactionCount = 0;
for ($i = 0; $i < 200; $i++) {
    $accountId = mt_rand(1, 9); // 账户ID从1到9
    $type = randomElement(['income', 'expense', 'transfer']);
    $amount = randomFloat(100, 20000);
    $balance = randomFloat(1000, 100000);
    $description = $type . '交易记录';
    $transactionDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO finance_transactions 
            (account_id, type, amount, balance, description, transaction_date, created_at, updated_at)
            VALUES 
            ($accountId, '$type', $amount, $balance, '$description', '$transactionDate', '$transactionDate', '$transactionDate')";
    
    if (pg_query($conn, $sql)) {
        $transactionCount++;
    }
}

echo "   ✅ 生成了 {$transactionCount} 条财务交易记录\n\n";

// ==================== 10. 生成更多项目管理数据 ====================
echo "10. 生成更多项目管理数据...\n";

// 更多项目成员
$memberCount = 0;
foreach ($projectIds as $projectId) {
    $numMembers = mt_rand(3, 8);
    $usedEmployees = [];
    
    for ($i = 0; $i < $numMembers; $i++) {
        $employeeId = randomElement($employeeIds);
        if (in_array($employeeId, $usedEmployees)) continue;
        $usedEmployees[] = $employeeId;
        
        $role = randomElement(['member', 'member', 'leader', 'observer']);
        $joinedAt = randomDate($startDate, $endDate);
        
        // 检查是否已存在
        $checkExisting = pg_query($conn, "SELECT id FROM project_members 
                                         WHERE project_id = $projectId AND employee_id = $employeeId");
        if (pg_fetch_assoc($checkExisting)) {
            continue;
        }
        
        $sql = "INSERT INTO project_members 
                (project_id, employee_id, role, joined_at, created_at, updated_at)
                VALUES 
                ($projectId, $employeeId, '$role', '$joinedAt', '$joinedAt', '$joinedAt')";
        
        if (pg_query($conn, $sql)) {
            $memberCount++;
        }
    }
}

echo "   ✅ 生成了 {$memberCount} 条项目成员记录\n";

// 项目任务
$taskCount = 0;
$taskStatuses = ['todo', 'in_progress', 'review', 'done'];
$taskPriorities = ['low', 'medium', 'high', 'urgent'];

for ($i = 0; $i < 100; $i++) {
    $projectId = (count($projectIds) > 0) ? randomElement($projectIds) : 1;
    $assigneeId = randomElement($employeeIds);
    if (!is_numeric($assigneeId)) $assigneeId = 1;
    $title = '项目任务' . ($i + 1);
    $description = '这是任务' . ($i + 1) . '的详细描述';
    $status = randomElement($taskStatuses);
    $priority = randomElement($taskPriorities);
    $dueDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO project_tasks 
            (project_id, assignee_id, title, description, status, priority, due_date, created_at, updated_at)
            VALUES 
            ($projectId, $assigneeId, '$title', '$description', '$status', '$priority', '$dueDate', NOW(), NOW())";
    
    if (pg_query($conn, $sql)) {
        $taskCount++;
    }
}

echo "   ✅ 生成了 {$taskCount} 条项目任务记录\n\n";

// ==================== 11. 生成更多客户服务数据 ====================
echo "11. 生成更多客户服务数据...\n";

// 更多服务工单
$serviceOrderCount = 0;
$serviceTypes = ['repair', 'maintenance', 'installation', 'consultation', 'training'];
$serviceStatuses = ['pending', 'assigned', 'in_progress', 'resolved', 'closed'];
$priorities = ['low', 'medium', 'high', 'urgent'];

for ($i = 0; $i < 80; $i++) {
    $customerId = mt_rand(1, 48);
    $type = randomElement($serviceTypes);
    $title = $type . '服务工单' . ($i + 1);
    $description = '这是' . $type . '服务工单的描述';
    $status = randomElement($serviceStatuses);
    $priority = randomElement($priorities);
    $createdAt = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO service_orders 
            (customer_id, type, title, description, status, priority, created_at, updated_at)
            VALUES 
            ($customerId, '$type', '$title', '$description', '$status', '$priority', '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $serviceOrderCount++;
    }
}

echo "   ✅ 生成了 {$serviceOrderCount} 条服务工单记录\n\n";

// ==================== 12. 生成更多销售数据 ====================
echo "12. 生成更多销售数据...\n";

// 更多销售线索
$leadCount = 0;
$leadStatuses = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost'];
$sources = ['website', 'referral', 'exhibition', 'cold_call', 'advertisement'];

for ($i = 0; $i < 100; $i++) {
    $name = '线索联系人' . ($i + 1);
    $company = '潜在客户公司' . ($i + 1);
    $phone = '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999);
    $email = 'lead' . ($i + 1) . '@potential.com';
    $status = randomElement($leadStatuses);
    $source = randomElement($sources);
    $createdAt = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO leads 
            (name, company, phone, email, status, source, created_at, updated_at)
            VALUES 
            ('$name', '$company', '$phone', '$email', '$status', '$source', '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $leadCount++;
    }
}

echo "   ✅ 生成了 {$leadCount} 条销售线索记录\n";

// 更多销售机会
$opportunityCount = 0;
$opportunityStatuses = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'];

for ($i = 0; $i < 80; $i++) {
    $customerId = mt_rand(1, 48);
    $title = '销售机会' . ($i + 1);
    $amount = randomFloat(10000, 500000);
    $status = randomElement($opportunityStatuses);
    $expectedCloseDate = randomDate($startDate, $endDate);
    $createdAt = randomDate($startDate, $expectedCloseDate);
    
    $sql = "INSERT INTO opportunities 
            (customer_id, title, amount, status, expected_close_date, created_at, updated_at)
            VALUES 
            ($customerId, '$title', $amount, '$status', '$expectedCloseDate', '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $opportunityCount++;
    }
}

echo "   ✅ 生成了 {$opportunityCount} 条销售机会记录\n\n";

// ==================== 13. 生成更多采购数据 ====================
echo "13. 生成更多采购数据...\n";

// 更多采购订单
$purchaseOrderCount = 0;
$purchaseStatuses = ['draft', 'pending', 'approved', 'ordered', 'received', 'cancelled'];

for ($i = 0; $i < 60; $i++) {
    $supplierId = mt_rand(1, 29);
    $orderNo = 'PO' . date('Ymd') . str_pad($i + 1, 4, '0', STR_PAD_LEFT);
    $totalAmount = randomFloat(5000, 200000);
    $status = randomElement($purchaseStatuses);
    $orderDate = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO purchase_orders 
            (supplier_id, order_no, total_amount, status, order_date, created_at, updated_at)
            VALUES 
            ($supplierId, '$orderNo', $totalAmount, '$status', '$orderDate', '$orderDate', '$orderDate')";
    
    if (pg_query($conn, $sql)) {
        $purchaseOrderCount++;
    }
}

echo "   ✅ 生成了 {$purchaseOrderCount} 条采购订单记录\n\n";

// ==================== 14. 生成消息通知数据 ====================
echo "14. 生成消息通知数据...\n";

// 检查notifications表结构
$checkTable = pg_query($conn, "SELECT column_name FROM information_schema.columns 
                              WHERE table_name = 'notifications'");
$columns = [];
while ($row = pg_fetch_assoc($checkTable)) {
    $columns[] = $row['column_name'];
}

echo "   notifications表字段: " . implode(', ', $columns) . "\n";

$notificationCount = 0;
$notificationTypes = ['system', 'approval', 'project', 'attendance', 'expense', 'customer', 'vehicle'];
$priorities = ['low', 'medium', 'high'];

for ($i = 0; $i < 300; $i++) {
    $receiverId = randomElement($employeeIds);
    if (!is_numeric($receiverId)) $receiverId = 1;
    $type = randomElement($notificationTypes);
    $title = $type . '通知' . ($i + 1);
    $content = '这是' . $type . '的通知内容。';
    $priority = randomElement($priorities);
    $isRead = randomElement([true, false, false]); // 33%已读
    $createdAt = randomDate($startDate, $endDate);
    
    $sql = "INSERT INTO notifications 
            (receiver_id, type, title, content, priority, is_read, created_at, updated_at)
            VALUES 
            ($receiverId, '$type', '$title', '$content', '$priority', $isRead, '$createdAt', '$createdAt')";
    
    if (pg_query($conn, $sql)) {
        $notificationCount++;
    }
}

echo "   ✅ 生成了 {$notificationCount} 条消息通知记录\n\n";

// ==================== 最终统计 ====================
echo "================ 最终数据统计 ==================\n";

$tables = [
    'users' => '用户',
    'employee_profiles' => '员工档案',
    'attendance_records' => '考勤记录',
    'expense_claims' => '报销记录',
    'vehicles' => '车辆',
    'vehicle_insurance' => '车辆保险',
    'vehicle_maintenance_records' => '车辆保养',
    'fuel_cards' => '油卡',
    'inventory_items' => '库存物品',
    'inventory_warehouses' => '仓库',
    'inventory_categories' => '库存分类',
    'stock_records' => '库存流水',
    'customers' => '客户',
    'projects' => '项目',
    'project_members' => '项目成员',
    'project_tasks' => '项目任务',
    'service_orders' => '服务工单',
    'leads' => '销售线索',
    'opportunities' => '销售机会',
    'quotations' => '报价单',
    'purchase_orders' => '采购订单',
    'receivables' => '应收记录',
    'payables' => '应付记录',
    'finance_accounts' => '财务账户',
    'finance_transactions' => '财务交易',
    'approvals' => '审批记录',
    'approval_records' => '审批流程记录',
    'notifications' => '消息通知',
    'disk_folders' => '网盘文件夹',
    'disk_files' => '网盘文件',
    'knowledge_articles' => '知识库文章',
    'suppliers' => '供应商'
];

foreach ($tables as $table => $name) {
    $result = pg_query($conn, "SELECT COUNT(*) as count FROM $table");
    if ($result) {
        $row = pg_fetch_assoc($result);
        $count = $row['count'];
        echo sprintf("  %-20s: %6d 条\n", $name, $count);
    }
}

echo "\n✅ 所有测试数据生成完成！\n";
echo "⏰ 数据时间跨度: 2025-12-01 至 2026-06-22 (至少6个月)\n";
echo "📅 生成时间: " . date('Y-m-d H:i:s') . "\n";

// 关闭数据库连接
pg_close($conn);
?>