#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修正版 - 生成模拟数据（ENUM 值已修正）"""
import paramiko
import requests

SSH_HOST = '172.20.0.139'
SSH_USER = 'nbcy'
SSH_PASS = 'admin123'

def ssh_connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
    return ssh

# PHP seed script - 所有 ENUM 值已对齐数据库定义
PHP_SEED = r"""<?php
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
$total = 0; $success = 0;
function seed($label, $callback) {
    global $total, $success;
    $total++;
    try {
        $count = $callback();
        $success++;
        echo "  [OK] $label: $count\n";
    } catch (\Exception $e) {
        echo "  [ERR] $label: " . $e->getMessage() . "\n";
    }
}

// 1. 部门
echo "--- 1. 部门 ---\n";
seed('部门', function() {
    $data = [
        ['name'=>'总经理办公室','parent_id'=>null,'manager_id'=>1,'sort_order'=>1,'status'=>'active'],
        ['name'=>'工程部','parent_id'=>null,'manager_id'=>2,'sort_order'=>2,'status'=>'active'],
        ['name'=>'技术支持部','parent_id'=>null,'manager_id'=>4,'sort_order'=>3,'status'=>'active'],
        ['name'=>'销售部','parent_id'=>null,'manager_id'=>2,'sort_order'=>4,'status'=>'active'],
        ['name'=>'财务部','parent_id'=>null,'manager_id'=>1,'sort_order'=>5,'status'=>'active'],
        ['name'=>'行政人事部','parent_id'=>null,'manager_id'=>1,'sort_order'=>6,'status'=>'active'],
        ['name'=>'采购部','parent_id'=>null,'manager_id'=>2,'sort_order'=>7,'status'=>'active'],
        ['name'=>'施工一队','parent_id'=>2,'manager_id'=>3,'sort_order'=>1,'status'=>'active'],
        ['name'=>'施工二队','parent_id'=>2,'manager_id'=>3,'sort_order'=>2,'status'=>'active'],
        ['name'=>'维保组','parent_id'=>3,'manager_id'=>4,'sort_order'=>1,'status'=>'active'],
    ];
    Department::upsert($data, ['name']);
    return count($data);
});

seed('岗位', function() {
    $depts = Department::pluck('id','name')->toArray();
    $posList = [
        '总经理办公室'=>[['总经理',1],['副总经理',2]],
        '工程部'=>[['工程经理',1],['项目经理',2],['施工主管',3],['弱电工程师',4]],
        '技术支持部'=>[['技术经理',1],['技术主管',2],['维保工程师',3],['售后工程师',4]],
        '销售部'=>[['销售经理',1],['销售主管',2],['业务员',3]],
        '财务部'=>[['财务经理',1],['会计',2],['出纳',3]],
        '行政人事部'=>[['行政经理',1],['人事专员',2],['行政专员',2]],
        '采购部'=>[['采购经理',1],['采购专员',2]],
        '施工一队'=>[['队长',1],['组员',3]],
        '施工二队'=>[['队长',1],['组员',3]],
        '维保组'=>[['组长',1],['组员',2]],
    ];
    $c = 0;
    foreach($posList as $dn => $ps) {
        $did = $depts[$dn] ?? 1;
        foreach($ps as $p) {
            Position::firstOrCreate(['name'=>$p[0],'department_id'=>$did], [
                'level'=>$p[1],'description'=>$p[0],'status'=>'active','sort_order'=>$p[1]
            ]);
            $c++;
        }
    }
    return $c;
});

// 2. 员工 (20个)
echo "\n--- 2. 员工 ---\n";
seed('用户+档案', function() {
    $names = ['王强','李伟','张敏','赵磊','刘洋','陈静','杨帆','黄海','周婷','吴刚','孙亮','马超','朱丽','胡明','郭峰','林芳','何军','高洁','罗勇','梁志远'];
    $depts = Department::pluck('id')->toArray();
    $positions = Position::pluck('id','department_id')->toArray();
    $c = 0;
    foreach($names as $i => $name) {
        $did = $depts[($i+1) % count($depts)];
        $pid = $positions[$did] ?? Position::first()->id;
        $user = User::create([
            'name' => $name, 'username' => 'user' . ($i+6),
            'email' => 'u' . ($i+6) . '@oa.com',
            'phone' => '138' . str_pad(rand(10000000,99999999),8,'0'),
            'password' => Hash::make('admin123'),
            'department_id' => $did, 'position_id' => $pid,
            'status' => 'active', 'gender' => ($i%3==0)?'female':'male',
        ]);
        EmployeeProfile::create([
            'user_id' => $user->id,
            'employee_no' => 'EMP' . str_pad($i+6,4,'0',STR_PAD_LEFT),
            'hire_date' => now()->subDays(rand(30,730))->toDateString(),
            'contract_type' => ['fixed','open','trial'][rand(0,2)],
            'contract_start' => now()->subDays(rand(30,365))->toDateString(),
            'contract_end' => now()->addDays(rand(180,730))->toDateString(),
            'base_salary' => rand(5000,2000)*10+5000,
            'salary_allowance' => rand(500,3000),
            'emergency_contact' => '联系人'.$name,
            'emergency_phone' => '139' . str_pad(rand(10000000,99999999),8,'0'),
        ]);
        $c++;
    }
    return $c;
});

seed('技能+证书', function() {
    $skills = ['海康安装','大华调试','视频监控','门禁系统','报警系统','网络布线','综合布线','弱电施工','CAD设计','电气安装'];
    $cats = ['install','debug','network','maintain','other'];
    $c = 0;
    foreach($skills as $s) {
        $sk = SkillTag::firstOrCreate(['name'=>$s], ['category'=>$cats[array_rand($cats)],'color'=>'#409eff','description'=>$s]);
        $c++;
    }
    $employees = EmployeeProfile::all();
    $sids = SkillTag::pluck('id')->toArray();
    foreach($employees as $emp) {
        $n = rand(2,4);
        $sel = array_rand($sids, min($n, count($sids)));
        if (!is_array($sel)) $sel = [$sel];
        foreach($sel as $sid) {
            DB::table('employee_skills')->insertOrIgnore(['employee_profile_id'=>$emp->id,'skill_tag_id'=>$sids[$sid],'proficiency'=>rand(1,5),'created_at'=>now(),'updated_at'=>now()]);
            $c++;
        }
    }
    $certNames = ['低压电工证','弱电工程师证','安防工程师证','一级建造师','消防工程师证','网络工程师证'];
    foreach($employees as $emp) {
        if (rand(0,1)) continue;
        Certificate::create([
            'employee_profile_id'=>$emp->id,
            'certificate_name'=>$certNames[array_rand($certNames)],
            'certificate_no'=>'CERT'.rand(100000,999999),
            'issue_date'=>now()->subYears(rand(1,5))->toDateString(),
            'expire_date'=>now()->addDays(rand(-30,730))->toDateString(),
            'issuer'=>'培训机构','status'=>'valid','remind_days'=>30,
        ]);
        $c++;
    }
    return $c;
});

// 3. 客户
echo "\n--- 3. 客户 ---\n";
seed('客户+联系人+设备', function() {
    $customers = [
        ['瑞丰科技产业园','科技/互联网','vip','北京市朝阳区'],
        ['万达商业广场','商业地产','vip','北京市朝阳区'],
        ['恒大地产集团','房地产','vip','广州市天河区'],
        ['鹏程实验学校','教育','normal','合肥市蜀山区'],
        ['阳光医院','医疗健康','normal','合肥市庐阳区'],
        ['锦绣花园小区','物业管理','normal','合肥市包河区'],
        ['鼎盛制造有限公司','制造业','normal','南京市江宁区'],
        ['中鼎国际酒店','酒店餐饮','vip','厦门市思明区'],
        ['绿城物业服务集团','物业管理','normal','杭州市西湖区'],
        ['天安数码城','产业园区','normal','深圳市南山区'],
        ['国盛证券大厦','金融','vip','北京市西城区'],
        ['红星美凯龙商场','商业零售','normal','上海市普陀区'],
        ['博瑞生物医药园','医药','normal','南京市浦口区'],
        ['锦绣幼儿园','教育','normal','合肥市高新区'],
        ['通泰物流中心','物流仓储','normal','厦门市湖里区'],
    ];
    $userIds = User::where('id','>',5)->pluck('id')->toArray();
    $catEnum = ['vip','normal','potential'];
    $devTypes = ['camera','access_control','alarm','network','fire','other'];
    $devStatuses = ['normal','fault','maintaining'];
    $cids = [];
    foreach($customers as $cust) {
        $c = Customer::create([
            'name'=>$cust[0], 'credit_code'=>'91'.rand(100000,999999).'MA01'.strtoupper(substr(md5($cust[0]),0,6)),
            'industry'=>$cust[1], 'category'=>$catEnum[rand(0,2)],
            'province'=>'北京市','city'=>'北京市','district'=>$cust[3],'address'=>$cust[3],
            'longitude'=>116.4+rand(0,100)/100,'latitude'=>39.9+rand(0,100)/100,
            'tags'=>['安防',rand(0,1)?'VIP':'长期'],
            'source'=>['网络','转介绍','展会','电话'][rand(0,3)],
            'status'=>'active','assigned_user_id'=>$userIds[array_rand($userIds)],
        ]);
        $cids[] = $c->id;
        CustomerContact::create(['customer_id'=>$c->id,'name'=>'张经理','position'=>'工程部','phone'=>'139'.rand(10000000,99999999),'email'=>'zhang@cust.com','is_primary'=>true]);
        CustomerContact::create(['customer_id'=>$c->id,'name'=>'李总','position'=>'管理层','phone'=>'138'.rand(10000000,99999999),'email'=>'li@cust.com','is_primary'=>false]);
        $nd = rand(2,5);
        for($d=0;$d<$nd;$d++) {
            CustomerDevice::create([
                'customer_id'=>$c->id,
                'device_name'=>['海康高清摄像头','NVR录像机','门禁控制器','报警主机','可视对讲机','道闸'][$d%6],
                'device_type'=>$devTypes[$d%count($devTypes)],
                'brand'=>['海康威视','大华','霍尼韦尔'][rand(0,2)],
                'model'=>['DS-2CD2T47','DS-7608','ASI7213'][$d%3],
                'serial_number'=>'SN'.rand(100000,999999),
                'install_location'=>$cust[3].'号',
                'install_date'=>now()->subDays(rand(30,730))->toDateString(),
                'warranty_end'=>now()->addDays(rand(-30,730))->toDateString(),
                'status'=>$devStatuses[rand(0,2)],
            ]);
        }
    }
    return count($cids).' 客户';
});

seed('跟进记录', function() {
    $customers = Customer::all();
    $userIds = User::where('id','>',5)->pluck('id')->toArray();
    $types = ['visit','call','online','other'];
    $c = 0;
    foreach($customers as $cust) {
        $n = rand(2,5);
        for($i=0;$i<$n;$i++) {
            FollowUpRecord::create([
                'customer_id'=>$cust->id,'user_id'=>$userIds[array_rand($userIds)],
                'type'=>$types[array_rand($types)],
                'content'=>'与客户沟通安防系统需求，了解当前系统运行状况',
                'next_follow_up_date'=>now()->addDays(rand(3,14))->toDateString(),
                'next_follow_up_note'=>'跟进报价方案',
            ]);
            $c++;
        }
    }
    return $c;
});

// 4. 项目
echo "\n--- 4. 项目 ---\n";
seed('项目+合同+供应商', function() {
    $customers = Customer::inRandomOrder()->limit(12)->get();
    $users = User::where('id','>',2)->pluck('id')->toArray();
    $stages = ['initiation','inquiry','contract','purchase','construction','settlement','warranty'];
    $types = ['camera','access_control','alarm','comprehensive','network','cloud_platform'];
    $names = ['视频监控系统改造','门禁系统安装','报警系统升级','安防综合管理平台','停车场管理系统','可视对讲系统','周界防范系统','智能楼宇系统','消防报警联动','电子巡更系统','视频监控扩容','人脸识别门禁'];
    $prios = ['low','medium','high','urgent'];
    $count = 0;
    foreach($customers as $idx => $cust) {
        $stage = $stages[array_rand($stages)];
        $budget = rand(5,200)*10000;
        $startD = now()->subDays(rand(10,365));
        $endD = (clone $startD)->addDays(rand(30,180));
        $proj = Project::create([
            'project_no'=>'PRJ2025'.str_pad($idx+1,3,'0',STR_PAD_LEFT),
            'name'=>$cust->name.'-'.$names[$idx%count($names)],
            'customer_id'=>$cust->id,'type'=>$types[$idx%count($types)],
            'stage'=>$stage,
            'status'=>in_array($stage,['settlement','warranty'])?'completed':'in_progress',
            'description'=>$names[$idx%count($names)].'项目',
            'budget_device'=>$budget*0.5,'budget_material'=>$budget*0.15,
            'budget_labor'=>$budget*0.25,'budget_outsource'=>$budget*0.05,'budget_other'=>$budget*0.05,
            'progress'=>in_array($stage,['warranty'])?100:rand(10,95),
            'manager_id'=>$users[array_rand($users)],
            'start_date'=>$startD->toDateString(),'end_date'=>$endD->toDateString(),
            'actual_end_date'=>in_array($stage,['warranty','settlement'])?$endD->toDateString():null,
            'priority'=>$prios[rand(0,3)],
        ]);
        ProjectContract::create([
            'project_id'=>$proj->id,'contract_no'=>'HT'.date('Ymd').rand(100,999),
            'contract_amount'=>$budget,'payment_method'=>'分期付款',
            'contract_start'=>$startD->toDateString(),'contract_end'=>$endD->toDateString(),
            'status'=>'active','signed_at'=>$startD,
        ]);
        for($j=0;$j<rand(3,8);$j++) {
            ConstructionLog::create([
                'project_id'=>$proj->id,'user_id'=>$users[array_rand($users)],
                'work_date'=>$startD->copy()->addDays($j+1)->toDateString(),
                'weather'=>['晴','多云','阴','小雨'][rand(0,3)],
                'content'=>'完成前端设备安装'.($j+1),
                'problems'=>rand(0,1)?'部分线路需要调整':null,
                'solutions'=>rand(0,1)?'重新布线路由':null,
                'work_hours'=>rand(60,100)/10.0,
                'location'=>'施工现场'.($j+1).'区','status'=>'normal',
            ]);
        }
        $count++;
    }
    $suppliers = [['海康威视代理商','张经理','0571-88001234'],['大华股份代理商','李经理','0571-88005678'],['华为安防经销商','王经理','0755-28780000'],['线缆供应商','刘经理','021-54880000'],['辅材供应商','陈经理','0571-88990000'],['UPS电源供应商','杨经理','020-82480000']];
    foreach($suppliers as $s) {
        Supplier::create(['name'=>$s[0],'contact_person'=>$s[1],'phone'=>$s[2],'email'=>strtolower($s[1]).'@supplier.com','address'=>'供应商地址','category'=>['设备','辅材'][rand(0,1)],'rating'=>rand(3,5),'status'=>'active']);
    }
    return $count.' 项目, '.count($suppliers).' 供应商';
});

// 5. 售后服务
echo "\n--- 5. 售后服务 ---\n";
seed('工单+日志+维保', function() {
    $customers = Customer::inRandomOrder()->limit(10)->get();
    $users = User::where('id','>',2)->pluck('id')->toArray();
    $statuses = ['pending','assigned','in_progress','completed','confirmed','archived','cancelled'];
    $urgencies = ['normal','urgent','critical'];
    $faults = ['监控画面模糊','门禁无法刷卡','录像回放失败','报警系统误报','摄像头离线','NVR存储满','门禁控制器故障','对讲系统无声音','道闸不开','人脸识别失败','系统卡顿','网络断开'];
    $svcTypes = ['warranty','non_warranty','maintenance'];
    $count = 0;
    foreach($customers as $cust) {
        $n = rand(2,5);
        for($i=0;$i<$n;$i++) {
            $status = $statuses[array_rand($statuses)];
            $so = ServiceOrder::create([
                'order_no'=>'SO2025'.str_pad(rand(1,999),3,'0',STR_PAD_LEFT),
                'customer_id'=>$cust->id,
                'fault_description'=>$faults[array_rand($faults)],
                'urgency'=>$urgencies[array_rand($urgencies)],
                'service_type'=>$svcTypes[array_rand($svcTypes)],
                'status'=>$status,
                'assigned_to'=>$users[array_rand($users)],
                'assigned_at'=>in_array($status,['assigned','in_progress','completed','confirmed'])?now():null,
                'started_at'=>in_array($status,['in_progress','completed','confirmed'])?now()->subHours(rand(1,48)):null,
                'completed_at'=>in_array($status,['completed','confirmed'])?now()->subHours(rand(1,24)):null,
                'created_by'=>$users[array_rand($users)],
                'sla_hours'=>[4,8,24,48][array_rand([0,1,2,3])],
            ]);
            if (!in_array($status,['pending','cancelled'])) {
                ServiceOrderLog::create(['service_order_id'=>$so->id,'user_id'=>$users[array_rand($users)],'action'=>'assigned','content'=>'工单已派发']);
            }
            if (in_array($status,['in_progress','completed','confirmed'])) {
                ServiceOrderLog::create(['service_order_id'=>$so->id,'user_id'=>$users[array_rand($users)],'action'=>'started','content'=>'已到达现场开始处理','location'=>'客户现场']);
            }
            $count++;
        }
    }
    foreach($customers->take(5) as $cust) {
        MaintenanceContract::create([
            'contract_no'=>'WB'.date('Ymd').rand(100,999),'customer_id'=>$cust->id,
            'amount'=>rand(1,10)*10000,
            'start_date'=>now()->subMonths(rand(1,12))->toDateString(),
            'end_date'=>now()->addMonths(rand(1,12))->toDateString(),
            'inspection_frequency'=>['monthly','quarterly','semi_annual'][rand(0,2)],
            'scope'=>'安防设备年度维保','status'=>'active',
        ]);
    }
    return $count.' 工单, 5 维保合同';
});

// 6. 报销
echo "\n--- 6. 报销 ---\n";
seed('报销单+明细', function() {
    $users = User::where('id','>',5)->pluck('id')->toArray();
    $categories = ['travel','hospitality','office','transport','project_cost','other'];
    $descs = ['出差住宿费','客户招待用餐','采购办公用品','打车公交费','项目材料费','杂项费用'];
    $statuses = ['draft','submitted','approved','rejected','paid'];
    $count = 0;
    foreach($users as $uid) {
        $n = rand(1,4);
        for($i=0;$i<$n;$i++) {
            $ci = array_rand($categories);
            $amount = rand(100,5000);
            $status = $statuses[array_rand($statuses)];
            $claim = ExpenseClaim::create([
                'user_id'=>$uid,'category'=>$categories[$ci],
                'total_amount'=>$amount,'description'=>$descs[$ci],
                'status'=>$status,'approver_id'=>1,
                'approved_at'=>in_array($status,['approved','paid'])?now():null,
                'paid_amount'=>in_array($status,['paid'])?$amount:0,
                'paid_at'=>$status=='paid'?now():null,
            ]);
            $ni = rand(1,3);
            for($j=0;$j<$ni;$j++) {
                ExpenseItem::create([
                    'expense_claim_id'=>$claim->id,
                    'item_date'=>now()->subDays(rand(1,30))->toDateString(),
                    'description'=>$descs[$ci].($j+1),
                    'amount'=>round($amount/$ni,2),'category'=>$categories[$ci],
                ]);
            }
            $count++;
        }
    }
    return $count.' 报销单';
});

// 7. 车辆
echo "\n--- 7. 车辆 ---\n";
seed('车辆+保险+保养+使用', function() {
    $vehicles = [
        ['皖A12345','五菱','宏光','白色',58000],
        ['皖B56789','江淮','瑞风','白色',125000],
        ['皖C90123','丰田','卡罗拉','黑色',148000],
        ['皖D34567','金杯','海狮','白色',89000],
        ['皖E78901','比亚迪','宋PLUS','白色',156000],
    ];
    $userIds = User::pluck('id')->toArray();
    $deptIds = Department::pluck('id')->toArray();
    $fuelTypes = ['gas','diesel','electric','hybrid'];
    $vStatuses = ['normal','maintenance'];
    $vids = [];
    foreach($vehicles as $v) {
        $veh = Vehicle::create([
            'plate_no'=>$v[0],'brand'=>$v[1],'model'=>$v[2],'color'=>$v[3],
            'purchase_date'=>now()->subDays(rand(365,1095))->toDateString(),
            'purchase_price'=>$v[4],
            'department_id'=>$deptIds[array_rand($deptIds)],
            'responsible_user_id'=>$userIds[array_rand($userIds)],
            'status'=>$vStatuses[rand(0,1)],
            'vin'=>'LSVAU'.rand(100000,999999),
            'engine_no'=>'ENG'.rand(100000,999999),
            'seats'=>[5,7,5,9,5][count($vids)],
            'fuel_type'=>$fuelTypes[rand(0,3)],
        ]);
        $vids[] = $veh->id;
        VehicleInsurance::create(['vehicle_id'=>$veh->id,'insurance_company'=>'中国人保','policy_no'=>'PICC'.rand(100000,999999),'type'=>'交强险+商业险','premium'=>rand(2000,6000),'start_date'=>now()->toDateString(),'end_date'=>now()->addYear()->toDateString(),'status'=>'active']);
        VehicleMaintenanceRecord::create(['vehicle_id'=>$veh->id,'maintenance_type'=>'常规保养','mileage'=>rand(5000,30000),'cost'=>rand(300,2000),'maintenance_date'=>now()->subDays(rand(10,180))->toDateString(),'description'=>'更换机油机滤','next_maintenance_mileage'=>10000,'next_maintenance_date'=>now()->addMonths(6)->toDateString(),'handled_by'=>$userIds[array_rand($userIds)]]);
    }
    $reqStatuses = ['draft','submitted','approved','rejected','cancelled'];
    foreach($vids as $vid) {
        for($i=0;$i<rand(3,8);$i++) {
            $status = $reqStatuses[rand(0,4)];
            VehicleUsageRequest::create([
                'vehicle_id'=>$vid,'applicant_id'=>$userIds[array_rand($userIds)],
                'usage_date'=>now()->subDays(rand(1,30))->toDateString(),
                'start_time'=>'08:00','end_time'=>'18:00',
                'destination'=>['客户现场','公司','仓库','工地'][rand(0,3)],
                'purpose'=>'项目施工用车','passengers'=>rand(1,5),
                'self_drive'=>rand(0,1)?true:false,
                'status'=>$status,'approver_id'=>1,
                'approved_at'=>$status=='approved'?now():null,
                'actual_mileage'=>$status=='approved'?rand(20,200):null,
            ]);
        }
    }
    return count($vehicles).' 车辆';
});

// 8. 库存
echo "\n--- 8. 库存 ---\n";
seed('仓库+库存+出入库', function() {
    $userIds = User::pluck('id')->toArray();
    Warehouse::firstOrCreate(['code'=>'WH01'],['name'=>'主仓库','type'=>'main','address'=>'公司一楼','manager_id'=>$userIds[0],'status'=>'active']);
    Warehouse::firstOrCreate(['code'=>'WH02'],['name'=>'辅材仓库','type'=>'aftermarket','address'=>'公司二楼','manager_id'=>$userIds[1],'status'=>'active']);
    $warehouses = Warehouse::all();
    $items = [
        ['海康高清摄像头','DS-2CD2T47G2-L','安装',850,'台'],
        ['海康NVR录像机','DS-7608N-K2','调试',3200,'台'],
        ['大华门禁控制器','ASI7213Y','安装',1500,'台'],
        ['门禁读卡器','DAIC-MF','调试',280,'个'],
        ['报警主机','2316PLUS','维护',2100,'台'],
        ['红外对射探测器','PB-60','安装',450,'对'],
        ['网线CAT6','六类网线','network',380,'箱'],
        ['电源线RVV','2芯电源线','other',180,'卷'],
        ['PVC穿线管','PVC25','install',12,'根'],
        ['水晶头','RJ45','network',35,'盒'],
        ['摄像机支架','不锈钢支架','install',25,'个'],
        ['光纤跳线','SC-LC 3米','network',15,'条'],
        ['光纤收发器','单模百兆','network',120,'对'],
        ['交换机','16口千兆','network',680,'台'],
        ['UPS电源','1KVA在线式','other',1500,'台'],
        ['监控硬盘','4TB监控级','other',520,'块'],
    ];
    $count = 0;
    foreach($items as $item) {
        $stock = rand(5,100);
        InventoryItem::create([
            'name'=>$item[0],'code'=>'ITM'.str_pad($count+1,4,'0',STR_PAD_LEFT),
            'category'=>$item[2],'specification'=>$item[1],
            'unit'=>$item[3],'safety_stock'=>10,
            'current_stock'=>$stock,'cost_price'=>$item[4],
            'sell_price'=>round($item[4]*1.3,2),
            'warehouse_id'=>$warehouses->first()->id,
            'location'=>'A区'.rand(1,5).'排'.rand(1,10).'列',
            'has_serial'=>in_array($item[2],['install','debug','maintain']),
            'status'=>$stock<=10?'low_stock':'normal',
        ]);
        $count++;
    }
    $inventory = InventoryItem::all();
    $rc = 0;
    $srTypes = ['in','out','transfer','check'];
    foreach($inventory->take(10) as $inv) {
        for($j=0;$j<rand(1,4);$j++) {
            $qty = rand(1,10);
            StockRecord::create([
                'record_no'=>'SR'.date('Ymd').str_pad($rc+1,3,'0',STR_PAD_LEFT),
                'inventory_item_id'=>$inv->id,'warehouse_id'=>$warehouses->first()->id,
                'type'=>$srTypes[array_rand($srTypes)],'quantity'=>$qty,
                'remaining_stock'=>$inv->current_stock,
                'operator_id'=>$userIds[array_rand($userIds)],
                'remark'=>'库存操作记录',
            ]);
            $rc++;
        }
    }
    return $count.' 库存, '.$rc.' 出入库记录';
});

// 9. 财务
echo "\n--- 9. 财务 ---\n";
seed('应收应付', function() {
    $customers = Customer::inRandomOrder()->limit(8)->get();
    $suppliers = Supplier::inRandomOrder()->limit(4)->get();
    $projects = Project::inRandomOrder()->limit(3)->get();
    $projId = $projects->first() ? $projects->first()->id : null;
    $rc = 0;
    foreach($customers as $c) {
        $amount = rand(5,100)*10000;
        $received = rand(0,round($amount*0.8/10000))*10000;
        Receivable::create([
            'customer_id'=>$c->id,'project_id'=>$projId,
            'amount'=>$amount,'received_amount'=>$received,
            'remaining_amount'=>$amount-$received,
            'due_date'=>now()->addDays(rand(-30,90))->toDateString(),
            'received_date'=>$received>0?now()->subDays(rand(1,30))->toDateString():null,
            'status'=>($amount-$received)<=0?'paid':'partial',
        ]);
        $rc++;
    }
    foreach($suppliers as $s) {
        $amount = rand(2,50)*10000;
        $paid = rand(0,round($amount*0.7/10000))*10000;
        Payable::create([
            'supplier_id'=>$s->id,'project_id'=>$projId,
            'amount'=>$amount,'paid_amount'=>$paid,
            'remaining_amount'=>$amount-$paid,
            'due_date'=>now()->addDays(rand(-15,60))->toDateString(),
            'paid_date'=>$paid>0?now()->subDays(rand(1,30))->toDateString():null,
            'payment_term'=>'月结30天',
            'status'=>($amount-$paid)<=0?'paid':'partial',
        ]);
        $rc++;
    }
    return $rc;
});

// 10. 考勤
echo "\n--- 10. 考勤 ---\n";
seed('打卡+请假+加班', function() {
    $users = User::where('status','active')->where('id','>',5)->get();
    $leaveTypes = ['annual','personal','sick','marriage','other'];
    $compTypes = ['pay','leave'];
    $ac=0;$lc=0;$oc=0;
    for($d=29;$d>=0;$d--) {
        $date = now()->subDays($d);
        if ($date->isWeekend()) continue;
        foreach($users as $user) {
            if (rand(1,100)>85) continue;
            $hIn = rand(0,30); $mOut = rand(30,59);
            AttendanceRecord::create([
                'user_id'=>$user->id,'date'=>$date->toDateString(),
                'clock_in'=>$date->copy()->setTime(8,$hIn)->toDateTimeString(),
                'clock_in_location'=>'公司',
                'clock_in_lat'=>31.82+rand(0,100)/10000,
                'clock_in_lng'=>117.23+rand(0,100)/10000,
                'clock_out'=>$date->copy()->setTime(17,$mOut)->toDateTimeString(),
                'clock_out_location'=>'公司',
                'clock_out_lat'=>31.82+rand(0,100)/10000,
                'clock_out_lng'=>117.23+rand(0,100)/10000,
                'status'=>'normal','work_hours'=>8.0,
                'overtime_hours'=>rand(0,3)%2==0?0:rand(5,30)/10.0,
            ]);
            $ac++;
        }
    }
    foreach($users as $user) {
        if (rand(0,1)) continue;
        $n = rand(1,2);
        for($j=0;$j<$n;$j++) {
            LeaveRequest::create([
                'user_id'=>$user->id,'type'=>$leaveTypes[array_rand($leaveTypes)],
                'start_date'=>now()->subDays(rand(1,15))->toDateString(),
                'end_date'=>now()->subDays(rand(0,14))->toDateString(),
                'days'=>rand(1,5).'.0','reason'=>'个人事务需请假处理',
                'status'=>['pending','approved','rejected'][rand(0,2)],
                'approver_id'=>1,
            ]);
            $lc++;
        }
    }
    foreach($users->take(10) as $user) {
        if (rand(0,1)) continue;
        OvertimeRequest::create([
            'user_id'=>$user->id,
            'overtime_date'=>now()->subDays(rand(1,14))->toDateString(),
            'start_time'=>'18:00','end_time'=>['20:00','21:00','22:00'][rand(0,2)],
            'hours'=>[2.0,3.0,4.0][rand(0,2)],
            'reason'=>'项目紧急加班赶工',
            'compensation_type'=>$compTypes[rand(0,1)],
            'status'=>['pending','approved'][rand(0,1)],
            'approver_id'=>1,
        ]);
        $oc++;
    }
    return $ac.' 打卡, '.$lc.' 请假, '.$oc.' 加班';
});

// 11. 网盘
echo "\n--- 11. 网盘 ---\n";
seed('文件夹+文件', function() {
    $userIds = User::pluck('id')->toArray();
    $folders = [
        ['公司制度',null,true],['项目资料',null,true],['技术文档',null,true],['培训资料',null,true],
        ['项目管理流程',null,false],['财务制度',null,false],['安全规范',null,false],
    ];
    $fidMap = [];
    foreach($folders as $i=>$f) {
        $folder = DiskFolder::create(['parent_id'=>$f[1],'name'=>$f[0],'path'=>'/'.$f[0],'created_by'=>$userIds[array_rand($userIds)],'is_system'=>$f[2]]);
        $fidMap[$i] = $folder->id;
    }
    $fc = count($folders);
    $files = [
        ['安防工程设计规范.pdf',0,2048000,'pdf'],
        ['弱电施工标准.pdf',0,1536000,'pdf'],
        ['海康DS-2CD2T47安装手册.pdf',2,512000,'pdf'],
        ['大华门禁配置指南.pdf',2,768000,'pdf'],
        ['2025年度项目总结.xlsx',1,256000,'xlsx'],
        ['项目验收模板.docx',1,128000,'docx'],
        ['员工考勤管理制度.pdf',0,256000,'pdf'],
        ['NVR存储计算表.xlsx',2,64000,'xlsx'],
    ];
    foreach($files as $f) {
        DiskFile::create([
            'folder_id'=>$fidMap[$f[1]],'name'=>$f[0],'original_name'=>$f[0],
            'extension'=>$f[3],'mime_type'=>'application/octet-stream',
            'size'=>$f[2],'path'=>'/storage/disk/'.$f[0],
            'uploaded_by'=>$userIds[array_rand($userIds)],'version'=>1,
            'description'=>substr($f[0],0,-4),'is_starred'=>rand(0,1),
        ]);
        $fc++;
    }
    return $fc;
});

// 12. 知识库
echo "\n--- 12. 知识库 ---\n";
seed('分类+文章', function() {
    $catData = [
        ['安防基础知识',null,0],['设备安装',null,1],['故障排查',null,2],['项目管理',null,3],['行业标准',null,4],
        ['视频监控系统','安防基础知识',0],['门禁系统','安防基础知识',1],['报警系统','安防基础知识',2],
        ['摄像机安装规范','设备安装',0],['门禁安装指南','设备安装',1],
        ['监控画面故障排查','故障排查',0],['门禁故障排查','故障排查',1],
        ['弱电施工规范','行业标准',0],['GB50198标准解读','行业标准',1],
    ];
    $catMap = [];
    foreach($catData as $c) {
        $parent = ($c[1]!==null && isset($catMap[$c[1]])) ? $catMap[$c[1]] : null;
        $cat = KnowledgeCategory::create(['parent_id'=>$parent,'name'=>$c[0],'icon'=>'document','sort_order'=>$c[2],'description'=>$c[0]]);
        $catMap[$c[0]] = $cat->id;
    }
    $userIds = User::pluck('id')->toArray();
    $articles = [
        ['视频监控摄像机选型指南','视频监控系统','介绍安防项目中如何选择合适的摄像机类型'],
        ['NVR录像存储时间计算','视频监控系统','根据摄像机数量、分辨率、码流计算存储容量'],
        ['门禁系统布线规范','门禁系统','门禁控制器安装位置、通讯线缆布线要求'],
        ['报警系统调试步骤','报警系统','报警主机编程、防区设置、联动配置'],
        ['监控摄像头安装角度','摄像机安装规范','不同场景的摄像头最佳安装高度和角度'],
        ['海康威视平台配置','监控画面故障排查','iVMS平台添加设备、配置视频流等常见问题'],
        ['弱电工程验收标准','弱电施工规范','安防弱电工程验收的检查项目和测试方法'],
        ['项目成本控制方法','项目管理','安防工程项目成本构成及控制方法'],
        ['施工进度管理技巧','项目管理','如何制定施工计划、协调人员、控制工期'],
        ['GB50198条文解读','GB50198标准解读','民用闭路监视电视系统工程技术规范条文解读'],
    ];
    $ac = 0;
    foreach($articles as $a) {
        KnowledgeArticle::create([
            'category_id'=>$catMap[$a[1]]??1,'title'=>$a[0],
            'content'=>'<h2>'.$a[0].'</h2><p>'.$a[2].'</p><h3>一、概述</h3><p>本文档旨在为工程人员提供参考指导。</p><h3>二、详细说明</h3><p>具体技术细节和实施步骤请参考正文内容。</p><h3>三、注意事项</h3><p>施工过程中请注意安全规范。</p>',
            'author_id'=>$userIds[array_rand($userIds)],
            'tags'=>['安防','技术','规范'],'view_count'=>rand(10,500),'like_count'=>rand(0,50),
            'status'=>'published','published_at'=>now()->subDays(rand(1,180)),'summary'=>$a[2],
        ]);
        $ac++;
    }
    return count($catData).' 分类, '.$ac.' 文章';
});

// 13. 系统日志
echo "\n--- 13. 系统日志 ---\n";
seed('操作日志', function() {
    $userIds = User::pluck('id')->toArray();
    $logTypes = ['login','logout','operation','error','login_failed'];
    $actions = [
        ['login','auth'],['list','project'],['create','service_order'],['update','customer'],
        ['submit','expense'],['approve','leave'],['view','dashboard'],['create','inventory'],
    ];
    $c = 0;
    for($d=29;$d>=0;$d--) {
        $n = rand(3,10);
        for($j=0;$j<$n;$j++) {
            $a = $actions[array_rand($actions)];
            DB::table('system_logs')->insert([
                'user_id'=>$userIds[array_rand($userIds)],
                'type'=>$logTypes[array_rand($logTypes)],
                'module'=>$a[1],'action'=>$a[0],
                'description'=>$a[0].' '.$a[1],
                'ip'=>'192.168.1.'.rand(1,254),
                'user_agent'=>'Mozilla/5.0 (Windows NT 10.0)',
                'created_at'=>now()->subDays($d)->subHours(rand(8,18)),
                'updated_at'=>now()->subDays($d)->subHours(rand(8,18)),
            ]);
            $c++;
        }
    }
    return $c;
});

DB::statement('SET FOREIGN_KEY_CHECKS=1;');
echo "\n========================================\n";
echo "完成: $success/$total 项成功\n";
echo "========================================\n";
"""

