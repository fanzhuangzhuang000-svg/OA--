<?php
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
echo "=== START ===\n";

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use App\Models\User;
use App\Models\Department;
use App\Models\Position;
use App\Models\EmployeeProfile;
use App\Models\SkillTag;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\CustomerContact;
use App\Models\CustomerDevice;
use App\Models\FollowUpRecord;
use App\Models\Project;
use App\Models\ProjectContract;
use App\Models\Supplier;
use App\Models\ConstructionLog;
use App\Models\ServiceOrder;
use App\Models\ServiceOrderLog;
use App\Models\MaintenanceContract;
use App\Models\ExpenseClaim;
use App\Models\ExpenseItem;
use App\Models\Vehicle;
use App\Models\VehicleInsurance;
use App\Models\VehicleMaintenanceRecord;
use App\Models\VehicleUsageRequest;
use App\Models\Warehouse;
use App\Models\InventoryItem;
use App\Models\StockRecord;
use App\Models\Receivable;
use App\Models\Payable;
use App\Models\DiskFolder;
use App\Models\DiskFile;
use App\Models\KnowledgeCategory;
use App\Models\KnowledgeArticle;
use App\Models\AttendanceRecord;
use App\Models\LeaveRequest;
use App\Models\OvertimeRequest;

$ok = 0;
$er = 0;

function seed($label, $fn) {
    global $ok, $er;
    try {
        $c = $fn();
        $ok++;
        echo "  [OK] $label: $c\n";
    } catch (\Exception $e) {
        $er++;
        echo "  [ERR] $label: " . $e->getMessage() . "\n";
    }
}

// ========== 1. 部门 + 岗位 ==========
echo "--- 1. 部门/岗位 ---\n";
seed('部门', function() {
    $depts = [
        ['总经理办公室', null, 1], ['工程部', null, 2], ['技术支持部', null, 3],
        ['销售部', null, 4], ['财务部', null, 5], ['行政人事部', null, 6],
        ['采购部', null, 7], ['施工一队', 2, 1], ['施工二队', 2, 2], ['维保组', 3, 3],
    ];
    foreach ($depts as $d) {
        Department::create(['name' => $d[0], 'parent_id' => $d[1], 'manager_id' => $d[2], 'sort_order' => $d[2], 'status' => 'active']);
    }
    return count($depts);
});

seed('岗位', function() {
    $dm = Department::pluck('id', 'name')->toArray();
    $positions = [
        '总经理办公室' => [['总经理', 1], ['副总经理', 2]],
        '工程部' => [['工程经理', 1], ['项目经理', 2], ['施工主管', 3], ['弱电工程师', 4]],
        '技术支持部' => [['技术经理', 1], ['技术主管', 2], ['维保工程师', 3]],
        '销售部' => [['销售经理', 1], ['销售主管', 2], ['业务员', 3]],
        '财务部' => [['财务经理', 1], ['会计', 2], ['出纳', 3]],
        '行政人事部' => [['行政经理', 1], ['人事专员', 2]],
        '采购部' => [['采购经理', 1], ['采购专员', 2]],
        '施工一队' => [['队长', 1], ['组员', 3]],
        '施工二队' => [['队长', 1], ['组员', 3]],
        '维保组' => [['组长', 1], ['组员', 2]],
    ];
    $c = 0;
    foreach ($positions as $deptName => $posList) {
        $did = $dm[$deptName] ?? 1;
        foreach ($posList as $p) {
            Position::create(['name' => $p[0], 'department_id' => $did, 'level' => $p[1], 'status' => 'active', 'sort_order' => $p[1]]);
            $c++;
        }
    }
    return $c;
});

