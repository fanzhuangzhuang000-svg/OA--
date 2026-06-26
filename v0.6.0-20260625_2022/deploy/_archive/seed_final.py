#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终版 - 修正所有ENUM值并生成完整模拟数据"""
import paramiko, requests

SSH_HOST = '172.20.0.139'; SSH_USER = 'nbcy'; SSH_PASS = 'admin123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(f'echo {SSH_PASS} | sudo -S bash -c "{cmd}"', timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Step 1: Fix vehicle_insurance model table name (it's singular in DB)
print("[1] 修复 vehicle_insurance 模型表名...")
run("cd /var/www/oa-api && chown nbcy:nbcy .")
sftp = ssh.open_sftp()
# Read the model file
with sftp.open('/var/www/oa-api/app/Models/OtherModels.php', 'r') as f:
    model_content = f.read().decode('utf-8')
if "'vehicle_insurances'" in model_content:
    model_content = model_content.replace("'vehicle_insurances'", "'vehicle_insurance'")
    with sftp.open('/var/www/oa-api/app/Models/OtherModels.php', 'w') as f:
        f.write(model_content)
    print("  Fixed: vehicle_insurances -> vehicle_insurance")
else:
    print("  Already fixed or not found")

# Step 2: Clean all data tables
print("[2] 清空所有业务数据...")
clean_sql = """SET FOREIGN_KEY_CHECKS=0;
TRUNCATE employee_profiles; TRUNCATE employee_skills; TRUNCATE certificates;
TRUNCATE departments; TRUNCATE positions;
TRUNCATE customers; TRUNCATE customer_contacts; TRUNCATE customer_devices; TRUNCATE follow_up_records;
TRUNCATE projects; TRUNCATE project_contracts; TRUNCATE construction_logs;
TRUNCATE project_members; TRUNCATE suppliers; TRUNCATE purchase_orders; TRUNCATE purchase_items;
TRUNCATE service_orders; TRUNCATE service_order_logs; TRUNCATE service_order_parts;
TRUNCATE maintenance_contracts;
TRUNCATE expense_claims; TRUNCATE expense_items; TRUNCATE approval_records;
TRUNCATE vehicles; TRUNCATE vehicle_insurance; TRUNCATE vehicle_maintenance_records; TRUNCATE vehicle_usage_requests;
TRUNCATE warehouses; TRUNCATE inventory_items; TRUNCATE stock_records; TRUNCATE device_serial_numbers;
TRUNCATE receivables; TRUNCATE payables;
TRUNCATE disk_folders; TRUNCATE disk_files;
TRUNCATE knowledge_categories; TRUNCATE knowledge_articles;
TRUNCATE attendance_records; TRUNCATE leave_requests; TRUNCATE overtime_requests;
TRUNCATE system_logs; TRUNCATE notifications;
DELETE FROM users WHERE id > 5;
SET FOREIGN_KEY_CHECKS=1;
SELECT COUNT(*) as users_remaining FROM users;"""

with sftp.open('/tmp/clean_data.sql', 'w') as f:
    f.write(clean_sql)
sftp.close()

out = run("mysql -u debian-sys-maint -pFLMoJ1vJcWhapbMF oa_db < /tmp/clean_data.sql")
print(f"  Clean result: {out}")

