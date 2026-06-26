"""批量生成 172 服务器测试数据 v2 - 按依赖顺序
- 基础数据(无依赖): skill_tags, positions, warehouses, departments
- 关联 user: employee_profiles
- 关联 employee_profile: employee_skills, certificates, employee_onboardings, employee_resignations
- 关联 project: project_contracts, project_materials, project_settlements, construction_logs, contract_payment_nodes
- 关联 inventory_item: device_serial_numbers
- 关联 customer_device: device_serial_numbers
"""
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

def get_ids(table, where=''):
    cmd = f"{PG} -t -A -c \"SELECT id FROM {table} {where} ORDER BY id;\""
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

# ============== 加载外键 ==============
print("Loading FK...")
USER_IDS = get_ids('users')
CUST_IDS = get_ids('customers')
PROJ_IDS = get_ids('projects')
VEH_IDS = get_ids('vehicles')
LEAD_IDS = get_ids('leads')
OPP_IDS = get_ids('opportunities')
SVC_IDS = get_ids('service_orders')
INV_IDS = get_ids('inventory_items')
print(f"users={len(USER_IDS)} customers={len(CUST_IDS)} projects={len(PROJ_IDS)} vehicles={len(VEH_IDS)} leads={len(LEAD_IDS)} opps={len(OPP_IDS)} svcs={len(SVC_IDS)} inv={len(INV_IDS)}")

def pick(xs):
    return random.choice(xs) if xs else None

# ============== 第 1 步: 无依赖基础表 ==============
print("\n=== Step 1: Base tables ===")