// ========== 2. 员工 ==========
echo "--- 2. 员工 ---\n";
seed('用户+档案', function() {
    $names = ['王强','李伟','张敏','赵磊','刘洋','陈静','杨帆','黄海','周婷','吴刚','孙亮','马超','朱丽','胡明','郭峰','林芳','何军','高洁','罗勇','梁志远'];
    $deptIds = Department::pluck('id')->toArray();
    $cTypes = ['fixed', 'open', 'trial'];
    $count = 0;
    foreach ($names as $i => $name) {
        $did = $deptIds[($i + 1) % count($deptIds)];
        $user = User::create([
            'name' => $name, 'username' => 'user' . ($i + 6),
            'email' => 'u' . ($i + 6) . '@oa.com',
            'phone' => '138' . str_pad(rand(10000000, 99999999), 8, '0'),
            'password' => Hash::make('admin123'),
            'department_id' => $did, 'status' => 'active',
            'gender' => ($i % 3 == 0) ? 'female' : 'male',
        ]);
        EmployeeProfile::create([
            'user_id' => $user->id,
            'employee_no' => 'EMP' . str_pad($i + 6, 4, '0', STR_PAD_LEFT),
            'hire_date' => now()->subDays(rand(30, 730))->toDateString(),
            'contract_type' => $cTypes[rand(0, 2)],
            'contract_start' => now()->subDays(rand(30, 365))->toDateString(),
            'contract_end' => now()->addDays(rand(180, 730))->toDateString(),
            'base_salary' => rand(5000, 2000) * 10 + 5000,
            'salary_allowance' => rand(500, 3000),
            'emergency_contact' => '联系人',
            'emergency_phone' => '139' . str_pad(rand(10000000, 99999999), 8, '0'),
        ]);
        $count++;
    }
    return $count;
});

seed('技能+证书', function() {
    $cats = ['install', 'debug', 'network', 'maintain', 'other'];
    $skillNames = ['海康安装', '大华调试', '监控', '门禁', '报警', '布线', '弱电', 'CAD', '电气', '网络'];
    foreach ($skillNames as $s) {
        SkillTag::firstOrCreate(['name' => $s], ['category' => $cats[array_rand($cats)], 'color' => '#409eff']);
    }
    $employees = EmployeeProfile::all();
    $skillIds = SkillTag::pluck('id')->toArray();
    $c = 0;
    foreach ($employees as $emp) {
        $n = rand(2, 4);
        $sel = array_rand($skillIds, min($n, count($skillIds)));
        if (!is_array($sel)) $sel = [$sel];
        foreach ($sel as $sid) {
            DB::table('employee_skills')->insertOrIgnore(['employee_profile_id' => $emp->id, 'skill_tag_id' => $skillIds[$sid], 'proficiency' => rand(1, 5), 'created_at' => now(), 'updated_at' => now()]);
            $c++;
        }
    }
    $certNames = ['电工证', '弱电证', '消防证', '建造师'];
    foreach ($employees as $emp) {
        if (rand(0, 1)) continue;
        Certificate::create(['employee_profile_id' => $emp->id, 'certificate_name' => $certNames[rand(0, 3)], 'certificate_no' => 'C' . rand(100000, 999999), 'issue_date' => now()->subYears(rand(1, 5))->toDateString(), 'expire_date' => now()->addDays(rand(-30, 730))->toDateString(), 'issuer' => '培训机构', 'status' => 'valid', 'remind_days' => 30]);
        $c++;
    }
    return $c;
});

