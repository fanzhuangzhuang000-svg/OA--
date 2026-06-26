import paramiko, json, urllib.request

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

USER_IDS = [1, 71, 72, 73]

# 用 Python 拼 INSERT，每条用真实 user_id
assignees = 'ARRAY[' + ','.join(str(u) for u in USER_IDS) + ']'
creators  = 'ARRAY[' + ','.join(str(u) for u in USER_IDS) + ']'

sql = f"""export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa << 'EOF'
-- 插 12 条完整工单，分配到 user 1/71/72/73
INSERT INTO service_orders (
  order_no, customer_id, fault_description, urgency, service_type, status,
  assigned_to, created_by, sla_hours,
  assigned_at, started_at, completed_at, confirmed_at, rating, review,
  created_at, updated_at
)
SELECT
  'SO-DASH-' || lpad(g::text, 3, '0'),
  ((g * 5) % 27) + 1,
  CASE g % 4 WHEN 0 THEN '监控无图像' WHEN 1 THEN '门禁失灵' WHEN 2 THEN '网络断线' ELSE '硬盘报警' END,
  CASE g % 3 WHEN 0 THEN 'high' WHEN 1 THEN 'normal' ELSE 'low' END,
  'warranty',
  'confirmed',
  CASE g % 4 WHEN 0 THEN 1 WHEN 1 THEN 71 WHEN 2 THEN 72 ELSE 73 END,
  CASE g % 4 WHEN 0 THEN 71 WHEN 1 THEN 72 WHEN 2 THEN 73 ELSE 1 END,
  24,
  (CURRENT_DATE - (g || ' days')::interval - interval '6 hours')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '5 hours 30 minutes')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '1 hour')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '30 minutes')::timestamp,
  4 + (g % 2),
  '处理及时',
  (CURRENT_DATE - (g || ' days')::interval)::timestamp,
  (CURRENT_DATE - (g || ' days')::interval + interval '5 hours')::timestamp
FROM generate_series(1, 12) AS g;

-- 验证平均响应
SELECT count(*) AS total,
       avg(EXTRACT(EPOCH FROM (started_at - assigned_at)) / 60)::int AS avg_resp_min
FROM service_orders
WHERE started_at IS NOT NULL AND assigned_at IS NOT NULL AND started_at >= assigned_at;
EOF
"""
stdin, stdout, stderr = ssh.exec_command(sql)
print("=== service_orders insert ===")
print(stdout.read().decode())
err = stderr.read().decode()
if err.strip():
    print("STDERR:", err[:500])

# 测 API
TOKEN = "505|vz372Noe6LnFj66AZXfHYJZOxKhOBMWTJEBjuYZmd8e94644"
req = urllib.request.Request("http://172.20.0.139/api/dashboard/service-stats",
    headers={"Authorization": f"Bearer {TOKEN}"})
print("=== service-stats API now ===")
print(urllib.request.urlopen(req).read().decode())

ssh.close()
