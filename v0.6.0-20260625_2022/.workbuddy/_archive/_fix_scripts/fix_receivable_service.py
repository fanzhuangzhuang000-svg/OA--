import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 1) 把 14 条 receivables 的 received_date 散到过去 12 个月，金额对应调整
sql1 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa << 'EOF'
-- 14 条记录按 id 升序，分配到 12 个月 + 1 重复
WITH months AS (
  SELECT generate_series(0, 13) AS idx
)
UPDATE receivables SET
  received_date = (CURRENT_DATE - (months.idx || ' months')::interval)::date,
  received_amount = CASE months.idx
    WHEN 0  THEN 1000000.00
    WHEN 1  THEN 800000.00
    WHEN 2  THEN 1200000.00
    WHEN 3  THEN 950000.00
    WHEN 4  THEN 1100000.00
    WHEN 5  THEN 750000.00
    WHEN 6  THEN 1300000.00
    WHEN 7  THEN 900000.00
    WHEN 8  THEN 1050000.00
    WHEN 9  THEN 850000.00
    WHEN 10 THEN 1150000.00
    WHEN 11 THEN 980000.00
    WHEN 12 THEN 1250000.00
    WHEN 13 THEN 1100000.00
  END,
  amount = CASE months.idx
    WHEN 0  THEN 1000000.00
    WHEN 1  THEN 800000.00
    WHEN 2  THEN 1200000.00
    WHEN 3  THEN 950000.00
    WHEN 4  THEN 1100000.00
    WHEN 5  THEN 750000.00
    WHEN 6  THEN 1300000.00
    WHEN 7  THEN 900000.00
    WHEN 8  THEN 1050000.00
    WHEN 9  THEN 850000.00
    WHEN 10 THEN 1150000.00
    WHEN 11 THEN 980000.00
    WHEN 12 THEN 1250000.00
    WHEN 13 THEN 1100000.00
  END,
  status = 'fully_paid'
FROM months
WHERE receivables.id = (SELECT id FROM receivables ORDER BY id LIMIT 1 OFFSET months.idx);

-- 检查分布
SELECT to_char(received_date, 'YYYY-MM') AS month, count(*), sum(received_amount)::int AS amt
FROM receivables WHERE received_date IS NOT NULL
GROUP BY to_char(received_date, 'YYYY-MM') ORDER BY month;
EOF
"""
stdin, stdout, stderr = ssh.exec_command(sql1)
print("=== receivables redistribution ===")
print(stdout.read().decode())
err = stderr.read().decode()
if err.strip():
    print("STDERR:", err[:500])

# 2) 给 service_orders 增加已完成的工单（有响应时间）
# 先看现有工单 ID
sql2 = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa -c "SELECT id, order_no, status, started_at, completed_at, rating FROM service_orders ORDER BY id;" 2>&1"""
stdin, stdout, stderr = ssh.exec_command(sql2)
print("=== existing service_orders ===")
print(stdout.read().decode())

ssh.close()