// ========== 3. 客户 ==========
echo "--- 3. 客户 ---\n";
seed('客户+联系人+设备', function() {
    $custData = [
        ['瑞丰科技产业园', '科技', 'vip'], ['万达商业广场', '地产', 'vip'], ['恒大地产集团', '房地产', 'vip'],
        ['鹏程实验学校', '教育', 'normal'], ['阳光医院', '医疗', 'normal'], ['锦绣花园小区', '物业', 'normal'],
        ['鼎盛制造有限公司', '制造', 'normal'], ['中鼎国际酒店', '酒店', 'vip'], ['绿城物业', '物业', 'normal'],
        ['天安数码城', '产业园', 'normal'], ['国盛证券大厦', '金融', 'vip'], ['红星美凯龙', '零售', 'normal'],
        ['博瑞生物', '医药', 'normal'], ['锦绣幼儿园', '教育', 'normal'], ['通泰物流', '物流', 'normal'],
    ];
    $userIds = User::where('id', '>', 5)->pluck('id')->toArray();
    $devTypes = ['camera', 'access_control', 'alarm', 'network', 'fire', 'other'];
    $devStatuses = ['normal', 'fault', 'maintaining'];
    $devNames = ['高清摄像头', 'NVR录像机', '门禁控制器', '报警主机', '对讲机'];
    $count = 0;
    foreach ($custData as $cd) {
        $cust = Customer::create([
            'name' => $cd[0], 'credit_code' => '91' . rand(100000, 999999) . 'AB',
            'industry' => $cd[1], 'category' => $cd[2],
            'province' => '北京市', 'city' => '北京市', 'district' => $cd[0], 'address' => $cd[0] . '地址',
            'tags' => ['安防'], 'source' => ['网络', '转介绍', '展会'][rand(0, 2)],
            'status' => 'active', 'assigned_user_id' => $userIds[array_rand($userIds)],
        ]);
        $count++;
        CustomerContact::create(['customer_id' => $cust->id, 'name' => '张经理', 'position' => '工程部', 'phone' => '139' . rand(10000000, 99999999), 'is_primary' => true]);
        CustomerContact::create(['customer_id' => $cust->id, 'name' => '李总', 'position' => '管理层', 'phone' => '138' . rand(10000000, 99999999), 'is_primary' => false]);
        for ($d = 0; $d < rand(2, 5); $d++) {
            CustomerDevice::create([
                'customer_id' => $cust->id, 'device_name' => $devNames[$d % 5],
                'device_type' => $devTypes[$d % 6], 'brand' => '海康', 'model' => 'DS-' . $d,
                'serial_number' => 'SN' . rand(100000, 999999), 'install_location' => '现场',
                'install_date' => now()->subDays(rand(30, 730))->toDateString(),
                'warranty_end' => now()->addDays(rand(-30, 730))->toDateString(),
                'status' => $devStatuses[rand(0, 2)],
            ]);
        }
    }
    return $count . ' 客户';
});

seed('跟进记录', function() {
    $customers = Customer::all();
    $userIds = User::where('id', '>', 5)->pluck('id')->toArray();
    $types = ['visit', 'call', 'online', 'other'];
    $c = 0;
    foreach ($customers as $cust) {
        for ($i = 0; $i < rand(2, 5); $i++) {
            FollowUpRecord::create(['customer_id' => $cust->id, 'user_id' => $userIds[array_rand($userIds)], 'type' => $types[array_rand($types)], 'content' => '沟通安防需求', 'next_follow_up_date' => now()->addDays(rand(3, 14))->toDateString(), 'next_follow_up_note' => '跟进方案']);
            $c++;
        }
    }
    return $c;
});

// ========== 4. 项目 ==========
echo "--- 4. 项目 ---\n";
seed('项目+合同+供应商', function() {
    $customers = Customer::inRandomOrder()->limit(12)->get();
    $userIds = User::where('id', '>', 2)->pluck('id')->toArray();
    $stages = ['initiation', 'inquiry', 'contract', 'purchase', 'construction', 'settlement', 'warranty'];
    $types = ['camera', 'access_control', 'alarm', 'comprehensive', 'network', 'cloud_platform'];
    $names = ['视频监控改造', '门禁系统安装', '报警系统升级', '综合安防平台', '停车场管理', '对讲系统', '周界防范', '智能楼宇', '消防联动', '巡更系统', '监控扩容', '人脸门禁'];
    $priorities = ['low', 'medium', 'high', 'urgent'];
    $count = 0;
    foreach ($customers as $idx => $cust) {
        $stage = $stages[array_rand($stages)];
        $budget = rand(5, 200) * 10000;
        $startDate = now()->subDays(rand(10, 365));
        $endDate = (clone $startDate)->addDays(rand(30, 180));
        $proj = Project::create([
            'project_no' => 'PRJ2025' . str_pad($count + 1, 3, '0', STR_PAD_LEFT),
            'name' => $cust->name . '-' . $names[$idx % 12],
            'customer_id' => $cust->id, 'type' => $types[$idx % 6], 'stage' => $stage,
            'status' => in_array($stage, ['settlement', 'warranty']) ? 'completed' : 'in_progress',
            'budget_device' => $budget * 0.5, 'budget_material' => $budget * 0.15,
            'budget_labor' => $budget * 0.25, 'budget_outsource' => $budget * 0.05, 'budget_other' => $budget * 0.05,
            'progress' => in_array($stage, ['warranty']) ? 100 : rand(10, 95),
            'manager_id' => $userIds[array_rand($userIds)],
            'start_date' => $startDate->toDateString(), 'end_date' => $endDate->toDateString(),
            'actual_end_date' => in_array($stage, ['warranty', 'settlement']) ? $endDate->toDateString() : null,
            'priority' => $priorities[rand(0, 3)],
        ]);
        ProjectContract::create(['project_id' => $proj->id, 'contract_no' => 'HT' . date('Ymd') . rand(100, 999), 'contract_amount' => $budget, 'payment_method' => 'installment', 'contract_start' => $startDate->toDateString(), 'contract_end' => $endDate->toDateString(), 'status' => 'active', 'signed_at' => $startDate]);
        for ($j = 0; $j < rand(3, 6); $j++) {
            ConstructionLog::create(['project_id' => $proj->id, 'user_id' => $userIds[array_rand($userIds)], 'work_date' => $startDate->copy()->addDays($j + 1)->toDateString(), 'weather' => ['晴', '多云', '阴'][rand(0, 2)], 'content' => '完成安装' . ($j + 1), 'work_hours' => rand(6, 10) + 0.5]);
        }
        $count++;
    }
    $suppliers = [['海康代理商', '张经理', '0571-8001'], ['大华代理商', '李经理', '0571-8002'], ['线缆供应商', '刘经理', '021-8003'], ['辅材供应商', '陈经理', '0571-8004'], ['UPS供应商', '杨经理', '020-8005']];
    foreach ($suppliers as $s) {
        Supplier::create(['name' => $s[0], 'contact_person' => $s[1], 'phone' => $s[2], 'category' => ['设备', '辅材'][rand(0, 1)], 'rating' => rand(3, 5), 'status' => 'active']);
    }
    return $count . ' 项目';
});

