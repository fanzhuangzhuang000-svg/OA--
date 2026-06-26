"""最后一波修复 - 唯一约束 / 字段名 / check 约束"""
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
    return [int(x) for x in stdout.read().decode().strip().split('\n') if x.strip().isdigit()]

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

# FK
USER_IDS = get_ids('users')
CUST_IDS = get_ids('customers')
PROJ_IDS = get_ids('projects')
VEH_IDS = get_ids('vehicles')
INV_IDS = get_ids('inventory_items')
WH_IDS = get_ids('warehouses')
SHIFT_IDS = get_ids('shifts')
KC_IDS = get_ids('knowledge_categories')
SVC_IDS = get_ids('service_orders')
SG_IDS = get_ids('shift_groups')
FU_IDS = get_ids('sales_follow_ups')
PI_IDS = get_ids('process_instances')

# ============== 1. stock_records (加 timestamp 区分) ==============
print("stock_records...", end=' ')
n = insert('stock_records', ['record_no','inventory_item_id','warehouse_id','type','quantity','remaining_stock','operator_id','remark','created_at','updated_at','project_id'], [
    (f'SR-{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(100,999)}', pick(INV_IDS), pick(WH_IDS),
     random.choice(['in','out']), random.randint(5,50), random.randint(5,50),
     pick(USER_IDS), random.choice(['采购入库','项目领用','调拨']),
     rand_dt(900), rand_dt(900), pick(PROJ_IDS) if random.random() > 0.3 else None)
    for _ in range(80)
])
print(f'{n} rows')

# ============== 2. employee_skills (去重) ==============
print("employee_skills...", end=' ')
EMP_IDS = get_ids('employee_profiles')
SKILL_IDS = get_ids('skill_tags')
pairs = set()
skill_vals = []
attempts = 0
while len(skill_vals) < 30 and attempts < 1000:
    eid, sid = pick(EMP_IDS), pick(SKILL_IDS)
    if (eid, sid) not in pairs:
        pairs.add((eid, sid))
        skill_vals.append((eid, sid, random.choice(['beginner','intermediate','advanced','expert']), rand_dt(2000), rand_dt(900)))
    attempts += 1
n = insert('employee_skills', ['employee_profile_id','skill_tag_id','proficiency','created_at','updated_at'], skill_vals)
print(f'{n} rows')

