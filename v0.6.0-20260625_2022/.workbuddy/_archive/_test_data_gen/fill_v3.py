"""172 服务器全量测试数据生成 v3 - 完整 schema"""
import paramiko, random, json
from datetime import datetime, timedelta

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

DB_PWD = 'oa_pg_pwd_782997781'
PG = f"export PGPASSWORD='{DB_PWD}' && psql -U oa_user -d security_oa"

def run(sql):
    cmd = f'{PG} -c "{sql}" 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace')

def get_ids(table):
    cmd = f"{PG} -t -A -c \"SELECT id FROM {table} ORDER BY id;\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8', errors='replace').strip()
    return [int(x) for x in raw.split('\n') if x.strip().isdigit()]

def insert(table, columns, values_list, batch=50):
    if not values_list: return 0
    total = 0
    for i in range(0, len(values_list), batch):
        chunk = values_list[i:i+batch]
        vals = []
        for row in chunk:
            cells = []
            for v in row:
                if v is None: cells.append('NULL')
                elif isinstance(v, bool): cells.append('TRUE' if v else 'FALSE')
                elif isinstance(v, (int, float)): cells.append(str(v))
                elif isinstance(v, (dict, list)):
                    s = json.dumps(v, ensure_ascii=False).replace("'", "''")
                    cells.append(f"'{s}'::json")
                else:
                    s = str(v).replace("'", "''")
                    cells.append(f"'{s}'")
            vals.append('(' + ','.join(cells) + ')')
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES {','.join(vals)};"
        out = run(sql)
        if 'ERROR' in out:
            err_line = [l for l in out.split('\n') if 'ERROR' in l]
            print(f'  [FAIL] {err_line[0][:200] if err_line else out[:200]}')
            return total
        total += len(chunk)
    return total

def rand_date(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime('%Y-%m-%d')
def rand_dt(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0,23), minutes=random.randint(0,59))).strftime('%Y-%m-%d %H:%M:%S')
def pick(xs):
    return random.choice(xs) if xs else None

# ============== 加载基础 ==============
print("Loading FK...")
USER_IDS = get_ids('users')
CUST_IDS = get_ids('customers')
PROJ_IDS = get_ids('projects')
VEH_IDS = get_ids('vehicles')
LEAD_IDS = get_ids('leads')
OPP_IDS = get_ids('opportunities')
SVC_IDS = get_ids('service_orders')
INV_IDS = get_ids('inventory_items')
NOTI_IDS = get_ids('notifications')
SUPP_IDS = get_ids('suppliers')

print(f"users={len(USER_IDS)} customers={len(CUST_IDS)} projects={len(PROJ_IDS)} vehicles={len(VEH_IDS)} leads={len(LEAD_IDS)} opps={len(OPP_IDS)} svcs={len(SVC_IDS)} inv={len(INV_IDS)} supp={len(SUPP_IDS)}")

# 已有: skill_tags(8), departments(6), employee_profiles(4)
EMP_IDS = get_ids('employee_profiles')
SKILL_IDS = get_ids('skill_tags')
DEPT_IDS = get_ids('departments')

# ============== 第 1 步：补稀疏表 + 关键关联 ==============
print("\n=== Step 1: Sparse fixes ===")