// ========== 5. 售后 ==========
echo "--- 5. 售后 ---\n";
seed('工单+维保', function() {
    $customers = Customer::inRandomOrder()->limit(10)->get();
    $userIds = User::where('id', '>', 2)->pluck('id')->toArray();
    $statuses = ['pending', 'assigned', 'in_progress', 'completed', 'confirmed', 'archived', 'cancelled'];
    $urgencies = ['normal', 'urgent', 'critical'];
    $faults = ['画面模糊', '无法刷卡', '回放失败', '误报', '离线', '存储满', '控制器故障', '无声音', '道闸不开', '识别失败', '卡顿', '断网'];
    $svcTypes = ['warranty', 'non_warranty', 'maintenance'];
    $count = 0;
    foreach ($customers as $cust) {
        for ($i = 0; $i < rand(2, 5); $i++) {
            $status = $statuses[array_rand($statuses)];
            $so = ServiceOrder::create([
                'order_no' => 'SO' . date('Ymd') . str_pad($count + 1, 3, '0', STR_PAD_LEFT),
                'customer_id' => $cust->id, 'fault_description' => $faults[array_rand($faults)],
                'urgency' => $urgencies[array_rand($urgencies)], 'service_type' => $svcTypes[array_rand($svcTypes)],
                'status' => $status, 'assigned_to' => $userIds[array_rand($userIds)],
                'assigned_at' => in_array($status, ['assigned', 'in_progress', 'completed', 'confirmed']) ? now() : null,
                'started_at' => in_array($status, ['in_progress', 'completed', 'confirmed']) ? now()->subHours(rand(1, 48)) : null,
                'completed_at' => in_array($status, ['completed', 'confirmed']) ? now()->subHours(rand(1, 24)) : null,
                'created_by' => $userIds[array_rand($userIds)], 'sla_hours' => [4, 8, 24, 48][rand(0, 3)],
            ]);
            if (!in_array($status, ['pending', 'cancelled'])) {
                ServiceOrderLog::create(['service_order_id' => $so->id, 'user_id' => $userIds[array_rand($userIds)], 'action' => 'assigned', 'content' => '已派发']);
            }
            if (in_array($status, ['in_progress', 'completed', 'confirmed'])) {
                ServiceOrderLog::create(['service_order_id' => $so->id, 'user_id' => $userIds[array_rand($userIds)], 'action' => 'started', 'content' => '到达现场']);
            }
            $count++;
        }
    }
    foreach ($customers->take(5) as $cust) {
        MaintenanceContract::create(['contract_no' => 'WB' . date('Ymd') . rand(100, 999), 'customer_id' => $cust->id, 'amount' => rand(1, 10) * 10000, 'start_date' => now()->subMonths(rand(1, 12))->toDateString(), 'end_date' => now()->addMonths(rand(1, 12))->toDateString(), 'inspection_frequency' => ['monthly', 'quarterly', 'biannual'][rand(0, 2)], 'scope' => '安防维保', 'status' => 'active']);
    }
    return $count . ' 工单';
});

