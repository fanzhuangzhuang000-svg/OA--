import paramiko, time, random
from datetime import datetime, timedelta

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

DB = "oa_user"
DBPWD = "oa_pg_pwd_782997781"
DBNAME = "security_oa"

def q(sql, fetch=False):
    """执行 SQL"""
    full = f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -c \"{sql}\""
    stdin, stdout, stderr = ssh.exec_command(full)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if 'ERROR' in err or 'ERROR' in out:
        # 提取错误行
        for line in (err+out).split('\n'):
            if 'ERROR' in line:
                return ("ERR", line.strip())
        return ("ERR", (err+out)[:300])
    if fetch:
        return out
    return ("OK", out.strip())

def get_ids(table, limit=None):
    full = f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -t -c \"SELECT id FROM {table}"
    if limit:
        full += f" ORDER BY id LIMIT {limit}"
    full += ";\""
    stdin, stdout, stderr = ssh.exec_command(full)
    out = stdout.read().decode()
    return [int(x) for x in out.split() if x.strip().isdigit()]

# 1. 框架表 - jobs/failed_jobs/sessions/cache_locks/role_has_permissions/model_has_permissions/password_reset_tokens
# 全部跳过 (Laravel 框架内部表，不影响前端)

# 2. purchase_shipments - 30 条
print("=== purchase_shipments ===")
contract_ids = get_ids("purchase_contracts")
supplier_ids = get_ids("suppliers")
statuses = ['shipped', 'in_transit', 'delivered', 'pending']
carriers = ['顺丰快递', '京东物流', '德邦物流', '中通快递', '跨越速运', '自提']

batch = []
for i in range(30):
    code = f"PS{time.time_ns()}{i}"
    contract_id = random.choice(contract_ids)
    supplier_id = random.choice(supplier_ids)
    shipped = (datetime(2025,1,1) + timedelta(days=random.randint(0,540))).date()
    arrival = shipped + timedelta(days=random.randint(2,15))
    arrived = arrival + timedelta(days=random.randint(0,5)) if random.random() > 0.4 else None
    status = random.choice(statuses)
    carrier = random.choice(carriers)
    tracking = f"SF{random.randint(100000000,999999999)}{i:02d}"
    consignee = random.choice(['张三', '李四', '王五', '赵六'])
    remark = random.choice(['', '加急', '易碎品', '已签收', '工作日配送', ''])

    arrived_str = f"'{arrived}'" if arrived else "NULL"
    remark_v = f"'{remark}'" if remark else "NULL"

    batch.append(f"('{code}', {contract_id}, {supplier_id}, '{shipped}', '{arrival}', {arrived_str}, '{carrier}', '{tracking}', '{status}', '{consignee}', {remark_v})")

# 分批插入（每 10 条）
for i in range(0, len(batch), 10):
    chunk = batch[i:i+10]
    sql = f"""INSERT INTO purchase_shipments (code, contract_id, supplier_id, shipped_at, expected_arrival_at, arrived_at, carrier, tracking_no, status, consignee, remark) VALUES {','.join(chunk)};"""
    st, msg = q(sql)
    if st == "ERR":
        print(f"  batch {i//10+1} ERR: {msg}")
    else:
        print(f"  batch {i//10+1} OK ({len(chunk)})")
    time.sleep(0.3)

# 3. purchase_shipment_items - 60 条
print("=== purchase_shipment_items ===")
shipment_ids = get_ids("purchase_shipments")
materials = ['海康威视DS-2CD2T47摄像机', '大华DH-IPC-HFW2431T摄像机', '硬盘录像机NVR-8路', 'POE交换机8口', '网线超五类305米', '光纤跳线SC-LC 3米', '支架万向', '电源适配器12V2A', '防水接线盒', '门禁读卡器']
units = ['台', '个', '箱', '套', '米', '盘', '件', '只', '套', '套']

batch = []
for i in range(60):
    shipment_id = random.choice(shipment_ids)
    material = random.choice(materials)
    spec = random.choice(['标准版', '高清', '4MP', 'POE供电', '室内型', '室外防水'])
    qty = random.randint(1, 50)
    unit = random.choice(units)
    batch.append(f"({shipment_id}, '{material}', '{spec}', {qty}, '{unit}')")