# Step 3: Upload and run the fixed PHP seed
print("[3] 上传修正版 seed 脚本...")
PHP_SEED = r"""<?php
require_once __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();
echo "=== 开始 ===\n";
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

$ok=0;$err=0;
function S($n,$fn){global $ok,$err;try{$c=$fn();$ok++;echo"  OK $n: $c\n";}catch(\Exception$e){$err++;echo"  ERR $n: ".$e->getMessage()."\n";}}

// 1. 部门+岗位
echo "---1---\n";
S('部门',function(){
    $d=[['总经理办公室',null,1],['工程部',null,2],['技术支持部',null,3],['销售部',null,4],['财务部',null,5],['行政人事部',null,6],['采购部',null,7],['施工一队',2,1],['施工二队',2,2],['维保组',3,3]];
    foreach($d as $v) Department::create(['name'=>$v[0],'parent_id'=>$v[1],'manager_id'=>$v[2],'sort_order'=>$v[2],'status'=>'active']);
    return count($d);
});
S('岗位',function(){
    $dm=Department::pluck('id','name')->toArray();
    $ps=['总经理办公室'=>[['总经理',1],['副总经理',2]],'工程部'=>[['工程经理',1],['项目经理',2],['施工主管',3],['弱电工程师',4]],'技术支持部'=>[['技术经理',1],['技术主管',2],['维保工程师',3]],'销售部'=>[['销售经理',1],['销售主管',2],['业务员',3]],'财务部'=>[['财务经理',1],['会计',2],['出纳',3]],'行政人事部'=>[['行政经理',1],['人事专员',2]],'采购部'=>[['采购经理',1],['采购专员',2]],'施工一队'=>[['队长',1],['组员',3]],'施工二队'=>[['队长',1],['组员',3]],'维保组'=>[['组长',1],['组员',2]]];
    $c=0;foreach($ps as $dn=>$pl){$did=$dm[$dn]??1;foreach($pl as $p){Position::create(['name'=>$p[0],'department_id'=>$did,'level'=>$p[1],'status'=>'active','sort_order'=>$p[1]]);$c++;}}return $c;
});

// 2. 员工(20人)
echo "---2---\n";
S('用户+档案',function(){
    $names=['王强','李伟','张敏','赵磊','刘洋','陈静','杨帆','黄海','周婷','吴刚','孙亮','马超','朱丽','胡明','郭峰','林芳','何军','高洁','罗勇','梁志远'];
    $depts=Department::pluck('id')->toArray();
    $c=0;foreach($names as $i=>$nm){
        $did=$depts[($i+1)%count($depts)];
        $u=User::create(['name'=>$nm,'username'=>'user'.($i+6),'email'=>'u'.($i+6).'@oa.com','phone'=>'138'.str_pad(rand(10000000,99999999),8,'0'),'password'=>Hash::make('admin123'),'department_id'=>$did,'status'=>'active','gender'=>($i%3==0)?'female':'male']);
        EmployeeProfile::create(['user_id'=>$u->id,'employee_no'=>'EMP'.str_pad($i+6,4,'0',STR_PAD_LEFT),'hire_date'=>now()->subDays(rand(30,730))->toDateString(),'contract_type'=>['fixed','open','trial'][rand(0,2)],'contract_start'=>now()->subDays(rand(30,365))->toDateString(),'contract_end'=>now()->addDays(rand(180,730))->toDateString(),'base_salary'=>rand(5000,2000)*10+5000,'salary_allowance'=>rand(500,3000),'emergency_contact'=>$nm.'的紧急联系人','emergency_phone'=>'139'.str_pad(rand(10000000,99999999),8,'0')]);
        $c++;
    }return $c;
});
S('技能+证书',function(){
    $cats=['install','debug','network','maintain','other'];
    foreach(['海康安装','大华调试','监控','门禁','报警','布线','弱电','CAD','电气','网络'] as $s){
        SkillTag::create(['name'=>$s,'category'=>$cats[array_rand($cats)],'color'=>'#409eff','description'=>$s]);
    }
    $eps=EmployeeProfile::all();$sids=SkillTag::pluck('id')->toArray();$c=0;
    foreach($eps as $ep){$n=rand(2,4);$sel=array_rand($sids,min($n,count($sids)));if(!is_array($sel))$sel=[$sel];foreach($sel as $sid){DB::table('employee_skills')->insertOrIgnore(['employee_profile_id'=>$ep->id,'skill_tag_id'=>$sids[$sid],'proficiency'=>rand(1,5),'created_at'=>now(),'updated_at'=>now()]);$c++;}}
    foreach($eps as $ep){if(rand(0,1))continue;Certificate::create(['employee_profile_id'=>$ep->id,'certificate_name'=>['电工证','弱电证','消防证','建造师'][rand(0,3)],'certificate_no'=>'CERT'.rand(100000,999999),'issue_date'=>now()->subYears(rand(1,5))->toDateString(),'expire_date'=>now()->addDays(rand(-30,730))->toDateString(),'issuer'=>'培训机构','status'=>'valid','remind_days'=>30]);$c++;}
    return $c;
});

// 3. 客户(15)
echo "---3---\n";
S('客户+联系人+设备',function(){
    $custs=[['瑞丰科技产业园','科技','vip'],['万达商业广场','地产','vip'],['恒大地产集团','房地产','vip'],['鹏程实验学校','教育','normal'],['阳光医院','医疗','normal'],['锦绣花园小区','物业','normal'],['鼎盛制造有限公司','制造','normal'],['中鼎国际酒店','酒店','vip'],['绿城物业','物业','normal'],['天安数码城','产业园','normal'],['国盛证券大厦','金融','vip'],['红星美凯龙','零售','normal'],['博瑞生物','医药','normal'],['锦绣幼儿园','教育','normal'],['通泰物流','物流','normal']];
    $uids=User::where('id','>',5)->pluck('id')->toArray();
    $devT=['camera','access_control','alarm','network','fire','other'];
    $devS=['normal','fault','maintaining'];
    $cid=[];foreach($custs as $c){
        $cust=Customer::create(['name'=>$c[0],'credit_code'=>'91'.rand(100000,999999).'ABC','industry'=>$c[1],'category'=>$c[2],'province'=>'北京市','city'=>'北京市','district'=>$c[0],'address'=>$c[0].'地址','tags'=>['安防'],'source'=>['网络','转介绍','展会'][rand(0,2)],'status'=>'active','assigned_user_id'=>$uids[array_rand($uids)]]);
        $cid[]=$cust->id;
        CustomerContact::create(['customer_id'=>$cust->id,'name'=>'张经理','position'=>'工程部','phone'=>'139'.rand(10000000,99999999),'is_primary'=>true]);
        CustomerContact::create(['customer_id'=>$cust->id,'name'=>'李总','position'=>'管理层','phone'=>'138'.rand(10000000,99999999),'is_primary'=>false]);
        for($d=0;$d<rand(2,5);$d++) CustomerDevice::create(['customer_id'=>$cust->id,'device_name'=>['高清摄像头','NVR','门禁控制器','报警主机','对讲机'][$d%5],'device_type'=>$devT[$d%6],'brand'=>'海康','model'=>'DS-'.$d,'serial_number'=>'SN'.rand(100000,999999),'install_location'=>'现场','install_date'=>now()->subDays(rand(30,730))->toDateString(),'warranty_end'=>now()->addDays(rand(-30,730))->toDateString(),'status'=>$devS[rand(0,2)]]);
    }return count($cid);
});

// 4. 项目(12)
echo "---4---\n";
S('项目+合同+供应商',function(){
    $custs=Customer::inRandomOrder()->limit(12)->get();
    $uids=User::where('id','>',2)->pluck('id')->toArray();
    $stages=['initiation','inquiry','contract','purchase','construction','settlement','warranty'];
    $types=['camera','access_control','alarm','comprehensive','network','cloud_platform'];
    $names=['视频监控系统改造','门禁系统安装','报警系统升级','综合安防平台','停车场管理系统','对讲系统','周界防范','智能楼宇','消防报警联动','电子巡更','监控扩容','人脸门禁'];
    $prios=['low','medium','high','urgent'];
    $c=0;foreach($custs as $i=>$cust){
        $st=$stages[array_rand($stages)];$bd=rand(5,200)*10000;
        $sd=now()->subDays(rand(10,365));$ed=(clone $sd)->addDays(rand(30,180));
        $p=Project::create(['project_no'=>'PRJ2025'.str_pad($c+1,3,'0',STR_PAD_LEFT),'name'=>$cust->name.'-'.$names[$c%12],'customer_id'=>$cust->id,'type'=>$types[$c%6],'stage'=>$st,'status'=>in_array($st,['settlement','warranty'])?'completed':'in_progress','budget_device'=>$bd*0.5,'budget_material'=>$bd*0.15,'budget_labor'=>$bd*0.25,'budget_outsource'=>$bd*0.05,'budget_other'=>$bd*0.05,'progress'=>in_array($st,['warranty'])?100:rand(10,95),'manager_id'=>$uids[array_rand($uids)],'start_date'=>$sd->toDateString(),'end_date'=>$ed->toDateString(),'actual_end_date'=>in_array($st,['warranty','settlement'])?$ed->toDateString():null,'priority'=>$prios[rand(0,3)]]);
        ProjectContract::create(['project_id'=>$p->id,'contract_no'=>'HT'.date('Ymd').rand(100,999),'contract_amount'=>$bd,'payment_method'=>'installment','contract_start'=>$sd->toDateString(),'contract_end'=>$ed->toDateString(),'status'=>'active','signed_at'=>$sd]);
        for($j=0;$j<rand(3,6);$j++) ConstructionLog::create(['project_id'=>$p->id,'user_id'=>$uids[array_rand($uids)],'work_date'=>$sd->copy()->addDays($j+1)->toDateString(),'weather'=>['晴','多云','阴'][rand(0,2)],'content'=>'完成设备安装'.($j+1),'work_hours'=>rand(60,100)/10.0]);
        $c++;
    }
    [['海康代理商','张经理'],['大华代理商','李经理'],['线缆供应商','刘经理'],['辅材供应商','陈经理'],['UPS供应商','杨经理']]=null;
    foreach([['海康代理商','张经理','0571-88001234'],['大华代理商','李经理','0571-88005678'],['线缆供应商','刘经理','021-54880000'],['辅材供应商','陈经理','0571-88990000'],['UPS供应商','杨经理','020-82480000']] as $s) Supplier::create(['name'=>$s[0],'contact_person'=>$s[1],'phone'=>$s[2],'category'=>['设备','辅材'][rand(0,1)],'rating'=>rand(3,5),'status'=>'active']);
    return $c.' 项目';
});

// 5. 售后(40+工单)
echo "---5---\n";
S('售后工单+维保',function(){
    $custs=Customer::inRandomOrder()->limit(10)->get();
    $uids=User::where('id','>',2)->pluck('id')->toArray();
    $sts=['pending','assigned','in_progress','completed','confirmed','archived','cancelled'];
    $urgs=['normal','urgent','critical'];
    $faults=['监控画面模糊','门禁无法刷卡','录像回放失败','报警系统误报','摄像头离线','NVR存储满','门禁控制器故障','对讲无声音','道闸不开','人脸识别失败','系统卡顿','网络断开'];
    $svcT=['warranty','non_warranty','maintenance'];
    $c=0;foreach($custs as $cust){
        for($i=0;$i<rand(2,5);$i++){
            $st=$sts[array_rand($sts)];
            $so=ServiceOrder::create(['order_no'=>'SO2025'.str_pad(rand(1,999),3,'0',STR_PAD_LEFT),'customer_id'=>$cust->id,'fault_description'=>$faults[array_rand($faults)],'urgency'=>$urgs[array_rand($urgs)],'service_type'=>$svcT[array_rand($svcT)],'status'=>$st,'assigned_to'=>$uids[array_rand($uids)],'assigned_at'=>in_array($st,['assigned','in_progress','completed','confirmed'])?now():null,'started_at'=>in_array($st,['in_progress','completed','confirmed'])?now()->subHours(rand(1,48)):null,'completed_at'=>in_array($st,['completed','confirmed'])?now()->subHours(rand(1,24)):null,'created_by'=>$uids[array_rand($uids)],'sla_hours'=>[4,8,24,48][rand(0,3)]]);
            if(!in_array($st,['pending','cancelled'])) ServiceOrderLog::create(['service_order_id'=>$so->id,'user_id'=>$uids[array_rand($uids)],'action'=>'assigned','content'=>'工单已派发']);
            if(in_array($st,['in_progress','completed','confirmed'])) ServiceOrderLog::create(['service_order_id'=>$so->id,'user_id'=>$uids[array_rand($uids)],'action'=>'started','content'=>'已到达现场','location'=>'客户现场']);
            $c++;
        }
    }
    foreach($custs->take(5) as $cust) MaintenanceContract::create(['contract_no'=>'WB'.date('Ymd').rand(100,999),'customer_id'=>$cust->id,'amount'=>rand(1,10)*10000,'start_date'=>now()->subMonths(rand(1,12))->toDateString(),'end_date'=>now()->addMonths(rand(1,12))->toDateString(),'inspection_frequency'=>['monthly','quarterly','biannual'][rand(0,2)],'scope'=>'安防设备维保','status'=>'active']);
    return $c.' 工单';
});

// 6. 报销
echo "---6---\n";
S('报销',function(){
    $uids=User::where('id','>',5)->pluck('id')->toArray();
    $cats=['travel','hospitality','office','transport','project_cost','other'];
    $descs=['出差住宿费','招待用餐','办公费用','交通费','项目材料费','其他'];
    $sts=['draft','submitted','approved','rejected','paid'];
    $c=0;foreach($uids as $uid){for($i=0;$i<rand(1,4);$i++){
        $ci=array_rand($cats);$amt=rand(100,5000);$st=$sts[array_rand($sts)];
        $cl=ExpenseClaim::create(['user_id'=>$uid,'category'=>$cats[$ci],'total_amount'=>$amt,'description'=>$descs[$ci],'status'=>$st,'approver_id'=>1,'approved_at'=>in_array($st,['approved','paid'])?now():null,'paid_amount'=>$st=='paid'?$amt:0,'paid_at'=>$st=='paid'?now():null]);
        for($j=0;$j<rand(1,3);$j++) ExpenseItem::create(['expense_claim_id'=>$cl->id,'item_date'=>now()->subDays(rand(1,30))->toDateString(),'description'=>$descs[$ci].($j+1),'amount'=>round($amt/rand(1,3),2),'category'=>$cats[$ci]]);
        $c++;
    }}return $c;
});

// 7. 车辆
echo "---7---\n";
S('车辆',function(){
    $uids=User::pluck('id')->toArray();$dids=Department::pluck('id')->toArray();
    $fuels=['gas','diesel','electric','hybrid'];$vsts=['normal','maintenance'];
    $vids=[];
    foreach([['皖A12345','五菱','宏光',58000],['皖B56789','江淮','瑞风',125000],['皖C90123','丰田','卡罗拉',148000],['皖D34567','金杯','海狮',89000],['皖E78901','比亚迪','宋PLUS',156000]] as $v){
        $veh=Vehicle::create(['plate_no'=>$v[0],'brand'=>$v[1],'model'=>$v[2],'color'=>'白色','purchase_date'=>now()->subDays(rand(365,1095))->toDateString(),'purchase_price'=>$v[3],'department_id'=>$dids[array_rand($dids)],'responsible_user_id'=>$uids[array_rand($uids)],'status'=>$vsts[rand(0,1)],'vin'=>'LSVAU'.rand(100000,999999),'engine_no'=>'ENG'.rand(100000,999999),'seats'=>rand(5,9),'fuel_type'=>$fuels[rand(0,3)]]);
        $vids[]=$veh->id;
        VehicleInsurance::create(['vehicle_id'=>$veh->id,'insurance_company'=>'中国人保','policy_no'=>'PICC'.rand(100000,999999),'type'=>'交强险','premium'=>rand(2000,6000),'start_date'=>now()->toDateString(),'end_date'=>now()->addYear()->toDateString(),'status'=>'active']);
        VehicleMaintenanceRecord::create(['vehicle_id'=>$veh->id,'maintenance_type'=>'常规保养','mileage'=>rand(5000,30000),'cost'=>rand(300,2000),'maintenance_date'=>now()->subDays(rand(10,180))->toDateString(),'description'=>'更换机油机滤','handled_by'=>$uids[array_rand($uids)]]);
    }
    $reqSts=['draft','submitted','approved','rejected'];
    foreach($vids as $vid){for($i=0;$i<rand(3,8);$i++){
        $st=$reqSts[rand(0,3)];
        VehicleUsageRequest::create(['vehicle_id'=>$vid,'applicant_id'=>$uids[array_rand($uids)],'usage_date'=>now()->subDays(rand(1,30))->toDateString(),'start_time'=>'08:00','end_time'=>'18:00','destination'=>['客户现场','公司','仓库','工地'][rand(0,3)],'purpose'=>'施工用车','passengers'=>rand(1,5),'self_drive'=>rand(0,1)?true:false,'status'=>$st,'approver_id'=>1,'approved_at'=>$st=='approved'?now():null,'actual_mileage'=>$st=='approved'?rand(20,200):null]);
    }}
    return count($vids).' 车辆';
});

// 8. 库存
echo "---8---\n";
S('库存',function(){
    $uids=User::pluck('id')->toArray();
    Warehouse::create(['name'=>'主仓库','code'=>'WH01','type'=>'main','address'=>'公司一楼','manager_id'=>$uids[0],'status'=>'active']);
    Warehouse::create(['name'=>'辅材仓库','code'=>'WH02','type'=>'aftermarket','address'=>'公司二楼','manager_id'=>$uids[1],'status'=>'active']);
    $wId=Warehouse::first()->id;
    $items=[['海康高清摄像头','DS-2CD2T47G2-L','install',850,'台'],['海康NVR录像机','DS-7608N-K2','debug',3200,'台'],['大华门禁控制器','ASI7213Y','install',1500,'台'],['门禁读卡器','DAIC-MF','debug',280,'个'],['报警主机','2316PLUS','maintain',2100,'台'],['红外探测器','PB-60','install',450,'对'],['六类网线','CAT6','network',380,'箱'],['电源线RVV','2x1.5','other',180,'卷'],['PVC管','PVC25','install',12,'根'],['水晶头','RJ45','network',35,'盒'],['摄像机支架','不锈钢','install',25,'个'],['光纤跳线','SC-LC','network',15,'条'],['光纤收发器','单模百兆','network',120,'对'],['千兆交换机','16口','network',680,'台'],['UPS电源','1KVA','other',1500,'台'],['监控硬盘','4TB','other',520,'块']];
    $c=0;$srTypes=['in','out','transfer','check'];
    foreach($items as $item){
        $stock=rand(5,100);
        InventoryItem::create(['name'=>$item[0],'code'=>'ITM'.str_pad($c+1,4,'0',STR_PAD_LEFT),'category'=>$item[2],'specification'=>$item[1],'unit'=>$item[3],'safety_stock'=>10,'current_stock'=>$stock,'cost_price'=>floatval($item[4]),'sell_price'=>round(floatval($item[4])*1.3,2),'warehouse_id'=>$wId,'location'=>'A'.rand(1,5).'-'.rand(1,10),'has_serial'=>in_array($item[2],['install','debug','maintain']),'status'=>$stock<=10?'low_stock':'normal']);
        for($j=0;$j<rand(1,4);$j++) StockRecord::create(['record_no'=>'SR'.date('Ymd').str_pad($c+1,3,'0',STR_PAD_LEFT),'inventory_item_id'=>$c+1,'warehouse_id'=>$wId,'type'=>$srTypes[array_rand($srTypes)],'quantity'=>rand(1,10),'remaining_stock'=>$stock,'operator_id'=>$uids[array_rand($uids)],'remark'=>'库存操作']);
        $c++;
    }
    return $c;
});

// 9. 财务
echo "---9---\n";
S('财务',function(){
    $custs=Customer::inRandomOrder()->limit(8)->get();
    $supps=Supplier::inRandomOrder()->limit(4)->get();
    $pId=Project::first()?Project::first()->id:null;
    $c=0;
    foreach($custs as $cust){$a=rand(5,100)*10000;$r=rand(0,round($a*0.8/10000))*10000;Receivable::create(['customer_id'=>$cust->id,'project_id'=>$pId,'amount'=>$a,'received_amount'=>$r,'remaining_amount'=>$a-$r,'due_date'=>now()->addDays(rand(-30,90))->toDateString(),'received_date'=>$r>0?now()->subDays(rand(1,30))->toDateString():null,'status'=>($a-$r)<=0?'paid':'partial']);$c++;}
    foreach($supps as $sup){$a=rand(2,50)*10000;$p=rand(0,round($a*0.7/10000))*10000;Payable::create(['supplier_id'=>$sup->id,'project_id'=>$pId,'amount'=>$a,'paid_amount'=>$p,'remaining_amount'=>$a-$p,'due_date'=>now()->addDays(rand(-15,60))->toDateString(),'paid_date'=>$p>0?now()->subDays(rand(1,30))->toDateString():null,'payment_term'=>'月结30天','status'=>($a-$p)<=0?'paid':'partial']);$c++;}
    return $c;
});

// 10. 考勤(最近30天)
echo "---10---\n";
S('考勤',function(){
    $users=User::where('status','active')->where('id','>',5)->get();
    $lts=['annual','personal','sick','marriage','other'];
    $ac=0;$lc=0;$oc=0;
    for($d=29;$d>=0;$d--){$dt=now()->subDays($d);if($dt->isWeekend())continue;foreach($users as $u){if(rand(1,100)>85)continue;AttendanceRecord::create(['user_id'=>$u->id,'date'=>$dt->toDateString(),'clock_in'=>$dt->copy()->setTime(8,rand(0,30))->toDateTimeString(),'clock_in_location'=>'公司','clock_out'=>$dt->copy()->setTime(17,rand(30,59))->toDateTimeString(),'clock_out_location'=>'公司','status'=>'normal','work_hours'=>8.0,'overtime_hours'=>rand(0,30)/10.0]);$ac++;}}
    foreach($users as $u){if(rand(0,1))continue;for($j=0;$j<rand(1,2);$j++) LeaveRequest::create(['user_id'=>$u->id,'type'=>$lts[array_rand($lts)],'start_date'=>now()->subDays(rand(1,15))->toDateString(),'end_date'=>now()->subDays(rand(0,14))->toDateString(),'days'=>rand(1,5).'.0','reason'=>'个人事务','status'=>['pending','approved','rejected'][rand(0,2)],'approver_id'=>1]);$lc++;}
    foreach($users->take(10) as $u){if(rand(0,1))continue;OvertimeRequest::create(['user_id'=>$u->id,'overtime_date'=>now()->subDays(rand(1,14))->toDateString(),'start_time'=>'18:00','end_time'=>['20:00','21:00','22:00'][rand(0,2)],'hours'=>[2.0,3.0,4.0][rand(0,2)],'reason'=>'项目加班','compensation_type'=>['pay','leave'][rand(0,1)],'status'=>['pending','approved'][rand(0,1)],'approver_id'=>1]);$oc++;}
    return "$ac 打卡,$lc 请假,$oc 加班";
});

// 11. 网盘
echo "---11---\n";
S('网盘',function(){
    $uids=User::pluck('id')->toArray();$c=0;
    foreach(['公司制度','项目资料','技术文档','培训资料','安全管理'] as $nm){
        $f=DiskFolder::create(['name'=>$nm,'path'=>'/'.$nm,'created_by'=>$uids[array_rand($uids)],'is_system'=>false]);$c++;
    }
    $fids=DiskFolder::pluck('id')->toArray();
    foreach([['安防设计规范.pdf',0,2e6],['施工标准.pdf',0,1.5e6],['海康安装手册.pdf',2,5e5],['大华配置指南.pdf',2,7.5e5],['项目总结.xlsx',1,2.5e5],['验收模板.docx',1,1.3e5],['考勤制度.pdf',0,2.5e5],['NVR计算表.xlsx',2,6e4]] as $f){
        DiskFile::create(['folder_id'=>$fids[$f[1]]??$fids[0],'name'=>$f[0],'original_name'=>$f[0],'extension'=>substr(strrchr($f[0],'.'),1),'mime_type'=>'application/octet-stream','size'=>$f[2],'path'=>'/storage/'.$f[0],'uploaded_by'=>$uids[array_rand($uids)],'version'=>1,'is_starred'=>rand(0,1)]);$c++;
    }
    return $c;
});

// 12. 知识库
echo "---12---\n";
S('知识库',function(){
    $uids=User::pluck('id')->toArray();$c=0;
    $catData=[['安防基础',null],['设备安装',null],['故障排查',null],['项目管理',null],['行业标准',null],['视频监控','安防基础'],['门禁系统','安防基础'],['报警系统','安防基础'],['安装规范','设备安装'],['故障排查','故障排查'],['弱电规范','行业标准']];
    $cm=[];
    foreach($catData as $cd){$par=($cd[1]!==null&&isset($cm[$cd[1]]))?$cm[$cd[1]]:null;$cat=KnowledgeCategory::create(['parent_id'=>$par,'name'=>$cd[0],'icon'=>'document','sort_order'=>$c]);$cm[$cd[0]]=$cat->id;$c++;}
    $arts=[['摄像机选型指南','视频监控','介绍安防项目摄像机选型方法'],['存储计算','视频监控','NVR容量计算方法'],['布线规范','门禁系统','门禁安装布线技术要求'],['报警调试','报警系统','报警主机配置流程'],['安装角度','安装规范','最佳安装高度角度'],['平台配置','故障排查','iVMS配置问题解决'],['验收标准','弱电规范','弱电工程验收标准'],['成本控制','项目管理','项目成本管控方法'],['进度管理','项目管理','施工计划与工期控制'],['国标解读','行业标准','GB50198条文解读']];
    foreach($arts as $a){KnowledgeArticle::create(['category_id'=>$cm[$a[1]]??1,'title'=>$a[0],'content'=>'<h2>'.$a[0].'</h2><p>'.$a[2].'</p><p>详细技术内容。</p>','author_id'=>$uids[array_rand($uids)],'tags'=>['安防','技术'],'view_count'=>rand(10,500),'like_count'=>rand(0,50),'status'=>'published','published_at'=>now()->subDays(rand(1,180)),'summary'=>$a[2]]);$c++;}
    return $c;
});

// 13. 日志
echo "---13---\n";
S('日志',function(){
    $uids=User::pluck('id')->toArray();$c=0;
    $types=['login','logout','operation','login_failed'];
    for($d=29;$d>=0;$d--){for($j=0;$j<rand(3,10);$j++){
        DB::table('system_logs')->insert(['user_id'=>$uids[array_rand($uids)],'type'=>$types[array_rand($types)],'module'=>['auth','project','service','expense','dashboard'][rand(0,4)],'action'=>['login','view','create','update'][rand(0,3)],'description'=>'操作记录','ip'=>'192.168.1.'.rand(1,254),'user_agent'=>'Mozilla/5.0','created_at'=>now()->subDays($d)->subHours(rand(8,18))]);
        $c++;
    }}return $c;
});

echo "\n=== 完成: $ok OK / $err ERR ===\n";
"""