// ========== 6. 报销 ==========
echo "--- 6. 报销 ---\n";
seed('报销', function() {
    $userIds = User::where('id', '>', 5)->pluck('id')->toArray();
    $categories = ['travel', 'hospitality', 'office', 'transport', 'project_cost', 'other'];
    $descs = ['住宿费', '招待费', '办公费', '交通费', '材料费', '其他'];
    $statuses = ['draft', 'submitted', 'approved', 'rejected', 'paid'];
    $count = 0;
    foreach ($userIds as $uid) {
        for ($i = 0; $i < rand(1, 4); $i++) {
            $ci = array_rand($categories);
            $amount = rand(100, 5000);
            $status = $statuses[array_rand($statuses)];
            $claim = ExpenseClaim::create(['user_id' => $uid, 'category' => $categories[$ci], 'total_amount' => $amount, 'description' => $descs[$ci], 'status' => $status, 'approver_id' => 1, 'approved_at' => in_array($status, ['approved', 'paid']) ? now() : null, 'paid_amount' => $status == 'paid' ? $amount : 0, 'paid_at' => $status == 'paid' ? now() : null]);
            for ($j = 0; $j < rand(1, 3); $j++) {
                ExpenseItem::create(['expense_claim_id' => $claim->id, 'item_date' => now()->subDays(rand(1, 30))->toDateString(), 'description' => $descs[$ci], 'amount' => round($amount / rand(1, 3), 2), 'category' => $categories[$ci]]);
            }
            $count++;
        }
    }
    return $count;
});

// ========== 7. 车辆 ==========
echo "--- 7. 车辆 ---\n";
seed('车辆', function() {
    $userIds = User::pluck('id')->toArray();
    $deptIds = Department::pluck('id')->toArray();
    $fuels = ['gas', 'diesel', 'electric', 'hybrid'];
    $vehicles = [['皖A12345', '五菱', '宏光', 58000], ['皖B56789', '江淮', '瑞风', 125000], ['皖C90123', '丰田', '卡罗拉', 148000], ['皖D34567', '金杯', '海狮', 89000], ['皖E78901', '比亚迪', '宋PLUS', 156000]];
    $vids = [];
    foreach ($vehicles as $v) {
        $veh = Vehicle::create(['plate_no' => $v[0], 'brand' => $v[1], 'model' => $v[2], 'color' => '白色', 'purchase_date' => now()->subDays(rand(365, 1095))->toDateString(), 'purchase_price' => $v[3], 'department_id' => $deptIds[array_rand($deptIds)], 'responsible_user_id' => $userIds[array_rand($userIds)], 'status' => 'normal', 'vin' => 'LSVAU' . rand(100000, 999999), 'engine_no' => 'E' . rand(100000, 999999), 'seats' => rand(5, 9), 'fuel_type' => $fuels[rand(0, 3)]]);
        $vids[] = $veh->id;
        VehicleInsurance::create(['vehicle_id' => $veh->id, 'insurance_company' => '中国人保', 'policy_no' => 'PICC' . rand(100000, 999999), 'type' => 'compulsory', 'premium' => rand(2000, 6000), 'start_date' => now()->toDateString(), 'end_date' => now()->addYear()->toDateString(), 'status' => 'active']);
        VehicleMaintenanceRecord::create(['vehicle_id' => $veh->id, 'maintenance_type' => 'routine', 'mileage' => rand(5000, 30000), 'cost' => rand(300, 2000), 'maintenance_date' => now()->subDays(rand(10, 180))->toDateString(), 'description' => '更换机油', 'handled_by' => $userIds[array_rand($userIds)]]);
    }
    foreach ($vids as $vid) {
        for ($i = 0; $i < rand(3, 8); $i++) {
            VehicleUsageRequest::create(['vehicle_id' => $vid, 'applicant_id' => $userIds[array_rand($userIds)], 'usage_date' => now()->subDays(rand(1, 30))->toDateString(), 'start_time' => '08:00', 'end_time' => '18:00', 'destination' => ['现场', '公司', '仓库', '工地'][rand(0, 3)], 'purpose' => '施工用车', 'passengers' => rand(1, 5), 'self_drive' => rand(0, 1) ? true : false, 'status' => ['pending', 'approved', 'rejected', 'using', 'returned'][rand(0, 4)], 'approver_id' => 1, 'actual_mileage' => rand(20, 200)]);
        }
    }
    return count($vehicles);
});

