"""修复 v3 失败的所有表 - 基于实际 schema"""
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

# 加载 FK
print("Loading FK...")
USER_IDS = get_ids('users')
CUST_IDS = get_ids('customers')
PROJ_IDS = get_ids('projects')
VEH_IDS = get_ids('vehicles')
INV_IDS = get_ids('inventory_items')
DEPT_IDS = get_ids('departments')
OPP_IDS = get_ids('opportunities')
WH_IDS = get_ids('warehouses')
SHIFT_IDS = get_ids('shifts')
PT_IDS = get_ids('process_templates')
KC_IDS = get_ids('knowledge_categories')
SVC_IDS = get_ids('service_orders')
SG_IDS = get_ids('shift_groups')
FU_IDS = get_ids('sales_follow_ups')
INVCAT_IDS = get_ids('inventory_categories')

print(f"depts={len(DEPT_IDS)} invcat={len(INVCAT_IDS)} wh={len(WH_IDS)}")

# ============== Fix 1: positions (有 department_id 外键) ==============
print("\n=== Fix 1: positions ===")
n = insert('positions', ['name','department_id','level','description','status','sort_order','created_at','updated_at'], [
    (name, pick(DEPT_IDS), level, desc, 'active', sort, rand_dt(2000), rand_dt(900))
    for name, level, desc, sort in [
        ('技术总监', 'P8', '技术团队负责人', 80),
        ('项目经理', 'P6', '项目交付管理', 60),
        ('高级工程师', 'P7', '核心技术骨干', 70),
        ('工程师', 'P5', '项目实施', 50),
        ('销售经理', 'P6', '销售团队管理', 60),
        ('销售代表', 'P4', '客户开发', 40),
        ('财务主管', 'P6', '财务管理', 60),
        ('行政专员', 'P4', '行政事务', 40),
    ]
])
print(f'{n} rows')
POS_IDS = get_ids('positions')

# 补 employee_onboardings 现在需要 position_id
print("re-do employee_onboardings with valid position_id...", end=' ')
# 先清掉 user_id_unique 冲突（之前的）
run("DELETE FROM employee_onboardings")
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

# ============== Fix 2: stock_records (record_no 唯一) ==============
print("\n=== Fix 2: stock_records ===")
def make_sr():
    return f'SR{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(100,999)}'
n = insert('stock_records', ['record_no','inventory_item_id','warehouse_id','type','quantity','remaining_stock','operator_id','remark','created_at','updated_at','project_id'], [
    (make_sr(), pick(INV_IDS), pick(WH_IDS),
     random.choice(['in','out']), random.randint(5,50), random.randint(5,50),
     pick(USER_IDS), random.choice(['采购入库','项目领用','调拨']), rand_dt(900), rand_dt(900), pick(PROJ_IDS) if random.random() > 0.3 else None)
    for _ in range(50)
])
print(f'{n} rows')

# ============== Fix 3: employee_skills (使用去重) ==============
print("\n=== Fix 3: employee_skills ===")
EMP_IDS = get_ids('employee_profiles')
SKILL_IDS = get_ids('skill_tags')
pairs = set()
skill_vals = []
attempts = 0
while len(skill_vals) < 50 and attempts < 500:
    eid, sid = pick(EMP_IDS), pick(SKILL_IDS)
    if (eid, sid) not in pairs:
        pairs.add((eid, sid))
        skill_vals.append((eid, sid, random.choice(['beginner','intermediate','advanced','expert']), rand_dt(2000), rand_dt(900)))
    attempts += 1
n = insert('employee_skills', ['employee_profile_id','skill_tag_id','proficiency','created_at','updated_at'], skill_vals)
print(f'{n} rows')

# ============== Fix 4: device_serial_numbers (serial 唯一) ==============
print("\n=== Fix 4: device_serial_numbers ===")
CDEV_IDS = get_ids('customer_devices')
STOCK_IDS = get_ids('stock_records')
def make_sn():
    return f'SN-{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(1000,9999)}'
