"""分批填充 172 服务器 59 张空表 + 补稀疏表"""
import paramiko, random
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

def cols(table):
    cmd = f"{PG} -t -A -c \"\\d {table}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raw = stdout.read().decode('utf-8', errors='replace')
    # 解析：'| col_name | type | ...'
    result = []
    for line in raw.split('\n'):
        if '|' in line and 'NOT NULL' not in line and 'character varying' in line or '|' in line and 'integer' in line or '|' in line and 'text' in line or '|' in line and 'timestamp' in line or '|' in line and 'numeric' in line or '|' in line and 'boolean' in line or '|' in line and 'date' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2 and parts[0] != 'Column' and not parts[0].startswith('Indexes') and not parts[0].startswith('---'):
                result.append(parts[0])
    return result

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
                else:
                    s = str(v).replace("'", "''")
                    cells.append(f"'{s}'")
            vals.append('(' + ','.join(cells) + ')')
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES {','.join(vals)};"
        out = run(sql)
        if 'ERROR' in out:
            # 提取第一个错误
            err_line = [l for l in out.split('\n') if 'ERROR' in l]
            print(f'  [FAIL] {err_line[0][:150] if err_line else out[:150]}')
            return total
        total += len(chunk)
    return total

def rand_date(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime('%Y-%m-%d')
def rand_dt(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0,23), minutes=random.randint(0,59))).strftime('%Y-%m-%d %H:%M:%S')

# 预加载
print("Loading foreign keys...")
USER_IDS = get_ids('users')
CUST_IDS = get_ids('customers')
PROJ_IDS = get_ids('projects')
VEH_IDS = get_ids('vehicles')
LEAD_IDS = get_ids('leads')
OPP_IDS = get_ids('opportunities')
SVC_IDS = get_ids('service_orders')
INV_IDS = get_ids('inventory_items')
NOTI_IDS = get_ids('notifications')
USAGE_IDS = get_ids('vehicle_usage_requests')
print(f"users={len(USER_IDS)} customers={len(CUST_IDS)} projects={len(PROJ_IDS)} vehicles={len(VEH_IDS)} leads={len(LEAD_IDS)} opps={len(OPP_IDS)} svcs={len(SVC_IDS)}")

def pick(xs, default=1):
    return random.choice(xs) if xs else default

# ============== 批次 1: 业务核心表 ==============
print("\n=== Batch 1: Core business ===")

# 1.1 customer_devices
print("customer_devices...", end=' ')
cols = ['customer_id', 'device_name', 'device_type', 'brand', 'model', 'serial_no', 'install_date', 'status', 'created_at', 'updated_at']
vals = []
for _ in range(60):
    vals.append((
        pick(CUST_IDS),
        f'摄像头-{random.randint(1,9999):04d}',
        random.choice(['摄像头', '门禁', '报警器', '对讲', '道闸']),
        random.choice(['海康', '大华', '宇视', '华为']),
        f'M{random.randint(100,9999)}',
        f'SN{random.randint(100000,999999)}',
        rand_date(900),
        random.choice(['active','inactive','maintenance']),
        rand_dt(900), rand_dt(900)
    ))
n = insert('customer_devices', cols, vals)
print(f'{n} rows')

# 1.2 device_serial_numbers
print("device_serial_numbers...", end=' ')
cols = ['serial_no', 'device_name', 'device_type', 'status', 'assigned_to', 'assigned_at', 'created_at', 'updated_at']
vals = []
for _ in range(80):
    vals.append((
        f'SN-{datetime.now().year}-{random.randint(10000,99999)}',
        f'设备-{random.randint(1,9999)}',
        random.choice(['IPC', 'NVR', '门禁', '对讲']),
        random.choice(['in_stock', 'assigned', 'in_use', 'retired']),
        pick(CUST_IDS, None) if random.random() > 0.3 else None,
        rand_dt(900) if random.random() > 0.3 else None,
        rand_dt(900), rand_dt(900)
    ))
n = insert('device_serial_numbers', cols, vals)
print(f'{n} rows')

# 1.3 employee_profiles (扩展 user 信息)
print("employee_profiles...", end=' ')
cols = ['user_id', 'employee_no', 'real_name', 'id_card', 'gender', 'birth_date', 'phone', 'emergency_contact', 'emergency_phone', 'address', 'join_date', 'education', 'major', 'graduation_school', 'position', 'level', 'status', 'created_at', 'updated_at']
vals = []
for uid in USER_IDS:
    for _ in range(3):
        vals.append((
            uid,
            f'E{datetime.now().year}{random.randint(1000,9999)}',
            random.choice(['张伟', '李娜', '王芳', '陈军', '刘洋', '杨敏', '黄磊', '周婷']),
            f'110{random.randint(19800101,20050101)}',
            random.choice(['男','女']),
            rand_date(8000),
            f'1{random.randint(3,9)}{random.randint(10000000,99999999)}',
            '紧急联系人',
            f'1{random.randint(3,9)}{random.randint(10000000,99999999)}',
            f'北京市朝阳区{random.randint(1,200)}号',
            rand_date(2000),
            random.choice(['本科', '大专', '硕士']),
            random.choice(['计算机', '电子', '通信', '自动化']),
            random.choice(['清华', '北大', '北航', '北邮']),
            random.choice(['工程师', '主管', '经理']),
            random.choice(['P5', 'P6', 'P7']),
            'active',
            rand_dt(2000), rand_dt(900)
        ))
n = insert('employee_profiles', cols, vals)
print(f'{n} rows')

# 1.4 employee_skills
print("employee_skills...", end=' ')
cols = ['user_id', 'skill_name', 'skill_level', 'certified', 'cert_no', 'cert_date', 'created_at', 'updated_at']
vals = []
for uid in USER_IDS:
    for _ in range(4):
        vals.append((
            uid,
            random.choice(['网络工程', '安防系统', 'Python', '项目管理', '客户沟通', 'CAD制图', '弱电集成']),
            random.choice(['初级', '中级', '高级', '专家']),
            random.random() > 0.5,
            f'CERT-{random.randint(10000,99999)}' if random.random() > 0.5 else None,
            rand_date(2000) if random.random() > 0.5 else None,
            rand_dt(2000), rand_dt(900)
        ))
n = insert('employee_skills', cols, vals)
print(f'{n} rows')

# 1.5 certificates
print("certificates...", end=' ')
cols = ['user_id', 'cert_type', 'cert_name', 'cert_no', 'issue_date', 'expire_date', 'issue_org', 'status', 'created_at', 'updated_at']
vals = []
for uid in USER_IDS:
    for _ in range(2):
        issued = datetime.now() - timedelta(days=random.randint(100, 1500))
        vals.append((
            uid,
            random.choice(['建造师', '安全员', '电工证', '高空作业', '工程师职称']),
            f'{random.choice(["一级","二级","三级"])}证书',
            f'CERT{datetime.now().year}{random.randint(10000,99999)}',
            issued.strftime('%Y-%m-%d'),
            (issued + timedelta(days=365*3)).strftime('%Y-%m-%d'),
            random.choice(['住建部', '安监局', '人社部']),
            random.choice(['有效', '过期', '即将过期']),
            rand_dt(2000), rand_dt(900)
        ))
n = insert('certificates', cols, vals)
print(f'{n} rows')

ssh.close()
print("\n=== Batch 1 done ===")
