"""修复 152 的 leads/opps 等表未创建问题（migration 已存在但表已存在）"""
import paramiko
HOST = '152.136.115.121'
USER = 'ubuntu'
PASS = 'Aa782997781.'

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS)

# 1. 查看当前 migration 状态
cmds = [
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | tail -15',
]
for cmd in cmds:
    print('>>>', cmd)
    si, so, se = c.exec_command(cmd)
    print(so.read().decode('utf-8', errors='ignore'))

# 2. 写一个 SQL 直接创建缺失的 5 张表（绕过 migrate）
# leads / opportunities / quotations / quotation_items / referrers / project_pool / sales_follow_ups / sales_follow_up_attachments
sql_script = r"""
-- 1. leads
CREATE TABLE IF NOT EXISTS leads (
  id BIGSERIAL PRIMARY KEY,
  lead_no VARCHAR(32) UNIQUE NOT NULL,
  customer_id BIGINT NULL,
  customer_name VARCHAR(255) NULL,
  contact_name VARCHAR(100) NULL,
  contact_phone VARCHAR(50) NULL,
  source VARCHAR(50) NULL,
  rating VARCHAR(20) NULL DEFAULT 'C',
  stage VARCHAR(30) NULL DEFAULT 'new',
  estimated_amount DECIMAL(12,2) NULL DEFAULT 0,
  notes TEXT NULL,
  owner_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON leads TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE leads_id_seq TO oa_user;

-- 2. opportunities
CREATE TABLE IF NOT EXISTS opportunities (
  id BIGSERIAL PRIMARY KEY,
  opportunity_no VARCHAR(32) UNIQUE NOT NULL,
  lead_id BIGINT NULL,
  customer_id BIGINT NULL,
  customer_name VARCHAR(255) NULL,
  name VARCHAR(255) NOT NULL,
  stage VARCHAR(30) NULL DEFAULT 'requirement',
  estimated_amount DECIMAL(12,2) NULL DEFAULT 0,
  probability INT NULL DEFAULT 50,
  expected_sign_date DATE NULL,
  lost_reason VARCHAR(50) NULL,
  lost_notes TEXT NULL,
  sales_id BIGINT NULL,
  presale_id BIGINT NULL,
  owner_id BIGINT NULL,
  project_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON opportunities TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE opportunities_id_seq TO oa_user;

-- 3. quotations
CREATE TABLE IF NOT EXISTS quotations (
  id BIGSERIAL PRIMARY KEY,
  quotation_no VARCHAR(32) UNIQUE NOT NULL,
  opportunity_id BIGINT NOT NULL,
  version INT NULL DEFAULT 1,
  status VARCHAR(30) NULL DEFAULT 'draft',
  subtotal DECIMAL(12,2) NULL DEFAULT 0,
  discount_rate DECIMAL(5,2) NULL DEFAULT 0,
  discount_amount DECIMAL(12,2) NULL DEFAULT 0,
  tax_rate DECIMAL(5,2) NULL DEFAULT 0,
  tax_amount DECIMAL(12,2) NULL DEFAULT 0,
  total DECIMAL(12,2) NULL DEFAULT 0,
  valid_until DATE NULL,
  notes TEXT NULL,
  creator_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON quotations TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE quotations_id_seq TO oa_user;

-- 4. quotation_items
CREATE TABLE IF NOT EXISTS quotation_items (
  id BIGSERIAL PRIMARY KEY,
  quotation_id BIGINT NOT NULL,
  inventory_item_id BIGINT NULL,
  product_name VARCHAR(255) NOT NULL,
  spec VARCHAR(255) NULL,
  unit VARCHAR(20) NULL,
  quantity DECIMAL(10,2) NULL DEFAULT 1,
  unit_price DECIMAL(12,2) NULL DEFAULT 0,
  subtotal DECIMAL(12,2) NULL DEFAULT 0,
  sort INT NULL DEFAULT 0,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL
);
GRANT ALL ON quotation_items TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE quotation_items_id_seq TO oa_user;

-- 5. referrers
CREATE TABLE IF NOT EXISTS referrers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(50) NULL,
  customer_id BIGINT NULL,
  rate DECIMAL(5,2) NULL DEFAULT 10,
  total_commission DECIMAL(12,2) NULL DEFAULT 0,
  notes TEXT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON referrers TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE referrers_id_seq TO oa_user;

-- 6. project_pool
CREATE TABLE IF NOT EXISTS project_pool (
  id BIGSERIAL PRIMARY KEY,
  opportunity_id BIGINT NULL,
  customer_id BIGINT NULL,
  customer_name VARCHAR(255) NULL,
  name VARCHAR(255) NOT NULL,
  contract_amount DECIMAL(12,2) NULL DEFAULT 0,
  status VARCHAR(30) NULL DEFAULT 'pending',
  expected_start_date DATE NULL,
  expected_end_date DATE NULL,
  project_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON project_pool TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE project_pool_id_seq TO oa_user;

-- 7. sales_follow_ups
CREATE TABLE IF NOT EXISTS sales_follow_ups (
  id BIGSERIAL PRIMARY KEY,
  target_type VARCHAR(50) NOT NULL,
  target_id BIGINT NOT NULL,
  follow_type VARCHAR(50) NULL,
  content TEXT NULL,
  next_follow_date DATE NULL,
  creator_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL,
  deleted_at TIMESTAMP(0) NULL
);
GRANT ALL ON sales_follow_ups TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE sales_follow_ups_id_seq TO oa_user;

-- 8. sales_follow_up_attachments
CREATE TABLE IF NOT EXISTS sales_follow_up_attachments (
  id BIGSERIAL PRIMARY KEY,
  follow_up_id BIGINT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  original_name VARCHAR(255) NULL,
  mime_type VARCHAR(100) NULL,
  size BIGINT NULL,
  path VARCHAR(500) NULL,
  uploader_id BIGINT NULL,
  created_at TIMESTAMP(0) NULL,
  updated_at TIMESTAMP(0) NULL
);
GRANT ALL ON sales_follow_up_attachments TO oa_user;
GRANT USAGE, SELECT ON SEQUENCE sales_follow_up_attachments_id_seq TO oa_user;

-- 写 migration 记录（让 artisan migrate:status 不再 Pending）
INSERT INTO migrations (migration, batch)
SELECT m, COALESCE((SELECT MAX(batch) FROM migrations), 1)
FROM (VALUES
  ('2026_06_19_100001_create_leads_table'),
  ('2026_06_19_100002_create_opportunities_table'),
  ('2026_06_19_100003_create_quotation_and_referrer_tables'),
  ('2026_06_19_100004_create_follow_up_tables'),
  ('2026_06_19_100005_create_project_pool_table')
) AS v(m)
WHERE NOT EXISTS (SELECT 1 FROM migrations WHERE migrations.migration = v.m);
"""