# Reconnect (previous connection may have timed out)
ssh.close()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=10)
sftp = ssh.open_sftp()
run("chown nbcy:nbcy /var/www/oa-api")

with sftp.open('/var/www/oa-api/seed_demo_data.php', 'w') as f:
    f.write(PHP_SEED)
sftp.close()

out = run("cd /var/www/oa-api && php seed_demo_data.php", timeout=120)
print(out)

# 恢复权限
run("chown www-data:www-data /var/www/oa-api")

ssh.close()

# 验证
print("\n" + "="*60)
print("验证数据:")
print("="*60)
r = requests.post('http://172.20.0.139:3001/api/auth/login', json={'username':'admin','password':'admin123'}, timeout=10)
if r.status_code == 200:
    token = r.json()['data']['token']
    headers = {'Authorization': f'Bearer {token}'}
    eps = [
        ('GET','/api/employees','员工'),('GET','/api/departments','部门'),
        ('GET','/api/customers','客户'),('GET','/api/projects','项目'),
        ('GET','/api/service-orders','售后'),('GET','/api/expenses','报销'),
        ('GET','/api/vehicles','车辆'),('GET','/api/inventory','库存'),
        ('GET','/api/finance/receivables','应收'),('GET','/api/finance/payables','应付'),
        ('GET','/api/attendance/records?month=2026-06','考勤'),
        ('GET','/api/disk/folders','网盘'),('GET','/api/knowledge/categories','知识库'),
    ]
    print(f"{'模块':<8} {'状态':<6} {'数据量':<10}")
    print("-"*35)
    for m, p, n in eps:
        try:
            r2 = requests.get(f'http://172.20.0.139:3001{p}', headers=headers, timeout=10)
            if r2.status_code == 200:
                d = r2.json()
                if isinstance(d, dict) and 'data' in d:
                    dd = d['data']
                    cnt = dd.get('total', dd.get('items', len(dd) if isinstance(dd, list) else '?'))
                else:
                    cnt = '?'
                print(f"{n:<8} 200   {str(cnt):<10}")
            else:
                print(f"{n:<8} {r2.status_code:<6} {'--':<10}")
        except Exception as e:
            print(f"{n:<8} ERR   {str(e)[:20]}")
print("\n数据生成完成!")