for i in range(0, len(batch), 15):
    chunk = batch[i:i+15]
    sql = f"INSERT INTO purchase_shipment_items (shipment_id, material, spec, quantity, unit) VALUES {','.join(chunk)};"
    st, msg = q(sql)
    if st == "ERR":
        print(f"  batch {i//10+1} ERR: {msg}")
    else:
        print(f"  batch {i//10+1} OK ({len(chunk)})")
    time.sleep(0.3)

# 4. purchase_logistics - 50 条（每条 shipment 平均 1-3 条）
print("=== purchase_logistics ===")
events = [
    ('已揽收', '深圳南山集散中心', '揽件成功'),
    ('运输中', '广州转运中心', '到达中转站'),
    ('运输中', '武汉转运中心', '继续运输'),
    ('派送中', '北京海淀分拣中心', '准备派送'),
    ('派送中', '北京海淀分拣中心', '快递员已出发'),
    ('已签收', '客户前台', '已签收'),
    ('运输中', '上海转运中心', '正常中转'),
    ('已揽收', '深圳福田收件点', '上门取件'),
]

batch = []
for sid in shipment_ids[:25]:
    n = random.randint(1, 3)
    for j in range(n):
        status, location, desc = random.choice(events)
        event_at = datetime(2025,1,1) + timedelta(days=random.randint(0,540), hours=random.randint(0,23))
        operator = random.choice(['快递员A', '快递员B', '张师傅', '李师傅'])
        batch.append(f"({sid}, 'SF{random.randint(100000000,999999999)}', '{event_at}', '{location}', '{status}', '{desc}', '{operator}')")

for i in range(0, len(batch), 15):
    chunk = batch[i:i+15]
    sql = f"INSERT INTO purchase_logistics (shipment_id, tracking_no, event_at, location, status, description, operator) VALUES {','.join(chunk)};"
    st, msg = q(sql)
    if st == "ERR":
        print(f"  batch {i//10+1} ERR: {msg}")
    else:
        print(f"  batch {i//10+1} OK ({len(chunk)})")
    time.sleep(0.3)

# 5. purchase_payment_requests - 25 条
print("=== purchase_payment_requests ===")
user_ids = get_ids("users")
statuses = ['pending', 'approved', 'rejected', 'paid']
payment_types = ['full', 'partial', 'deposit', 'final']

batch = []
for i in range(25):
    code = f"PR{time.time_ns()}{i}"
    contract_id = random.choice(contract_ids)
    supplier_id = random.choice(supplier_ids)
    amount = round(random.uniform(5000, 200000), 2)
    payment_type = random.choice(payment_types)
    request_date = (datetime(2025,1,1) + timedelta(days=random.randint(0,540))).date()
    status = random.choice(statuses)
    applicant = random.choice(['张三', '李四', '王五', '赵六'])
    applicant_id = random.choice(user_ids)
    reason = random.choice(['设备采购', '备货付款', '合同尾款', '紧急补货', '季度结算'])
    approver_id = random.choice(user_ids) if status != 'pending' else 'NULL'
    approved_at = f"'{request_date + timedelta(days=random.randint(1,5))}'" if status != 'pending' else 'NULL'
    remark = random.choice(['', '紧急', '已审核', ''])

    remark_v = f"'{remark}'" if remark else "NULL"
    # reason 字段里可能有单引号字符，统一转义
    reason_v = "'" + reason.replace("'", "''") + "'"
    applicant_v = "'" + applicant.replace("'", "''") + "'"

    batch.append(f"('{code}', {contract_id}, {supplier_id}, {amount}, '{payment_type}', '{request_date}', '{status}', {applicant_v}, {applicant_id}, {reason_v}, {approver_id}, {approved_at}, {remark_v})")

for i in range(0, len(batch), 10):
    chunk = batch[i:i+10]
    sql = f"""INSERT INTO purchase_payment_requests (code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, reason, approver_id, approved_at, approve_remark) VALUES {','.join(chunk)};"""
    st, msg = q(sql)
    if st == "ERR":
        print(f"  batch {i//10+1} ERR: {msg}")
    else:
        print(f"  batch {i//10+1} OK ({len(chunk)})")
    time.sleep(0.3)

# 6. purchase_payments - 20 条
print("=== purchase_payments ===")
prq_ids = get_ids("purchase_payment_requests")
methods = ['transfer', 'cash', 'check', 'alipay', 'wechat']