# 1.1 positions (实际列: name, code, level, sort, is_active, description)
print("positions...", end=' ')
n = insert('positions', ['name','code','level','sort','is_active','description','created_at','updated_at'], [
    ('技术总监', 'TECH_DIR', 'P8', 80, True, '技术团队负责人', rand_dt(2000), rand_dt(900)),
    ('项目经理', 'PM', 'P6', 60, True, '项目交付管理', rand_dt(2000), rand_dt(900)),
    ('高级工程师', 'SR_ENG', 'P7', 70, True, '核心技术骨干', rand_dt(2000), rand_dt(900)),
    ('工程师', 'ENG', 'P5', 50, True, '项目实施', rand_dt(2000), rand_dt(900)),
    ('销售经理', 'SALES_MGR', 'P6', 60, True, '销售团队管理', rand_dt(2000), rand_dt(900)),
    ('销售代表', 'SALES', 'P4', 40, True, '客户开发', rand_dt(2000), rand_dt(900)),
    ('财务主管', 'FIN_MGR', 'P6', 60, True, '财务管理', rand_dt(2000), rand_dt(900)),
    ('行政专员', 'ADMIN', 'P4', 40, True, '行政事务', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')
POS_IDS = get_ids('positions')

# 1.2 warehouses (实际列: name, code, type, address, manager_id, status, description)
print("warehouses...", end=' ')
n = insert('warehouses', ['name','code','type','address','manager_id','status','description','created_at','updated_at'], [
    ('北京主仓', f'WH-BJ-{random.randint(100,999)}', 'main', '北京市朝阳区', pick(USER_IDS), 'active', '主仓库', rand_dt(2000), rand_dt(900)),
    ('上海分仓', f'WH-SH-{random.randint(100,999)}', 'branch', '上海市浦东新区', pick(USER_IDS), 'active', '分仓库', rand_dt(2000), rand_dt(900)),
    ('广州分仓', f'WH-GZ-{random.randint(100,999)}', 'branch', '广州市天河区', pick(USER_IDS), 'active', '分仓库', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')
WH_IDS = get_ids('warehouses')

# 1.3 stock_records
print("stock_records...", end=' ')
n = insert('stock_records', ['record_no','inventory_item_id','warehouse_id','type','quantity','remaining_stock','operator_id','remark','created_at','updated_at','project_id'], [
    (f'SR{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}', pick(INV_IDS), pick(WH_IDS),
     random.choice(['in','out']), random.randint(5,50), random.randint(5,50),
     pick(USER_IDS), random.choice(['采购入库','项目领用','调拨']), rand_dt(900), rand_dt(900), pick(PROJ_IDS) if random.random() > 0.3 else None)
    for _ in range(60)
])
print(f'{n} rows')
STOCK_IDS = get_ids('stock_records')

# 1.4 employee_onboardings (实际列：notes 不存在，用 remark)
print("employee_onboardings...", end=' ')
n = insert('employee_onboardings', ['user_id','hire_date','department_id','position_id','mentor_id','probation_months','probation_end_date','contract_start','contract_end','id_card_no','education_level','education_school','education_major','status','remark','onboarded_by','created_at','updated_at'], [
    (uid, rand_date(2000), pick(DEPT_IDS), pick(POS_IDS), pick(USER_IDS), random.choice([1,3,6]),
     (datetime.now() - timedelta(days=random.randint(30,180))).strftime('%Y-%m-%d'),
     rand_date(2000), (datetime.now() + timedelta(days=random.randint(365,1095))).strftime('%Y-%m-%d'),
     f'110{random.randint(19800101,20050101)}',
     random.choice(['本科','大专','硕士']),
     random.choice(['清华','北大','北航','北邮']),
     random.choice(['计算机','电子','通信','自动化']),
     'active', '入职流程', pick(USER_IDS), rand_dt(2000), rand_dt(900))
    for uid in USER_IDS
])
print(f'{n} rows')

# 1.5 employee_resignations (实际列：handover_to 不存在，用 handover_to_user_id)
print("employee_resignations...", end=' ')
n = insert('employee_resignations', ['user_id','resign_date','notice_date','last_work_day','resign_type','reason','handover_to_user_id','handover_note','all_assets_returned','final_salary_amount','status','remark','approved_by','created_by','created_at','updated_at'], [
    (pick(USER_IDS), rand_date(800), rand_date(800), rand_date(800),
     random.choice(['voluntary','involuntary']), random.choice(['个人发展','家庭原因','薪资','其他']),
     pick(USER_IDS), '工作已交接', True, round(random.uniform(5000,30000),2),
     'approved', '已批准', pick(USER_IDS), pick(USER_IDS), rand_dt(800), rand_dt(800))
    for _ in range(3)
])
print(f'{n} rows')

# 1.6 employee_skills (避免唯一约束冲突：用组合去重)
print("employee_skills...", end=' ')
pairs = set()
skill_vals = []
attempts = 0
while len(skill_vals) < 60 and attempts < 500:
    eid, sid = pick(EMP_IDS), pick(SKILL_IDS)
    if (eid, sid) not in pairs:
        pairs.add((eid, sid))
        skill_vals.append((eid, sid, random.choice(['beginner','intermediate','advanced','expert']), rand_dt(2000), rand_dt(900)))
    attempts += 1
n = insert('employee_skills', ['employee_profile_id','skill_tag_id','proficiency','created_at','updated_at'], skill_vals)
print(f'{n} rows')

# ============== 第 2 步：customer_devices + device_serial_numbers ==============
print("\n=== Step 2: Devices ===")

# 2.1 customer_devices
print("customer_devices...", end=' ')
n = insert('customer_devices', ['customer_id','project_id','device_name','device_type','brand','model','serial_number','install_location','install_date','warranty_end','status','notes','created_at','updated_at'], [
    (pick(CUST_IDS), pick(PROJ_IDS) if random.random() > 0.3 else None,
     f'摄像头-{random.randint(1,9999):04d}',
     random.choice(['camera','access_control','alarm','intercom','barrier']),
     random.choice(['海康','大华','宇视','华为']),
     f'M{random.randint(100,9999)}',
     f'SN{datetime.now().year}{random.randint(100000,999999)}',
     random.choice(['大门','机房','一楼','二楼','停车场']),
     rand_date(900),
     (datetime.now() + timedelta(days=random.randint(180,1095))).strftime('%Y-%m-%d'),
     random.choice(['normal','maintenance','broken']),
     None, rand_dt(900), rand_dt(900))
    for _ in range(80)
])
print(f'{n} rows')
CDEV_IDS = get_ids('customer_devices')

# 2.2 device_serial_numbers (依赖 inventory_item_id)
print("device_serial_numbers...", end=' ')
n = insert('device_serial_numbers', ['inventory_item_id','serial_number','status','project_id','customer_device_id','stock_record_id','install_date','notes','created_at','updated_at'], [
    (pick(INV_IDS), f'SN-{datetime.now().year}-{random.randint(10000,99999)}',
     random.choice(['in_stock','assigned','in_use','retired']),
     pick(PROJ_IDS) if random.random() > 0.3 else None,
     pick(CDEV_IDS) if random.random() > 0.5 else None,
     pick(STOCK_IDS) if random.random() > 0.5 else None,
     rand_date(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for _ in range(100)
])
print(f'{n} rows')

# ============== 第 3 步：项目关联表 ==============
print("\n=== Step 3: Project-related ===")

# 3.1 project_contracts
print("project_contracts...", end=' ')
n = insert('project_contracts', ['project_id','contract_no','contract_amount','payment_method','contract_start','contract_end','status','signed_at','notes','created_at','updated_at'], [
    (pid, f'CT{datetime.now().year}{random.randint(1000,9999)}', round(random.uniform(50000,5000000),2),
     random.choice(['installment','lump_sum','milestone']),
     rand_date(900), (datetime.now() + timedelta(days=random.randint(180,730))).strftime('%Y-%m-%d'),
     random.choice(['draft','active','completed','terminated']),
     rand_dt(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for pid in PROJ_IDS[:30]
])
print(f'{n} rows')
CONTRACT_IDS = get_ids('project_contracts')

# 3.2 contract_payment_nodes
print("contract_payment_nodes...", end=' ')
n = insert('contract_payment_nodes', ['contract_id','name','percentage','amount','planned_date','actual_date','status','paid_amount','notes','created_at','updated_at'], [
    (pick(CONTRACT_IDS), f'第{idx+1}期款', [30,40,30][idx], round(random.uniform(10000,500000),2),
     rand_date(500), rand_date(300) if random.random() > 0.4 else None,
     random.choice(['pending','partial','paid']),
     round(random.uniform(0,500000),2) if random.random() > 0.3 else 0,
     None, rand_dt(900), rand_dt(900))
    for idx in range(3) for _ in range(30)
])
print(f'{n} rows')

# 3.3 project_materials
print("project_materials...", end=' ')
n = insert('project_materials', ['project_id','material_name','specification','quantity','unit','unit_cost','total_cost','used_by','use_date','inventory_item_id','notes','created_at','updated_at'], [
    (pick(PROJ_IDS), f'材料-{random.randint(1,9999)}', f'规格{random.randint(1,100)}',
     round(random.uniform(1,100),2), random.choice(['个','箱','米','台','根']),
     round(random.uniform(10,5000),2), round(random.uniform(100,100000),2),
     pick(USER_IDS), rand_date(900),
     pick(INV_IDS) if random.random() > 0.5 else None,
     None, rand_dt(900), rand_dt(900))
    for _ in range(100)
])
print(f'{n} rows')

# 3.4 project_settlements
print("project_settlements...", end=' ')
n = insert('project_settlements', ['project_id','total_income','total_cost','cost_labor','cost_material','cost_outsource','cost_other','profit','profit_rate','settlement_date','status','notes','created_at','updated_at'], [
    (pid, round(random.uniform(100000,5000000),2), round(random.uniform(80000,4000000),2),
     round(random.uniform(20000,1000000),2), round(random.uniform(30000,2000000),2),
     round(random.uniform(10000,500000),2), round(random.uniform(5000,200000),2),
     round(random.uniform(10000,1000000),2), round(random.uniform(5,40),2),
     rand_date(800) if random.random() > 0.3 else None,
     random.choice(['draft','submitted','approved','rejected']),
     None, rand_dt(900), rand_dt(900))
    for pid in PROJ_IDS[:25]
])
print(f'{n} rows')

# 3.5 construction_logs
print("construction_logs...", end=' ')
n = insert('construction_logs', ['project_id','user_id','work_date','weather','content','problems','solutions','photos','work_hours','location','status','created_at','updated_at'], [
    (pick(PROJ_IDS), pick(USER_IDS), rand_date(365),
     random.choice(['晴','多云','阴','小雨','大雨']),
     f'今日完成{random.choice(["布线","设备安装","调试","验收"])}工作',
     random.choice([None,'部分设备故障','线材不足','协调问题']),
     random.choice([None,'已更换设备','已补货','已沟通']),
     json.dumps([{'name':f'photo_{i}.jpg','url':f'/photos/{i}.jpg'} for i in range(random.randint(0,3))]),
     round(random.uniform(4,10),1),
     random.choice(['北京市朝阳区','上海市浦东','广州市天河']),
     random.choice(['submitted','reviewed','rejected']),
     rand_dt(365), rand_dt(365))
    for _ in range(150)
])
print(f'{n} rows')

# 3.6 maintenance_contracts
print("maintenance_contracts...", end=' ')
n = insert('maintenance_contracts', ['contract_no','customer_id','amount','start_date','end_date','inspection_frequency','scope','status','notes','created_at','updated_at'], [
    (f'MC{datetime.now().year}{random.randint(1000,9999)}', pick(CUST_IDS),
     round(random.uniform(10000,200000),2), rand_date(800),
     (datetime.now() + timedelta(days=random.randint(180,730))).strftime('%Y-%m-%d'),
     random.choice(['monthly','quarterly','semi_annual','annual']),
     random.choice(['设备巡检','故障维修','系统升级','综合']),
     random.choice(['active','expired','terminated']),
     None, rand_dt(900), rand_dt(900))
    for _ in range(15)
])
print(f'{n} rows')

# ============== 第 4 步：销售/采购关联 ==============
print("\n=== Step 4: Sales/Purchase ===")

# 4.1 purchase_requirements
print("purchase_requirements...", end=' ')
n = insert('purchase_requirements', ['code','project_id','material','spec','quantity','unit','need_date','priority','status','creator','remark','created_at','updated_at'], [
    (f'PR{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}',
     pick(PROJ_IDS), f'材料{random.randint(1,9999)}', f'规格{random.randint(1,100)}',
     round(random.uniform(1,500),2), random.choice(['个','箱','米','台']),
     rand_date(500), random.choice(['low','medium','high','urgent']),
     random.choice(['pending','approved','rejected','completed']),
     random.choice(['张三','李四','王五']),
     None, rand_dt(900), rand_dt(900))
    for _ in range(30)
])
print(f'{n} rows')
REQ_IDS = get_ids('purchase_requirements')

# 4.2 purchase_plans
print("purchase_plans...", end=' ')
n = insert('purchase_plans', ['code','requirement_id','project_id','title','total_amount','plan_date','priority','status','submitter_id','submitted_at','approver_id','approved_at','remark','created_at','updated_at'], [
    (f'PP{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}',
     pick(REQ_IDS), pick(PROJ_IDS), f'采购计划-{random.randint(1,9999)}',
     round(random.uniform(10000,500000),2), rand_date(500),
     random.choice(['low','medium','high','urgent']),
     random.choice(['draft','submitted','approved','rejected','completed']),
     pick(USER_IDS), rand_dt(500),
     pick(USER_IDS) if random.random() > 0.3 else None, rand_dt(500) if random.random() > 0.3 else None,
     None, rand_dt(500), rand_dt(500))
    for _ in range(25)
])
print(f'{n} rows')
PLAN_IDS = get_ids('purchase_plans')

# 4.3 purchase_orders
print("purchase_orders...", end=' ')
n = insert('purchase_orders', ['project_id','supplier_id','po_no','total_amount','status','approved_by','approved_at','notes','created_at','updated_at'], [
    (pick(PROJ_IDS), pick(SUPP_IDS), f'PO{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}',
     round(random.uniform(5000,300000),2),
     random.choice(['draft','submitted','approved','received','completed','cancelled']),
     pick(USER_IDS) if random.random() > 0.3 else None,
     rand_dt(500) if random.random() > 0.3 else None,
     None, rand_dt(500), rand_dt(500))
    for _ in range(30)
])
print(f'{n} rows')
PO_IDS = get_ids('purchase_orders')

# 4.4 purchase_items
print("purchase_items...", end=' ')
n = insert('purchase_items', ['purchase_order_id','item_name','specification','quantity','unit','unit_price','total_price','received_quantity','notes','created_at','updated_at'], [
    (pick(PO_IDS), f'物品{random.randint(1,9999)}', f'规格{random.randint(1,100)}',
     round(random.uniform(1,100),2), random.choice(['个','箱','米','台']),
     round(random.uniform(10,5000),2), round(random.uniform(100,100000),2),
     round(random.uniform(0,100),2), None, rand_dt(500), rand_dt(500))
    for _ in range(80)
])
print(f'{n} rows')

# 4.5 purchase_contracts
print("purchase_contracts...", end=' ')
n = insert('purchase_contracts', ['code','plan_id','project_id','supplier_id','title','total_amount','signed_at','start_date','end_date','payment_terms','delivery_address','status','signer','signer_id','remark','created_at','updated_at'], [
    (f'PC{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}',
     pick(PLAN_IDS) if random.random() > 0.3 else None, pick(PROJ_IDS), pick(SUPP_IDS),
     f'采购合同-{random.randint(1,9999)}',
     round(random.uniform(10000,500000),2),
     rand_date(500) if random.random() > 0.3 else None,
     rand_date(500), (datetime.now() + timedelta(days=random.randint(60,365))).strftime('%Y-%m-%d'),
     random.choice(['月结30天','月结60天','货到付款','预付30%']),
     random.choice(['北京仓库','上海仓库','项目现场']),
     random.choice(['draft','active','completed','terminated']),
     '签约人', pick(USER_IDS),
     None, rand_dt(500), rand_dt(500))
    for _ in range(15)
])
print(f'{n} rows')

# 4.6 quotations
print("quotations...", end=' ')
n = insert('quotations', ['quote_no','opportunity_id','version','subtotal','discount_rate','discount_amount','tax_rate','tax_amount','total_amount','valid_until','status','notes','created_by','sent_at','responded_at','created_at','updated_at'], [
    (f'Q{datetime.now().strftime("%Y%m%d")}{random.randint(1000,9999)}',
     pick(OPP_IDS), random.randint(1,3),
     round(random.uniform(10000,500000),2), round(random.uniform(0,20),2),
     round(random.uniform(0,50000),2), 13.0,
     round(random.uniform(1000,50000),2), round(random.uniform(10000,500000),2),
     (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
     random.choice(['draft','sent','accepted','rejected','expired']),
     None, pick(USER_IDS),
     rand_dt(500) if random.random() > 0.3 else None,
     rand_dt(300) if random.random() > 0.3 else None,
     rand_dt(500), rand_dt(500))
    for _ in range(20)
])
print(f'{n} rows')
QUOTE_IDS = get_ids('quotations')

# 4.7 quotation_items
print("quotation_items...", end=' ')
n = insert('quotation_items', ['quotation_id','inventory_item_id','name','specification','unit','quantity','unit_price','total_price','remark','created_at','updated_at'], [
    (pick(QUOTE_IDS), pick(INV_IDS) if random.random() > 0.3 else None,
     f'报价项目-{random.randint(1,9999)}', f'规格{random.randint(1,100)}',
     random.choice(['个','箱','米','台']),
     round(random.uniform(1,50),2), round(random.uniform(100,5000),2),
     round(random.uniform(100,100000),2), None, rand_dt(500), rand_dt(500))
    for _ in range(60)
])
print(f'{n} rows')

# 4.8 sales_products
print("sales_products...", end=' ')
n = insert('sales_products', ['code','name','category_id','unit','spec','sale_price','cost_price','description','status','created_at','updated_at'], [
    (f'SP{random.randint(1000,9999)}', f'销售产品-{random.randint(1,9999)}',
     pick(INV_IDS), random.choice(['个','箱','米','台']),
     f'规格{random.randint(1,100)}',
     round(random.uniform(100,5000),2), round(random.uniform(50,3000),2),
     '热销产品', 'active', rand_dt(900), rand_dt(900))
    for _ in range(20)
])
print(f'{n} rows')

# 4.9 sales_follow_up_attachments
print("sales_follow_up_attachments...", end=' ')
FU_IDS = get_ids('sales_follow_ups')
n = insert('sales_follow_up_attachments', ['follow_up_id','file_name','file_path','file_size','mime_type','uploaded_by','created_at','updated_at'], [
    (pick(FU_IDS), f'附件{random.randint(1,9999)}.pdf', f'/uploads/{random.randint(1000,9999)}.pdf',
     random.randint(1000,5000000), 'application/pdf',
     pick(USER_IDS), rand_dt(900), rand_dt(900))
    for _ in range(40)
])
print(f'{n} rows')

# ============== 第 5 步：车辆关联 ==============
print("\n=== Step 5: Vehicle-related ===")

# 5.1 fuel_cards
print("fuel_cards...", end=' ')
n = insert('fuel_cards', ['card_no','vehicle_id','provider','card_type','balance','status','issue_date','expire_date','notes','created_at','updated_at'], [
    (f'FC{random.randint(100000,999999)}', pick(VEH_IDS), random.choice(['中石化','中石油']),
     random.choice(['主卡','副卡']), round(random.uniform(100,5000),2),
     'active', rand_date(800),
     (datetime.now() + timedelta(days=random.randint(365,1095))).strftime('%Y-%m-%d'),
     None, rand_dt(800), rand_dt(800))
    for _ in range(5)
])
print(f'{n} rows')
FC_IDS = get_ids('fuel_cards')

# 5.2 fuel_card_recharges
print("fuel_card_recharges...", end=' ')
n = insert('fuel_card_recharges', ['fuel_card_id','recharge_no','amount','recharge_date','operator_id','payment_method','notes','created_at','updated_at'], [
    (pick(FC_IDS), f'RE{random.randint(10000,99999)}',
     round(random.uniform(500,3000),2), rand_date(800),
     pick(USER_IDS), random.choice(['现金','转账','油票']),
     '充值', rand_dt(800), rand_dt(800))
    for _ in range(30)
])
print(f'{n} rows')

# 5.3 vehicle_insurance
print("vehicle_insurance...", end=' ')
n = insert('vehicle_insurance', ['vehicle_id','insurance_no','company','type','premium','coverage_amount','start_date','end_date','status','notes','created_at','updated_at'], [
    (pick(VEH_IDS), f'INS{random.randint(100000,999999)}',
     random.choice(['平安','人保','太平洋']),
     random.choice(['交强险','商业险','车损险','三者险']),
     round(random.uniform(2000,15000),2), round(random.uniform(50000,1000000),2),
     rand_date(800), (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
     'active', None, rand_dt(800), rand_dt(800))
    for _ in range(5)
])
print(f'{n} rows')

# 5.4 vehicle_maintenance_records
print("vehicle_maintenance_records...", end=' ')
n = insert('vehicle_maintenance_records', ['vehicle_id','maintenance_no','type','mileage','cost','maintenance_date','workshop','description','next_date','status','created_at','updated_at'], [
    (pick(VEH_IDS), f'MT{random.randint(10000,99999)}',
     random.choice(['常规保养','维修','事故修复','年检']),
     random.randint(10000,200000), round(random.uniform(200,5000),2),
     rand_date(800), random.choice(['4S店','普通修理厂','专修店']),
     '更换机油滤清器', (datetime.now() + timedelta(days=random.randint(90,365))).strftime('%Y-%m-%d'),
     'completed', rand_dt(800), rand_dt(800))
    for _ in range(20)
])
print(f'{n} rows')

# ============== 第 6 步：售后/排班/审批 ==============
print("\n=== Step 6: Service/Schedule/Approval ===")

# 6.1 service_order_parts
print("service_order_parts...", end=' ')
n = insert('service_order_parts', ['service_order_id','inventory_item_id','part_name','quantity','unit_cost','total_cost','created_at','updated_at'], [
    (pick(SVC_IDS), pick(INV_IDS) if random.random() > 0.3 else None,
     f'配件-{random.randint(1,9999)}', random.randint(1,10),
     round(random.uniform(10,500),2), round(random.uniform(10,5000),2),
     rand_dt(800), rand_dt(800))
    for _ in range(40)
])
print(f'{n} rows')

# 6.2 schedules
print("schedules...", end=' ')
SHIFT_IDS = get_ids('shifts')
n = insert('schedules', ['user_id','group_id','shift_id','date','status','note','created_by','created_at','updated_at'], [
    (pick(USER_IDS), None, pick(SHIFT_IDS), rand_date(120),
     random.choice(['scheduled','completed','absent','leave']),
     None, pick(USER_IDS), rand_dt(120), rand_dt(120))
    for _ in range(120)
])
print(f'{n} rows')

# 6.3 shift_groups
print("shift_groups...", end=' ')
n = insert('shift_groups', ['name','code','leader_id','color','description','is_active','created_at','updated_at'], [
    ('A组', f'SG-A{random.randint(10,99)}', pick(USER_IDS), '#1D9E75', '白班小组', True, rand_dt(900), rand_dt(900)),
    ('B组', f'SG-B{random.randint(10,99)}', pick(USER_IDS), '#BA7517', '夜班小组', True, rand_dt(900), rand_dt(900)),
    ('C组', f'SG-C{random.randint(10,99)}', pick(USER_IDS), '#534AB7', '机动小组', True, rand_dt(900), rand_dt(900)),
])
print(f'{n} rows')
SG_IDS = get_ids('shift_groups')

# 6.4 shift_group_members
print("shift_group_members...", end=' ')
seen = set()
mem_vals = []
attempts = 0
while len(mem_vals) < 12 and attempts < 200:
    pair = (pick(SG_IDS), pick(USER_IDS))
    if pair not in seen:
        seen.add(pair)
        mem_vals.append((pair[0], pair[1], rand_date(800), rand_dt(800), rand_dt(800)))
    attempts += 1
n = insert('shift_group_members', ['group_id','user_id','joined_at','created_at','updated_at'], mem_vals)
print(f'{n} rows')

# 6.5 approval_records
print("approval_records...", end=' ')
n = insert('approval_records', ['approvable_type','approvable_id','approver_id','level','action','comment','approved_at','created_at','updated_at'], [
    (random.choice(['Project','ExpenseClaim','LeaveRequest','PurchaseOrder']),
     random.randint(1, 100), pick(USER_IDS), random.randint(1,3),
     random.choice(['approved','rejected','pending']),
     '审批意见', rand_dt(900), rand_dt(900), rand_dt(900))
    for _ in range(80)
])
print(f'{n} rows')

# 6.6 approval_templates
print("approval_templates...", end=' ')
n = insert('approval_templates', ['name','type','steps','is_active','description','created_at','updated_at'], [
    ('请假审批', 'leave', json.dumps([{'level':1,'role':'直属上级'},{'level':2,'role':'部门经理'}]), True, '标准请假流程', rand_dt(900), rand_dt(900)),
    ('报销审批', 'expense', json.dumps([{'level':1,'role':'直属上级'},{'level':2,'role':'财务'},{'level':3,'role':'总经理'}]), True, '标准报销流程', rand_dt(900), rand_dt(900)),
    ('采购审批', 'purchase', json.dumps([{'level':1,'role':'采购主管'},{'level':2,'role':'经理'}]), True, '采购流程', rand_dt(900), rand_dt(900)),
])
print(f'{n} rows')

# ============== 第 7 步：网盘/知识库/流程 ==============
print("\n=== Step 7: Disk/Knowledge/Process ===")

# 7.1 disk_folders
print("disk_folders...", end=' ')
n = insert('disk_folders', ['name','parent_id','owner_id','path','is_public','created_at','updated_at'], [
    ('项目资料', None, pick(USER_IDS), '/项目资料', True, rand_dt(900), rand_dt(900)),
    ('合同模板', None, pick(USER_IDS), '/合同模板', True, rand_dt(900), rand_dt(900)),
    ('技术文档', None, pick(USER_IDS), '/技术文档', True, rand_dt(900), rand_dt(900)),
    ('客户资料', None, pick(USER_IDS), '/客户资料', False, rand_dt(900), rand_dt(900)),
])
print(f'{n} rows')
FOLDER_IDS = get_ids('disk_folders')

# 7.2 disk_files
print("disk_files...", end=' ')
n = insert('disk_files', ['folder_id','name','path','size','mime_type','extension','uploaded_by','created_at','updated_at'], [
    (pick(FOLDER_IDS), f'文件-{random.randint(1,9999)}.pdf', f'/files/{random.randint(1000,9999)}.pdf',
     random.randint(1000,10000000),
     random.choice(['application/pdf','image/jpeg','application/vnd.ms-excel','application/msword']),
     random.choice(['pdf','jpg','xls','doc']),
     pick(USER_IDS), rand_dt(900), rand_dt(900))
    for _ in range(60)
])
print(f'{n} rows')

# 7.3 disk_settings
print("disk_settings...", end=' ')
n = insert('disk_settings', ['user_id','total_quota','used_space','is_default','created_at','updated_at'], [
    (uid, 1073741824, random.randint(1000000, 100000000), True, rand_dt(900), rand_dt(900))
    for uid in USER_IDS
])
print(f'{n} rows')

# 7.4 knowledge_categories
KC_IDS = get_ids('knowledge_categories')
if not KC_IDS:
    n = insert('knowledge_categories', ['name','parent_id','sort','description','created_at','updated_at'], [
        ('技术文档', None, 1, '技术类', rand_dt(900), rand_dt(900)),
        ('业务流程', None, 2, '业务类', rand_dt(900), rand_dt(900)),
        ('常见问题', None, 3, 'FAQ', rand_dt(900), rand_dt(900)),
    ])
    print(f"knowledge_categories: {n} rows (new)")
    KC_IDS = get_ids('knowledge_categories')
else:
    print(f"knowledge_categories: {len(KC_IDS)} (existing)")

# 7.5 knowledge_articles
print("knowledge_articles...", end=' ')
n = insert('knowledge_articles', ['title','category_id','content','author_id','view_count','like_count','is_published','published_at','created_at','updated_at'], [
    (f'知识库文章-{random.randint(1,9999)}', pick(KC_IDS), '这是文章内容...',
     pick(USER_IDS), random.randint(0,500), random.randint(0,100),
     True, rand_dt(900), rand_dt(900), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

# 7.6 process_templates
PT_IDS = get_ids('process_templates')
print(f"process_templates: {len(PT_IDS)} (existing)")

# 7.7 process_instances
print("process_instances...", end=' ')
n = insert('process_instances', ['template_id','business_type','business_id','applicant_id','current_node','status','started_at','completed_at','created_at','updated_at'], [
    (pick(PT_IDS) if PT_IDS else None, random.choice(['leave','expense','purchase']),
     random.randint(1, 100), pick(USER_IDS), '审批中',
     random.choice(['pending','approved','rejected','in_progress']),
     rand_dt(300), rand_dt(100) if random.random() > 0.5 else None,
     rand_dt(300), rand_dt(300))
    for _ in range(50)
])
print(f'{n} rows')

# 7.8 process_inspections
print("process_inspections...", end=' ')
n = insert('process_inspections', ['process_instance_id','node_name','inspector_id','result','comment','inspected_at','created_at','updated_at'], [
    (None, f'节点{random.randint(1,5)}', pick(USER_IDS),
     random.choice(['pass','reject','pending']),
     '验收意见', rand_dt(300), rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# 7.9 process_signatures
print("process_signatures...", end=' ')
n = insert('process_signatures', ['process_instance_id','signer_id','signature_path','signed_at','ip_address','created_at','updated_at'], [
    (None, pick(USER_IDS), f'/signatures/{random.randint(1000,9999)}.png',
     rand_dt(300), f'192.168.1.{random.randint(1,254)}',
     rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# 7.10 process_images
print("process_images...", end=' ')
n = insert('process_images', ['process_instance_id','image_path','thumbnail_path','uploaded_by','created_at','updated_at'], [
    (None, f'/process/{random.randint(1000,9999)}.jpg', f'/process/thumb_{random.randint(1000,9999)}.jpg',
     pick(USER_IDS), rand_dt(300), rand_dt(300))
    for _ in range(30)
])
print(f'{n} rows')

# 7.11 project_pool
print("project_pool...", end=' ')
n = insert('project_pool', ['name','description','customer_id','manager_id','status','expected_value','created_at','updated_at'], [
    (f'项目池-{random.randint(1,9999)}', '潜在项目', pick(CUST_IDS), pick(USER_IDS),
     random.choice(['potential','negotiating','quoted','won','lost']),
     round(random.uniform(50000,5000000),2), rand_dt(900), rand_dt(900))
    for _ in range(20)
])
print(f'{n} rows')

# 7.12 referrers
print("referrers...", end=' ')
n = insert('referrers', ['name','phone','email','company','relationship','status','notes','created_at','updated_at'], [
    (f'介绍人-{random.randint(1,9999)}', f'1{random.randint(3,9)}{random.randint(10000000,99999999)}',
     f'ref{random.randint(1,9999)}@example.com', f'公司{random.randint(1,999)}',
     random.choice(['老客户','朋友','合作伙伴','其他']),
     'active', None, rand_dt(900), rand_dt(900))
    for _ in range(15)
])
print(f'{n} rows')

# 7.13 approval_records_v2
print("approval_records_v2...", end=' ')
n = insert('approval_records_v2', ['flow_type','flow_id','approver_id','step','action','comment','created_at','updated_at'], [
    (random.choice(['leave','expense','purchase','project']),
     random.randint(1, 100), pick(USER_IDS), random.randint(1,3),
     random.choice(['approved','rejected']), '审批', rand_dt(900), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

# 7.14 cache_locks (Laravel 框架表)
print("cache_locks...", end=' ')
n = insert('cache_locks', ['key','owner','expiration'], [
    (f'lock_{i}', f'owner_{i}', 9999999999) for i in range(5)
])
print(f'{n} rows')

ssh.close()
print("\n=== ALL DONE ===")
