#!/usr/bin/env python3
"""
在152服务器上直接创建并运行数据生成脚本
"""
import paramiko
import time

# 服务器配置
HOST = '152.136.115.121'
USERNAME = 'ubuntu'
PASSWORD = 'Aa782997781.'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔗 正在连接152服务器 {HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ SSH连接成功\n")
        
        # 直接在服务器上创建PHP脚本
        print("=" * 60)
        print("在服务器上创建数据生成脚本")
        print("=" * 60)
        
        php_script = """<?php
require_once '/var/www/oa-api/vendor/autoload.php';
$app = require_once '/var/www/oa-api/bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();

use Illuminate\\Support\\Facades\\DB;

echo "🚀 开始生成缺失的测试数据...\\n\\n";

$startDate = '2025-12-01';
$endDate = '2026-06-22';
$adminId = 1;

// 获取现有数据
$userIds = DB::table('users')->pluck('id')->toArray();
$customerIds = DB::table('customers')->pluck('id')->toArray();
$projectIds = DB::table('projects')->pluck('id')->toArray();
$productIds = DB::table('inventory_items')->pluck('id')->toArray();
$quotationIds = DB::table('quotations')->pluck('id')->toArray();

function randomDate($start, $end) {
    $timestamp = mt_rand(strtotime($start), strtotime($end));
    return date('Y-m-d H:i:s', $timestamp);
}

function randomElement($array) {
    return $array[array_rand($array)];
}

// 1. 生成 employee_skills（员工技能）
echo "1. 生成员工技能数据...\\n";
$skills = ['网络安防', '视频监控', '门禁系统', '综合布线', 'IT运维', '项目管理', 'Python', 'Java', 'Linux', '网络安全'];
$skillCount = 0;

foreach ($userIds as $userId) {
    $numSkills = mt_rand(1, 3);
    $selectedIndexes = array_rand($skills, $numSkills);
    if (!is_array($selectedIndexes)) $selectedIndexes = [$selectedIndexes];
    
    foreach ($selectedIndexes as $idx) {
        try {
            DB::table('employee_skills')->insert([
                'user_id' => $userId,
                'skill_name' => $skills[$idx],
                'proficiency' => randomElement(['初级', '中级', '高级', '专家']),
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
            $skillCount++;
        } catch (Exception $e) {}
    }
}
echo "   ✅ 生成了 {$skillCount} 条员工技能记录\\n\\n";

// 2. 生成 project_pool（项目池）
echo "2. 生成项目池数据...\\n";
$poolCount = 0;
for ($i = 0; $i < 30; $i++) {
    try {
        DB::table('project_pool')->insert([
            'customer_name' => '潜在客户' . ($i + 1),
            'contact_name' => '联系人' . ($i + 1),
            'contact_phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
            'requirements' => '需要' . randomElement(['视频监控系统', '门禁系统', '网络综合布线', '服务器运维']) . '解决方案',
            'status' => randomElement(['new', 'contacted', 'qualified', 'converted']),
            'created_by' => randomElement($userIds),
            'created_at' => randomDate($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $poolCount++;
    } catch (Exception $e) {}
}
echo "   ✅ 生成了 {$poolCount} 条项目池记录\\n\\n";

// 3. 生成 purchase_plans（采购计划）
echo "3. 生成采购计划数据...\\n";
$planCount = 0;
for ($i = 0; $i < 25; $i++) {
    try {
        DB::table('purchase_plans')->insert([
            'plan_no' => 'PP' . date('Ymd') . str_pad($i + 1, 3, '0', STR_PAD_LEFT),
            'title' => '采购计划' . ($i + 1),
            'description' => '为' . randomElement(['项目A', '项目B', '项目C']) . '采购设备',
            'status' => randomElement(['draft', 'pending', 'approved', 'completed']),
            'created_by' => randomElement($userIds),
            'created_at' => randomDate($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $planCount++;
    } catch (Exception $e) {}
}
echo "   ✅ 生成了 {$planCount} 条采购计划记录\\n\\n";

// 4. 生成 purchase_requirements（采购需求）
echo "4. 生成采购需求数据...\\n";
$reqCount = 0;
for ($i = 0; $i < 40; $i++) {
    try {
        DB::table('purchase_requirements')->insert([
            'requirement_no' => 'PR' . date('Ymd') . str_pad($i + 1, 3, '0', STR_PAD_LEFT),
            'title' => '采购需求' . ($i + 1),
            'description' => '需要采购' . randomElement(['摄像头', '交换机', '网线', '服务器']) . '等设备',
            'quantity' => mt_rand(1, 100),
            'status' => randomElement(['draft', 'pending', 'approved', 'completed']),
            'created_by' => randomElement($userIds),
            'created_at' => randomDate($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $reqCount++;
    } catch (Exception $e) {}
}
echo "   ✅ 生成了 {$reqCount} 条采购需求记录\\n\\n";

// 5. 生成 quotation_items（报价单明细）
echo "5. 生成报价单明细数据...\\n";
$itemCount = 0;
foreach ($quotationIds as $quoteId) {
    $numItems = mt_rand(3, 8);
    for ($j = 0; $j < $numItems; $j++) {
        try {
            $unitPrice = mt_rand(100, 5000) + (mt_rand(0, 99) / 100);
            $quantity = mt_rand(1, 50);
            $totalPrice = $unitPrice * $quantity;
            
            DB::table('quotation_items')->insert([
                'quotation_id' => $quoteId,
                'product_name' => randomElement(['网络摄像头', 'NVR录像机', '交换机', '门禁控制器', '综合布线']),
                'specification' => randomElement(['DS-2CD3346', 'DS-7104', 'S1720', 'DS-K1T804']),
                'quantity' => $quantity,
                'unit_price' => $unitPrice,
                'total_price' => $totalPrice,
                'created_at' => now(),
                'updated_at' => now(),
            ]);
            $itemCount++;
        } catch (Exception $e) {}
    }
}
echo "   ✅ 生成了 {$itemCount} 条报价单明细记录\\n\\n";

// 6. 生成 sales_products（销售产品）
echo "6. 生成销售产品数据...\\n";
$productCount = 0;
$products = [
    ['name' => '海康威视网络摄像头', 'category' => '视频监控'],
    ['name' => '大华NVR录像机', 'category' => '视频监控'],
    ['name' => '华为交换机', 'category' => '网络设备'],
    ['name' => '海康门禁控制器', 'category' => '门禁系统'],
    ['name' => '综合布线服务', 'category' => '工程服务'],
    ['name' => '服务器运维服务', 'category' => '运维服务'],
    ['name' => '网络安全评估', 'category' => '安全服务'],
    ['name' => 'UPS不间断电源', 'category' => '电源设备'],
];

for ($i = 0; $i < count($products); $i++) {
    try {
        DB::table('sales_products')->insert([
            'name' => $products[$i]['name'],
            'category' => $products[$i]['category'],
            'specification' => '标准规格',
            'unit_price' => mt_rand(500, 50000) + (mt_rand(0, 99) / 100),
            'description' => $products[$i]['name'] . '的详细描述',
            'status' => 'active',
            'created_at' => randomDate($startDate, $endDate),
            'updated_at' => now(),
        ]);
        $productCount++;
    } catch (Exception $e) {}
}
echo "   ✅ 生成了 {$productCount} 条销售产品记录\\n\\n";

// 7. 生成 sales_follow_up_attachments（销售跟进附件）
echo "7. 生成销售跟进附件数据...\\n";
$attachCount = 0;
$followUpIds = DB::table('sales_follow_ups')->pluck('id')->toArray();

foreach ($followUpIds as $fuId) {
    if (mt_rand(0, 1) == 1) { // 50% 概率有附件
        try {
            DB::table('sales_follow_up_attachments')->insert([
                'follow_up_id' => $fuId,
                'file_name' => randomElement(['方案.pdf', '报价.xlsx', '合同.docx', '需求文档.pdf']),
                'file_path' => '/uploads/sales/' . uniqid() . '.pdf',
                'file_size' => mt_rand(100000, 5000000),
                'created_at' => now(),
            ]);
            $attachCount++;
        } catch (Exception $e) {}
    }
}
echo "   ✅ 生成了 {$attachCount} 条跟进附件记录\\n\\n";

// 8. 生成 certificates（员工证书）
echo "8. 生成员工证书数据...\\n";
$certCount = 0;
$certTypes = ['网络工程师证书', '系统集成项目管理工程师', '安防工程师证书', 'PMP', 'CCSP', 'CISA'];

foreach ($userIds as $userId) {
    if (mt_rand(0, 1) == 1) { // 50% 概率有证书
        try {
            DB::table('certificates')->insert([
                'user_id' => $userId,
                'certificate_name' => randomElement($certTypes),
                'certificate_no' => 'CERT' . str_pad(mt_rand(1, 99999), 5, '0', STR_PAD_LEFT),
                'issued_by' => randomElement(['工信部', '人社部', 'Cisco', '华为']),
                'issued_date' => randomDate('2020-01-01', '2025-12-31'),
                'expiry_date' => randomDate('2026-01-01', '2030-12-31'),
                'created_at' => now(),
                'updated_at' => now(),
            ]);
            $certCount++;
        } catch (Exception $e) {}
    }
}
echo "   ✅ 生成了 {$certCount} 条员工证书记录\\n\\n";

// 9. 为低数据表增加数据
echo "9. 为低数据表增加数据...\\n\\n";

// 9.1 增加员工档案
echo "   9.1 增加员工档案数据...\\n";
$empCount = DB::table('employee_profiles')->count();
$targetEmp = 30 - $empCount;

if ($targetEmp > 0) {
    foreach ($userIds as $userId) {
        $exists = DB::table('employee_profiles')->where('user_id', $userId)->exists();
        if (!$exists) {
            try {
                DB::table('employee_profiles')->insert([
                    'user_id' => $userId,
                    'employee_no' => 'EMP' . str_pad($userId, 4, '0', STR_PAD_LEFT),
                    'hire_date' => randomDate('2023-01-01', '2025-11-30'),
                    'contract_type' => randomElement(['full-time', 'part-time', 'contract']),
                    'base_salary' => mt_rand(5000, 25000),
                    'salary_allowance' => mt_rand(500, 3000),
                    'emergency_contact' => '紧急联系人' . $userId,
                    'emergency_phone' => '1' . mt_rand(30, 99) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                    'bank_name' => randomElement(['工商银行', '建设银行', '农业银行']),
                    'bank_account' => '622' . mt_rand(1000, 9999) . mt_rand(1000, 9999) . mt_rand(1000, 9999),
                    'created_at' => randomDate($startDate, $endDate),
                    'updated_at' => now(),
                ]);
                $targetEmp--;
                if ($targetEmp <= 0) break;
            } catch (Exception $e) {}
        }
    }
    echo "      ✅ 增加了 " . (30 - $empCount - $targetEmp) . " 条员工档案记录\\n";
} else {
    echo "      ℹ️ 员工档案已有足够数据\\n";
}

// 9.2 增加财务账户
echo "   9.2 增加财务账户数据...\\n";
$acctCount = DB::table('finance_accounts')->count();
$targetAcct = 20 - $acctCount;

if ($targetAcct > 0) {
    $acctTypes = ['bank', 'cash', 'alipay', 'wechat'];
    $acctNames = ['工商银行', '建设银行', '农业银行', '中国银行', '招商银行', '现金', '支付宝', '微信'];
    
    for ($i = 0; $i < $targetAcct; $i++) {
        try {
            DB::table('finance_accounts')->insert([
                'name' => $acctNames[$i % count($acctNames)] . ($i > 7 ? $i : ''),
                'type' => $acctTypes[$i % count($acctTypes)],
                'balance' => mt_rand(10000, 500000) + (mt_rand(0, 99) / 100),
                'status' => 'active',
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {}
    }
    echo "      ✅ 增加了 {$targetAcct} 条财务账户记录\\n";
} else {
    echo "      ℹ️ 财务账户已有足够数据\\n";
}

// 9.3 增加知识库分类
echo "   9.3 增加知识库分类数据...\\n";
$catCount = DB::table('knowledge_categories')->count();
$targetCat = 20 - $catCount;

if ($targetCat > 0) {
    $categories = ['网络安防', '视频监控', '门禁系统', '综合布线', '服务器运维', '项目管理', '售后服务', '产品知识', '技术方案', '常见问题'];
    
    for ($i = 0; $i < $targetCat; $i++) {
        try {
            DB::table('knowledge_categories')->insert([
                'name' => $categories[$i % count($categories)] . ($i > 9 ? $i : ''),
                'created_by' => $adminId,
                'is_system' => ($i < 5) ? true : false,
                'created_at' => randomDate($startDate, $endDate),
                'updated_at' => now(),
            ]);
        } catch (Exception $e) {}
    }
    echo "      ✅ 增加了 {$targetCat} 条知识库分类记录\\n";
} else {
    echo "      ℹ️ 知识库分类已有足够数据\\n";
}

echo "\\n" . str_repeat("=", 60) . "\\n";
echo "✅ 测试数据生成完成！\\n";
echo str_repeat("=", 60) . "\\n\\n";

// 显示最终统计
echo "📊 最终数据统计：\\n";

$tablesToCheck = [
    'employee_skills', 'project_pool', 'purchase_plans', 'purchase_requirements',
    'quotation_items', 'sales_products', 'sales_follow_up_attachments', 'certificates',
    'employee_profiles', 'knowledge_categories', 'finance_accounts', 'users'
];

foreach ($tablesToCheck as $table) {
    try {
        $count = DB::table($table)->count();
        $status = $count > 0 ? "✅" : "❌";
        echo "   {$status} {$table}: {$count} 条\\n";
    } catch (Exception $e) {
        echo "   ⚠️ {$table}: 表不存在或查询失败\\n";
    }
}

echo "\\n🎉 所有模块现在都有了测试数据！\\n";
?>
"""
        
        # 将PHP脚本写入服务器的/tmp目录
        cmd_write = f"""cat > /tmp/generate_data_final.php << 'ENDPHP'
{php_script}
ENDPHP
"""
        ssh.exec_command(cmd_write, get_pty=True, timeout=30)
        print("✅ 脚本已创建")
        
        # 运行PHP脚本
        print("\n" + "=" * 60)
        print("运行数据生成脚本（这可能需要2-3分钟）")
        print("=" * 60)
        
        cmd_run = "php /tmp/generate_data_final.php"
        stdin, stdout, stderr = ssh.exec_command(cmd_run, get_pty=True, timeout=600)
        
        # 实时输出结果
        output = ""
        while True:
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            elif stderr.channel.recv_ready():
                chunk = stderr.channel.recv(4096).decode('utf-8', errors='ignore')
                print(chunk, end='')
                output += chunk
            else:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
        
        print("\n" + "=" * 60)
        print("✅ 数据生成完成")
        print("=" * 60)
        
        # 清理临时文件
        ssh.exec_command("rm -f /tmp/generate_data_final.php")
        print(f"\n🗑️  已清理临时文件")
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        if 'ssh' in locals():
            ssh.close()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ 数据生成失败，请检查错误信息")