batch = []
for i in range(20):
    code = f"PY{time.time_ns()}{i}"
    prq_id = random.choice(prq_ids) if prq_ids else 'NULL'
    contract_id = random.choice(contract_ids)
    supplier_id = random.choice(supplier_ids)
    amount = round(random.uniform(5000, 200000), 2)
    method = random.choice(methods)
    paid_at = (datetime(2025,1,1) + timedelta(days=random.randint(0,540))).date()
    voucher = f"V{paid_at.strftime('%Y%m%d')}{i:03d}"
    operator = random.choice(['张三', '李四', '王五', '赵六'])
    operator_id = random.choice(user_ids)
    status = 'success'
    remark = random.choice(['', '正常付款', '加急', '已完成'])

    remark_v = f"'{remark}'" if remark else "NULL"
    prq_id_v = prq_id if prq_id != 'NULL' else 'NULL'

    batch.append(f"('{code}', {prq_id_v}, {contract_id}, {supplier_id}, {amount}, '{method}', '{paid_at}', '{voucher}', '{operator}', {operator_id}, '{status}', {remark_v})")

for i in range(0, len(batch), 10):
    chunk = batch[i:i+10]
    sql = f"""INSERT INTO purchase_payments (code, payment_request_id, contract_id, supplier_id, amount, payment_method, paid_at, voucher_no, operator, operator_id, status, remark) VALUES {','.join(chunk)};"""
    st, msg = q(sql)
    if st == "ERR":
        print(f"  batch {i//10+1} ERR: {msg}")
    else:
        print(f"  batch {i//10+1} OK ({len(chunk)})")
    time.sleep(0.3)

# 7. 框架表 - sessions / jobs（要一些用户用着的感觉）
# sessions - 5 条
print("=== sessions ===")
batch = []
for uid in user_ids[:4]:
    sid = f"sess_{time.time_ns()}{uid}"
    ip = f"192.168.1.{random.randint(1,254)}"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    payload = f"_token=abc{uid};user_id={uid}"
    last = int(time.time()) - random.randint(0, 3600)
    batch.append(f"('{sid}', {uid}, '{ip}', '{ua}', '{payload}', {last})")
sql = f"INSERT INTO sessions (id, user_id, ip_address, user_agent, payload, last_activity) VALUES {','.join(batch)};"
st, msg = q(sql)
print(f"  sessions: {st} - {msg[:200] if st=='OK' else msg}")

# jobs - 3 条（占位队列任务）
print("=== jobs ===")
batch = []
for i in range(3):
    queue = random.choice(['default', 'emails', 'notifications'])
    payload = '{"displayName":"App\\\\Jobs\\\\TestJob","job":"test","data":{}}'
    attempts = random.randint(1, 3)
    available = int(time.time()) - random.randint(0, 3600)
    created = available - random.randint(60, 600)
    batch.append(f"('{queue}', '{payload}', {attempts}, {available}, {created})")
sql = f"INSERT INTO jobs (queue, payload, attempts, available_at, created_at) VALUES {','.join(batch)};"
st, msg = q(sql)
print(f"  jobs: {st} - {msg[:200] if st=='OK' else msg}")

# failed_jobs - 2 条
print("=== failed_jobs ===")
batch = []
for i in range(2):
    uuid_str = f"uuid-{time.time_ns()}{i}"
    conn = "redis"
    queue = "default"
    payload = '{"job":"test"}'
    exc = "RuntimeException: test failure"
    batch.append(f"('{uuid_str}', '{conn}', '{queue}', '{payload}', '{exc}', NOW())")
sql = f"INSERT INTO failed_jobs (uuid, connection, queue, payload, exception, failed_at) VALUES {','.join(batch)};"
st, msg = q(sql)
print(f"  failed_jobs: {st} - {msg[:200] if st=='OK' else msg}")

# 总结
print("\n=== 最终统计 ===")
for t in ['jobs','failed_jobs','sessions','cache_locks','role_has_permissions',
          'model_has_permissions','password_reset_tokens','purchase_logistics',
          'purchase_payment_requests','purchase_payments','purchase_shipment_items',
          'purchase_shipments']:
    stdin, stdout, stderr = ssh.exec_command(
        f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -t -c \"SELECT COUNT(*) FROM {t};\""
    )
    print(f"  {t}: {stdout.read().decode().strip()}")

ssh.close()
print("done")
