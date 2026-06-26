"""最后一波 - 收尾所有失败"""
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

def rand_dt(days_back=365):
    return (datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0,23), minutes=random.randint(0,59))).strftime('%Y-%m-%d %H:%M:%S')
def pick(xs):
    return random.choice(xs) if xs else None

USER_IDS = get_ids('users')
PI_IDS = get_ids('process_instances')
FOLDER_IDS = get_ids('disk_folders')

# 1. employee_skills (unique 违反)
print("employee_skills...", end=' ')
EMP_IDS = get_ids('employee_profiles')
SKILL_IDS = get_ids('skill_tags')
# 拿到已有 (emp, skill) 组合
cmd = f"{PG} -t -A -c \"SELECT employee_profile_id||'-'||skill_tag_id FROM employee_skills;\""
stdin, stdout, stderr = ssh.exec_command(cmd)
existing = set(stdout.read().decode().strip().split('\n'))
print(f"  existing: {len(existing)}")

pairs = set()
skill_vals = []
attempts = 0
while len(skill_vals) < 20 and attempts < 2000:
    eid, sid = pick(EMP_IDS), pick(SKILL_IDS)
    k = f'{eid}-{sid}'
    if k not in existing and k not in pairs:
        pairs.add(k)
        skill_vals.append((eid, sid, random.choice(['beginner','intermediate','advanced','expert']), rand_dt(2000), rand_dt(900)))
    attempts += 1
n = insert('employee_skills', ['employee_profile_id','skill_tag_id','proficiency','created_at','updated_at'], skill_vals)
print(f'{n} rows')

# 2. disk_settings (json 报错 - 实际值需要 double quotes)
print("disk_settings...", end=' ')
n = insert('disk_settings', ['key','value','created_at','updated_at'], [
    (f'user_quota_{uid}', '{"quota":1073741824,"used":100000}', rand_dt(900), rand_dt(900))
    for uid in USER_IDS
])
print(f'{n} rows')

# 3. process_inspections (inspection_date 必填)
print("process_inspections...", end=' ')
n = insert('process_inspections', ['process_instance_id','inspection_type','inspector_id','inspector_name','inspection_date','created_at','updated_at'], [
    (pick(PI_IDS), random.choice(['initial','final','spot','acceptance']),
     pick(USER_IDS), f'检查员{random.randint(1,5)}',
     rand_dt(300), rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# 4. process_signatures (signature_data 必填)
print("process_signatures...", end=' ')
n = insert('process_signatures', ['process_instance_id','inspection_id','signer_type','signer_id','signer_name','signature_data','created_at','updated_at'], [
    (pick(PI_IDS), None, random.choice(['user','customer','supervisor']),
     pick(USER_IDS), f'签字人{random.randint(1,5)}',
     'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==',  # 占位 data
     rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

# 5. process_images (file_path 必填)
print("process_images...", end=' ')
n = insert('process_images', ['process_instance_id','inspection_id','category','file_type','file_name','file_path','created_at','updated_at'], [
    (pick(PI_IDS), None, random.choice(['before','after','issue','other']),
     random.choice(['image','document']),
     f'file_{random.randint(1,9999)}.jpg',
     f'/process_images/{random.randint(1000,9999)}.jpg',
     rand_dt(300), rand_dt(300))
    for _ in range(30)
])
print(f'{n} rows')

# 6. approval_records_v2 (applicant_id 必填)
print("approval_records_v2...", end=' ')
n = insert('approval_records_v2', ['code','type','sub_type','title','priority','status','amount','applicant_id','created_at','updated_at'], [
    (f'AR{datetime.now().strftime("%H%M%S%f")[:10]}-{random.randint(100,999)}',
     random.choice(['leave','expense','purchase','project']),
     random.choice(['standard','urgent','special']),
     f'审批-{random.randint(1,9999)}',
     random.choice(['low','normal','high','urgent']),
     random.choice(['pending','approved','rejected']),
     round(random.uniform(100,100000),2),
     pick(USER_IDS),
     rand_dt(900), rand_dt(900))
    for _ in range(50)
])
print(f'{n} rows')

ssh.close()
print("\n=== ALL DONE ===")
