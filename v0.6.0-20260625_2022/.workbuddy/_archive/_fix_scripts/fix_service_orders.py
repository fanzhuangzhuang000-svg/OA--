import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=15)

# 给 3 条 service_orders 补 assigned_at / completed_at（确保 started_at >= assigned_at）
sql = """export PGPASSWORD='oa_pg_pwd_782997781' && psql -U oa_user -d security_oa << 'EOF'
UPDATE service_orders SET
  assigned_at = started_at - interval '45 minutes',
  completed_at = started_at + interval '4 hours',
  confirmed_at = started_at + interval '5 hours'
WHERE id IN (1,2,3);

-- 再插 7 条新增的、有完整时间字段的工单，分布到过去 30 天
INSERT INTO service_orders (
  order_no, customer_id, fault_description, urgency, service_type, status,
  assigned_to, created_by, sla_hours,
  assigned_at, started_at, completed_at, confirmed_at, rating, review,
  created_at, updated_at
)
SELECT
  'SO-DASH-' || lpad(g::text, 3, '0'),
  ((g * 5) % 27) + 1,                                -- 客户 id 在 1-27
  CASE g % 4 WHEN 0 THEN '监控无图像' WHEN 1 THEN '门禁失灵' WHEN 2 THEN '网络断线' ELSE '硬盘报警' END,
  CASE g % 3 WHEN 0 THEN 'high' WHEN 1 THEN 'normal' ELSE 'low' END,
  'warranty',
  'confirmed',
  ((g % 3) + 1)::bigint,                              -- 分配给 user 1-3
  ((g % 3) + 1)::bigint,
  24,
  (CURRENT_DATE - (g || ' days')::interval - interval '6 hours')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '5 hours 30 minutes')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '1 hour')::timestamp,
  (CURRENT_DATE - (g || ' days')::interval - interval '30 minutes')::timestamp,
  4 + (g % 2),
  '处理及时',
  (CURRENT_DATE - (g || ' days')::interval)::timestamp,
  (CURRENT_DATE - (g || ' days')::interval + interval '5 hours')::timestamp
FROM generate_series(1, 7) AS g;

-- 验证
SELECT count(*), avg(EXTRACT(EPOCH FROM (started_at - assigned_at)) / 60)::int AS avg_resp_min
FROM service_orders
WHERE started_at IS NOT NULL AND assigned_at IS NOT NULL AND started_at >= assigned_at;
EOF
"""
stdin, stdout, stderr = ssh.exec_command(sql)
print(stdout.read().decode())
err = stderr.read().decode()
if err.strip():
    print("STDERR:", err[:500])

# 测一下 API
import urllib.request, json
req = urllib.request.Request("http://172.20.0.139/api/dashboard/service-stats",
    headers={"Authorization": "Bearer 505|vz372Noe6LnFj66AZXfHYJZOxKhOBMWTJEBjuYZmd8e94644"})
print("=== service-stats API now ===")
print(urllib.request.urlopen(req).read().decode())

req2 = urllib.request.Request("http://172.20.0.139/api/dashboard/revenue-trend",
    headers={"Authorization": "Bearer 505|vz372Noe6LnFj66AZXfHYJZOxKhOBMWTJEBjuYZmd8e94644"})
print("=== revenue-trend API now ===")
data = json.loads(urllib.request.urlopen(req2).read().decode())
for m in data['data']:
    print(f"  {m['month']}: {m['value']:>12.0f}  height={m['height']}")

ssh.close()
