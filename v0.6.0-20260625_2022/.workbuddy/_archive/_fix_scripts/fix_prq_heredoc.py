import paramiko, time, random
from datetime import datetime, timedelta

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

DB = "oa_user"
DBPWD = "oa_pg_pwd_782997781"
DBNAME = "security_oa"

def get_ids(table, limit=None):
    full = f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -t -c \"SELECT id FROM {table}"
    if limit:
        full += f" ORDER BY id LIMIT {limit}"
    full += ";\""
    stdin, stdout, stderr = ssh.exec_command(full)
    out = stdout.read().decode()
    return [int(x) for x in out.split() if x.strip().isdigit()]

# 修 purchase_payment_requests - 走 heredoc，避免引号被 shell 吞
print("=== purchase_payment_requests (heredoc) ===")
contract_ids = get_ids("purchase_contracts")
supplier_ids = get_ids("suppliers")
user_ids = get_ids("users")
statuses = ['pending', 'approved', 'rejected', 'paid']
payment_types = ['full', 'partial', 'deposit', 'final']

sql_lines = ["INSERT INTO purchase_payment_requests (code, contract_id, supplier_id, amount, payment_type, request_date, status, applicant, applicant_id, reason, approver_id, approved_at, approve_remark) VALUES"]
values = []
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
    values.append(f"('{code}', {contract_id}, {supplier_id}, {amount}, '{payment_type}', '{request_date}', '{status}', '{applicant}', {applicant_id}, '{reason}', {approver_id}, {approved_at}, {remark_v})")

sql_lines.append(',\n'.join(values) + ';')
full_sql = '\n'.join(sql_lines)

# 写到 /tmp 用文件传，避免引号转义
with open(r'D:\work\website\OA\.workbuddy\tmp_prq.sql', 'w', encoding='utf-8') as f:
    f.write(full_sql)

sftp = ssh.open_sftp()
sftp.put(r'D:\work\website\OA\.workbuddy\tmp_prq.sql', '/tmp/prq.sql')
sftp.close()

cmd = f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -f /tmp/prq.sql 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print(f"  STDOUT: {out[:300]}")
print(f"  STDERR: {err[:300] if err else '(empty)'}")

# 验证
stdin, stdout, stderr = ssh.exec_command(
    f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -t -c \"SELECT COUNT(*) FROM purchase_payment_requests;\""
)
print(f"  RESULT count: {stdout.read().decode().strip()}")

# 清临时
ssh.exec_command('rm -f /tmp/prq.sql')

# 总结
print("\n=== 最终统计（12 张目标表）===")
for t in ['jobs','failed_jobs','sessions','cache_locks','role_has_permissions',
          'model_has_permissions','password_reset_tokens','purchase_logistics',
          'purchase_payment_requests','purchase_payments','purchase_shipment_items',
          'purchase_shipments']:
    stdin, stdout, stderr = ssh.exec_command(
        f"export PGPASSWORD='{DBPWD}' && psql -U {DB} -d {DBNAME} -t -c \"SELECT COUNT(*) FROM {t};\""
    )
    cnt = stdout.read().decode().strip().replace('\n', ' ')
    print(f"  {t}: {cnt}")

ssh.close()
print("done")