# ============== 3. device_serial_numbers (timestamp 去重) ==============
print("device_serial_numbers...", end=' ')
CDEV_IDS = get_ids('customer_devices')
STOCK_IDS = get_ids('stock_records')
n = insert('device_serial_numbers', ['inventory_item_id','serial_number','status','project_id','customer_device_id','stock_record_id','install_date','notes','created_at','updated_at'], [
    (pick(INV_IDS), f'SN-{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(1000,9999)}',
     random.choice(['in_stock','assigned','in_use','retired']),
     pick(PROJ_IDS) if random.random() > 0.3 else None,
     pick(CDEV_IDS) if random.random() > 0.5 else None,
     pick(STOCK_IDS) if random.random() > 0.5 else None,
     rand_date(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for _ in range(80)
])
print(f'{n} rows')

# ============== 4. project_contracts (timestamp 去重) ==============
print("project_contracts...", end=' ')
n = insert('project_contracts', ['project_id','contract_no','contract_amount','payment_method','contract_start','contract_end','status','signed_at','notes','created_at','updated_at'], [
    (pid, f'CT-{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(100,999)}',
     round(random.uniform(50000,5000000),2),
     random.choice(['installment','lump_sum','milestone']),
     rand_date(900), (datetime.now() + timedelta(days=random.randint(180,730))).strftime('%Y-%m-%d'),
     random.choice(['draft','active','completed','terminated']),
     rand_dt(900) if random.random() > 0.3 else None,
     None, rand_dt(900), rand_dt(900))
    for pid in PROJ_IDS[:40]
])
print(f'{n} rows')

# ============== 5. sales_follow_up_attachments (实际列: name, path, mime, size) ==============
print("sales_follow_up_attachments...", end=' ')
n = insert('sales_follow_up_attachments', ['follow_up_id','name','path','mime','size','created_at','updated_at'], [
    (pick(FU_IDS), f'附件{random.randint(1,9999)}.pdf', f'/uploads/{random.randint(1000,9999)}.pdf',
     'application/pdf', random.randint(1000,5000000), rand_dt(900), rand_dt(900))
    for _ in range(30)
])
print(f'{n} rows')

# ============== 6. fuel_card_recharges (实际列: card_id, amount, recharge_date, payment_method, operator, voucher_no) ==============
print("fuel_card_recharges...", end=' ')
FC_IDS = get_ids('fuel_cards')
n = insert('fuel_card_recharges', ['card_id','amount','recharge_date','payment_method','operator','voucher_no','notes','created_at','updated_at'], [
    (pick(FC_IDS), round(random.uniform(500,3000),2), rand_date(800),
     random.choice(['现金','转账','油票']),
     f'操作员{random.randint(1,5)}',
     f'V{random.randint(100000,999999)}',
     '充值', rand_dt(800), rand_dt(800))
    for _ in range(20)
])
print(f'{n} rows')

# ============== 7. vehicle_insurance (实际列: vehicle_id, insurance_company, policy_no, type, premium, start_date, end_date) ==============
print("vehicle_insurance...", end=' ')
n = insert('vehicle_insurance', ['vehicle_id','insurance_company','policy_no','type','premium','start_date','end_date','status','notes','created_at','updated_at'], [
    (pick(VEH_IDS), random.choice(['平安','人保','太平洋']),
     f'POL-{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(100,999)}',
     random.choice(['交强险','商业险','车损险','三者险']),
     round(random.uniform(2000,15000),2),
     rand_date(800), (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
     'active', None, rand_dt(800), rand_dt(800))
    for _ in range(5)
])
print(f'{n} rows')

# ============== 8. vehicle_maintenance_records (实际列: vehicle_id, maintenance_type, mileage, cost, maintenance_date, description, next_maintenance_mileage, next_maintenance_date, handled_by) ==============
print("vehicle_maintenance_records...", end=' ')
n = insert('vehicle_maintenance_records', ['vehicle_id','maintenance_type','mileage','cost','maintenance_date','description','next_maintenance_mileage','next_maintenance_date','handled_by','created_at','updated_at'], [
    (pick(VEH_IDS), random.choice(['routine','repair','inspection','accident']),
     random.randint(10000,200000), round(random.uniform(200,5000),2),
     rand_date(800), '更换机油滤清器',
     random.randint(50000,250000), (datetime.now() + timedelta(days=random.randint(90,365))).strftime('%Y-%m-%d'),
     pick(USER_IDS), rand_dt(800), rand_dt(800))
    for _ in range(20)
])
print(f'{n} rows')

# ============== 9. schedules (status check: scheduled/rest/sick/leave) ==============
print("schedules...", end=' ')
# 先清掉之前的
run("DELETE FROM schedules")
existing = set()  # (user_id, date) 去重
vals = []
attempts = 0
while len(vals) < 200 and attempts < 1000:
    uid = pick(USER_IDS)
    d = rand_date(180)
    if (uid, d) not in existing:
        existing.add((uid, d))
        vals.append((uid, pick(SG_IDS) if SG_IDS else None, pick(SHIFT_IDS), d,
                     random.choice(['scheduled','rest','sick','leave']),
                     None, pick(USER_IDS), rand_dt(180), rand_dt(180)))
    attempts += 1
n = insert('schedules', ['user_id','group_id','shift_id','date','status','note','created_by','created_at','updated_at'], vals)
print(f'{n} rows')

# ============== 10. approval_templates (steps 字段是 json) ==============
print("approval_templates...", end=' ')
# 看到错误是 'invalid input syntax for type json' - 说明 columns 没全对
# 实际列: name, type, module, description, steps, enabled, ...
# 试 steps 用 NULL（看是否 nullable）
n = insert('approval_templates', ['name','type','module','description','steps','enabled','created_at','updated_at'], [
    ('请假审批', 'leave', 'attendance', '标准请假流程', None, True, rand_dt(900), rand_dt(900)),
    ('报销审批', 'expense', 'finance', '标准报销流程', None, True, rand_dt(900), rand_dt(900)),
    ('采购审批', 'purchase', 'procurement', '采购流程', None, True, rand_dt(900), rand_dt(900)),
])
print(f'{n} rows')

# ============== 11. disk_files (实际列有 original_name 必填) ==============
print("disk_files...", end=' ')
# dump schema
cmd = f"{PG} -c \"\\d disk_files\" 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd)
schema = stdout.read().decode('utf-8', errors='replace')
print("  schema snippet:")
for line in schema.split('\n')[:20]:
    print('   ', line)
FOLDER_IDS = get_ids('disk_folders')
n = insert('disk_files', ['folder_id','name','original_name','path','size','mime_type','extension','uploaded_by','created_at','updated_at'], [
    (pick(FOLDER_IDS), f'file_{i}.pdf', f'原始-{random.randint(1,9999)}.pdf', f'/files/{i}.pdf',
     random.randint(1000,10000000),
     random.choice(['application/pdf','image/jpeg']),
     random.choice(['pdf','jpg']),
     pick(USER_IDS), rand_dt(900), rand_dt(900))
    for i in range(50)
])
print(f'{n} rows')

# ============== 12. disk_settings (key/value 模式) ==============
print("disk_settings...", end=' ')
n = insert('disk_settings', ['key','value','created_at','updated_at'], [
    (f'user_quota_{uid}', json.dumps({'quota':1073741824,'used':random.randint(0,1073741824)}), rand_dt(900), rand_dt(900))
    for uid in USER_IDS
])
print(f'{n} rows')

# ============== 13. knowledge_articles (实际列: title, content, category_id, author_id, tags, view_count, like_count, status, published_at, summary, cover_image, is_featured, slug) ==============
print("knowledge_articles...", end=' ')
# dump
cmd = f"{PG} -c \"\\d knowledge_articles\" 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd)
schema = stdout.read().decode('utf-8', errors='replace')
# 找 required columns
print("  schema snippet:")
for line in schema.split('\n')[:20]:
    print('   ', line)
# 试 title, content, category_id, author_id, view_count, like_count, status
n = insert('knowledge_articles', ['title','content','category_id','author_id','view_count','like_count','status','published_at','summary','created_at','updated_at'], [
    (f'知识库文章-{random.randint(1,9999)}', '这是文章内容...',
     pick(KC_IDS), pick(USER_IDS),
     random.randint(0,500), random.randint(0,100),
     random.choice(['draft','published','archived']),
     rand_dt(900) if random.random() > 0.3 else None,
     '文章摘要', rand_dt(900), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

# ============== 14. process_inspections (实际列: process_instance_id, inspection_type, inspector_id, inspector_name) ==============
print("process_inspections...", end=' ')
n = insert('process_inspections', ['process_instance_id','inspection_type','inspector_id','inspector_name','created_at','updated_at'], [
    (pick(PI_IDS), random.choice(['initial','final','spot','acceptance']),
     pick(USER_IDS), f'检查员{random.randint(1,5)}',
     rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# ============== 15. process_signatures (实际列: process_instance_id, inspection_id, signer_type, signer_id, signer_name) ==============
print("process_signatures...", end=' ')
n = insert('process_signatures', ['process_instance_id','inspection_id','signer_type','signer_id','signer_name','created_at','updated_at'], [
    (pick(PI_IDS), None, random.choice(['user','customer','supervisor']),
     pick(USER_IDS), f'签字人{random.randint(1,5)}',
     rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# ============== 16. process_images (实际列: process_instance_id, inspection_id, category, file_type, file_name) ==============
print("process_images...", end=' ')
n = insert('process_images', ['process_instance_id','inspection_id','category','file_type','file_name','created_at','updated_at'], [
    (pick(PI_IDS), None, random.choice(['before','after','issue','other']),
     random.choice(['image','document']),
     f'file_{random.randint(1,9999)}.jpg', rand_dt(300), rand_dt(300))
    for _ in range(30)
])
print(f'{n} rows')

# ============== 17. approval_records_v2 (实际列: code, type, sub_type, title, priority, status, amount) ==============
print("approval_records_v2...", end=' ')
n = insert('approval_records_v2', ['code','type','sub_type','title','priority','status','amount','created_at','updated_at'], [
    (f'AR{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(100,999)}',
     random.choice(['leave','expense','purchase','project']),
     random.choice(['standard','urgent','special']),
     f'审批-{random.randint(1,9999)}',
     random.choice(['low','normal','high','urgent']),
     random.choice(['pending','approved','rejected']),
     round(random.uniform(100,100000),2),
     rand_dt(900), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

ssh.close()
print("\n=== FINAL FIX DONE ===")