// ========== 8. 库存 ==========
echo "--- 8. 库存 ---\n";
seed('库存', function() {
    $userIds = User::pluck('id')->toArray();
    Warehouse::firstOrCreate(['code' => 'WH01'], ['name' => '主仓库', 'type' => 'main', 'address' => '一楼', 'manager_id' => $userIds[0], 'status' => 'active']);
    Warehouse::firstOrCreate(['code' => 'WH02'], ['name' => '辅材仓库', 'type' => 'aftermarket', 'address' => '二楼', 'manager_id' => $userIds[1], 'status' => 'active']);
    $wId = Warehouse::first()->id;
    $items = [
        ['海康摄像头', 'DS-2CD2T47G2', 'install', 850, '台'], ['NVR录像机', 'DS-7608N', 'debug', 3200, '台'],
        ['门禁控制器', 'ASI7213', 'install', 1500, '台'], ['读卡器', 'DAIC-MF', 'debug', 280, '个'],
        ['报警主机', '2316', 'maintain', 2100, '台'], ['红外探测器', 'PB-60', 'install', 450, '对'],
        ['网线CAT6', 'CAT6', 'network', 380, '箱'], ['电源线', 'RVV', 'other', 180, '卷'],
        ['PVC管', 'PVC25', 'install', 12, '根'], ['水晶头', 'RJ45', 'network', 35, '盒'],
        ['支架', '不锈钢', 'install', 25, '个'], ['光纤跳线', 'SC-LC', 'network', 15, '条'],
        ['收发器', '百兆', 'network', 120, '对'], ['交换机', '16口', 'network', 680, '台'],
        ['UPS', '1KVA', 'other', 1500, '台'], ['硬盘', '4TB', 'other', 520, '块'],
    ];
    $srTypes = ['in', 'out', 'transfer', 'check'];
    $count = 0;
    $srCounter = 0;
    foreach ($items as $item) {
        $stock = rand(5, 100);
        $ii = InventoryItem::create(['name' => $item[0], 'code' => 'ITM' . str_pad($count + 1, 4, '0', STR_PAD_LEFT), 'category' => $item[2], 'specification' => $item[1], 'unit' => $item[3], 'safety_stock' => 10, 'current_stock' => $stock, 'cost_price' => floatval($item[4]), 'sell_price' => round(floatval($item[4]) * 1.3, 2), 'warehouse_id' => $wId, 'location' => 'A' . rand(1, 5) . '-' . rand(1, 10), 'has_serial' => in_array($item[2], ['install', 'debug', 'maintain']), 'status' => $stock <= 10 ? 'inactive' : 'active']);
        for ($j = 0; $j < rand(1, 4); $j++) {
            $srCounter++;
            StockRecord::create(['record_no' => 'SR' . date('YmdHis') . str_pad($srCounter, 4, '0', STR_PAD_LEFT), 'inventory_item_id' => $ii->id, 'warehouse_id' => $wId, 'type' => $srTypes[array_rand($srTypes)], 'quantity' => rand(1, 10), 'remaining_stock' => $stock, 'operator_id' => $userIds[array_rand($userIds)]]);
        }
        $count++;
    }
    return $count;
});