# 1.1 skill_tags
print("skill_tags...", end=' ')
n = insert('skill_tags', ['name', 'category', 'description', 'created_at', 'updated_at'], [
    ('网络工程', '技术', '网络规划与配置', rand_dt(2000), rand_dt(900)),
    ('安防系统', '技术', '视频监控/门禁/报警', rand_dt(2000), rand_dt(900)),
    ('弱电集成', '技术', '综合布线', rand_dt(2000), rand_dt(900)),
    ('Python', '编程', '自动化脚本', rand_dt(2000), rand_dt(900)),
    ('项目管理', '管理', 'PMP体系', rand_dt(2000), rand_dt(900)),
    ('客户沟通', '管理', '需求挖掘', rand_dt(2000), rand_dt(900)),
    ('CAD制图', '技术', 'AutoCAD工程图', rand_dt(2000), rand_dt(900)),
    ('数据库', '技术', 'PostgreSQL/MySQL', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')

# 1.2 positions
print("positions...", end=' ')
n = insert('positions', ['name', 'department', 'level', 'description', 'created_at', 'updated_at'], [
    ('技术总监', '技术部', 'P8', '技术团队负责人', rand_dt(2000), rand_dt(900)),
    ('项目经理', '项目部', 'P6', '项目交付管理', rand_dt(2000), rand_dt(900)),
    ('高级工程师', '技术部', 'P7', '核心技术骨干', rand_dt(2000), rand_dt(900)),
    ('工程师', '技术部', 'P5', '项目实施工程师', rand_dt(2000), rand_dt(900)),
    ('销售经理', '销售部', 'P6', '销售团队管理', rand_dt(2000), rand_dt(900)),
    ('销售代表', '销售部', 'P4', '客户开发', rand_dt(2000), rand_dt(900)),
    ('财务主管', '财务部', 'P6', '财务管理', rand_dt(2000), rand_dt(900)),
    ('行政专员', '行政部', 'P4', '行政事务', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')

# 1.3 departments (补几个)
print("departments...", end=' ')
n = insert('departments', ['name', 'parent_id', 'manager_id', 'description', 'created_at', 'updated_at'], [
    ('技术部', None, pick(USER_IDS), '负责技术研发', rand_dt(2000), rand_dt(900)),
    ('项目部', None, pick(USER_IDS), '负责项目实施', rand_dt(2000), rand_dt(900)),
    ('销售部', None, pick(USER_IDS), '负责销售业务', rand_dt(2000), rand_dt(900)),
    ('财务部', None, pick(USER_IDS), '负责财务管理', rand_dt(2000), rand_dt(900)),
    ('行政部', None, pick(USER_IDS), '负责行政事务', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')

# 1.4 warehouses
print("warehouses...", end=' ')
n = insert('warehouses', ['code', 'name', 'location', 'manager_id', 'capacity', 'status', 'created_at', 'updated_at'], [
    (f'WH-{random.randint(100,999)}', '北京主仓', '北京市朝阳区', pick(USER_IDS), 1000, 'active', rand_dt(2000), rand_dt(900)),
    (f'WH-{random.randint(100,999)}', '上海分仓', '上海市浦东新区', pick(USER_IDS), 500, 'active', rand_dt(2000), rand_dt(900)),
    (f'WH-{random.randint(100,999)}', '广州分仓', '广州市天河区', pick(USER_IDS), 500, 'active', rand_dt(2000), rand_dt(900)),
])
print(f'{n} rows')

# 1.5 stock_records
print("stock_records...", end=' ')
warehouse_ids = get_ids('warehouses')
n = insert('stock_records', ['warehouse_id', 'inventory_item_id', 'quantity', 'type', 'notes', 'created_at', 'updated_at'], [
    (pick(warehouse_ids), pick(INV_IDS), random.randint(10,100), 'in', '初始入库', rand_dt(900), rand_dt(900))
    for _ in range(40)
])
print(f'{n} rows')

# ============== 第 2 步: 关联 user ==============
print("\n=== Step 2: User-related ===")

# 2.1 employee_profiles
print("employee_profiles...", end=' ')
emp_vals = []
for uid in USER_IDS:
    emp_vals.append((
        uid,
        f'E{datetime.now().year}{random.randint(1000,9999)}',
        rand_date(2000),
        None,
        random.choice(['open', 'fixed', 'part_time']),
        rand_date(2000),
        (datetime.now() + timedelta(days=random.randint(365,1095))).strftime('%Y-%m-%d'),
        round(random.uniform(8000, 30000), 2),
        round(random.uniform(1000, 5000), 2),
        '紧急联系人',
        f'1{random.randint(3,9)}{random.randint(10000000,99999999)}',
        random.choice(['工商银行', '建设银行', '招商银行']),
        f'{random.randint(622202,622299)}{random.randint(1000000,9999999)}',
        None,
        rand_dt(2000), rand_dt(900)
    ))
n = insert('employee_profiles', ['user_id','employee_no','hire_date','leave_date','contract_type','contract_start','contract_end','base_salary','salary_allowance','emergency_contact','emergency_phone','bank_name','bank_account','notes','created_at','updated_at'], emp_vals)
print(f'{n} rows')

EMP_IDS = get_ids('employee_profiles')
print(f"  -> employee_profile ids: {EMP_IDS}")

# 2.2 employee_skills
print("employee_skills...", end=' ')
SKILL_IDS = get_ids('skill_tags')
n = insert('employee_skills', ['employee_profile_id','skill_tag_id','proficiency','created_at','updated_at'], [
    (pick(EMP_IDS), pick(SKILL_IDS), random.choice(['beginner','intermediate','advanced','expert']), rand_dt(2000), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

# 2.3 certificates
print("certificates...", end=' ')
cert_vals = []
for emp_id in EMP_IDS:
    for _ in range(3):
        issued = datetime.now() - timedelta(days=random.randint(100, 1500))
        cert_vals.append((
            emp_id,
            f'{random.choice(["一级","二级","三级"])}{random.choice(["建造师","安全员","工程师"])}',
            f'CERT{datetime.now().year}{random.randint(10000,99999)}',
            issued.strftime('%Y-%m-%d'),
            (issued + timedelta(days=365*3)).strftime('%Y-%m-%d'),
            random.choice(['住建部', '安监局', '人社部']),
            random.choice(['valid', 'expired', 'expiring']),
            None,
            30,
            rand_dt(2000), rand_dt(900)
        ))
n = insert('certificates', ['employee_profile_id','certificate_name','certificate_no','issue_date','expire_date','issuer','status','attachment','remind_days','created_at','updated_at'], cert_vals)
print(f'{n} rows')

# 2.4 employee_onboardings
print("employee_onboardings...", end=' ')
DEPT_IDS = get_ids('departments')
POS_IDS = get_ids('positions')
n = insert('employee_onboardings', ['user_id','hire_date','department_id','position_id','mentor_id','probation_months','probation_end_date','contract_start','contract_end','id_card_no','notes','status','created_at','updated_at'], [
    (uid, rand_date(2000), pick(DEPT_IDS), pick(POS_IDS), pick(USER_IDS), random.choice([1,3,6]),
     (datetime.now() - timedelta(days=random.randint(30,180))).strftime('%Y-%m-%d'),
     rand_date(2000), (datetime.now() + timedelta(days=random.randint(365,1095))).strftime('%Y-%m-%d'),
     f'110{random.randint(19800101,20050101)}', '入职流程', 'completed', rand_dt(2000), rand_dt(900))
    for uid in USER_IDS
])
print(f'{n} rows')

# 2.5 employee_resignations
print("employee_resignations...", end=' ')
n = insert('employee_resignations', ['user_id','resign_date','reason','handover_to','notes','status','created_at','updated_at'], [
    (pick(USER_IDS), rand_date(800), random.choice(['个人发展','家庭原因','薪资','其他']),
     pick(USER_IDS), '已交接', 'approved', rand_dt(800), rand_dt(800))
    for _ in range(2)
])
print(f'{n} rows')

ssh.close()
print("\n=== Step 1-2 done ===")
