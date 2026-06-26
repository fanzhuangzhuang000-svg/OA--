"""last-final fix"""
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

# 1. employee_skills (之前的还在 - skip 跳过)
# 2. disk_settings (json 报错 - 试不同的 json 格式)
print("disk_settings...", end=' ')
# 用 PSQL 直接构造 JSON 字符串
n = 0
for uid in USER_IDS:
    sql = f"INSERT INTO disk_settings (key, value, created_at, updated_at) VALUES ('user_quota_{uid}', '{{\"quota\":1073741824,\"used\":100000}}'::json, NOW(), NOW());"
    out = run(sql)
    if 'ERROR' not in out:
        n += 1
print(f'{n} rows')

# 3. process_signatures (signed_at 必填)
print("process_signatures...", end=' ')
n = insert('process_signatures', ['process_instance_id','inspection_id','signer_type','signer_id','signer_name','signature_data','signed_at','created_at','updated_at'], [
    (pick(PI_IDS), None, random.choice(['user','customer','supervisor']),
     pick(USER_IDS), f'签字人{random.randint(1,5)}',
     'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==',
     rand_dt(300), rand_dt(300), rand_dt(300))
    for _ in range(40)
])
print(f'{n} rows')

ssh.close()
print("\n=== LAST-FINAL DONE ===")