print("连接服务器...")
ssh = ssh_connect()

# 先清空旧数据（保留用户和角色）
print("清空旧数据...")
stdin, stdout, stderr = ssh.exec_command(
    f"echo {SSH_PASS} | sudo -S bash -c 'cd /var/www/oa-api && php artisan tinker --execute=\"echo \\\"Cleaning...\\n\\\"; DB::statement(\\\"SET FOREIGN_KEY_CHECKS=0\\\"); DB::table(\\\"employee_profiles\\\")->truncate(); DB::table(\\\"employee_skills\\\")->truncate(); DB::table(\\\"certificates\\\")->truncate(); DB::table(\\\"departments\\\")->truncate(); DB::table(\\\"positions\\\")->truncate(); DB::table(\\\"customers\\\")->truncate(); DB::table(\\\"customer_contacts\\\")->truncate(); DB::table(\\\"customer_devices\\\")->truncate(); DB::table(\\\"follow_up_records\\\")->truncate(); DB::table(\\\"projects\\\")->truncate(); DB::table(\\\"project_contracts\\\")->truncate(); DB::table(\\\"construction_logs\\\")->truncate(); DB::table(\\\"suppliers\\\")->truncate(); DB::table(\\\"service_orders\\\")->truncate(); DB::table(\\\"service_order_logs\\\")->truncate(); DB::table(\\\"maintenance_contracts\\\")->truncate(); DB::table(\\\"expense_claims\\\")->truncate(); DB::table(\\\"expense_items\\\")->truncate(); DB::table(\\\"vehicles\\\")->truncate(); DB::table(\\\"vehicle_insurances\\\")->truncate(); DB::table(\\\"vehicle_maintenance_records\\\")->truncate(); DB::table(\\\"vehicle_usage_requests\\\")->truncate(); DB::table(\\\"warehouses\\\")->truncate(); DB::table(\\\"inventory_items\\\")->truncate(); DB::table(\\\"stock_records\\\")->truncate(); DB::table(\\\"receivables\\\")->truncate(); DB::table(\\\"payables\\\")->truncate(); DB::table(\\\"disk_folders\\\")->truncate(); DB::table(\\\"disk_files\\\")->truncate(); DB::table(\\\"knowledge_categories\\\")->truncate(); DB::table(\\\"knowledge_articles\\\")->truncate(); DB::table(\\\"attendance_records\\\")->truncate(); DB::table(\\\"leave_requests\\\")->truncate(); DB::table(\\\"overtime_requests\\\")->truncate(); DB::table(\\\"system_logs\\\")->truncate(); DB::statement(\\\"SET FOREIGN_KEY_CHECKS=1\\\"); DB::table(\\\"users\\\")->where(\\\"id\\\",\\\">\\\", 5)->delete(); echo \\\"Done\\n\\\";\"'",
    timeout=60
)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 上传并执行 seed 脚本
print("\n上传 seed 脚本...")
stdin, stdout, stderr = ssh.exec_command(f"echo {SSH_PASS} | sudo -S chown nbcy:nbcy /var/www/oa-api", timeout=10)
stdout.read()