// ========== 9. 财务 ==========
echo "--- 9. 财务 ---\n";
seed('应收应付', function() {
    $customers = Customer::inRandomOrder()->limit(8)->get();
    $suppliers = Supplier::inRandomOrder()->limit(4)->get();
    $projId = Project::first() ? Project::first()->id : null;
    $count = 0;
    foreach ($customers as $cust) {
        $amount = rand(5, 100) * 10000;
        $received = rand(0, round($amount * 0.8 / 10000)) * 10000;
        Receivable::create(['customer_id' => $cust->id, 'project_id' => $projId, 'amount' => $amount, 'received_amount' => $received, 'remaining_amount' => $amount - $received, 'due_date' => now()->addDays(rand(-30, 90))->toDateString(), 'received_date' => $received > 0 ? now()->subDays(rand(1, 30))->toDateString() : null, 'status' => ($amount - $received) <= 0 ? 'paid' : 'partial']);
        $count++;
    }
    foreach ($suppliers as $sup) {
        $amount = rand(2, 50) * 10000;
        $paid = rand(0, round($amount * 0.7 / 10000)) * 10000;
        Payable::create(['supplier_id' => $sup->id, 'project_id' => $projId, 'amount' => $amount, 'paid_amount' => $paid, 'remaining_amount' => $amount - $paid, 'due_date' => now()->addDays(rand(-15, 60))->toDateString(), 'paid_date' => $paid > 0 ? now()->subDays(rand(1, 30))->toDateString() : null, 'payment_term' => '月结30天', 'status' => ($amount - $paid) <= 0 ? 'paid' : 'partial']);
        $count++;
    }
    return $count;
});

// ========== 10. 考勤 ==========
echo "--- 10. 考勤 ---\n";
seed('考勤', function() {
    $users = User::where('status', 'active')->where('id', '>', 5)->get();
    $leaveTypes = ['annual', 'personal', 'sick', 'marriage', 'other'];
    $ac = 0; $lc = 0; $oc = 0;
    for ($d = 29; $d >= 0; $d--) {
        $date = now()->subDays($d);
        if ($date->isWeekend()) continue;
        foreach ($users as $user) {
            if (rand(1, 100) > 85) continue;
            AttendanceRecord::create(['user_id' => $user->id, 'date' => $date->toDateString(), 'clock_in' => $date->copy()->setTime(8, rand(0, 30))->toDateTimeString(), 'clock_in_location' => '公司', 'clock_out' => $date->copy()->setTime(17, rand(30, 59))->toDateTimeString(), 'clock_out_location' => '公司', 'status' => 'normal', 'work_hours' => 8.0, 'overtime_hours' => rand(0, 30) / 10.0]);
            $ac++;
        }
    }
    foreach ($users as $user) {
        if (rand(0, 1)) continue;
        for ($j = 0; $j < rand(1, 2); $j++) {
            LeaveRequest::create(['user_id' => $user->id, 'type' => $leaveTypes[array_rand($leaveTypes)], 'start_date' => now()->subDays(rand(1, 15))->toDateString(), 'end_date' => now()->subDays(rand(0, 14))->toDateString(), 'days' => rand(1, 5) . '.0', 'reason' => '个人事务', 'status' => ['pending', 'approved', 'rejected'][rand(0, 2)], 'approver_id' => 1]);
            $lc++;
        }
    }
    foreach ($users->take(10) as $user) {
        if (rand(0, 1)) continue;
        OvertimeRequest::create(['user_id' => $user->id, 'overtime_date' => now()->subDays(rand(1, 14))->toDateString(), 'start_time' => '18:00', 'end_time' => ['20:00', '21:00', '22:00'][rand(0, 2)], 'hours' => [2.0, 3.0, 4.0][rand(0, 2)], 'reason' => '项目加班', 'compensation_type' => ['pay', 'leave'][rand(0, 1)], 'status' => ['pending', 'approved'][rand(0, 1)], 'approver_id' => 1]);
        $oc++;
    }
    return "$ac 打卡, $lc 请假, $oc 加班";
});