# 写 SQL 到远程文件
sftp = c.open_sftp()
with sftp.open('/tmp/fix_tables.sql', 'w') as f:
    f.write(sql_script)
sftp.close()

# 执行
print('>>> PGPASSWORD=... psql -f /tmp/fix_tables.sql')
si, so, se = c.exec_command('PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -f /tmp/fix_tables.sql 2>&1 | tail -30')
out = so.read().decode('utf-8', errors='ignore')
print(out)
err = se.read().decode('utf-8', errors='ignore')
if err.strip(): print('ERR:', err[:500])

# 验证
cmds = [
    'PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c "\\dt" 2>&1 | grep -E "leads|opportunities|quotations|referrers|project_pool|sales_follow"',
    'cd /var/www/oa-api && sudo -u www-data php artisan migrate:status 2>&1 | tail -10',
]
for cmd in cmds:
    print('>>>', cmd)
    si, so, se = c.exec_command(cmd)
    print(so.read().decode('utf-8', errors='ignore'))

# 3. 登录 + 测 API
print('=== 登录测试 ===')
si, so, se = c.exec_command('curl -s -X POST http://127.0.0.1/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin123"}\' 2>&1')
login_resp = so.read().decode('utf-8', errors='ignore')
print('LOGIN:', login_resp[:300])

import re, json
try:
    j = json.loads(login_resp)
    token = j.get('data', {}).get('token') or j.get('token')
    print('TOKEN:', token[:50] if token else 'EMPTY')
    if token:
        for url in ['/api/sales/leads', '/api/finance/receivables', '/api/knowledge/categories', '/api/finance/payables', '/api/disk/folders']:
            si, so, se = c.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://127.0.0.1{url} -o /dev/null -w "{url}: %{{http_code}}\\n"')
            print(so.read().decode('utf-8', errors='ignore').strip())
except Exception as e:
    print('JSON parse fail:', e)

c.close()
print('\nDONE')