n = insert('device_serial_numbers', ['inventory_item_id','serial_number','status','project_id','customer_device_id','stock_record_id','install_date','notes','created_at','updated_at'], [
    (pick(INV_IDS), make_sn(),
     random.choice(['in_stock','assigned','in_use','retired']),
     pick(PROJ_IDS) if random.random() > 0.3 else None,
     pick(CDEV_IDS) if random.random() > 0.5 else None,
     pick(STOCK_IDS) if random.random() > 0.5 else None,
     rand_date(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for _ in range(80)
])
print(f'{n} rows')

# ============== Fix 5: project_contracts (contract_no 唯一) ==============
print("\n=== Fix 5: project_contracts ===")
def make_ct():
    return f'CT{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(100,999)}'
n = insert('project_contracts', ['project_id','contract_no','contract_amount','payment_method','contract_start','contract_end','status','signed_at','notes','created_at','updated_at'], [
    (pid, make_ct(), round(random.uniform(50000,5000000),2),
     random.choice(['installment','lump_sum','milestone']),
     rand_date(900), (datetime.now() + timedelta(days=random.randint(180,730))).strftime('%Y-%m-%d'),
     random.choice(['draft','active','completed','terminated']),
     rand_dt(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for pid in PROJ_IDS[:30]
])
print(f'{n} rows')

# ============== Fix 6: construction_logs (json 字段处理) ==============
print("\n=== Fix 6: construction_logs ===")
# photos 是 json, 改用 '[]' 或正常 JSON
n = insert('construction_logs', ['project_id','user_id','work_date','weather','content','problems','solutions','photos','work_hours','location','status','created_at','updated_at'], [
    (pick(PROJ_IDS), pick(USER_IDS), rand_date(365),
     random.choice(['晴','多云','阴','小雨','大雨']),
     f'今日完成{random.choice(["布线","设备安装","调试","验收"])}工作',
     random.choice([None,'部分设备故障','线材不足','协调问题']),
     random.choice([None,'已更换设备','已补货','已沟通']),
     '[]',  # 用空数组
     round(random.uniform(4,10),1),
     random.choice(['北京市朝阳区','上海市浦东','广州市天河']),
     random.choice(['submitted','reviewed','rejected']),
     rand_dt(365), rand_dt(365))
    for _ in range(150)
])
print(f'{n} rows')

# ============== Fix 7: sales_products (category_id 实际是 inventory_categories) ==============
print("\n=== Fix 7: sales_products ===")
n = insert('sales_products', ['code','name','category_id','unit','spec','sale_price','cost_price','description','status','created_at','updated_at'], [
    (f'SP{datetime.now().strftime("%H%M%S")}{random.randint(100,999)}', f'销售产品-{random.randint(1,9999)}',
     pick(INVCAT_IDS) if INVCAT_IDS else None,
     random.choice(['个','箱','米','台']),
     f'规格{random.randint(1,100)}',
     round(random.uniform(100,5000),2), round(random.uniform(50,3000),2),
     '热销产品', 'active', rand_dt(900), rand_dt(900))
    for _ in range(20)
])
print(f'{n} rows')

# ============== Fix 8: sales_follow_up_attachments ==============
print("\n=== Fix 8: sales_follow_up_attachments ===")
# 找 schema
print("  schema:")
schema_cmd = f"{PG} -c \"\\d sales_follow_up_attachments\" 2>&1"
stdin, stdout, stderr = ssh.exec_command(schema_cmd)
print(stdout.read().decode()[:1500])

# 直接根据常见命名试
n = insert('sales_follow_up_attachments', ['follow_up_id','filename','path','size','mime_type','uploaded_by','created_at','updated_at'], [
    (pick(FU_IDS), f'附件{random.randint(1,9999)}.pdf', f'/uploads/{random.randint(1000,9999)}.pdf',
     random.randint(1000,5000000), 'application/pdf',
     pick(USER_IDS), rand_dt(900), rand_dt(900))
    for _ in range(30)
])
print(f'{n} rows')

# ============== Fix 9: vehicle 系列 ==============
print("\n=== Fix 9: vehicle ===")

# 9.1 fuel_cards (实际列: card_no, card_name, vehicle_id, balance, status, issue_date, expire_date, notes)
print("fuel_cards...", end=' ')
def make_fc():
    return f'FC{datetime.now().strftime("%H%M%S")}{random.randint(10000,99999)}'
n = insert('fuel_cards', ['card_no','card_name','vehicle_id','balance','status','issue_date','expire_date','notes','created_at','updated_at'], [
    (make_fc(), f'油卡{random.randint(1,9999)}', pick(VEH_IDS),
     round(random.uniform(100,5000),2), 'active', rand_date(800),
     (datetime.now() + timedelta(days=random.randint(365,1095))).strftime('%Y-%m-%d'),
     None, rand_dt(800), rand_dt(800))
    for _ in range(8)
])
print(f'{n} rows')
FC_IDS = get_ids('fuel_cards')

# 9.2 fuel_card_recharges (实际列查 schema)
print("  fuel_card_recharges schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d fuel_card_recharges\" 2>&1")
print(stdout.read().decode()[:1200])

# 试 card_id
n = insert('fuel_card_recharges', ['card_id','recharge_no','amount','recharge_date','operator_id','payment_method','notes','created_at','updated_at'], [
    (pick(FC_IDS), f'RE{datetime.now().strftime("%H%M%S")}{random.randint(10000,99999)}',
     round(random.uniform(500,3000),2), rand_date(800),
     pick(USER_IDS), random.choice(['现金','转账','油票']),
     '充值', rand_dt(800), rand_dt(800))
    for _ in range(20)
])
print(f'  fuel_card_recharges: {n} rows')

# 9.3 vehicle_insurance
print("  vehicle_insurance schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d vehicle_insurance\" 2>&1")
print(stdout.read().decode()[:1500])

# 9.4 vehicle_maintenance_records
print("  vehicle_maintenance_records schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d vehicle_maintenance_records\" 2>&1")
print(stdout.read().decode()[:1500])

# ============== Fix 10: schedules (status check 约束) ==============
print("\n=== Fix 10: schedules ===")
print("  schedules schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d schedules\" 2>&1")
print(stdout.read().decode()[:1500])

# 查 check 约束允许哪些值
n = insert('schedules', ['user_id','group_id','shift_id','date','status','note','created_by','created_at','updated_at'], [
    (pick(USER_IDS), pick(SG_IDS) if SG_IDS else None, pick(SHIFT_IDS), rand_date(120),
     'normal',  # 试试 normal
     None, pick(USER_IDS), rand_dt(120), rand_dt(120))
    for _ in range(50)
])
print(f'  with normal: {n} rows')

# ============== Fix 11: approval_records (user_id 替换 approver_id) ==============
print("\n=== Fix 11: approval_records ===")
n = insert('approval_records', ['approvable_type','approvable_id','user_id','action','comment','status','created_at','updated_at'], [
    (random.choice(['Project','ExpenseClaim','LeaveRequest','PurchaseOrder']),
     random.randint(1, 100), pick(USER_IDS),
     random.choice(['approved','rejected','pending']),
     '审批意见', random.choice(['pending','approved','rejected']),
     rand_dt(900), rand_dt(900))
    for _ in range(80)
])
print(f'{n} rows')

# ============== Fix 12: approval_templates (is_active → enabled) ==============
print("\n=== Fix 12: approval_templates ===")
n = insert('approval_templates', ['name','type','module','description','steps','enabled','created_at','updated_at'], [
    ('请假审批', 'leave', 'attendance', '标准请假流程',
     json.dumps([{'level':1,'role':'直属上级'},{'level':2,'role':'部门经理'}]),
     True, rand_dt(900), rand_dt(900)),
    ('报销审批', 'expense', 'finance', '标准报销流程',
     json.dumps([{'level':1,'role':'直属上级'},{'level':2,'role':'财务'}]),
     True, rand_dt(900), rand_dt(900)),
    ('采购审批', 'purchase', 'procurement', '采购流程',
     json.dumps([{'level':1,'role':'采购主管'},{'level':2,'role':'经理'}]),
     True, rand_dt(900), rand_dt(900)),
])
print(f'{n} rows')

# ============== Fix 13: disk 系列 ==============
print("\n=== Fix 13: disk ===")
# 13.1 disk_folders (owner_id → created_by)
print("disk_folders...", end=' ')
n = insert('disk_folders', ['name','parent_id','path','created_by','is_system','project_id','created_at','updated_at'], [
    (f'文件夹{random.randint(1,9999)}', None, f'/folder_{i}', pick(USER_IDS), False,
     pick(PROJ_IDS) if random.random() > 0.5 else None, rand_dt(900), rand_dt(900))
    for i in range(8)
])
print(f'{n} rows')
FOLDER_IDS = get_ids('disk_folders')

# 13.2 disk_files (owner_id → uploaded_by, folder_id 必填)
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

# 13.3 disk_settings (user_id 不存在, 用 key/value)
print("disk_settings...", end=' ')
n = insert('disk_settings', ['key','value','created_at','updated_at'], [
    (f'setting_{i}', json.dumps({'value': i*100, 'enabled': True}), rand_dt(900), rand_dt(900))
    for i in range(10)
])
print(f'{n} rows')

# ============== Fix 14: knowledge_articles (is_published 不存在) ==============
print("\n=== Fix 14: knowledge_articles ===")
print("  schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d knowledge_articles\" 2>&1")
print(stdout.read().decode()[:1500])

# ============== Fix 15: process_instances (business_type 不存在) ==============
print("\n=== Fix 15: process_instances ===")
# 看到 column 列表：project_id, template_id, parent_id, code, name, sequence, planned_*, ...
n = insert('process_instances', ['project_id','template_id','parent_id','code','name','sequence','planned_start_date','planned_end_date','actual_start_date','actual_end_date','planned_duration_days','status','created_at','updated_at'], [
    (pick(PROJ_IDS), pick(PT_IDS) if PT_IDS else None, None,
     f'PI{datetime.now().strftime("%H%M%S")}{random.randint(100,999)}',
     f'流程实例-{random.randint(1,9999)}',
     random.randint(1,10),
     rand_date(300), (datetime.now() + timedelta(days=random.randint(30,180))).strftime('%Y-%m-%d'),
     rand_date(300) if random.random() > 0.3 else None, rand_date(100) if random.random() > 0.5 else None,
     random.randint(1,30),
     random.choice(['pending','in_progress','completed','cancelled']),
     rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# ============== Fix 16: process_inspections, signatures, images ==============
print("\n=== Fix 16: process 子表 ===")
# dump schema
for t in ['process_inspections','process_signatures','process_images']:
    stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d {t}\" 2>&1")
    print(f'  {t}:')
    print(stdout.read().decode()[:800])

# ============== Fix 17: project_pool ==============
print("\n=== Fix 17: project_pool ===")
n = insert('project_pool', ['pool_no','opportunity_id','name','customer_id','contract_amount','signed_at','status','related_project_id','notes','created_at','updated_at'], [
    (f'PP{datetime.now().strftime("%H%M%S")}{random.randint(100,999)}',
     pick(OPP_IDS) if random.random() > 0.3 else None,
     f'项目池-{random.randint(1,9999)}',
     pick(CUST_IDS) if random.random() > 0.3 else None,
     round(random.uniform(50000,5000000),2),
     rand_date(900) if random.random() > 0.3 else None,
     random.choice(['pending','active','completed','cancelled']),
     pick(PROJ_IDS) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for _ in range(20)
])
print(f'{n} rows')

# ============== Fix 18: referrers (实际列: name, phone, customer_id, bank_account, bank_name, commission_rate, total_commission, notes) ==============
print("\n=== Fix 18: referrers ===")
n = insert('referrers', ['name','phone','customer_id','bank_account','bank_name','commission_rate','total_commission','notes','created_at','updated_at'], [
    (f'介绍人-{random.randint(1,9999)}', f'1{random.randint(3,9)}{random.randint(10000000,99999999)}',
     pick(CUST_IDS) if random.random() > 0.5 else None,
     f'{random.randint(622202,622299)}{random.randint(1000000,9999999)}',
     random.choice(['工商银行','建设银行','招商银行']),
     round(random.uniform(1,15),2), round(random.uniform(0,50000),2),
     None, rand_dt(900), rand_dt(900))
    for _ in range(15)
])
print(f'{n} rows')

# ============== Fix 19: approval_records_v2 ==============
print("\n=== Fix 19: approval_records_v2 ===")
print("  schema:")
stdin, stdout, stderr = ssh.exec_command(f"{PG} -c \"\\d approval_records_v2\" 2>&1")
print(stdout.read().decode()[:1200])

# ============== Fix 20: cache_locks (expiration integer 太小) ==============
print("\n=== Fix 20: cache_locks ===")
n = insert('cache_locks', ['key','owner','expiration'], [
    (f'lock_{i}_{random.randint(10000,99999)}', f'owner_{i}', 2147483647) for i in range(5)
])
print(f'{n} rows')

ssh.close()
print("\n=== FIX DONE ===")