// ========== 11. 网盘 ==========
echo "--- 11. 网盘 ---\n";
seed('网盘', function() {
    $userIds = User::pluck('id')->toArray();
    $count = 0;
    foreach (['公司制度', '项目资料', '技术文档', '培训资料', '安全管理'] as $nm) {
        DiskFolder::create(['name' => $nm, 'path' => '/' . $nm, 'created_by' => $userIds[array_rand($userIds)], 'is_system' => false]);
        $count++;
    }
    $fids = DiskFolder::pluck('id')->toArray();
    $files = [['安防设计规范.pdf', 0, 2e6], ['施工标准.pdf', 0, 1.5e6], ['海康安装手册.pdf', 2, 5e5], ['大华配置指南.pdf', 2, 7.5e5], ['项目总结.xlsx', 1, 2.5e5], ['验收模板.docx', 1, 1.3e5], ['考勤制度.pdf', 0, 2.5e5], ['NVR计算表.xlsx', 2, 6e4]];
    foreach ($files as $f) {
        DiskFile::create(['folder_id' => $fids[$f[1]] ?? $fids[0], 'name' => $f[0], 'original_name' => $f[0], 'extension' => substr(strrchr($f[0], '.'), 1), 'mime_type' => 'application/octet-stream', 'size' => $f[2], 'path' => '/storage/' . $f[0], 'uploaded_by' => $userIds[array_rand($userIds)], 'version' => 1, 'is_starred' => rand(0, 1)]);
        $count++;
    }
    return $count;
});

// ========== 12. 知识库 ==========
echo "--- 12. 知识库 ---\n";
seed('知识库', function() {
    $userIds = User::pluck('id')->toArray();
    $catData = [['安防基础', null], ['设备安装', null], ['故障排查', null], ['项目管理', null], ['行业标准', null], ['视频监控', '安防基础'], ['门禁系统', '安防基础'], ['报警系统', '安防基础'], ['安装规范', '设备安装'], ['故障诊断', '故障排查'], ['弱电规范', '行业标准']];
    $catMap = [];
    $count = 0;
    foreach ($catData as $cd) {
        $parent = ($cd[1] !== null && isset($catMap[$cd[1]])) ? $catMap[$cd[1]] : null;
        $cat = KnowledgeCategory::create(['parent_id' => $parent, 'name' => $cd[0], 'icon' => 'document', 'sort_order' => $count]);
        $catMap[$cd[0]] = $cat->id;
        $count++;
    }
    $articles = [['摄像机选型指南', '视频监控', '介绍安防项目摄像机选型方法'], ['存储时间计算', '视频监控', 'NVR容量计算方法'], ['布线技术要求', '门禁系统', '门禁布线技术规范'], ['报警主机配置', '报警系统', '报警主机编程配置流程'], ['安装高度角度', '安装规范', '最佳安装高度角度'], ['平台配置问题', '故障诊断', 'iVMS常见问题解决'], ['验收标准规范', '弱电规范', '弱电工程验收标准'], ['成本管控方法', '项目管理', '项目成本构成与控制'], ['施工工期控制', '项目管理', '施工计划制定与协调'], ['国标条文解读', '行业标准', 'GB50198标准解读']];
    foreach ($articles as $a) {
        KnowledgeArticle::create(['category_id' => $catMap[$a[1]] ?? 1, 'title' => $a[0], 'content' => '<h2>' . $a[0] . '</h2><p>' . $a[2] . '</p><p>详细技术内容请参考正文。</p>', 'author_id' => $userIds[array_rand($userIds)], 'tags' => ['安防', '技术'], 'view_count' => rand(10, 500), 'like_count' => rand(0, 50), 'status' => 'published', 'published_at' => now()->subDays(rand(1, 180)), 'summary' => $a[2]]);
        $count++;
    }
    return $count;
});

// ========== 13. 日志 ==========
echo "--- 13. 日志 ---\n";
seed('系统日志', function() {
    $userIds = User::pluck('id')->toArray();
    $types = ['login', 'logout', 'operation', 'login_failed'];
    $modules = ['auth', 'project', 'service', 'expense', 'dashboard'];
    $actions = ['login', 'view', 'create', 'update'];
    $count = 0;
    for ($d = 29; $d >= 0; $d--) {
        for ($j = 0; $j < rand(3, 10); $j++) {
            DB::table('system_logs')->insert(['user_id' => $userIds[array_rand($userIds)], 'type' => $types[array_rand($types)], 'module' => $modules[array_rand($modules)], 'action' => $actions[array_rand($actions)], 'description' => '操作记录', 'ip' => '192.168.1.' . rand(1, 254), 'user_agent' => 'Mozilla/5.0', 'created_at' => now()->subDays($d)->subHours(rand(8, 18))]);
            $count++;
        }
    }
    return $count;
});

echo "\n========================================\n";
echo "完成: $ok OK / $er ERR\n";
echo "========================================\n";
