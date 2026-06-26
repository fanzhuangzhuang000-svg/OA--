#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成完整模拟数据 - 上传 PHP 脚本到服务器执行
"""
import paramiko
import requests
import time

SSH_HOST = '172.20.0.139'
SSH_USER = 'nbcy'
SSH_PASS = 'admin123'
SUDO_PASS = 'admin123'

def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    return ssh

def run_cmd(ssh, cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(f'echo {SUDO_PASS} | sudo -S {cmd}', timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

def upload_file(ssh, local_path, remote_path):
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()

# PHP seed script content
PHP_SEED = r'''<?php
/**
 * 安防运维OA系统 - 完整模拟数据生成
 */
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

echo "=== 开始生成模拟数据 ===\n\n";

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
use App\Models\ContractPaymentNode;
use App\Models\Supplier;
use App\Models\PurchaseOrder;
use App\Models\PurchaseItem;
use App\Models\ConstructionLog;
use App\Models\ProjectMaterial;
use App\Models\ProjectSettlement;
use App\Models\ServiceOrder;
use App\Models\ServiceOrderLog;
use App\Models\ServiceOrderPart;
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

DB::statement('SET FOREIGN_KEY_CHECKS=0;');
$total = 0;
$success = 0;

function seed($label, $callback) {
    global $total, $success;
    $total++;
    try {
        $count = $callback();
        $success++;
        echo "  [OK] $label: $count 条\n";
    } catch (\Exception $e) {
        echo "  [ERR] $label: " . $e->getMessage() . "\n";
    }
}

// =============================================
// 1. 部门和岗位
// =============================================
echo "--- 1. 部门与岗位 ---\n";
seed('部门', function() {
    $data = [
        ['id'=>1, 'name'=>'总经理办公室', 'parent_id'=>null, 'manager_id'=>1, 'sort_order'=>1, 'status'=>'active', 'description'=>'公司最高管理层'],
        ['id'=>2, 'name'=>'工程部', 'parent_id'=>null, 'manager_id'=>2, 'sort_order'=>2, 'status'=>'active', 'description'=>'负责安防工程项目实施'],
        ['id'=>3, 'name'=>'技术支持部', 'parent_id'=>null, 'manager_id'=>4, 'sort_order'=>3, 'status'=>'active', 'description'=>'售后服务与技术支持'],
        ['id'=>4, 'name'=>'销售部', 'parent_id'=>null, 'manager_id'=>2, 'sort_order'=>4, 'status'=>'active', 'description'=>'市场拓展与客户维护'],
        ['id'=>5, 'name'=>'财务部', 'parent_id'=>null, 'manager_id'=>1, 'sort_order'=>5, 'status'=>'active', 'description'=>'财务管理与核算'],
        ['id'=>6, 'name'=>'行政人事部', 'parent_id'=>null, 'manager_id'=>1, 'sort_order'=>6, 'status'=>'active', 'description'=>'人事行政后勤管理'],
        ['id'=>7, 'name'=>'采购部', 'parent_id'=>null, 'manager_id'=>2, 'sort_order'=>7, 'status'=>'active', 'description'=>'设备采购与供应链管理'],
        ['id'=>8, 'name'=>'施工一队', 'parent_id'=>2, 'manager_id'=>3, 'sort_order'=>1, 'status'=>'active', 'description'=>'工程施工一组'],
        ['id'=>9, 'name'=>'施工二队', 'parent_id'=>2, 'manager_id'=>3, 'sort_order'=>2, 'status'=>'active', 'description'=>'工程施工二组'],
        ['id'=>10, 'name'=>'维保组', 'parent_id'=>3, 'manager_id'=>4, 'sort_order'=>1, 'status'=>'active', 'description'=>'日常维保服务'],
    ];
    Department::upsert($data, ['id']);
    return count($data);
});

seed('岗位', function() {
    $data = [];
    $positions = [
        '总经理办公室' => [['总经理','A'],['副总经理','B']],
        '工程部' => [['工程经理','A'],['项目经理','B'],['施工主管','C'],['施工员','D'],['弱电工程师','D']],
        '技术支持部' => [['技术经理','A'],['技术主管','B'],['维保工程师','C'],['售后工程师','D']],
        '销售部' => [['销售经理','A'],['销售主管','B'],['业务员','C']],
        '财务部' => [['财务经理','A'],['会计','B'],['出纳','C']],
        '行政人事部' => [['行政经理','A'],['人事专员','B'],['行政专员','B'],['前台','C']],
        '采购部' => [['采购经理','A'],['采购专员','B']],
        '施工一队' => [['队长','B'],['组员','D']],
        '施工二队' => [['队长','B'],['组员','D']],
        '维保组' => [['组长','B'],['组员','C']],
    ];
    $deptMap = [];
    foreach(Department::all() as $d) $deptMap[$d->name] = $d->id;
    $id = 1;
    foreach($positions as $deptName => $posList) {
        $deptId = $deptMap[$deptName] ?? 1;
        foreach($posList as $p) {
            $data[] = ['id'=>$id++, 'name'=>$p[0], 'department_id'=>$deptId, 'level'=>$p[1], 'description'=>$p[0], 'status'=>'active', 'sort_order'=>$id];
        }
    }
    Position::upsert($data, ['id']);
    return count($data);
});

// =============================================
// 2. 员工 (创建20个员工)
// =============================================
echo "\n--- 2. 员工 ---\n";
seed('用户+档案', function() {
    $names = [
        '王强','李伟','张敏','赵磊','刘洋','陈静','杨帆','黄海','周婷','吴刚',
        '孙亮','马超','朱丽','胡明','郭峰','林芳','何军','高洁','罗勇','梁志远',
    ];
    $deptIds = range(1, 10);
    $posMap = [];
    foreach(Position::all() as $p) {
        if (!isset($posMap[$p->department_id])) $posMap[$p->department_id] = [];
        $posMap[$p->department_id][] = $p->id;
    }
    $count = 0;
    foreach($names as $i => $name) {
        $deptId = $deptIds[($i + 1) % count($deptIds)];
        $posId = $posMap[$deptId][$i % count($posMap[$deptId])] ?? 1;
        $phone = '138' . str_pad(rand(10000000, 99999999), 8, '0');
        $userId = User::create([
            'name' => $name,
            'username' => 'user' . ($i + 6),
            'email' => strtolower($name) . ($i+6) . '@oa.com',
            'phone' => $phone,
            'password' => Hash::make('admin123'),
            'department_id' => $deptId,
            'position_id' => $posId,
            'status' => 'active',
            'gender' => ($i % 3 == 0) ? 'female' : 'male',
            'avatar' => null,
        ])->id;
        EmployeeProfile::create([
            'user_id' => $userId,
            'employee_no' => 'EMP' . str_pad($i + 6, 4, '0', STR_PAD_LEFT),
            'hire_date' => now()->subDays(rand(30, 730))->toDateString(),
            'contract_type' => ['fixed', 'permanent', 'probation'][rand(0,2)],
            'contract_start' => now()->subDays(rand(30, 365))->toDateString(),
            'contract_end' => now()->addDays(rand(180, 730))->toDateString(),
            'base_salary' => rand(5000, 2000) * 10 + 5000,
            'salary_allowance' => rand(500, 3000),
            'emergency_contact' => '应急联系人' . $name,
            'emergency_phone' => '139' . str_pad(rand(10000000, 99999999), 8, '0'),
        ]);
        $count++;
    }
    return $count;
});

seed('技能标签', function() {
    $skills = [
        ['海康威视','设备','blue',0],['大华','设备','red',1],['华为','设备','green',2],
        ['视频监控','技术','#409eff',3],['门禁系统','技术','#67c23a',4],['报警系统','技术','#e6a23c',5],
        ['网络布线','技术','#909399',6],['综合布线','技术','#b37feb',7],['弱电施工','技术','#36cfc9',8],
        ['CAD设计','软件','#ff7a45',9],['电气安装','技术','#ff4d4f',10],
    ];
    foreach($skills as $s) {
        SkillTag::firstOrCreate(['name'=>$s[0]], [
            'category'=>$s[1], 'color'=>$s[2], 'description'=>$s[0], 'sort_order'=>$s[3]
        ]);
    }
    // 给每个员工随机分配技能
    $employees = EmployeeProfile::all();
    $skillIds = SkillTag::pluck('id')->toArray();
    $count = 0;
    foreach($employees as $emp) {
        $n = rand(2, 5);
        $selected = array_rand($skillIds, min($n, count($skillIds)));
        if (!is_array($selected)) $selected = [$selected];
        foreach($selected as $sid) {
            DB::table('employee_skills')->insertOrIgnore([
                'employee_profile_id' => $emp->id,
                'skill_tag_id' => $skillIds[$sid],
                'proficiency' => rand(1, 5),
                'created_at' => now(), 'updated_at' => now(),
            ]);
            $count++;
        }
    }
    return $count;
});

seed('证书', function() {
    $certs = [
        '低压电工操作证','弱电工程师证','安防工程师证','一级建造师','消防工程师证',
        '网络工程师认证','安全生产许可证','质量管理体系认证',
    ];
    $employees = EmployeeProfile::all();
    $count = 0;
    foreach($employees as $emp) {
        if (rand(0, 1)) continue; // 50%概率
        $n = rand(1, 3);
        for($j=0; $j<$n; $j++) {
            Certificate::create([
                'employee_profile_id' => $emp->id,
                'certificate_name' => $certs[array_rand($certs)],
                'certificate_no' => 'CERT' . rand(100000, 999999),
                'issue_date' => now()->subYears(rand(1, 5))->toDateString(),
                'expire_date' => now()->addDays(rand(-30, 730))->toDateString(),
                'issuer' => '培训机构',
                'status' => 'valid',
                'remind_days' => 30,
            ]);
            $count++;
        }
    }
    return $count;
});

// =============================================
// 3. 客户
// =============================================
echo "\n--- 3. 客户 ---\n";
seed('客户+联系人+设备', function() {
    $customers = [
        ['瑞丰科技产业园','91110105MA01ABCDEF','科技/互联网','vip','北京市','朝阳区','建国路88号'],
        ['万达商业广场','91110108MA01BCDEFG','商业地产','vip','北京市','朝阳区','大望路1号'],
        ['恒大地产集团','91440106MA01CDEFAB','房地产','vip','广州市','天河区','天河路385号'],
        ['鹏程实验学校','91340100MA01DEFGHI','教育','normal','合肥市','蜀山区','长江西路666号'],
        ['阳光医院','91340100MA01EFGHJK','医疗健康','normal','合肥市','庐阳区','濉溪路120号'],
        ['锦绣花园小区','91340100MA01FGHIJK','物业管理','normal','合肥市','包河区','花园大道99号'],
        ['鼎盛制造有限公司','91320100MA01GHIJKL','制造业','normal','南京市','江宁区','科建路29号'],
        ['中鼎国际酒店','91350100MA01HIJKLM','酒店餐饮','vip','厦门市','思明区','鹭江道168号'],
        ['绿城物业服务集团','91330100MA01IJKLMN','物业管理','normal','杭州市','西湖区','文三路488号'],
        ['天安数码城','91440300MA01JKLMNO','产业园区','potential','深圳市','南山区','科发路8号'],
        ['国盛证券大厦','91110000MA01LMNOPQ','金融','vip','北京市','西城区','金融大街15号'],
        ['红星美凯龙商场','91310100MA01MNOPQR','商业零售','normal','上海市','普陀区','真北路1208号'],
        ['博瑞生物医药园','91320100MA01NOPQRS','医药','potential','南京市','浦口区','药谷大道88号'],
        ['锦绣幼儿园','91340100MA01OPQRST','教育','normal','合肥市','高新区','望江西路800号'],
        ['通泰物流中心','91350100MA01PQRSTU','物流仓储','normal','厦门市','湖里区','机场北路12号'],
    ];
    $userIds = User::where('id', '>', 5)->pluck('id')->toArray();
    $cids = [];
    foreach($customers as $c) {
        $cust = Customer::create([
            'name' => $c[0], 'credit_code' => $c[1], 'industry' => $c[2],
            'category' => $c[3], 'province' => $c[4], 'city' => $c[5],
            'district' => $c[6], 'address' => $c[6],
            'longitude' => 116.4 + rand(0, 100) / 100,
            'latitude' => 39.9 + rand(0, 100) / 100,
            'tags' => ['安防', rand(0,1) ? 'VIP' : '长期'],
            'source' => ['网络','转介绍','展会','电话'][rand(0,3)],
            'status' => 'active',
            'assigned_user_id' => $userIds[array_rand($userIds)],
            'description' => $c[0] . '安防系统项目客户',
        ]);
        $cids[] = $cust->id;
        // 联系人
        $contacts = [
            ['张经理','工程部','1390000'.rand(1000,9999)],
            ['李总','管理层','1380000'.rand(1000,9999)],
        ];
        foreach($contacts as $j => $ct) {
            CustomerContact::create([
                'customer_id' => $cust->id, 'name' => $ct[0], 'position' => $ct[1],
                'phone' => $ct[2], 'email' => strtolower($ct[0]) . '@'.$cust->name.'.com',
                'is_primary' => $j == 0, 'wechat' => 'wx_'.$ct[0],
            ]);
        }
        // 设备 (每个客户2-5台)
        $devices = [
            ['高清摄像头','摄像头','海康威视','DS-2CD2T47G2-L'],
            ['NVR录像机','录像设备','海康威视','DS-7608N-K2'],
            ['门禁控制器','门禁','大华','ASI7213Y'],
            ['报警主机','报警','霍尼韦尔','2316PLUS'],
            ['可视对讲机','对讲','安居宝','L7-200'],
            ['停车场道闸','停车场','捷顺','JSDZ042'],
        ];
        $nd = rand(2, 5);
        for($d=0; $d<$nd; $d++) {
            $dev = $devices[$d % count($devices)];
            CustomerDevice::create([
                'customer_id' => $cust->id, 'device_name' => $dev[0],
                'device_type' => $dev[1], 'brand' => $dev[2], 'model' => $dev[3],
                'serial_number' => 'SN'.rand(100000,999999),
                'install_location' => $c[5] . $c[6] . rand(1,50) . '号',
                'install_date' => now()->subDays(rand(30, 730))->toDateString(),
                'warranty_end' => now()->addDays(rand(-30, 730))->toDateString(),
                'status' => ['online','offline','maintenance'][rand(0,2)],
            ]);
        }
    }
    return count($cids) . ' 客户';
});

seed('跟进记录', function() {
    $customers = Customer::all();
    $userIds = User::where('id', '>', 5)->pluck('id')->toArray();
    $types = ['phone','visit','email','wechat','meeting'];
    $count = 0;
    foreach($customers as $c) {
        $n = rand(2, 6);
        for($i=0; $i<$n; $i++) {
            FollowUpRecord::create([
                'customer_id' => $c->id,
                'user_id' => $userIds[array_rand($userIds)],
                'type' => $types[array_rand($types)],
                'content' => '与客户沟通安防系统升级需求，了解当前系统运行状况',
                'next_follow_up_date' => now()->addDays(rand(3, 14))->toDateString(),
                'next_follow_up_note' => '跟进报价方案',
            ]);
            $count++;
        }
    }
    return $count;
});

// =============================================
// 4. 项目
// =============================================
echo "\n--- 4. 项目 ---\n";
seed('项目+合同+供应商', function() {
    $customers = Customer::inRandomOrder()->limit(12)->get();
    $users = User::where('id', '>', 2)->pluck('id')->toArray();
    $stages = ['initiation','inquiry','contract','purchase','construction','settlement','warranty'];
    $types = ['video','access','alarm','integration','parking','intercom'];
    $names = [
        '视频监控系统改造','门禁系统安装','报警系统升级','安防综合管理平台',
        '停车场管理系统','可视对讲系统','周界防范系统','智能楼宇系统',
        '消防报警联动','电子巡更系统','视频监控扩容','人脸识别门禁',
    ];
    $count = 0;
    foreach($customers as $idx => $cust) {
        $stage = $stages[array_rand($stages)];
        $budget = rand(5, 200) * 10000;
        $startD = now()->subDays(rand(10, 365));
        $endD = (clone $startD)->addDays(rand(30, 180));
        $proj = Project::create([
            'project_no' => 'PRJ2025' . str_pad($idx+1, 3, '0', STR_PAD_LEFT),
            'name' => $cust->name . '-' . $names[$idx % count($names)],
            'customer_id' => $cust->id,
            'type' => $types[$idx % count($types)],
            'stage' => $stage,
            'status' => in_array($stage, ['settlement','warranty']) ? 'completed' : 'active',
            'description' => $names[$idx % count($names)] . '项目施工',
            'budget_device' => $budget * 0.5,
            'budget_material' => $budget * 0.15,
            'budget_labor' => $budget * 0.25,
            'budget_outsource' => $budget * 0.05,
            'budget_other' => $budget * 0.05,
            'progress' => in_array($stage, ['warranty']) ? 100 : rand(10, 95),
            'manager_id' => $users[array_rand($users)],
            'start_date' => $startD->toDateString(),
            'end_date' => $endD->toDateString(),
            'actual_end_date' => in_array($stage, ['warranty','settlement']) ? $endD->toDateString() : null,
            'priority' => ['low','medium','high'][rand(0,2)],
        ]);
        // 合同
        ProjectContract::create([
            'project_id' => $proj->id,
            'contract_no' => 'HT' . date('Ymd') . rand(100, 999),
            'contract_amount' => $budget,
            'payment_method' => '分期付款',
            'contract_start' => $startD->toDateString(),
            'contract_end' => $endD->toDateString(),
            'status' => 'active',
            'signed_at' => $startD,
            'notes' => '合同条款详见附件',
        ]);
        // 施工日志
        for($j=0; $j<rand(3,8); $j++) {
            ConstructionLog::create([
                'project_id' => $proj->id,
                'user_id' => $users[array_rand($users)],
                'work_date' => $startD->addDays(rand(1,5))->toDateString(),
                'weather' => ['晴','多云','阴','小雨'][rand(0,3)],
                'content' => '完成前端设备安装' . ($j+1),
                'problems' => rand(0,1) ? '部分线路需要调整' : null,
                'solutions' => rand(0,1) ? '重新布线路由' : null,
                'photos' => null,
                'work_hours' => rand(6, 10) + 0.5,
                'location' => '施工现场' . ($j+1) . '区',
                'status' => 'normal',
            ]);
        }
        $count++;
    }
    // 供应商
    $suppliers = [
        ['海康威视代理商','张经理','0571-88001234'],
        ['大华股份代理商','李经理','0571-88005678'],
        ['华为安防经销商','王经理','0755-28780000'],
        ['正泰电器总代','赵经理','0577-62880000'],
        ['线缆供应商','刘经理','021-54880000'],
        ['UPS电源供应商','陈经理','020-82480000'],
        ['机柜支架供应商','杨经理','0512-62880000'],
        ['辅材供应商','黄经理','0571-88990000'],
    ];
    foreach($suppliers as $s) {
        Supplier::create([
            'name' => $s[0], 'contact_person' => $s[1], 'phone' => $s[2],
            'email' => strtolower($s[1]) . '@supplier.com', 'address' => '供应商地址',
            'category' => ['设备','辅材'][rand(0,1)], 'rating' => rand(3, 5), 'status' => 'active',
        ]);
    }
    return $count . ' 项目, ' . count($suppliers) . ' 供应商';
});

// =============================================
// 5. 售后服务工单
// =============================================
echo "\n--- 5. 售后服务 ---\n";
seed('工单+日志+维保合同', function() {
    $customers = Customer::inRandomOrder()->limit(10)->get();
    $users = User::where('id', '>', 2)->pluck('id')->toArray();
    $statuses = ['pending','assigned','in_progress','completed','confirmed','archived','cancelled'];
    $urgencies = ['normal','urgent','critical'];
    $faults = [
        '监控画面模糊','门禁无法刷卡','录像回放失败','报警系统误报',
        '摄像头离线','NVR存储满','门禁控制器故障','对讲系统无声音',
        '道闸不开','人脸识别失败','系统卡顿','网络连接断开',
    ];
    $serviceTypes = ['repair','maintenance','installation','inspection','upgrade'];
    $count = 0;
    foreach($customers as $cust) {
        $n = rand(2, 5);
        for($i=0; $i<$n; $i++) {
            $status = $statuses[array_rand($statuses)];
            $so = ServiceOrder::create([
                'order_no' => 'SO2025' . str_pad(rand(1,999), 3, '0', STR_PAD_LEFT),
                'customer_id' => $cust->id,
                'fault_description' => $faults[array_rand($faults)],
                'urgency' => $urgencies[array_rand($urgencies)],
                'service_type' => $serviceTypes[array_rand($serviceTypes)],
                'status' => $status,
                'assigned_to' => $users[array_rand($users)],
                'assigned_at' => in_array($status, ['assigned','in_progress','completed','confirmed']) ? now() : null,
                'started_at' => in_array($status, ['in_progress','completed','confirmed']) ? now()->subHours(rand(1,48)) : null,
                'completed_at' => in_array($status, ['completed','confirmed']) ? now()->subHours(rand(1,24)) : null,
                'created_by' => $users[array_rand($users)],
                'sla_hours' => [4, 8, 24, 48][array_rand([0,1,2,3])],
            ]);
            // 工单日志
            if (!in_array($status, ['pending','cancelled'])) {
                ServiceOrderLog::create([
                    'service_order_id' => $so->id,
                    'user_id' => $users[array_rand($users)],
                    'action' => 'assigned',
                    'content' => '工单已派发给技术人员',
                ]);
            }
            if (in_array($status, ['in_progress','completed','confirmed'])) {
                ServiceOrderLog::create([
                    'service_order_id' => $so->id,
                    'user_id' => $users[array_rand($users)],
                    'action' => 'started',
                    'content' => '已到达现场开始处理',
                    'location' => '客户现场',
                    'gps_lat' => 39.9 + rand(0, 100) / 100,
                    'gps_lng' => 116.4 + rand(0, 100) / 100,
                ]);
            }
            $count++;
        }
    }
    // 维保合同
    foreach($customers->take(5) as $cust) {
        MaintenanceContract::create([
            'contract_no' => 'WB' . date('Ymd') . rand(100, 999),
            'customer_id' => $cust->id,
            'amount' => rand(1, 10) * 10000,
            'start_date' => now()->subMonths(rand(1, 12))->toDateString(),
            'end_date' => now()->addMonths(rand(1, 12))->toDateString(),
            'inspection_frequency' => ['monthly','quarterly','semi_annual'][rand(0,2)],
            'scope' => '安防设备年度维保',
            'status' => 'active',
        ]);
    }
    return $count . ' 工单, 5 维保合同';
});

// =============================================
// 6. 报销
// =============================================
echo "\n--- 6. 报销 ---\n";
seed('报销单+明细', function() {
    $users = User::where('id', '>', 5)->pluck('id')->toArray();
    $categories = ['travel','hospitality','office','transport','project_cost','other'];
    $catNames = ['差旅费','招待费','办公费','交通费','项目成本','其他'];
    $descriptions = [
        '出差住宿费','客户招待用餐','采购办公用品','打车/公交费用','项目材料费','杂项费用',
    ];
    $statuses = ['pending','approved','rejected','cancelled'];
    $count = 0;
    foreach($users as $uid) {
        $n = rand(1, 4);
        for($i=0; $i<$n; $i++) {
            $ci = array_rand($categories);
            $amount = rand(100, 5000);
            $status = $statuses[array_rand($statuses)];
            $claim = ExpenseClaim::create([
                'user_id' => $uid,
                'category' => $categories[$ci],
                'total_amount' => $amount,
                'description' => $descriptions[$ci],
                'status' => $status,
                'approver_id' => 1,
                'approved_at' => $status == 'approved' ? now() : null,
                'paid_amount' => $status == 'approved' ? $amount : 0,
                'paid_at' => $status == 'approved' ? now()->addDays(rand(1,5)) : null,
            ]);
            // 明细
            $ni = rand(1, 3);
            for($j=0; $j<$ni; $j++) {
                ExpenseItem::create([
                    'expense_claim_id' => $claim->id,
                    'item_date' => now()->subDays(rand(1, 30))->toDateString(),
                    'description' => $descriptions[$ci] . ($j+1),
                    'amount' => round($amount / $ni, 2),
                    'category' => $categories[$ci],
                ]);
            }
            $count++;
        }
    }
    return $count . ' 报销单';
});

// =============================================
// 7. 车辆
// =============================================
echo "\n--- 7. 车辆 ---\n";
seed('车辆+保险+保养+使用', function() {
    $vehicles = [
        ['皖A·A1234','五菱','宏光','白色','2023-01-15',58000],
        ['皖A·B5678','江淮','瑞风','白色','2022-06-20',125000],
        ['皖A·C9012','丰田','卡罗拉','黑色','2021-09-10',148000],
        ['皖A·D3456','金杯','海狮','白色','2020-03-25',89000],
        ['皖A·E7890','比亚迪','宋PLUS','白色','2023-05-08',156000],
    ];
    $userIds = User::pluck('id')->toArray();
    $deptIds = Department::pluck('id')->toArray();
    $vids = [];
    foreach($vehicles as $v) {
        $veh = Vehicle::create([
            'plate_no' => $v[0], 'brand' => $v[1], 'model' => $v[2],
            'color' => $v[3], 'purchase_date' => $v[4], 'purchase_price' => $v[5],
            'department_id' => $deptIds[array_rand($deptIds)],
            'responsible_user_id' => $userIds[array_rand($userIds)],
            'status' => 'available', 'vin' => 'LSVAU'.rand(100000,999999),
            'engine_no' => 'ENG'.rand(100000,999999),
            'seats' => [5,7,5,9,5][count($vids)], 'fuel_type' => '汽油',
        ]);
        $vids[] = $veh->id;
        // 保险
        VehicleInsurance::create([
            'vehicle_id' => $veh->id, 'insurance_company' => '中国人保',
            'policy_no' => 'PICC' . rand(100000, 999999),
            'type' => '交强险+商业险', 'premium' => rand(2000, 6000),
            'start_date' => now()->toDateString(), 'end_date' => now()->addYear()->toDateString(),
            'status' => 'active',
        ]);
        // 保养记录
        VehicleMaintenanceRecord::create([
            'vehicle_id' => $veh->id, 'maintenance_type' => '常规保养',
            'mileage' => rand(5000, 30000), 'cost' => rand(300, 2000),
            'maintenance_date' => now()->subDays(rand(10, 180))->toDateString(),
            'description' => '更换机油机滤', 'next_maintenance_mileage' => 10000,
            'next_maintenance_date' => now()->addMonths(6)->toDateString(),
            'handled_by' => $userIds[array_rand($userIds)],
        ]);
    }
    // 使用申请记录
    foreach($vids as $vid) {
        $n = rand(3, 8);
        for($i=0; $i<$n; $i++) {
            $status = ['pending','approved','rejected','cancelled'][rand(0,3)];
            VehicleUsageRequest::create([
                'vehicle_id' => $vid,
                'applicant_id' => $userIds[array_rand($userIds)],
                'usage_date' => now()->subDays(rand(1, 30))->toDateString(),
                'start_time' => '08:00', 'end_time' => '18:00',
                'destination' => ['客户现场','公司','仓库','工地'][rand(0,3)],
                'purpose' => '项目施工用车',
                'passengers' => rand(1, 5),
                'self_drive' => rand(0, 1),
                'status' => $status,
                'approver_id' => 1,
                'approved_at' => $status == 'approved' ? now() : null,
                'actual_mileage' => $status == 'approved' ? rand(20, 200) : null,
                'start_mileage' => $status == 'approved' ? rand(10000, 50000) : null,
                'end_mileage' => $status == 'approved' ? rand(10000, 50200) : null,
            ]);
        }
    }
    return count($vehicles) . ' 车辆';
});

// =============================================
// 8. 库存
// =============================================
echo "\n--- 8. 库存 ---\n";
seed('仓库+库存+出入库', function() {
    $userIds = User::pluck('id')->toArray();
    // 仓库
    Warehouse::create(['name'=>'主仓库','code'=>'WH01','type'=>'main','address'=>'公司一楼','manager_id'=>$userIds[0],'status'=>'active','description'=>'主要设备存放仓库']);
    Warehouse::create(['name'=>'辅材仓库','code'=>'WH02','type'=>'auxiliary','address'=>'公司二楼','manager_id'=>$userIds[1],'status'=>'active','description'=>'线缆辅材仓库']);
    $warehouses = Warehouse::all();
    // 库存物品
    $items = [
        ['海康高清摄像头','DS-2CD2T47G2-L','摄像头','台',850],
        ['海康NVR录像机','DS-7608N-K2','录像设备','台',3200],
        ['大华门禁控制器','ASI7213Y','门禁','台',1500],
        ['门禁读卡器','DAIC-MF','门禁配件','个',280],
        ['报警主机','2316PLUS','报警设备','台',2100],
        ['红外对射探测器','PB-60','报警配件','对',450],
        ['网线(CAT6)','六类网线','线缆','箱',380],
        ['电源线 RVV2x1.5','2芯电源线','线缆','卷',180],
        ['PVC穿线管','PVC25','辅材','根',12],
        ['水晶头','RJ45','辅材','盒',35],
        ['摄像机支架','不锈钢支架','辅材','个',25],
        ['光纤跳线','SC-LC 3米','线缆','条',15],
        ['光纤收发器','单模百兆','网络设备','对',120],
        ['交换机','16口千兆','网络设备','台',680],
        ['UPS电源','1KVA在线式','电源设备','台',1500],
        ['监控硬盘','4TB监控级','存储','块',520],
    ];
    $count = 0;
    foreach($items as $item) {
        $stock = rand(5, 100);
        InventoryItem::create([
            'name' => $item[0], 'code' => 'ITM' . str_pad($count+1, 4, '0', STR_PAD_LEFT),
            'category' => $item[2], 'specification' => $item[1],
            'unit' => $item[3], 'safety_stock' => 10,
            'current_stock' => $stock, 'cost_price' => $item[4],
            'sell_price' => round($item[4] * 1.3, 2),
            'warehouse_id' => $warehouses->first()->id,
            'location' => 'A区'.rand(1,5).'排'.rand(1,10).'列',
            'has_serial' => in_array($item[2], ['摄像头','录像设备','门禁','报警设备']),
            'status' => $stock <= 10 ? 'low_stock' : 'normal',
        ]);
        $count++;
    }
    // 出入库记录
    $inventory = InventoryItem::all();
    $types = ['in','out','in','out','in'];
    $remarks = ['采购入库','项目领用','退货入库','项目领用','补货入库'];
    $rc = 0;
    foreach($inventory->take(10) as $inv) {
        for($j=0; $j<rand(1,4); $j++) {
            $type = $types[array_rand($types)];
            $qty = rand(1, 10);
            StockRecord::create([
                'record_no' => 'SR' . date('Ymd') . str_pad($rc+1, 3, '0', STR_PAD_LEFT),
                'inventory_item_id' => $inv->id,
                'warehouse_id' => $warehouses->first()->id,
                'type' => $type, 'quantity' => $qty,
                'remaining_stock' => $inv->current_stock,
                'operator_id' => $userIds[array_rand($userIds)],
                'remark' => $remarks[array_rand($remarks)],
            ]);
            $rc++;
        }
    }
    return $count . ' 库存, ' . $rc . ' 出入库记录';
});

// =============================================
// 9. 财务（应收应付）
// =============================================
echo "\n--- 9. 财务 ---\n";
seed('应收应付', function() {
    $customers = Customer::inRandomOrder()->limit(8)->get();
    $projects = Project::inRandomOrder()->limit(6)->get();
    $suppliers = Supplier::inRandomOrder()->limit(4)->get();
    $rc = 0;
    // 应收
    foreach($customers as $c) {
        $amount = rand(5, 100) * 10000;
        $received = rand(0, round($amount * 0.8 / 10000)) * 10000;
        Receivable::create([
            'customer_id' => $c->id,
            'project_id' => $projects->first() ? $projects->first()->id : null,
            'amount' => $amount,
            'received_amount' => $received,
            'remaining_amount' => $amount - $received,
            'due_date' => now()->addDays(rand(-30, 90))->toDateString(),
            'received_date' => $received > 0 ? now()->subDays(rand(1,30))->toDateString() : null,
            'status' => ($amount - $received) <= 0 ? 'paid' : 'partial',
        ]);
        $rc++;
    }
    // 应付
    foreach($suppliers as $s) {
        $amount = rand(2, 50) * 10000;
        $paid = rand(0, round($amount * 0.7 / 10000)) * 10000;
        Payable::create([
            'supplier_id' => $s->id,
            'project_id' => $projects->first() ? $projects->first()->id : null,
            'amount' => $amount,
            'paid_amount' => $paid,
            'remaining_amount' => $amount - $paid,
            'due_date' => now()->addDays(rand(-15, 60))->toDateString(),
            'paid_date' => $paid > 0 ? now()->subDays(rand(1,30))->toDateString() : null,
            'payment_term' => '月结30天',
            'status' => ($amount - $paid) <= 0 ? 'paid' : 'partial',
        ]);
        $rc++;
    }
    return $rc;
});

// =============================================
// 10. 考勤记录（最近30天）
// =============================================
echo "\n--- 10. 考勤 ---\n";
seed('打卡记录+请假+加班', function() {
    $users = User::where('status', 'active')->where('id', '>', 5)->get();
    $leaveTypes = ['annual','personal','sick','marriage','other'];
    $leaveNames = ['年假','事假','病假','婚假','其他'];
    $ac = 0; $lc = 0; $oc = 0;
    for($d = 29; $d >= 0; $d--) {
        $date = now()->subDays($d);
        if ($date->isWeekend()) continue; // 跳过周末
        foreach($users as $user) {
            // 80% 概率出勤
            if (rand(1, 100) > 80) continue;
            $clockIn = $date->copy()->setTime(8, rand(0, 30));
            $clockOut = $date->copy()->setTime(17, rand(30, 59));
            AttendanceRecord::create([
                'user_id' => $user->id,
                'date' => $date->toDateString(),
                'clock_in' => $clockIn->toDateTimeString(),
                'clock_in_location' => '公司',
                'clock_in_lat' => 31.82 + rand(0, 100) / 10000,
                'clock_in_lng' => 117.23 + rand(0, 100) / 10000,
                'clock_out' => $clockOut->toDateTimeString(),
                'clock_out_location' => '公司',
                'clock_out_lat' => 31.82 + rand(0, 100) / 10000,
                'clock_out_lng' => 117.23 + rand(0, 100) / 10000,
                'status' => 'normal',
                'work_hours' => 8.0,
                'overtime_hours' => rand(0, 3) % 2 == 0 ? 0 : rand(0.5, 3),
                'remark' => null,
            ]);
            $ac++;
        }
    }
    // 请假
    foreach($users as $user) {
        if (rand(0, 1)) continue;
        $n = rand(1, 2);
        for($j=0; $j<$n; $j++) {
            $li = array_rand($leaveTypes);
            $days = rand(1, 5) . '.0';
            LeaveRequest::create([
                'user_id' => $user->id,
                'type' => $leaveTypes[$li],
                'start_date' => now()->subDays(rand(1, 15))->toDateString(),
                'end_date' => now()->subDays(rand(0, 14))->toDateString(),
                'days' => $days,
                'reason' => '个人事务需请假处理',
                'status' => ['pending','approved','rejected'][rand(0,2)],
                'approver_id' => 1,
            ]);
            $lc++;
        }
    }
    // 加班
    foreach($users->take(10) as $user) {
        if (rand(0, 1)) continue;
        OvertimeRequest::create([
            'user_id' => $user->id,
            'overtime_date' => now()->subDays(rand(1, 14))->toDateString(),
            'start_time' => '18:00',
            'end_time' => ['20:00','21:00','22:00'][rand(0,2)],
            'hours' => [2.0, 3.0, 4.0][rand(0,2)],
            'reason' => '项目紧急加班赶工',
            'compensation_type' => ['pay','leave'][rand(0,1)],
            'status' => ['pending','approved'][rand(0,1)],
            'approver_id' => 1,
        ]);
        $oc++;
    }
    return $ac . ' 打卡, ' . $lc . ' 请假, ' . $oc . ' 加班';
});

// =============================================
// 11. 网盘
// =============================================
echo "\n--- 11. 网盘 ---\n";
seed('文件夹+文件', function() {
    $userIds = User::pluck('id')->toArray();
    $folders = [
        ['公司制度', null, true],
        ['项目资料', null, true],
        ['技术文档', null, true],
        ['培训资料', null, true],
        ['项目管理流程', 1, false],
        ['财务制度', 1, false],
        ['安全规范', 1, false],
        ['安防设计方案', 2, false],
        ['施工验收报告', 2, false],
        ['设备说明书', 3, false],
        ['安装调试手册', 3, false],
        ['新员工手册', 4, false],
        ['技术培训', 4, false],
    ];
    $fidMap = [];
    foreach($folders as $i => $f) {
        $folder = DiskFolder::create([
            'parent_id' => $f[1],
            'name' => $f[0],
            'path' => '/' . $f[0],
            'created_by' => $userIds[array_rand($userIds)],
            'is_system' => $f[2],
        ]);
        $fidMap[$i] = $folder->id;
    }
    $fc = count($folders);
    // 虚拟文件
    $files = [
        ['安防工程设计规范.pdf', 1, 2048000],
        ['弱电施工标准.pdf', 1, 1536000],
        ['海康DS-2CD2T47安装手册.pdf', 3, 512000],
        ['大华门禁系统配置指南.pdf', 3, 768000],
        ['2025年度项目总结.xlsx', 2, 256000],
        ['项目验收模板.docx', 2, 128000],
        ['海康iVMS配置手册.pdf', 3, 1024000],
        ['员工考勤管理制度.pdf', 1, 256000],
        ['报销审批流程.pdf', 1, 128000],
        ['NVR存储容量计算表.xlsx', 3, 64000],
    ];
    foreach($files as $f) {
        DiskFile::create([
            'folder_id' => $fidMap[$f[1]] ?? $fidMap[0],
            'name' => $f[0], 'original_name' => $f[0],
            'extension' => substr($f[0], strrpos($f[0], '.') + 1),
            'mime_type' => 'application/' . (str_contains($f[0], '.pdf') ? 'pdf' : (str_contains($f[0], '.xlsx') ? 'spreadsheet' : 'word')),
            'size' => $f[2],
            'path' => '/storage/disk/' . $f[0],
            'uploaded_by' => $userIds[array_rand($userIds)],
            'version' => 1,
            'description' => substr($f[0], 0, -4),
            'is_starred' => rand(0, 1),
        ]);
        $fc++;
    }
    return $fc;
});

// =============================================
// 12. 知识库
// =============================================
echo "\n--- 12. 知识库 ---\n";
seed('分类+文章', function() {
    $categories = [
        ['安防基础知识', null, 0],
        ['设备安装', null, 1],
        ['故障排查', null, 2],
        ['项目管理', null, 3],
        ['行业标准', null, 4],
        ['视频监控系统', '安防基础知识', 0],
        ['门禁系统', '安防基础知识', 1],
        ['报警系统', '安防基础知识', 2],
        ['摄像机安装规范', '设备安装', 0],
        ['门禁安装指南', '设备安装', 1],
        ['监控画面故障排查', '故障排查', 0],
        ['门禁故障排查', '故障排查', 1],
        ['弱电施工规范', '行业标准', 0],
        ['GB50198标准解读', '行业标准', 1],
    ];
    $catMap = [];
    foreach($categories as $c) {
        $parent = null;
        if ($c[1] !== null && isset($catMap[$c[1]])) {
            $parent = $catMap[$c[1]];
        }
        $cat = KnowledgeCategory::create([
            'parent_id' => $parent,
            'name' => $c[0],
            'icon' => 'document',
            'sort_order' => $c[2],
            'description' => $c[0] . '相关技术文档',
        ]);
        $catMap[$c[0]] = $cat->id;
    }
    $userIds = User::pluck('id')->toArray();
    $articles = [
        ['视频监控摄像机选型指南', '视频监控系统', '本文介绍安防项目中如何根据不同场景选择合适的摄像机类型，包括分辨率、镜头焦距、红外距离等参数的选择方法。'],
        ['NVR录像存储时间计算', '视频监控系统', '详细介绍如何根据摄像机数量、分辨率、码率等参数计算NVR所需的存储容量和存储天数。'],
        ['门禁系统布线规范', '门禁系统', '门禁控制器的安装位置选择、通讯线缆布线要求、电源供电方式等技术规范说明。'],
        ['报警系统调试步骤', '报警系统', '报警主机编程、防区设置、联动配置、测试方法等完整调试流程。'],
        ['监控摄像头安装角度', '摄像机安装规范', '不同安装位置（室内、室外、走廊、电梯）的摄像头最佳安装高度和角度建议。'],
        ['海康威视平台配置', '监控画面故障排查', 'iVMS平台添加设备、配置视频流、录像计划设置等常见问题排查。'],
        ['弱电工程验收标准', '弱电施工规范', '安防弱电工程验收的检查项目、质量标准和测试方法。'],
        ['GB50198-2011条文解读', 'GB50198标准解读', '民用闭路监视电视系统工程技术规范主要条文的详细解读。'],
        ['项目成本控制方法', '项目管理', '安防工程项目成本构成及控制方法，包括设备成本、人工成本、管理费用的管控。'],
        ['施工进度管理技巧', '项目管理', '如何制定施工计划、协调人员、控制工期的经验分享。'],
    ];
    $ac = 0;
    foreach($articles as $a) {
        KnowledgeArticle::create([
            'category_id' => $catMap[$a[1]] ?? 1,
            'title' => $a[0],
            'content' => '<h2>' . $a[0] . '</h2><p>' . $a[2] . '</p><p>这是一篇技术文档的详细内容，包含丰富的技术参数、安装步骤和注意事项。</p><h3>一、概述</h3><p>本文档旨在为工程人员提供参考指导。</p><h3>二、详细说明</h3><p>具体技术细节和实施步骤请参考正文内容。</p><h3>三、注意事项</h3><p>施工过程中请注意安全规范。</p>',
            'author_id' => $userIds[array_rand($userIds)],
            'tags' => ['安防', '技术', '规范'],
            'view_count' => rand(10, 500),
            'like_count' => rand(0, 50),
            'status' => 'published',
            'published_at' => now()->subDays(rand(1, 180)),
            'summary' => $a[2],
        ]);
        $ac++;
    }
    return count($categories) . ' 分类, ' . $ac . ' 文章';
});

// =============================================
// 13. 系统日志
// =============================================
echo "\n--- 13. 系统日志 ---\n";
seed('操作日志', function() {
    $userIds = User::pluck('id')->toArray();
    $actions = [
        ['用户登录','auth','login'],
        ['查看项目列表','project','list'],
        ['创建服务工单','service_order','create'],
        ['编辑客户信息','customer','update'],
        ['提交报销申请','expense','submit'],
        ['审批请假申请','leave','approve'],
        ['库存出库操作','inventory','out'],
        ['查看仪表盘','dashboard','view'],
    ];
    $count = 0;
    for($d = 29; $d >= 0; $d--) {
        $n = rand(3, 10);
        for($j=0; $j<$n; $j++) {
            $a = $actions[array_rand($actions)];
            DB::table('system_logs')->insert([
                'user_id' => $userIds[array_rand($userIds)],
                'module' => $a[1],
                'action' => $a[2],
                'description' => $a[0],
                'ip_address' => '192.168.1.' . rand(1, 254),
                'user_agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'created_at' => now()->subDays($d)->subHours(rand(8, 18)),
                'updated_at' => now()->subDays($d)->subHours(rand(8, 18)),
            ]);
            $count++;
        }
    }
    return $count;
});

DB::statement('SET FOREIGN_KEY_CHECKS=1;');

echo "\n========================================\n";
echo "完成: $success/$total 项全部成功\n";
echo "========================================\n";
''';

print("连接服务器...")
ssh = ssh_connect()
print("连接成功")

# 写入 PHP 脚本到 Laravel 目录
php_path = '/var/www/oa-api/seed_demo_data.php'
print(f"上传 PHP 脚本到 {php_path}...")
# 先修改权限
stdin, stdout, stderr = ssh.exec_command(f"echo {SUDO_PASS} | sudo -S chown nbcy:nbcy /var/www/oa-api", timeout=10)
stdout.read()
sftp = ssh.open_sftp()
with sftp.open(php_path, 'w') as f:
    f.write(PHP_SEED)
sftp.close()
print("上传完成")

# 执行
print("\n执行数据生成脚本...")
stdin, stdout, stderr = ssh.exec_command(f"echo {SUDO_PASS} | sudo -S bash -c 'cd /var/www/oa-api && php seed_demo_data.php'", timeout=120)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f"STDERR: {err}")

ssh.close()

# 验证数据
print("\n验证生成的数据...")
import requests
r = requests.post('http://172.20.0.139:3001/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['data']['token']
    headers = {'Authorization': f'Bearer {token}'}

    endpoints = [
        ('GET', '/api/employees', '员工'),
        ('GET', '/api/customers', '客户'),
        ('GET', '/api/projects', '项目'),
        ('GET', '/api/service-orders', '售后'),
        ('GET', '/api/expenses', '报销'),
        ('GET', '/api/vehicles', '车辆'),
        ('GET', '/api/inventory', '库存'),
        ('GET', '/api/finance/receivables', '应收'),
        ('GET', '/api/attendance/records', '考勤'),
        ('GET', '/api/disk/folders', '网盘'),
        ('GET', '/api/knowledge/categories', '知识库'),
    ]

    print(f"\n{'模块':<8} {'状态':<6} {'数据量':<10} 说明")
    print("-" * 50)
    for method, path, name in endpoints:
        try:
            url = f'http://172.20.0.139:3001{path}'
            if method == 'GET':
                r2 = requests.get(url, headers=headers, timeout=10)
            else:
                r2 = requests.post(url, headers=headers, timeout=10)
            if r2.status_code == 200:
                data = r2.json()
                if isinstance(data, dict) and 'data' in data:
                    d = data['data']
                    if isinstance(d, dict) and 'total' in d:
                        count = d['total']
                    elif isinstance(d, list):
                        count = len(d)
                    else:
                        count = '?'
                else:
                    count = '?'
                print(f"{name:<8} 200   {str(count):<10} OK")
            else:
                print(f"{name:<8} {r2.status_code:<6} {'--':<10} {r2.text[:40]}")
        except Exception as e:
            print(f"{name:<8} ERR   {'--':<10} {str(e)[:40]}")

print("\n数据生成完成！")