sftp = ssh.open_sftp()
php_path = '/var/www/oa-api/seed_demo_data.php'
with sftp.open(php_path, 'w') as f:
    f.write(PHP_SEED)
sftp.close()
print("上传完成")

print("\n执行数据生成...")
stdin, stdout, stderr = ssh.exec_command(f"echo {SSH_PASS} | sudo -S bash -c 'cd /var/www/oa-api && php seed_demo_data.php'", timeout=120)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(out)
if err and 'Warning' in err:
    # 只显示非 warning 的错误
    for line in err.split('\n'):
        if line and 'Warning' not in line and 'PHP' not in line:
            print(f"ERR: {line}")

# 恢复权限
stdin, stdout, stderr = ssh.exec_command(f"echo {SSH_PASS} | sudo -S chown www-data:www-data /var/www/oa-api", timeout=10)
stdout.read()

ssh.close()

# 验证
print("\n" + "="*60)
print("验证数据...")
print("="*60)
r = requests.post('http://172.20.0.139:3001/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['data']['token']
    headers = {'Authorization': f'Bearer {token}'}
    endpoints = [
        ('GET','/api/employees','员工'),('GET','/api/customers','客户'),
        ('GET','/api/projects','项目'),('GET','/api/service-orders','售后'),
        ('GET','/api/expenses','报销'),('GET','/api/vehicles','车辆'),
        ('GET','/api/inventory','库存'),('GET','/api/finance/receivables','应收'),
        ('GET','/api/attendance/records?month=2026-06','考勤'),
        ('GET','/api/disk/folders','网盘'),('GET','/api/knowledge/categories','知识库'),
        ('GET','/api/departments','部门'),('GET','/api/finance/payables','应付'),
    ]
    print(f"{'模块':<8} {'状态':<6} {'数据量':<10}")
    print("-" * 40)
    for method, path, name in endpoints:
        try:
            url = f'http://172.20.0.139:3001{path}'
            r2 = requests.get(url, headers=headers, timeout=10)
            if r2.status_code == 200:
                data = r2.json()
                if isinstance(data, dict) and 'data' in data:
                    d = data['data']
                    if isinstance(d, dict) and 'total' in d:
                        cnt = d['total']
                    elif isinstance(d, list):
                        cnt = len(d)
                    else:
                        cnt = '?'
                else:
                    cnt = '?'
                print(f"{name:<8} 200   {str(cnt):<10}")
            else:
                print(f"{name:<8} {r2.status_code:<6} {'--':<10}")
        except Exception as e:
            print(f"{name:<8} ERR   {'--':<10}")

print("\n数据生成完成！")
